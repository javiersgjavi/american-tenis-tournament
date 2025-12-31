#!/usr/bin/env python3
"""
Hyperparameter Optimization Script for American Padel Tournament.

This script runs systematic hyperparameter optimization tests to find
the best configurations for different tournament scenarios.

Usage:
    python run_hyperparameter_optimization.py [--quick] [--scenario SCENARIO]

Options:
    --quick: Run quick tests with fewer trials (faster, less accurate)
    --scenario: Test specific scenario (small/medium/large/all)

Author: AI System
Date: 2025-11-29
"""

import argparse
import sys
from pathlib import Path
from src.hyperparameter_optimizer import HyperparameterOptimizer, HyperparameterConfig
from analyze_results import print_analysis


def run_baseline_test(
    optimizer: HyperparameterOptimizer, config: HyperparameterConfig, n_trials: int = 10
):
    """Run baseline test with default configuration."""
    print("\n" + "=" * 60)
    print("BASELINE TEST - Default Configuration")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Players: {config.n_players}")
    print(f"  Matches: {config.n_matches}")
    print(f"  Population: {config.population_size}")
    print(f"  Generations: {config.generations}")
    print(f"  Mutation Rate: {config.mutation_rate}")
    print(f"  Crossover Rate: {config.crossover_rate}")
    print(f"  Elitism: {config.elitism_size}")

    results = optimizer.run_multiple_trials(config, n_trials=n_trials, verbose=True)
    optimizer._print_summary(results, "Baseline")

    return results


def run_small_tournament_optimization(quick: bool = False):
    """Optimize hyperparameters for small tournaments (4-5 players, 10-20 matches)."""
    print("\n" + "#" * 60)
    print("# SMALL TOURNAMENT OPTIMIZATION (4-5 players, 10-20 matches)")
    print("#" * 60)

    optimizer = HyperparameterOptimizer(output_dir="optimization_results/small")
    base_config = HyperparameterConfig.default(n_players=5, n_matches=15)

    n_trials = 3 if quick else 5

    # Baseline
    run_baseline_test(optimizer, base_config, n_trials=n_trials)

    # Test parameters
    optimizer.test_population_sizes(
        base_config, sizes=[25, 50, 75, 100], n_trials=n_trials
    )
    optimizer.test_generation_counts(
        base_config, counts=[50, 100, 150], n_trials=n_trials
    )
    optimizer.test_mutation_rates(
        base_config, rates=[0.05, 0.1, 0.15, 0.2], n_trials=n_trials
    )
    optimizer.test_crossover_rates(
        base_config, rates=[0.6, 0.7, 0.8, 0.9], n_trials=n_trials
    )
    optimizer.test_elitism_sizes(base_config, sizes=[1, 2, 3], n_trials=n_trials)

    # Analysis
    optimizer.print_analysis()

    # Export results
    optimizer.export_to_csv("small_tournament_results.csv")
    optimizer.export_to_json("small_tournament_results.json")

    # Best configuration
    best_config, best_result = optimizer.get_best_configuration("final_fitness")
    print("\n" + "=" * 60)
    print("BEST CONFIGURATION FOR SMALL TOURNAMENTS")
    print("=" * 60)
    print(f"  Population: {best_config.population_size}")
    print(f"  Generations: {best_config.generations}")
    print(f"  Mutation Rate: {best_config.mutation_rate}")
    print(f"  Crossover Rate: {best_config.crossover_rate}")
    print(f"  Elitism: {best_config.elitism_size}")
    print(f"\n  Best Fitness: {best_result.final_fitness:.2f}")
    print(f"  Quality: {best_result.quality_level}")
    print(f"  Time: {best_result.execution_time:.2f}s")
    print(f"  Cut Points: {best_result.acceptable_cuts_count}")

    # Display detailed analysis
    results_file = Path("optimization_results/small/small_tournament_results.json")
    if results_file.exists():
        print_analysis(results_file)


