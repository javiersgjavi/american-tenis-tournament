"""
Output formatting functions for American Padel Tournament.
Handles printing calendars, statistics, and results.
"""

import numpy as np
from .dataclasses import Calendar, Match
from .genetic_algorithm import detect_cut_points, validate_solution


def match_vector_to_string(match_vector: np.ndarray, n_players: int) -> str:
    """
    Convert a match vector to a readable string format.
    
    Args:
        match_vector: One-hot encoded match vector
        n_players: Number of players in the tournament
        
    Returns:
        String representation like "(A,B) vs (C,D)"
    """
    match = Match(match_vector=match_vector, n_players=n_players)
    team1, team2 = match.get_teams()
    
    # Convert indices to letters (A, B, C, ...)
    def idx_to_letter(idx):
        return chr(ord('A') + idx)
    
    team1_str = ','.join(idx_to_letter(p) for p in team1)
    team2_str = ','.join(idx_to_letter(p) for p in team2)
    
    return f"({team1_str}) vs ({team2_str})"


def print_calendar(calendar: Calendar, start_index: int = 1) -> None:
    """
    Print the complete match calendar.
    
    Args:
        calendar: Calendar to print
        start_index: Starting index for match numbering (default: 1)
    """
    if len(calendar) == 0:
        print("Calendar is empty.")
        return
    
    print("\n" + "="*60)
    print("MATCH CALENDAR")
    print("="*60)
    
    for i in range(len(calendar)):
        match_str = match_vector_to_string(
            calendar.matches[i],
            calendar.n_players
        )
        print(f"Match {i + start_index}: {match_str}")
    
    print("="*60)


def print_statistics(calendar: Calendar) -> None:
    """
    Print statistics about the calendar.
    
    Shows:
    - Matches per player
    - Balance information
    - Total matches
    
    Args:
        calendar: Calendar to analyze
    """
    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    
    # Get matches per player
    matches_per_player = calendar.get_matches_per_player()
    
    print(f"\nTotal matches: {len(calendar)}")
    print(f"Total players: {calendar.n_players}")
    
    print("\nMatches per player:")
    for player_idx in sorted(matches_per_player.keys()):
        player_name = chr(ord('A') + player_idx)
        count = matches_per_player[player_idx]
        print(f"  Player {player_name}: {count} matches")
    
    # Balance information
    counts = list(matches_per_player.values())
    if counts:
        max_matches = max(counts)
        min_matches = min(counts)
        avg_matches = sum(counts) / len(counts)
        
        print(f"\nBalance:")
        print(f"  Maximum: {max_matches} matches")
        print(f"  Minimum: {min_matches} matches")
        print(f"  Average: {avg_matches:.2f} matches")
        print(f"  Difference: {max_matches - min_matches}")
    
    print("="*60)


def print_cut_points(calendar: Calendar) -> None:
    """
    Print information about cut points in the calendar.
    
    Args:
        calendar: Calendar to analyze
    """
    print("\n" + "="*60)
    print("CUT POINTS")
    print("="*60)
    
    perfect_cuts, acceptable_cuts = detect_cut_points(calendar)
    
    if len(perfect_cuts) > 0:
        print(f"\nPerfect cuts (all players equal): {len(perfect_cuts)}")
        print(f"  Positions: {perfect_cuts[:10]}")  # Show first 10
        if len(perfect_cuts) > 10:
            print(f"  ... and {len(perfect_cuts) - 10} more")
        print(f"  First perfect cut at match: {perfect_cuts[0]}")
    else:
        print("\nNo perfect cuts found.")
    
    # Show acceptable cuts (excluding perfect ones)
    acceptable_only = [c for c in acceptable_cuts if c not in perfect_cuts]
    if len(acceptable_only) > 0:
        print(f"\nAcceptable cuts (difference ≤ 1): {len(acceptable_only)}")
        print(f"  Positions: {acceptable_only[:10]}")  # Show first 10
        if len(acceptable_only) > 10:
            print(f"  ... and {len(acceptable_only) - 10} more")
    else:
        if len(perfect_cuts) == 0:
            print("No acceptable cuts found.")
    
    print("="*60)


def print_results(
    calendar: Calendar,
    title: str = "AMERICAN PADEL TOURNAMENT - RESULTS"
) -> None:
    """
    Print complete results including calendar, statistics, and validation.
    
    Args:
        calendar: Calendar to display
        title: Title to display at the top
    """
    # Print header
    print("\n" + "="*60)
    print(title.center(60))
    print("="*60)
    
    # Validate solution
    is_valid, quality, message = validate_solution(calendar)
    
    print(f"\nSolution Quality: {quality}")
    print(f"Status: {'✓ Valid' if is_valid else '✗ Invalid'}")
    print(f"\n{message}")
    
    # Print calendar
    print_calendar(calendar)
    
    # Print statistics
    print_statistics(calendar)
    
    # Print cut points
    print_cut_points(calendar)
    
    # Final summary
    print("\n" + "="*60)
    print("END OF RESULTS")
    print("="*60 + "\n")

