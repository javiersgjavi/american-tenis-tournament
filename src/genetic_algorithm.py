"""
Genetic Algorithm implementation for American Padel Tournament.
Contains GA logic and fitness functions.
"""

import numpy as np
import random
from collections import defaultdict
from tqdm import tqdm
from joblib import Parallel, delayed

from .dataclasses import Match, Calendar, can_use_multiple_courts
from .utils import generate_random_match, is_valid_match


# ============================================================================
# FITNESS FUNCTIONS (PHASE 2)
# ============================================================================


def calculate_round_conflict_penalty(calendar: Calendar) -> float:
    """
    Calculate penalty for players appearing in multiple matches within the same round.

    This is a HARD CONSTRAINT. If any player is scheduled to play in two or more
    matches simultaneously (same round, different courts), the calendar is INVALID.

    Args:
        calendar: Calendar object to evaluate

    Returns:
        float('inf') if conflicts exist, 0.0 otherwise
    """
    if calendar.n_courts <= 1:
        return 0.0  # No conflicts possible with single court

    if calendar.has_round_conflicts():
        return float("inf")

    return 0.0


def calculate_balance_penalty(calendar: Calendar) -> float:
    """
    Calculate penalty for unbalanced matches per player.

    The penalty is based on the difference between the player with most matches
    and the player with fewest matches. We use squared difference to heavily
    penalize large imbalances.

    Formula: penalty = (max_matches - min_matches)²

    Args:
        calendar: Calendar object to evaluate

    Returns:
        Penalty value (0 = perfect balance, higher = worse balance)
    """
    matches_per_player = calendar.get_matches_per_player()

    if len(matches_per_player) == 0:
        return 0.0

    match_counts = list(matches_per_player.values())
    max_matches = max(match_counts)
    min_matches = min(match_counts)

    penalty = (max_matches - min_matches) ** 2
    return float(penalty)


def calculate_opponent_repetition_penalty(calendar: Calendar) -> float:
    """
    Calculate penalty for repeated opponent pairings.

    For each pair of players that face each other, we count how many times
    they play against each other. The penalty is the sum of (count - 1)²
    for all opponent pairs.

    Formula: penalty = Σ (opponent_count[pair] - 1)² for all opponent pairs

    Args:
        calendar: Calendar object to evaluate

    Returns:
        Penalty value (0 = no repetitions, higher = more repetitions)
    """
    opponent_counts = defaultdict(int)

    for match_vector in calendar.matches:
        match = Match(match_vector=match_vector, n_players=calendar.n_players)
        team1, team2 = match.get_teams()

        # Count all opponent pairings (team1 vs team2)
        for p1 in team1:
            for p2 in team2:
                # Use sorted tuple to avoid counting (A,B) and (B,A) separately
                pair = tuple(sorted([p1, p2]))
                opponent_counts[pair] += 1

    # Calculate penalty: sum of (count - 1)² for each pair
    penalty = sum((count - 1) ** 2 for count in opponent_counts.values())
    return float(penalty)


def calculate_team_repetition_penalty(calendar: Calendar) -> float:
    """
    Calculate penalty for repeated team pairings.

    For each pair of players that play together on the same team, we count
    how many times they team up. The penalty is the sum of (count - 1)²
    for all team pairs.

    Formula: penalty = Σ (team_count[pair] - 1)² for all team pairs

    Args:
        calendar: Calendar object to evaluate

    Returns:
        Penalty value (0 = no repetitions, higher = more repetitions)
    """
    team_counts = defaultdict(int)

    for match_vector in calendar.matches:
        match = Match(match_vector=match_vector, n_players=calendar.n_players)
        team1, team2 = match.get_teams()

        # Count team pairings in team1
        for i, p1 in enumerate(team1):
            for p2 in team1[i + 1 :]:
                pair = tuple(sorted([p1, p2]))
                team_counts[pair] += 1

        # Count team pairings in team2
        for i, p1 in enumerate(team2):
            for p2 in team2[i + 1 :]:
                pair = tuple(sorted([p1, p2]))
                team_counts[pair] += 1

    # Calculate penalty: sum of (count - 1)² for each pair
    penalty = sum((count - 1) ** 2 for count in team_counts.values())
    return float(penalty)


