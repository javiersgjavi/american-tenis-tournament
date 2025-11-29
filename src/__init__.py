"""
American Padel Tournament - Genetic Algorithm Package
"""

from .dataclasses import Match, Calendar
from .utils import generate_random_match, is_valid_match
from .genetic_algorithm import (
    calculate_balance_penalty,
    calculate_opponent_repetition_penalty,
    calculate_team_repetition_penalty,
    calculate_waiting_penalty,
    calculate_early_cut_bonus,
    calculate_fitness,
    GeneticAlgorithm,
    detect_cut_points,
    validate_solution,
)

__all__ = [
    'Match',
    'Calendar',
    'generate_random_match',
    'is_valid_match',
    'calculate_balance_penalty',
    'calculate_opponent_repetition_penalty',
    'calculate_team_repetition_penalty',
    'calculate_waiting_penalty',
    'calculate_early_cut_bonus',
    'calculate_fitness',
    'GeneticAlgorithm',
    'detect_cut_points',
    'validate_solution',
]
