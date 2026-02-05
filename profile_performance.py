"""
Performance profiling script for American Padel Tournament.
Measures execution time of key components with detailed breakdown.
"""

import time
import cProfile
import pstats
import io
from src.genetic_algorithm import GeneticAlgorithm, calculate_fitness
from src.dataclasses import Calendar
import numpy as np


def profile_fitness_components():
    """Profile individual fitness function components."""
    print("=" * 70)
    print("PROFILING FITNESS COMPONENTS")
    print("=" * 70)

    # Create a sample calendar
    n_players = 10
    n_rounds = 10
    n_courts = 2
    n_matches = n_rounds * n_courts

    ga = GeneticAlgorithm(
        n_players=n_players,
        n_rounds=n_rounds,
        n_courts=n_courts,
        population_size=1,
        generations=1,
    )

    calendar = ga._generate_valid_calendar()

    # Profile each fitness component
    from src.genetic_algorithm import (
        calculate_round_conflict_penalty,
        calculate_balance_penalty,
        calculate_opponent_repetition_penalty,
        calculate_team_repetition_penalty,
        calculate_waiting_penalty,
        calculate_early_cut_bonus,
    )

    components = [
        ("Round Conflict", calculate_round_conflict_penalty),
        ("Balance", calculate_balance_penalty),
        ("Opponent Repetition", calculate_opponent_repetition_penalty),
        ("Team Repetition", calculate_team_repetition_penalty),
        ("Waiting", calculate_waiting_penalty),
        ("Early Cut Bonus", calculate_early_cut_bonus),
    ]

    iterations = 1000
    print(f"\nRunning {iterations} iterations per component...\n")

    results = []
    for name, func in components:
        start = time.perf_counter()
        for _ in range(iterations):
            func(calendar)
        elapsed = time.perf_counter() - start
        avg_time = (elapsed / iterations) * 1000  # Convert to ms
        results.append((name, elapsed, avg_time))
        print(f"{name:25s}: {elapsed:6.3f}s total, {avg_time:7.4f}ms avg")

    total_time = sum(r[1] for r in results)
    print(f"\n{'TOTAL':25s}: {total_time:6.3f}s")

    # Show percentage breakdown
    print("\nPercentage breakdown:")
    for name, elapsed, _ in results:
        pct = (elapsed / total_time) * 100
        bar = "█" * int(pct / 2)
        print(f"{name:25s}: {pct:5.1f}% {bar}")


def profile_ga_operations():
    """Profile GA operations: selection, crossover, mutation."""
    print("\n" + "=" * 70)
    print("PROFILING GA OPERATIONS")
    print("=" * 70)

    n_players = 10
    n_rounds = 10
    n_courts = 2

    ga = GeneticAlgorithm(
        n_players=n_players,
        n_rounds=n_rounds,
        n_courts=n_courts,
        population_size=100,
        generations=1,
    )

    # Create population
    population = ga.initialize_population()
    fitness_scores = [ga.calculate_fitness_for_calendar(cal) for cal in population]

    iterations = 1000
    print(f"\nRunning {iterations} iterations per operation...\n")

    # Profile tournament selection
    start = time.perf_counter()
    for _ in range(iterations):
        ga.tournament_selection(population, fitness_scores)
    selection_time = time.perf_counter() - start

    # Profile crossover
    parent1, parent2 = population[0], population[1]
    start = time.perf_counter()
    for _ in range(iterations):
        ga.crossover(parent1, parent2)
    crossover_time = time.perf_counter() - start

    # Profile mutation
    start = time.perf_counter()
    for _ in range(iterations):
        ga.mutate(population[0])
    mutation_time = time.perf_counter() - start

    results = [
        ("Tournament Selection", selection_time),
        ("Crossover", crossover_time),
        ("Mutation", mutation_time),
    ]

    for name, elapsed in results:
        avg_time = (elapsed / iterations) * 1000
        print(f"{name:25s}: {elapsed:6.3f}s total, {avg_time:7.4f}ms avg")

    total_time = sum(r[1] for r in results)
    print(f"\n{'TOTAL':25s}: {total_time:6.3f}s")


def profile_full_ga_run():
    """Profile a complete small GA run with cProfile."""
    print("\n" + "=" * 70)
    print("PROFILING FULL GA RUN (50 generations)")
    print("=" * 70)
    print()

    pr = cProfile.Profile()
    pr.enable()

    ga = GeneticAlgorithm(
        n_players=10,
        n_rounds=10,
        n_courts=2,
        population_size=50,
        generations=50,
        mutation_rate=0.2,
        crossover_rate=0.8,
        elitism_size=2,
        n_jobs=1,  # Sequential for profiling
        early_stopping_patience=20,
    )

    start = time.perf_counter()
    best_calendar = ga.run(verbose=False)
    elapsed = time.perf_counter() - start

    pr.disable()

    print(f"Total execution time: {elapsed:.3f}s")
    print(f"\nTop 20 functions by cumulative time:\n")

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    print(s.getvalue())


def profile_calendar_operations():
    """Profile Calendar dataclass methods."""
    print("\n" + "=" * 70)
    print("PROFILING CALENDAR OPERATIONS")
    print("=" * 70)

    n_players = 10
    n_rounds = 10
    n_courts = 2

    ga = GeneticAlgorithm(
        n_players=n_players,
        n_rounds=n_rounds,
        n_courts=n_courts,
        population_size=1,
        generations=1,
    )

    calendar = ga._generate_valid_calendar()

    iterations = 1000
    print(f"\nRunning {iterations} iterations per operation...\n")

    # Profile get_matches_per_player
    start = time.perf_counter()
    for _ in range(iterations):
        calendar.get_matches_per_player()
    mpp_time = time.perf_counter() - start

    # Profile get_waiting_rounds_per_player
    start = time.perf_counter()
    for _ in range(iterations):
        calendar.get_waiting_rounds_per_player()
    wrpp_time = time.perf_counter() - start

    # Profile has_round_conflicts
    start = time.perf_counter()
    for _ in range(iterations):
        calendar.has_round_conflicts()
    hrc_time = time.perf_counter() - start

    # Profile is_valid
    start = time.perf_counter()
    for _ in range(iterations):
        calendar.is_valid()
    valid_time = time.perf_counter() - start

    results = [
        ("get_matches_per_player", mpp_time),
        ("get_waiting_rounds_per_player", wrpp_time),
        ("has_round_conflicts", hrc_time),
        ("is_valid", valid_time),
    ]

    for name, elapsed in results:
        avg_time = (elapsed / iterations) * 1000
        print(f"{name:35s}: {elapsed:6.3f}s total, {avg_time:7.4f}ms avg")

    total_time = sum(r[1] for r in results)
    print(f"\n{'TOTAL':35s}: {total_time:6.3f}s")


if __name__ == "__main__":
    profile_fitness_components()
    profile_ga_operations()
    profile_calendar_operations()
    profile_full_ga_run()