def calculate_waiting_penalty(calendar: Calendar) -> float:
    """
    Calculate penalty for players waiting too long between rounds.

    With multiple courts (n_courts > 1), waiting is measured in ROUNDS, not matches.
    A player is considered to play in a round if they have at least one match in that round.

    For each player, we find the gaps between consecutive rounds they play.
    The penalty is the sum of gap² for all gaps of all players.

    Formula: penalty = Σ Σ (gap)² for all players and their round gaps

    Example with n_courts=2:
        - Round 1: Matches 1-2, Round 2: Matches 3-4, Round 3: Matches 5-6
        - If player A plays in round 1 and round 3, gap is [1] (skipped round 2)
        - Penalty contribution = 1² = 1

    Args:
        calendar: Calendar object to evaluate

    Returns:
        Penalty value (0 = no waiting, higher = more waiting)
    """
    # get_waiting_rounds_per_player() already calculates gaps in terms of rounds
    waiting_rounds = calendar.get_waiting_rounds_per_player()

    penalty = 0.0
    for player, gaps in waiting_rounds.items():
        for gap in gaps:
            penalty += gap**2

    return float(penalty)


def calculate_early_cut_bonus(calendar: Calendar) -> float:
    """
    Calculate bonus for having cut points early in the calendar and maximizing total cut points.

    A cut point is a position where the tournament can be stopped with all
    players having played a balanced number of matches.

    IMPORTANT: With multiple courts (n_courts > 1), cut points are ONLY evaluated
    at round boundaries (end of complete rounds). It doesn't make sense to stop
    in the middle of a round where some courts have played and others haven't.

    Perfect cut: max_difference = 0 (all players played same number)
    Acceptable cut: max_difference ≤ 1

    The bonus rewards:
    1. Calendars where the first cut point appears early (high priority)
    2. Calendars with many cut points throughout (maximize flexibility)
    3. Calendars with well-distributed cut points (uniform spacing)

    Formula:
        bonus = 1000 / (first_perfect_cut_round + 1) +
                perfect_cut_count * 20.0 +
                acceptable_cut_count * 5.0 +
                distribution_bonus

    Args:
        calendar: Calendar object to evaluate

    Returns:
        Bonus value (higher = better, 0 = no early cuts)
    """
    if len(calendar) == 0:
        return 0.0

    first_perfect_cut = None
    first_acceptable_cut = None
    perfect_cut_count = 0
    acceptable_cut_count = 0
    perfect_cut_positions = []
    acceptable_cut_positions = []

    n_courts = calendar.n_courts
    total_rounds = calendar.get_total_rounds()

    # Check cut points only at round boundaries
    for round_num in range(1, total_rounds + 1):
        # Get the match index at the end of this round
        cut_index = round_num * n_courts
        # Make sure we don't exceed the calendar length (last round might be incomplete)
        cut_index = min(cut_index, len(calendar))

        # Count matches per player up to this point
        matches_count = {i: 0 for i in range(calendar.n_players)}

        for i in range(cut_index):
            match = calendar.get_match(i)
            players = match.get_players()
            for player in players:
                matches_count[player] += 1

        counts = list(matches_count.values())
        max_diff = max(counts) - min(counts)

        # Check for perfect cut
        if max_diff == 0:
            if first_perfect_cut is None:
                first_perfect_cut = round_num  # Store round number, not match index
            perfect_cut_count += 1
            perfect_cut_positions.append(round_num)
            acceptable_cut_count += 1  # Perfect cuts are also acceptable
            acceptable_cut_positions.append(round_num)
        # Check for acceptable cut (only if not perfect)
        elif max_diff <= 1:
            if first_acceptable_cut is None:
                first_acceptable_cut = round_num
            acceptable_cut_count += 1
            acceptable_cut_positions.append(round_num)

    bonus = 0.0

    # Main bonus: reward first perfect cut (inversely proportional to round position)
    if first_perfect_cut is not None:
        bonus += 1000.0 / first_perfect_cut
    elif first_acceptable_cut is not None:
        # If no perfect cut, give smaller bonus for acceptable cut
        bonus += 500.0 / first_acceptable_cut

    # IMPROVED: Significant bonus for total number of cut points
    # This maximizes flexibility - more cut points = more options to stop tournament
    bonus += perfect_cut_count * 20.0
    bonus += acceptable_cut_count * 5.0

    # Bonus for well-distributed cut points
    # Calculate distribution quality by measuring gaps between consecutive cuts
    if len(acceptable_cut_positions) >= 2:
        # Calculate gaps between consecutive cut points (in rounds)
        gaps = []
        for i in range(len(acceptable_cut_positions) - 1):
            gap = acceptable_cut_positions[i + 1] - acceptable_cut_positions[i]
            gaps.append(gap)

        # Calculate standard deviation of gaps (lower is better = more uniform)
        if gaps:
            avg_gap = sum(gaps) / len(gaps)
            variance = sum((g - avg_gap) ** 2 for g in gaps) / len(gaps)
            std_dev = variance**0.5

            # Bonus inversely proportional to standard deviation
            # Lower std_dev = more uniform distribution = higher bonus
            # Add 1 to avoid division by zero
            distribution_bonus = 50.0 / (std_dev + 1.0)
            bonus += distribution_bonus

            # Additional bonus if gaps are very uniform (std_dev < 2)
            if std_dev < 2.0:
                bonus += 25.0  # Extra bonus for excellent distribution

    return float(bonus)


