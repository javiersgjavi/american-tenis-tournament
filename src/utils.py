"""
Utility functions for American Padel Tournament.
Contains match generation and validation functions.
"""

import numpy as np
import random


def is_valid_match(match_vector: np.ndarray) -> bool:
    """
    Check if a match vector is valid.
    
    A valid match must have:
    - Exactly 4 ones (4 players)
    - Exactly 2 ones in first half (team 1)
    - Exactly 2 ones in second half (team 2)
    - No overlap between teams
    
    Args:
        match_vector: One-hot encoded match vector of length 2*n_players
        
    Returns:
        True if valid, False otherwise
    """
    if len(match_vector) % 2 != 0:
        return False
    
    n = len(match_vector) // 2
    team1 = match_vector[:n]
    team2 = match_vector[n:]
    
    # Check exactly 2 players per team
    if np.sum(team1) != 2 or np.sum(team2) != 2:
        return False
    
    # Check no overlap (no player in both teams)
    for i in range(n):
        if team1[i] == 1 and team2[i] == 1:
            return False
    
    return True


def generate_random_match(n_players: int) -> np.ndarray:
    """
    Generate a random valid match vector.
    
    Args:
        n_players: Number of players in the tournament
        
    Returns:
        Valid match vector of length 2*n_players
    """
    # Select 4 different players randomly
    players = random.sample(range(n_players), 4)
    
    # Randomly assign to teams (2 vs 2)
    team1_players = random.sample(players, 2)
    team2_players = [p for p in players if p not in team1_players]
    
    # Create one-hot encoded vector
    match_vector = np.zeros(2 * n_players, dtype=int)
    
    # Set team 1
    for player in team1_players:
        match_vector[player] = 1
    
    # Set team 2
    for player in team2_players:
        match_vector[n_players + player] = 1
    
    return match_vector

