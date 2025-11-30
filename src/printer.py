"""
Output formatting functions for American Padel Tournament.
Handles printing calendars, statistics, and results.
"""

import csv
import numpy as np
from pathlib import Path
from io import StringIO
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
        return chr(ord("A") + idx)

    team1_str = ",".join(idx_to_letter(p) for p in team1)
    team2_str = ",".join(idx_to_letter(p) for p in team2)

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

    print("\n" + "=" * 60)
    print("MATCH CALENDAR")
    print("=" * 60)

    for i in range(len(calendar)):
        match_str = match_vector_to_string(calendar.matches[i], calendar.n_players)
        print(f"Match {i + start_index}: {match_str}")

    print("=" * 60)


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
    print("\n" + "=" * 60)
    print("STATISTICS")
    print("=" * 60)

    # Get matches per player
    matches_per_player = calendar.get_matches_per_player()

    print(f"\nTotal matches: {len(calendar)}")
    print(f"Total players: {calendar.n_players}")

    print("\nMatches per player:")
    for player_idx in sorted(matches_per_player.keys()):
        player_name = chr(ord("A") + player_idx)
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

    print("=" * 60)


def print_cut_points(calendar: Calendar) -> None:
    """
    Print information about cut points in the calendar.

    Args:
        calendar: Calendar to analyze
    """
    print("\n" + "=" * 60)
    print("CUT POINTS")
    print("=" * 60)

    perfect_cuts, acceptable_cuts = detect_cut_points(calendar)

    if len(perfect_cuts) > 0:
        print(f"\nPerfect cuts (all players equal): {len(perfect_cuts)}")
        print(f"  Positions: {perfect_cuts}")  # Show ALL
        print(f"  First perfect cut at match: {perfect_cuts[0]}")
    else:
        print("\nNo perfect cuts found.")

    # Show acceptable cuts (excluding perfect ones)
    acceptable_only = [c for c in acceptable_cuts if c not in perfect_cuts]
    if len(acceptable_only) > 0:
        print(f"\nAcceptable cuts (difference ≤ 1): {len(acceptable_only)}")
        print(f"  Positions: {acceptable_only}")  # Show ALL
    else:
        if len(perfect_cuts) == 0:
            print("No acceptable cuts found.")

    print("=" * 60)