def calculate_fitness(
    calendar: Calendar,
    weight_balance: float = 100.0,
    weight_opponent_rep: float = 10.0,
    weight_team_rep: float = 10.0,
    weight_waiting: float = 5.0,
    weight_early_cut: float = 50.0,
) -> float:
    """
    Calculate combined fitness for a calendar.

    Fitness is calculated as negative sum of weighted penalties plus bonus.
    Higher fitness is better.

    HARD CONSTRAINTS (return -inf if violated):
    - All matches must be valid (4 different players)
    - No round conflicts (player in multiple matches of same round)

    Formula:
        fitness = -(
            w1 * penalty_balance +
            w2 * penalty_opponent_repetition +
            w3 * penalty_team_repetition +
            w4 * penalty_waiting
        ) + w5 * bonus_early_cuts

    Args:
        calendar: Calendar object to evaluate
        weight_balance: Weight for balance penalty (default: 100.0 - highest)
        weight_opponent_rep: Weight for opponent repetition (default: 10.0)
        weight_team_rep: Weight for team repetition (default: 10.0)
        weight_waiting: Weight for waiting penalty (default: 5.0)
        weight_early_cut: Weight for early cut bonus (default: 50.0)

    Returns:
        Fitness value (higher is better, -inf for invalid calendars)
    """
    # HARD CONSTRAINT 1: All matches must be valid
    if not calendar.is_valid():
        return float("-inf")

    # HARD CONSTRAINT 2: No round conflicts (player in multiple matches same round)
    penalty_round_conflict = calculate_round_conflict_penalty(calendar)
    if penalty_round_conflict == float("inf"):
        return float("-inf")

    # Calculate all penalties
    penalty_balance = calculate_balance_penalty(calendar)
    penalty_opponent = calculate_opponent_repetition_penalty(calendar)
    penalty_team = calculate_team_repetition_penalty(calendar)
    penalty_waiting = calculate_waiting_penalty(calendar)

    # Calculate bonus
    bonus_cut = calculate_early_cut_bonus(calendar)

    # Combined fitness (penalties are negative, bonus is positive)
    fitness = (
        -(
            weight_balance * penalty_balance
            + weight_opponent_rep * penalty_opponent
            + weight_team_rep * penalty_team
            + weight_waiting * penalty_waiting
        )
        + weight_early_cut * bonus_cut
    )

    return float(fitness)


