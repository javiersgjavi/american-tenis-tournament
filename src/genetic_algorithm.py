"""
Genetic Algorithm implementation for American Padel Tournament.
Contains GA logic and fitness functions.
"""

import numpy as np
import random
from collections import defaultdict

from .dataclasses import Match, Calendar
from .utils import generate_random_match, is_valid_match


# ============================================================================
# FITNESS FUNCTIONS (PHASE 2)
# ============================================================================

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
            for p2 in team1[i+1:]:
                pair = tuple(sorted([p1, p2]))
                team_counts[pair] += 1
        
        # Count team pairings in team2
        for i, p1 in enumerate(team2):
            for p2 in team2[i+1:]:
                pair = tuple(sorted([p1, p2]))
                team_counts[pair] += 1
    
    # Calculate penalty: sum of (count - 1)² for each pair
    penalty = sum((count - 1) ** 2 for count in team_counts.values())
    return float(penalty)


def calculate_waiting_penalty(calendar: Calendar) -> float:
    """
    Calculate penalty for players waiting too long between matches.
    
    For each player, we find the gaps between consecutive matches they play.
    The penalty is the sum of gap² for all gaps of all players.
    
    Formula: penalty = Σ Σ (gap)² for all players and their gaps
    
    Example: If player A plays matches [0, 3, 5], gaps are [2, 1],
             penalty contribution = 2² + 1² = 5
    
    Args:
        calendar: Calendar object to evaluate
        
    Returns:
        Penalty value (0 = no waiting, higher = more waiting)
    """
    waiting_rounds = calendar.get_waiting_rounds_per_player()
    
    penalty = 0.0
    for player, gaps in waiting_rounds.items():
        for gap in gaps:
            penalty += gap ** 2
    
    return float(penalty)