def print_heuristic_details(calendar: Calendar) -> None:
    """
    Print detailed statistics about heuristic objectives.

    Shows detailed information about:
    - Waiting times per player
    - Team repetitions
    - Opponent repetitions
    - Cut points flexibility

    Args:
        calendar: Calendar to analyze
    """
    from collections import defaultdict

    print("\n" + "=" * 60)
    print("DETAILED HEURISTIC ANALYSIS")
    print("=" * 60)

    # 1. WAITING TIMES ANALYSIS
    print("\n📊 1. WAITING TIMES (Rounds without playing)")
    print("-" * 60)

    waiting_rounds = calendar.get_waiting_rounds_per_player()

    if waiting_rounds:
        max_wait_overall = 0
        total_wait_time = 0
        player_max_waits = {}

        for player_idx, gaps in waiting_rounds.items():
            if gaps:
                max_wait = max(gaps)
                total_wait = sum(gaps)
                avg_wait = total_wait / len(gaps) if gaps else 0

                player_name = chr(ord("A") + player_idx)
                player_max_waits[player_name] = max_wait

                print(f"  Player {player_name}:")
                print(f"    • Maximum wait: {max_wait} rounds")
                print(f"    • Total wait: {total_wait} rounds")
                print(f"    • Average wait: {avg_wait:.2f} rounds")
                print(f"    • Number of gaps: {len(gaps)}")

                max_wait_overall = max(max_wait_overall, max_wait)
                total_wait_time += total_wait

        print(f"\n  📈 Waiting summary:")
        print(f"    • Global maximum wait: {max_wait_overall} rounds")
        if player_max_waits:
            worst_player = max(player_max_waits, key=player_max_waits.get)
            print(
                f"    • Player with longest wait: {worst_player} ({player_max_waits[worst_player]} rounds)"
            )
        print(f"    • Total waiting time: {total_wait_time} rounds")
    else:
        print("  ✓ No waiting times (all play consecutively)")

    # 2. TEAM REPETITIONS ANALYSIS
    print("\n🤝 2. TEAM REPETITIONS")
    print("-" * 60)

    team_counts = defaultdict(int)

    for match_vector in calendar.matches:
        match = Match(match_vector=match_vector, n_players=calendar.n_players)
        team1, team2 = match.get_teams()

        # Count team pairings
        for i, p1 in enumerate(team1):
            for p2 in team1[i + 1 :]:
                pair = tuple(sorted([p1, p2]))
                team_counts[pair] += 1

        for i, p1 in enumerate(team2):
            for p2 in team2[i + 1 :]:
                pair = tuple(sorted([p1, p2]))
                team_counts[pair] += 1

    if team_counts:
        max_repetitions = max(team_counts.values())
        repeated_teams = [
            (pair, count) for pair, count in team_counts.items() if count > 1
        ]

        print(f"  Total unique pairs: {len(team_counts)}")
        print(f"  Repeated pairs: {len(repeated_teams)}")
        print(f"  Maximum repetitions: {max_repetitions} times")

        if repeated_teams:
            # Sort by repetitions (descending)
            repeated_teams.sort(key=lambda x: x[1], reverse=True)
            print(f"\n  Top 5 most repeated pairs:")
            for pair, count in repeated_teams[:5]:
                p1_name = chr(ord("A") + pair[0])
                p2_name = chr(ord("A") + pair[1])
                print(f"    • ({p1_name},{p2_name}): {count} times")
        else:
            print("  ✓ No team repetitions")

    # 3. OPPONENT REPETITIONS ANALYSIS
    print("\n⚔️  3. OPPONENT REPETITIONS")
    print("-" * 60)

    opponent_counts = defaultdict(int)

    for match_vector in calendar.matches:
        match = Match(match_vector=match_vector, n_players=calendar.n_players)
        team1, team2 = match.get_teams()

        # Count opponent pairings
        for p1 in team1:
            for p2 in team2:
                pair = tuple(sorted([p1, p2]))
                opponent_counts[pair] += 1

    if opponent_counts:
        max_opponent_reps = max(opponent_counts.values())
        repeated_opponents = [
            (pair, count) for pair, count in opponent_counts.items() if count > 1
        ]

        print(f"  Total unique matchups: {len(opponent_counts)}")
        print(f"  Repeated matchups: {len(repeated_opponents)}")
        print(f"  Maximum repetitions: {max_opponent_reps} times")

        if repeated_opponents:
            # Sort by repetitions (descending)
            repeated_opponents.sort(key=lambda x: x[1], reverse=True)
            print(f"\n  Top 5 most repeated matchups:")
            for pair, count in repeated_opponents[:5]:
                p1_name = chr(ord("A") + pair[0])
                p2_name = chr(ord("A") + pair[1])
                print(f"    • {p1_name} vs {p2_name}: {count} times")
        else:
            print("  ✓ No opponent repetitions")

    # 4. CUT POINTS FLEXIBILITY
    print("\n✂️  4. CALENDAR FLEXIBILITY (Cut points)")
    print("-" * 60)

    perfect_cuts, acceptable_cuts = detect_cut_points(calendar)

    n_matches = len(calendar)
    flexibility_percent = (
        (len(acceptable_cuts) / n_matches * 100) if n_matches > 0 else 0
    )

    print(f"  Total matches: {n_matches}")
    print(f"  Perfect cut points: {len(perfect_cuts)}")
    print(f"  Acceptable cut points: {len(acceptable_cuts)}")
    print(f"  Flexibility: {flexibility_percent:.1f}% of calendar")

    if perfect_cuts:
        first_perfect_position = (
            (perfect_cuts[0] / n_matches * 100) if n_matches > 0 else 0
        )
        print(f"\n  📍 First perfect cut:")
        print(f"    • Position: match {perfect_cuts[0]}")
        print(f"    • Percentage: {first_perfect_position:.1f}% of calendar")

    if acceptable_cuts:
        first_acceptable_position = (
            (acceptable_cuts[0] / n_matches * 100) if n_matches > 0 else 0
        )
        print(f"\n  📍 First acceptable cut:")
        print(f"    • Position: match {acceptable_cuts[0]}")
        print(f"    • Percentage: {first_acceptable_position:.1f}% of calendar")

    # Distribution analysis
    if len(acceptable_cuts) >= 2:
        gaps = []
        for i in range(len(acceptable_cuts) - 1):
            gap = acceptable_cuts[i + 1] - acceptable_cuts[i]
            gaps.append(gap)

        if gaps:
            avg_gap = sum(gaps) / len(gaps)
            min_gap = min(gaps)
            max_gap = max(gaps)
            variance = sum((g - avg_gap) ** 2 for g in gaps) / len(gaps)
            std_dev = variance**0.5

            print(f"\n  📏 Distribution of cut points:")
            print(f"    • Average gap: {avg_gap:.2f} matches")
            print(f"    • Minimum gap: {min_gap} matches")
            print(f"    • Maximum gap: {max_gap} matches")
            print(f"    • Std deviation: {std_dev:.2f}")

            # Distribution quality assessment
            if std_dev < 2.0:
                print(f"    ✓ EXCELLENT distribution (very uniform)")
            elif std_dev < 4.0:
                print(f"    ✓ GOOD distribution (quite uniform)")
            elif std_dev < 6.0:
                print(f"    ⚠ ACCEPTABLE distribution (moderately uniform)")
            else:
                print(f"    ⚠ IRREGULAR distribution (gaps vary significantly)")

    # Overall quality assessment
    print(f"\n  🎯 Flexibility assessment:")
    if flexibility_percent >= 50:
        print(
            f"    ✓ EXCELLENT - Very flexible ({flexibility_percent:.1f}% are cut points)"
        )
    elif flexibility_percent >= 30:
        print(
            f"    ✓ GOOD - Quite flexible ({flexibility_percent:.1f}% are cut points)"
        )
    elif flexibility_percent >= 15:
        print(
            f"    ⚠ ACCEPTABLE - Moderately flexible ({flexibility_percent:.1f}% are cut points)"
        )
    else:
        print(
            f"    ⚠ LOW - Little flexibility ({flexibility_percent:.1f}% are cut points)"
        )

    print("=" * 60)