# ============================================================================
# CUT POINTS DETECTION (PHASE 4)
# ============================================================================


def detect_cut_points(calendar: Calendar) -> tuple[list[int], list[int]]:
    """
    Detect perfect and acceptable cut points in a calendar.

    A cut point is a position where the tournament can be stopped while
    maintaining balance:
    - Perfect cut: max_difference = 0 (all players played same number)
    - Acceptable cut: max_difference ≤ 1

    IMPORTANT: With multiple courts (n_courts > 1), cut points are ONLY evaluated
    at round boundaries (end of complete rounds). The returned indices are
    ROUND NUMBERS (1-based), not match indices.

    Args:
        calendar: Calendar to analyze

    Returns:
        Tuple of (perfect_cuts, acceptable_cuts) where each is a list of round numbers
    """
    perfect_cuts = []
    acceptable_cuts = []

    if len(calendar) == 0:
        return perfect_cuts, acceptable_cuts

    n_courts = calendar.n_courts
    total_rounds = calendar.get_total_rounds()

    # Check cut points only at round boundaries
    for round_num in range(1, total_rounds + 1):
        # Get the match index at the end of this round
        cut_index = round_num * n_courts
        # Make sure we don't exceed the calendar length (last round might be incomplete)
        cut_index = min(cut_index, len(calendar))

        # Count matches per player up to this point
        matches_count = {i: 0 for i in range(calendar.n_players)}

        for i in range(cut_index):
            match = calendar.get_match(i)
            players = match.get_players()
            for player in players:
                matches_count[player] += 1

        # Calculate difference
        counts = list(matches_count.values())
        max_diff = max(counts) - min(counts)

        # Check for perfect cut
        if max_diff == 0:
            perfect_cuts.append(round_num)
            acceptable_cuts.append(round_num)  # Perfect is also acceptable
        # Check for acceptable cut
        elif max_diff <= 1:
            acceptable_cuts.append(round_num)

    return perfect_cuts, acceptable_cuts


def validate_solution(calendar: Calendar) -> tuple[bool, str, str]:
    """
    Validate the quality of a calendar solution.

    Quality levels (based on round position, not match position):
    - EXCELLENT: First perfect cut in first 30% of rounds
    - GOOD: First perfect cut in first 50% of rounds
    - ACCEPTABLE: First acceptable cut in first 60% of rounds
    - REJECTED: No cut points or first cut after 60%

    Also validates that there are no round conflicts (player in multiple
    matches of the same round) when using multiple courts.

    Args:
        calendar: Calendar to validate

    Returns:
        Tuple of (is_valid, quality, message)
        - is_valid: True if solution meets minimum requirements
        - quality: Quality level string
        - message: Descriptive message about the solution
    """
    # Check if all matches are valid
    if not calendar.is_valid():
        return False, "REJECTED", "Calendar contains invalid matches"

    # Check for round conflicts (only relevant with multiple courts)
    if calendar.n_courts > 1 and calendar.has_round_conflicts():
        conflicts = calendar.get_round_conflicts()
        return (
            False,
            "REJECTED",
            f"Calendar has round conflicts: {len(conflicts)} player(s) scheduled "
            f"for multiple matches in the same round",
        )

    # Detect cut points (returns round numbers, not match indices)
    perfect_cuts, acceptable_cuts = detect_cut_points(calendar)

    total_rounds = calendar.get_total_rounds()

    if total_rounds == 0:
        return False, "REJECTED", "Calendar is empty"

    # Check for perfect cuts
    if len(perfect_cuts) > 0:
        first_perfect = perfect_cuts[0]
        position_percent = (first_perfect / total_rounds) * 100

        if position_percent <= 30:
            return (
                True,
                "EXCELLENT",
                f"Excellent! First perfect cut at round {first_perfect} "
                f"({position_percent:.1f}% of calendar). "
                f"Total perfect cuts: {len(perfect_cuts)}",
            )
        elif position_percent <= 50:
            return (
                True,
                "GOOD",
                f"Good solution. First perfect cut at round {first_perfect} "
                f"({position_percent:.1f}% of calendar). "
                f"Total perfect cuts: {len(perfect_cuts)}",
            )
        else:
            return (
                True,
                "ACCEPTABLE",
                f"Acceptable solution. First perfect cut at round {first_perfect} "
                f"({position_percent:.1f}% of calendar). "
                f"Total perfect cuts: {len(perfect_cuts)}",
            )

    # Check for acceptable cuts
    if len(acceptable_cuts) > 0:
        first_acceptable = acceptable_cuts[0]
        position_percent = (first_acceptable / total_rounds) * 100

        if position_percent <= 60:
            return (
                True,
                "ACCEPTABLE",
                f"Acceptable solution. First acceptable cut at round {first_acceptable} "
                f"({position_percent:.1f}% of calendar). "
                f"Total acceptable cuts: {len(acceptable_cuts)}",
            )
        else:
            return (
                False,
                "REJECTED",
                f"Solution rejected. First acceptable cut too late at round {first_acceptable} "
                f"({position_percent:.1f}% of calendar)",
            )

    # No cut points found
    return (
        False,
        "REJECTED",
        "Solution rejected. No cut points found (calendar is very unbalanced)",
    )