def calculate_early_cut_bonus(calendar: Calendar) -> float:
    """
    Calculate bonus for having cut points early in the calendar.
    
    A cut point is an index where the tournament can be stopped with all
    players having played a balanced number of matches.
    
    Perfect cut: max_difference = 0 (all players played same number)
    Acceptable cut: max_difference ≤ 1
    
    The bonus rewards calendars where the first cut point appears early.
    
    Formula: bonus = 1000 / (first_perfect_cut + 1) + additional_bonuses
    
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
    
    # Check each position in the calendar
    for cut_index in range(1, len(calendar) + 1):
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
                first_perfect_cut = cut_index
            perfect_cut_count += 1
        
        # Check for acceptable cut
        if max_diff <= 1 and first_acceptable_cut is None:
            first_acceptable_cut = cut_index
    
    bonus = 0.0
    
    # Main bonus: reward first perfect cut (inversely proportional to position)
    if first_perfect_cut is not None:
        bonus += 1000.0 / first_perfect_cut
    elif first_acceptable_cut is not None:
        # If no perfect cut, give smaller bonus for acceptable cut
        bonus += 500.0 / first_acceptable_cut
    
    # Additional bonus for multiple perfect cuts
    if perfect_cut_count > 1:
        bonus += perfect_cut_count * 10.0
    
    return float(bonus)


def calculate_fitness(
    calendar: Calendar,
    weight_balance: float = 100.0,
    weight_opponent_rep: float = 10.0,
    weight_team_rep: float = 10.0,
    weight_waiting: float = 5.0,
    weight_early_cut: float = 50.0
) -> float:
    """
    Calculate combined fitness for a calendar.
    
    Fitness is calculated as negative sum of weighted penalties plus bonus.
    Higher fitness is better.
    
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
        Fitness value (higher is better)
    """
    # Validate calendar first
    if not calendar.is_valid():
        return float('-inf')  # Invalid calendar gets worst possible fitness
    
    # Calculate all penalties
    penalty_balance = calculate_balance_penalty(calendar)
    penalty_opponent = calculate_opponent_repetition_penalty(calendar)
    penalty_team = calculate_team_repetition_penalty(calendar)
    penalty_waiting = calculate_waiting_penalty(calendar)
    
    # Calculate bonus
    bonus_cut = calculate_early_cut_bonus(calendar)
    
    # Combined fitness (penalties are negative, bonus is positive)
    fitness = -(
        weight_balance * penalty_balance +
        weight_opponent_rep * penalty_opponent +
        weight_team_rep * penalty_team +
        weight_waiting * penalty_waiting
    ) + weight_early_cut * bonus_cut
    
    return float(fitness)


# ============================================================================
# CUT POINTS DETECTION (TO BE IMPLEMENTED IN PHASE 4)
# ============================================================================

# TODO: Phase 4 - Implement cut points detection
# - detect_cut_points()
# - validate_solution()


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
    """
    
    def __init__(
        self,
        n_players: int,
        n_matches: int,
        population_size: int = 100,
        generations: int = 200,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        elitism_size: int = 2,
        weight_balance: float = 100.0,
        weight_opponent_rep: float = 10.0,
        weight_team_rep: float = 10.0,
        weight_waiting: float = 5.0,
        weight_early_cut: float = 50.0
    ):
        """
        Initialize the Genetic Algorithm.
        
        Args:
            n_players: Number of players in the tournament
            n_matches: Number of matches to generate
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
        """
        self.n_players = n_players
        self.n_matches = n_matches
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_size = elitism_size
        
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
        
        Returns:
            List of Calendar objects
        """
        population = []
        for _ in range(self.population_size):
            # Generate random matches for this calendar
            matches = []
            for _ in range(self.n_matches):
                match_vector = generate_random_match(self.n_players)
                matches.append(match_vector)
            
            # Create Calendar object
            matches_array = np.array(matches)
            calendar = Calendar(matches=matches_array, n_players=self.n_players)
            population.append(calendar)
        
        return population
    
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
            weight_early_cut=self.weight_early_cut
        )
    
    def tournament_selection(
        self,
        population: list[Calendar],
        fitness_scores: list[float],
        tournament_size: int = 3
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
    
    def crossover(self, parent1: Calendar, parent2: Calendar) -> tuple[Calendar, Calendar]:
        """
        Perform single-point crossover between two parents.
        
        Args:
            parent1: First parent calendar
            parent2: Second parent calendar
            
        Returns:
            Tuple of (child1, child2)
        """
        # Check if crossover should happen
        if random.random() > self.crossover_rate:
            # No crossover, return copies of parents
            child1_matches = np.copy(parent1.matches)
            child2_matches = np.copy(parent2.matches)
            return (
                Calendar(matches=child1_matches, n_players=self.n_players),
                Calendar(matches=child2_matches, n_players=self.n_players)
            )
        
        # Perform single-point crossover
        crossover_point = random.randint(1, self.n_matches - 1)
        
        # Create children by combining parent segments
        child1_matches = np.vstack([
            parent1.matches[:crossover_point],
            parent2.matches[crossover_point:]
        ])
        
        child2_matches = np.vstack([
            parent2.matches[:crossover_point],
            parent1.matches[crossover_point:]
        ])
        
        return (
            Calendar(matches=child1_matches, n_players=self.n_players),
            Calendar(matches=child2_matches, n_players=self.n_players)
        )
    
    def mutate(self, calendar: Calendar) -> Calendar:
        """
        Mutate a calendar using one of three mutation operators.
        
        Mutation types:
        1. Replace match: Replace one match with a new random match
        2. Swap matches: Swap the order of two matches
        3. Regenerate match: Completely regenerate a random match
        
        Args:
            calendar: Calendar to mutate
            
        Returns:
            Mutated calendar
        """
        # Check if mutation should happen
        if random.random() > self.mutation_rate:
            # No mutation, return copy
            matches_copy = np.copy(calendar.matches)
            return Calendar(matches=matches_copy, n_players=self.n_players)
        
        # Create a copy of matches
        mutated_matches = np.copy(calendar.matches)
        
        # Choose mutation type randomly
        mutation_type = random.choice(['replace', 'swap', 'regenerate'])
        
        if mutation_type == 'replace' or mutation_type == 'regenerate':
            # Replace/regenerate a random match
            match_idx = random.randint(0, self.n_matches - 1)
            mutated_matches[match_idx] = generate_random_match(self.n_players)
        
        elif mutation_type == 'swap':
            # Swap two random matches
            if self.n_matches >= 2:
                idx1, idx2 = random.sample(range(self.n_matches), 2)
                mutated_matches[idx1], mutated_matches[idx2] = (
                    mutated_matches[idx2].copy(),
                    mutated_matches[idx1].copy()
                )
        
        return Calendar(matches=mutated_matches, n_players=self.n_players)
    
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
            print(f"Inicializando población de {self.population_size} individuos...")
        
        population = self.initialize_population()
        
        # Track best individual
        best_calendar = None
        best_fitness = float('-inf')
        
        # Evolution loop
        for generation in range(self.generations):
            # Calculate fitness for all individuals
            fitness_scores = [
                self.calculate_fitness_for_calendar(cal) for cal in population
            ]
            
            # Update best individual
            gen_best_idx = fitness_scores.index(max(fitness_scores))
            gen_best_fitness = fitness_scores[gen_best_idx]
            
            if gen_best_fitness > best_fitness:
                best_fitness = gen_best_fitness
                best_calendar = population[gen_best_idx]
            
            # Track fitness history
            self.best_fitness_history.append(best_fitness)
            
            # Print progress
            if verbose and (generation % 10 == 0 or generation == self.generations - 1):
                print(f"Generación {generation + 1}/{self.generations} - "
                      f"Mejor fitness: {best_fitness:.2f}")
            
            # Create new generation
            new_population = []
            
            # Elitism: keep best individuals
            elite_indices = sorted(
                range(len(fitness_scores)),
                key=lambda i: fitness_scores[i],
                reverse=True
            )[:self.elitism_size]
            
            for idx in elite_indices:
                matches_copy = np.copy(population[idx].matches)
                new_population.append(
                    Calendar(matches=matches_copy, n_players=self.n_players)
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
            population = new_population[:self.population_size]
        
        if verbose:
            print(f"\n¡Optimización completada!")
            print(f"Mejor fitness alcanzado: {best_fitness:.2f}")
        
        return best_calendar
