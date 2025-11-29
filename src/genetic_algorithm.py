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
# GENETIC ALGORITHM CLASS (TO BE IMPLEMENTED IN PHASE 3)
# ============================================================================

# TODO: Phase 3 - Implement GeneticAlgorithm class
# - initialize_population()
# - tournament_selection()
# - crossover()
# - mutate()
# - calculate_fitness()
# - run()