def run_medium_tournament_optimization(quick: bool = False):
    """Optimize hyperparameters for medium tournaments (6-7 players, 30-50 matches)."""
    print("\n" + "#" * 60)
    print("# MEDIUM TOURNAMENT OPTIMIZATION (6-7 players, 30-50 matches)")
    print("#" * 60)

    optimizer = HyperparameterOptimizer(output_dir="optimization_results/medium")
    base_config = HyperparameterConfig.default(n_players=7, n_matches=30)

    n_trials = 3 if quick else 5

    # Baseline
    run_baseline_test(optimizer, base_config, n_trials=n_trials)

    # Test parameters
    optimizer.test_population_sizes(
        base_config, sizes=[50, 75, 100, 150], n_trials=n_trials
    )
    optimizer.test_generation_counts(
        base_config, counts=[100, 200, 300], n_trials=n_trials
    )
    optimizer.test_mutation_rates(
        base_config, rates=[0.05, 0.1, 0.15, 0.2], n_trials=n_trials
    )
    optimizer.test_crossover_rates(
        base_config, rates=[0.6, 0.7, 0.8, 0.9], n_trials=n_trials
    )
    optimizer.test_elitism_sizes(base_config, sizes=[1, 2, 3, 5], n_trials=n_trials)

    # Analysis
    optimizer.print_analysis()

    # Export results
    optimizer.export_to_csv("medium_tournament_results.csv")
    optimizer.export_to_json("medium_tournament_results.json")

    # Best configuration
    best_config, best_result = optimizer.get_best_configuration("final_fitness")
    print("\n" + "=" * 60)
    print("BEST CONFIGURATION FOR MEDIUM TOURNAMENTS")
    print("=" * 60)
    print(f"  Population: {best_config.population_size}")
    print(f"  Generations: {best_config.generations}")
    print(f"  Mutation Rate: {best_config.mutation_rate}")
    print(f"  Crossover Rate: {best_config.crossover_rate}")
    print(f"  Elitism: {best_config.elitism_size}")
    print(f"\n  Best Fitness: {best_result.final_fitness:.2f}")
    print(f"  Quality: {best_result.quality_level}")
    print(f"  Time: {best_result.execution_time:.2f}s")
    print(f"  Cut Points: {best_result.acceptable_cuts_count}")

    # Display detailed analysis
    results_file = Path("optimization_results/medium/medium_tournament_results.json")
    if results_file.exists():
        print_analysis(results_file)


def run_large_tournament_optimization(quick: bool = False):
    """Optimize hyperparameters for large tournaments (8-10 players, 60-100 matches)."""
    print("\n" + "#" * 60)
    print("# LARGE TOURNAMENT OPTIMIZATION (8-10 players, 60-100 matches)")
    print("#" * 60)

    optimizer = HyperparameterOptimizer(output_dir="optimization_results/large")
    base_config = HyperparameterConfig.default(n_players=8, n_matches=50)

    n_trials = 2 if quick else 3  # Fewer trials for large tournaments (slower)

    # Baseline
    run_baseline_test(optimizer, base_config, n_trials=n_trials)

    # Test parameters
    optimizer.test_population_sizes(
        base_config, sizes=[100, 150, 200, 250], n_trials=n_trials
    )
    optimizer.test_generation_counts(
        base_config, counts=[200, 300, 500], n_trials=n_trials
    )
    optimizer.test_mutation_rates(
        base_config, rates=[0.1, 0.15, 0.2], n_trials=n_trials
    )
    optimizer.test_crossover_rates(
        base_config, rates=[0.6, 0.7, 0.8], n_trials=n_trials
    )
    optimizer.test_elitism_sizes(base_config, sizes=[2, 3, 5], n_trials=n_trials)

    # Analysis
    optimizer.print_analysis()

    # Export results
    optimizer.export_to_csv("large_tournament_results.csv")
    optimizer.export_to_json("large_tournament_results.json")

    # Best configuration
    best_config, best_result = optimizer.get_best_configuration("final_fitness")
    print("\n" + "=" * 60)
    print("BEST CONFIGURATION FOR LARGE TOURNAMENTS")
    print("=" * 60)
    print(f"  Population: {best_config.population_size}")
    print(f"  Generations: {best_config.generations}")
    print(f"  Mutation Rate: {best_config.mutation_rate}")
    print(f"  Crossover Rate: {best_config.crossover_rate}")
    print(f"  Elitism: {best_config.elitism_size}")
    print(f"\n  Best Fitness: {best_result.final_fitness:.2f}")
    print(f"  Quality: {best_result.quality_level}")
    print(f"  Time: {best_result.execution_time:.2f}s")
    print(f"  Cut Points: {best_result.acceptable_cuts_count}")

    # Display detailed analysis
    results_file = Path("optimization_results/large/large_tournament_results.json")
    if results_file.exists():
        print_analysis(results_file)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Run hyperparameter optimization for American Padel Tournament"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick tests with fewer trials (faster but less accurate)",
    )
    parser.add_argument(
        "--scenario",
        choices=["small", "medium", "large", "all"],
        default="all",
        help="Test specific scenario (default: all)",
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("HYPERPARAMETER OPTIMIZATION FOR AMERICAN PADEL TOURNAMENT")
    print("=" * 60)
    print(f"\nMode: {'Quick' if args.quick else 'Full'}")
    print(f"Scenario: {args.scenario}")
    print("\nThis may take a while...")

    try:
        if args.scenario == "small" or args.scenario == "all":
            run_small_tournament_optimization(quick=args.quick)

        if args.scenario == "medium" or args.scenario == "all":
            run_medium_tournament_optimization(quick=args.quick)

        if args.scenario == "large" or args.scenario == "all":
            run_large_tournament_optimization(quick=args.quick)

        print("\n" + "=" * 60)
        print("OPTIMIZATION COMPLETE!")
        print("=" * 60)
        print("\nResults have been saved to the 'optimization_results/' directory.")
        print("Check the CSV and JSON files for detailed analysis.")

    except KeyboardInterrupt:
        print("\n\nOptimization interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during optimization: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
