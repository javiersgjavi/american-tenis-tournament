"""
Benchmark script for measuring genetic algorithm performance.
Runs a standard tournament configuration and measures execution time.
"""

import time
import json
from datetime import datetime
from pathlib import Path
import numpy as np

from src.genetic_algorithm import GeneticAlgorithm

# Standard test configuration
BENCHMARK_CONFIG = {
    "n_players": 10,
    "n_rounds": 10,
    "n_courts": 2,
    "population_size": 50,  # Reduced for faster benchmarking
    "generations": 50,      # Reduced for faster benchmarking
    "mutation_rate": 0.2,
    "crossover_rate": 0.8,
    "elitism_size": 2,
    "weight_balance": 100.0,
    "weight_opponent_rep": 10.0,
    "weight_team_rep": 10.0,
    "weight_waiting": 5.0,
    "weight_early_cut": 75.0,
    "n_jobs": -1,
    "early_stopping_patience": 20,
}

RESULTS_FILE = Path("benchmark_results.json")


def load_results():
    """Load previous benchmark results."""
    if RESULTS_FILE.exists():
        with open(RESULTS_FILE, "r") as f:
            return json.load(f)
    return []


def save_result(result):
    """Save a new benchmark result."""
    results = load_results()
    results.append(result)
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)


def run_benchmark(label="baseline", num_runs=3):
    """
    Run benchmark with current implementation.

    Args:
        label: Label for this benchmark (e.g., "baseline", "optimization-1")
        num_runs: Number of runs to average

    Returns:
        Dict with benchmark results
    """
    print(f"\n{'='*60}")
    print(f"Running benchmark: {label}")
    print(f"{'='*60}")
    print(f"Configuration: {BENCHMARK_CONFIG}")
    print(f"Number of runs: {num_runs}")
    print()

    times = []
    fitness_scores = []

    for run in range(num_runs):
        print(f"\n--- Run {run + 1}/{num_runs} ---")

        # Create GA instance
        ga = GeneticAlgorithm(**BENCHMARK_CONFIG)

        # Measure time
        start_time = time.time()
        best_calendar = ga.run(verbose=True)
        elapsed_time = time.time() - start_time

        # Get best fitness
        best_fitness = ga.best_fitness_history[-1] if ga.best_fitness_history else 0

        times.append(elapsed_time)
        fitness_scores.append(best_fitness)

        print(f"Run {run + 1} completed in {elapsed_time:.2f}s, best fitness: {best_fitness:.2f}")

    # Calculate statistics
    avg_time = np.mean(times)
    std_time = np.std(times)
    avg_fitness = np.mean(fitness_scores)
    std_fitness = np.std(fitness_scores)

    result = {
        "label": label,
        "timestamp": datetime.now().isoformat(),
        "config": BENCHMARK_CONFIG,
        "num_runs": num_runs,
        "times": times,
        "fitness_scores": fitness_scores,
        "avg_time": avg_time,
        "std_time": std_time,
        "avg_fitness": avg_fitness,
        "std_fitness": std_fitness,
    }

    # Print summary
    print(f"\n{'='*60}")
    print(f"Benchmark Results: {label}")
    print(f"{'='*60}")
    print(f"Average time: {avg_time:.2f}s ± {std_time:.2f}s")
    print(f"Average fitness: {avg_fitness:.2f} ± {std_fitness:.2f}")

    # Compare with previous results
    previous_results = load_results()
    if previous_results:
        baseline = previous_results[0]
        speedup = baseline["avg_time"] / avg_time
        time_saved = baseline["avg_time"] - avg_time
        improvement_pct = ((baseline["avg_time"] - avg_time) / baseline["avg_time"]) * 100

        print(f"\nComparison with baseline:")
        print(f"  Speedup: {speedup:.2f}x")
        print(f"  Time saved: {time_saved:.2f}s ({improvement_pct:.1f}% faster)")

        result["speedup_vs_baseline"] = speedup
        result["improvement_pct"] = improvement_pct

    print(f"{'='*60}\n")

    # Save result
    save_result(result)

    return result


def print_all_results():
    """Print summary of all benchmark results."""
    results = load_results()

    if not results:
        print("No benchmark results found.")
        return

    print(f"\n{'='*60}")
    print("BENCHMARK HISTORY")
    print(f"{'='*60}\n")

    baseline_time = results[0]["avg_time"]

    for i, result in enumerate(results):
        label = result["label"]
        avg_time = result["avg_time"]
        avg_fitness = result["avg_fitness"]
        timestamp = result["timestamp"]

        if i == 0:
            print(f"{i+1}. {label} (BASELINE)")
        else:
            speedup = baseline_time / avg_time
            improvement = ((baseline_time - avg_time) / baseline_time) * 100
            print(f"{i+1}. {label} - {speedup:.2f}x faster ({improvement:.1f}% improvement)")

        print(f"   Time: {avg_time:.2f}s | Fitness: {avg_fitness:.2f}")
        print(f"   Date: {timestamp[:19]}")
        print()

    print(f"{'='*60}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark genetic algorithm performance")
    parser.add_argument("--label", default="baseline", help="Label for this benchmark")
    parser.add_argument("--runs", type=int, default=3, help="Number of runs to average")
    parser.add_argument("--show-history", action="store_true", help="Show all benchmark results")

    args = parser.parse_args()

    if args.show_history:
        print_all_results()
    else:
        run_benchmark(label=args.label, num_runs=args.runs)
        print_all_results()