# ============================================================================
# GENETIC ALGORITHM CLASS (PHASE 3)
# ============================================================================


class GeneticAlgorithm:
    """
    Genetic Algorithm for optimizing tournament calendars.

    The GA uses:
    - Tournament selection for parent selection
    - Single-point crossover for recombination
    - Multiple mutation operators (swap, replace, regenerate)
    - Elitism to preserve best solutions

    With multiple courts (n_courts > 1):
    - Matches are grouped into rounds
    - n_rounds specifies the number of rounds to play
    - Total matches = n_rounds * n_courts
    - Round conflicts (player in multiple matches same round) are invalid
    """

    def __init__(
        self,
        n_players: int,
        n_rounds: int,
        population_size: int = 100,
        generations: int = 200,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        elitism_size: int = 2,
        weight_balance: float = 100.0,
        weight_opponent_rep: float = 10.0,
        weight_team_rep: float = 10.0,
        weight_waiting: float = 5.0,
        weight_early_cut: float = 50.0,
        n_jobs: int = 1,
        early_stopping_patience: int | None = None,
        n_courts: int = 1,
    ):
        """
        Initialize the Genetic Algorithm.

        Args:
            n_players: Number of players in the tournament
            n_rounds: Number of rounds to play (total matches = n_rounds * n_courts)
            population_size: Size of the population
            generations: Number of generations to evolve
            mutation_rate: Probability of mutation (0.0 to 1.0)
            crossover_rate: Probability of crossover (0.0 to 1.0)
            elitism_size: Number of best individuals to preserve
            weight_balance: Weight for balance penalty
            weight_opponent_rep: Weight for opponent repetition penalty
            weight_team_rep: Weight for team repetition penalty
            weight_waiting: Weight for waiting penalty
            weight_early_cut: Weight for early cut bonus
            n_jobs: Number of parallel jobs for fitness calculation (-1 for all cores, 1 for sequential)
            early_stopping_patience: Number of generations without improvement before stopping (None to disable)
            n_courts: Number of courts available (default: 1 = sequential play)
        """
        self.n_players = n_players
        self.n_courts = n_courts

        # Validate court configuration
        if n_courts < 1:
            raise ValueError(f"n_courts must be >= 1, got {n_courts}")

        if not can_use_multiple_courts(n_players, n_courts):
            min_players = 4 * n_courts
            raise ValueError(
                f"Not enough players for {n_courts} courts. "
                f"Need at least {min_players} players, got {n_players}"
            )

        # Store rounds and calculate total matches
        self.n_rounds = n_rounds
        self.n_matches = n_rounds * n_courts

        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_size = elitism_size
        self.n_jobs = n_jobs
        self.early_stopping_patience = early_stopping_patience

        # Fitness weights
        self.weight_balance = weight_balance
        self.weight_opponent_rep = weight_opponent_rep
        self.weight_team_rep = weight_team_rep
        self.weight_waiting = weight_waiting
        self.weight_early_cut = weight_early_cut

        # Track best fitness over generations
        self.best_fitness_history = []

    def initialize_population(self) -> list[Calendar]:
        """
        Initialize a random population of calendars.

        With multiple courts, generates calendars where no player appears
        in multiple matches of the same round (no round conflicts).

        Returns:
            List of Calendar objects
        """
        population = []
        for _ in range(self.population_size):
            calendar = self._generate_valid_calendar()
            population.append(calendar)

        return population

    def _generate_valid_calendar(self, max_attempts: int = 100) -> Calendar:
        """
        Generate a single valid calendar without round conflicts.

        Args:
            max_attempts: Maximum attempts per round to avoid conflicts

        Returns:
            Valid Calendar object
        """
        matches = []

        for round_num in range(self.n_rounds):
            round_matches = self._generate_round_without_conflicts(max_attempts)
            matches.extend(round_matches)

        matches_array = np.array(matches)
        return Calendar(
            matches=matches_array, n_players=self.n_players, n_courts=self.n_courts
        )

    def _generate_round_without_conflicts(
        self, max_attempts: int = 100
    ) -> list[np.ndarray]:
        """
        Generate matches for a single round without player conflicts.

        Each player can only appear in one match per round.

        Args:
            max_attempts: Maximum attempts to generate a valid round

        Returns:
            List of match vectors for the round
        """
        if self.n_courts == 1:
            # Single court - no conflicts possible
            return [generate_random_match(self.n_players)]

        for _ in range(max_attempts):
            round_matches = []
            players_used = set()
            success = True

            for court in range(self.n_courts):
                # Try to find a valid match for this court
                match_found = False
                for _ in range(50):  # Attempts to find a match
                    match_vector = generate_random_match(self.n_players)
                    # Get players in this match
                    players = set()
                    for i in range(self.n_players):
                        if (
                            match_vector[i] == 1
                            or match_vector[self.n_players + i] == 1
                        ):
                            players.add(i)

                    # Check if any player is already used in this round
                    if not players.intersection(players_used):
                        round_matches.append(match_vector)
                        players_used.update(players)
                        match_found = True
                        break

                if not match_found:
                    success = False
                    break

            if success:
                return round_matches

        # Fallback: generate random matches (may have conflicts, but fitness will be -inf)
        return [generate_random_match(self.n_players) for _ in range(self.n_courts)]

    def calculate_fitness_for_calendar(self, calendar: Calendar) -> float:
        """
        Calculate fitness for a calendar using configured weights.

        Args:
            calendar: Calendar to evaluate

        Returns:
            Fitness value (higher is better)
        """
        return calculate_fitness(
            calendar,
            weight_balance=self.weight_balance,
            weight_opponent_rep=self.weight_opponent_rep,
            weight_team_rep=self.weight_team_rep,
            weight_waiting=self.weight_waiting,
            weight_early_cut=self.weight_early_cut,
        )

    def tournament_selection(
        self,
        population: list[Calendar],
        fitness_scores: list[float],
        tournament_size: int = 3,
    ) -> Calendar:
        """
        Select an individual using tournament selection.

        Args:
            population: List of calendars
            fitness_scores: List of fitness values for each calendar
            tournament_size: Number of individuals in tournament

        Returns:
            Selected calendar
        """
        # Randomly select tournament_size individuals
        tournament_indices = random.sample(range(len(population)), tournament_size)

        # Find the best individual in the tournament
        best_idx = tournament_indices[0]
        best_fitness = fitness_scores[best_idx]

        for idx in tournament_indices[1:]:
            if fitness_scores[idx] > best_fitness:
                best_idx = idx
                best_fitness = fitness_scores[idx]

        return population[best_idx]

    def crossover(
        self, parent1: Calendar, parent2: Calendar
    ) -> tuple[Calendar, Calendar]:
        """
        Perform single-point crossover between two parents.

        With multiple courts, crossover happens at ROUND boundaries to maintain
        round integrity and minimize creation of invalid calendars.

        Args:
            parent1: First parent calendar
            parent2: Second parent calendar

        Returns:
            Tuple of (child1, child2)
        """
        # Check if crossover should happen or if we have only 1 round
        if random.random() > self.crossover_rate or self.n_rounds <= 1:
            # No crossover, return copies of parents
            child1_matches = np.copy(parent1.matches)
            child2_matches = np.copy(parent2.matches)
            return (
                Calendar(
                    matches=child1_matches,
                    n_players=self.n_players,
                    n_courts=self.n_courts,
                ),
                Calendar(
                    matches=child2_matches,
                    n_players=self.n_players,
                    n_courts=self.n_courts,
                ),
            )

        # Choose crossover point at round boundary
        crossover_round = random.randint(1, self.n_rounds - 1)
        crossover_point = crossover_round * self.n_courts

        # Create children by combining parent segments
        child1_matches = np.vstack(
            [parent1.matches[:crossover_point], parent2.matches[crossover_point:]]
        )

        child2_matches = np.vstack(
            [parent2.matches[:crossover_point], parent1.matches[crossover_point:]]
        )

        return (
            Calendar(
                matches=child1_matches, n_players=self.n_players, n_courts=self.n_courts
            ),
            Calendar(
                matches=child2_matches, n_players=self.n_players, n_courts=self.n_courts
            ),
        )

    def mutate(self, calendar: Calendar) -> Calendar:
        """
        Mutate a calendar using one of several mutation operators.

        Mutation types:
        1. Replace round: Replace all matches in a round with new valid ones
        2. Swap rounds: Swap the order of two rounds (preserves round integrity)
        3. Regenerate round: Regenerate a random round without conflicts

        With n_courts > 1, mutations operate on entire ROUNDS to maintain
        round integrity and avoid creating invalid calendars.

        Args:
            calendar: Calendar to mutate

        Returns:
            Mutated calendar
        """
        # Check if mutation should happen
        if random.random() > self.mutation_rate:
            # No mutation, return copy
            matches_copy = np.copy(calendar.matches)
            return Calendar(
                matches=matches_copy, n_players=self.n_players, n_courts=self.n_courts
            )

        # Create a copy of matches
        mutated_matches = np.copy(calendar.matches)

        # Choose mutation type randomly
        mutation_type = random.choice(
            ["replace_round", "swap_rounds", "regenerate_round"]
        )

        if mutation_type == "replace_round" or mutation_type == "regenerate_round":
            # Replace/regenerate all matches in a random round
            round_idx = random.randint(0, self.n_rounds - 1)
            start_match_idx = round_idx * self.n_courts

            # Generate new valid round without conflicts
            new_round_matches = self._generate_round_without_conflicts()
            for i, match_vector in enumerate(new_round_matches):
                mutated_matches[start_match_idx + i] = match_vector

        elif mutation_type == "swap_rounds":
            # Swap two random rounds
            if self.n_rounds >= 2:
                round1, round2 = random.sample(range(self.n_rounds), 2)
                start1 = round1 * self.n_courts
                start2 = round2 * self.n_courts

                # Swap all matches between the two rounds
                for i in range(self.n_courts):
                    mutated_matches[start1 + i], mutated_matches[start2 + i] = (
                        mutated_matches[start2 + i].copy(),
                        mutated_matches[start1 + i].copy(),
                    )

        return Calendar(
            matches=mutated_matches, n_players=self.n_players, n_courts=self.n_courts
        )

    def run(self, verbose: bool = True) -> Calendar:
        """
        Run the genetic algorithm.

        Args:
            verbose: If True, print progress information

        Returns:
            Best calendar found
        """
        # Initialize population
        if verbose:
            print(f"Initializing population of {self.population_size} individuals...")
            if self.n_courts > 1:
                print(f"  Courts: {self.n_courts}")
                print(f"  Rounds: {self.n_rounds}")
                print(
                    f"  Matches: {self.n_matches} ({self.n_courts} matches per round)"
                )

        population = self.initialize_population()

        # Track best individual
        best_calendar = None
        best_fitness = float("-inf")
        generations_without_improvement = 0

        # Evolution loop with progress bar
        pbar = tqdm(range(self.generations), desc="Evolving", disable=not verbose)

        for generation in pbar:
            # Calculate fitness for all individuals (parallelized if n_jobs > 1)
            if self.n_jobs == 1:
                # Sequential execution
                fitness_scores = [
                    self.calculate_fitness_for_calendar(cal) for cal in population
                ]
            else:
                # Parallel execution
                fitness_scores = Parallel(n_jobs=self.n_jobs, prefer="threads")(
                    delayed(self.calculate_fitness_for_calendar)(cal)
                    for cal in population
                )

            # Update best individual
            gen_best_idx = fitness_scores.index(max(fitness_scores))
            gen_best_fitness = fitness_scores[gen_best_idx]
            gen_avg_fitness = sum(fitness_scores) / len(fitness_scores)

            if gen_best_fitness > best_fitness:
                best_fitness = gen_best_fitness
                best_calendar = population[gen_best_idx]
                generations_without_improvement = 0

                # Check if we found a good solution
                is_valid, quality, _ = validate_solution(best_calendar)
                if verbose and is_valid:
                    tqdm.write(
                        f"🎯 Generation {generation + 1}: Found {quality} solution! Fitness: {best_fitness:.2f}"
                    )
            else:
                generations_without_improvement += 1

            # Track fitness history
            self.best_fitness_history.append(best_fitness)

            # Update progress bar
            pbar.set_postfix(
                {
                    "Best": f"{best_fitness:.2f}",
                    "Avg": f"{gen_avg_fitness:.2f}",
                    "No Improv": generations_without_improvement,
                }
            )

            # Check early stopping condition
            if (
                self.early_stopping_patience is not None
                and generations_without_improvement >= self.early_stopping_patience
            ):
                if verbose:
                    tqdm.write(
                        f"\n⏹️  Early stopping triggered after {generation + 1} generations"
                    )
                    tqdm.write(
                        f"   No improvement for {generations_without_improvement} generations"
                    )
                pbar.close()
                if verbose:
                    print(f"\n✓ Optimization completed (early stopping)!")
                    print(f"  Best fitness achieved: {best_fitness:.2f}")
                return best_calendar

            # Create new generation
            new_population = []

            # Elitism: keep best individuals
            elite_indices = sorted(
                range(len(fitness_scores)),
                key=lambda i: fitness_scores[i],
                reverse=True,
            )[: self.elitism_size]

            for idx in elite_indices:
                matches_copy = np.copy(population[idx].matches)
                new_population.append(
                    Calendar(
                        matches=matches_copy,
                        n_players=self.n_players,
                        n_courts=self.n_courts,
                    )
                )

            # Generate offspring to fill the rest of the population
            while len(new_population) < self.population_size:
                # Select parents
                parent1 = self.tournament_selection(population, fitness_scores)
                parent2 = self.tournament_selection(population, fitness_scores)

                # Crossover
                child1, child2 = self.crossover(parent1, parent2)

                # Mutation
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)

                # Add to new population
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)

            # Replace old population
            population = new_population[: self.population_size]

        pbar.close()

        if verbose:
            print(f"\n✓ Optimization completed!")
            print(f"  Best fitness achieved: {best_fitness:.2f}")

        return best_calendar