def print_results(
    calendar: Calendar, title: str = "AMERICAN PADEL TOURNAMENT - RESULTS"
) -> None:
    """
    Print complete results including calendar, statistics, and validation.

    Args:
        calendar: Calendar to display
        title: Title to display at the top
    """
    # Print header
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)

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

    # Print detailed heuristic analysis
    print_heuristic_details(calendar)

    # Final summary
    print("\n" + "=" * 60)
    print("END OF RESULTS")
    print("=" * 60 + "\n")


def export_calendar_to_csv(
    calendar: Calendar, output_path: str | Path, include_cut_points: bool = True
) -> None:
    """
    Export calendar to CSV file with optional cut point markers.

    Args:
        calendar: Calendar to export
        output_path: Path to output CSV file
        include_cut_points: Whether to include cut point markers
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Detect cut points if needed
    perfect_cuts, acceptable_cuts = [], []
    if include_cut_points:
        perfect_cuts, acceptable_cuts = detect_cut_points(calendar)

    # Write CSV
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Header
        writer.writerow(
            ["Match #", "Team 1", "Team 2", "Perfect Cut", "Acceptable Cut"]
        )

        # Matches
        for i, match_vector in enumerate(calendar.matches):
            match_num = i + 1
            match_str = match_vector_to_string(match_vector, calendar.n_players)

            # Parse teams from string
            parts = match_str.split(" vs ")
            team1 = parts[0].strip("()")
            team2 = parts[1].strip("()")

            # Check if this is a cut point
            is_perfect = "✓" if match_num in perfect_cuts else ""
            is_acceptable = "✓" if match_num in acceptable_cuts else ""

            writer.writerow([match_num, team1, team2, is_perfect, is_acceptable])


def export_results_to_txt(
    calendar: Calendar, output_path: str | Path, include_full_analysis: bool = True
) -> None:
    """
    Export complete results to TXT file.

    Args:
        calendar: Calendar to export
        output_path: Path to output TXT file
        include_full_analysis: Whether to include full heuristic analysis
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Capture all print output
    import sys

    old_stdout = sys.stdout
    sys.stdout = buffer = StringIO()

    try:
        # Print all results (this will go to buffer)
        print_results(calendar)
    finally:
        # Restore stdout
        sys.stdout = old_stdout

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(buffer.getvalue())


def export_all_outputs(
    calendar: Calendar,
    output_dir: str | Path = "outputs",
    base_filename: str = "tournament",
) -> dict[str, Path]:
    """
    Export all outputs (CSV and TXT) to the specified directory.

    Args:
        calendar: Calendar to export
        output_dir: Directory for output files (default: "outputs")
        base_filename: Base name for output files (default: "tournament")

    Returns:
        Dictionary with paths to created files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filenames
    csv_path = output_dir / f"{base_filename}_calendar.csv"
    txt_path = output_dir / f"{base_filename}_results.txt"

    # Export files
    export_calendar_to_csv(calendar, csv_path, include_cut_points=True)
    export_results_to_txt(calendar, txt_path, include_full_analysis=True)

    return {"csv": csv_path, "txt": txt_path}
