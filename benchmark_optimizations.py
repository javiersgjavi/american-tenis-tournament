"""
Benchmark script to measure performance improvements from vectorization optimizations.
Compares fitness component execution times.
"""

import time
import json
from datetime import datetime
from src.genetic_algorithm import GeneticAlgorithm

def benchmark_ga_run(label, config, num_runs=3):
    """Run GA benchmark with given configuration."""
    times = []
    fitness_scores = []

    for run in range(num_runs):
        print(f"  Run {run + 1}/{num_runs}...", end=" ", flush=True)

        ga = GeneticAlgorithm(**config)

        start = time.perf_counter()
        best_calendar = ga.run(verbose=False)
        elapsed = time.perf_counter() - start

        best_fitness = ga.calculate_fitness_for_calendar(best_calendar)

        times.append(elapsed)
        fitness_scores.append(best_fitness)

        print(f"{elapsed:.2f}s (fitness: {best_fitness:.2f})")

    avg_time = sum(times) / len(times)
    std_time = (sum((t - avg_time) ** 2 for t in times) / len(times)) ** 0.5
    avg_fitness = sum(fitness_scores) / len(fitness_scores)
    std_fitness = (sum((f - avg_fitness) ** 2 for f in fitness_scores) / len(fitness_scores)) ** 0.5

    result = {
        "label": label,
        "timestamp": datetime.now().isoformat(),
        "config": config,
        "num_runs": num_runs,
        "times": times,
        "fitness_scores": fitness_scores,
        "avg_time": avg_time,
        "std_time": std_time,
        "avg_fitness": avg_fitness,
        "std_fitness": std_fitness,
    }

    return result

def main():
    print("=" * 70)
    print("BENCHMARKING VECTORIZATION OPTIMIZATIONS")
    print("=" * 70)
    print()

    # Standard configuration for benchmarking
    config = {
        "n_players": 10,
        "n_rounds": 10,
        "n_courts": 2,
        "population_size": 50,
        "generations": 50,
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

    print("Configuration:")
    print(f"  Players: {config['n_players']}")
    print(f"  Rounds: {config['n_rounds']}")
    print(f"  Courts: {config['n_courts']}")
    print(f"  Population: {config['population_size']}")
    print(f"  Generations: {config['generations']}")
    print(f"  Runs per test: 3")
    print()

    # Load previous results to compare
    try:
        with open("benchmark_results.json", "r") as f:
            results = json.load(f)
            baseline_results = [r for r in results if r["label"] == "baseline"]
            if baseline_results:
                baseline = baseline_results[-1]  # Most recent baseline
                print(f"Baseline (from {baseline['timestamp'][:10]}):")
                print(f"  Average time: {baseline['avg_time']:.3f}s ± {baseline['std_time']:.3f}s")
                print()
    except FileNotFoundError:
        baseline = None
        results = []

    # Run new benchmark
    print("Running optimized version...")
    new_result = benchmark_ga_run("opt4-vectorize-waiting-conflicts", config)

    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    print(f"New optimized version:")
    print(f"  Average time: {new_result['avg_time']:.3f}s ± {new_result['std_time']:.3f}s")
    print(f"  Average fitness: {new_result['avg_fitness']:.2f} ± {new_result['std_fitness']:.2f}")

    if baseline:
        speedup = baseline['avg_time'] / new_result['avg_time']
        improvement_pct = ((baseline['avg_time'] - new_result['avg_time']) / baseline['avg_time']) * 100

        new_result['speedup_vs_baseline'] = speedup
        new_result['improvement_pct'] = improvement_pct

        print()
        print(f"Comparison to baseline:")
        print(f"  Speedup: {speedup:.2f}x")
        print(f"  Time reduction: {improvement_pct:.1f}%")
        print(f"  Time saved: {baseline['avg_time'] - new_result['avg_time']:.3f}s")

        # Compare to first baseline
        first_baseline = [r for r in results if r["label"] == "baseline"][0]
        total_speedup = first_baseline['avg_time'] / new_result['avg_time']
        print()
        print(f"Total improvement from original baseline:")
        print(f"  Original time: {first_baseline['avg_time']:.3f}s")
        print(f"  Current time: {new_result['avg_time']:.3f}s")
        print(f"  Total speedup: {total_speedup:.2f}x")
        print(f"  Total improvement: {((first_baseline['avg_time'] - new_result['avg_time']) / first_baseline['avg_time']) * 100:.1f}%")

    # Save results
    results.append(new_result)
    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print()
    print("Results saved to benchmark_results.json")

if __name__ == "__main__":
    main()
