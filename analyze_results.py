#!/usr/bin/env python3
"""
Hyperparameter optimization results analysis.

Analyzes optimization results and determines the best hyperparameters
based on different criteria: best fitness, most cut points, best balance, fastest time.
"""

import json
import csv
from pathlib import Path
from collections import defaultdict
from typing import Any
import statistics


def load_json_results(filepath: Path) -> list[dict[str, Any]]:
    """Load results from a JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def analyze_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze results and return statistics."""
    
    # Group by configuration (hyperparameters)
    config_groups: dict[str, list[dict]] = defaultdict(list)
    
    for result in results:
        # Create unique key for each configuration
        key = (
            f"pop={result['population_size']}, "
            f"gen={result['generations']}, "
            f"mut={result['mutation_rate']}, "
            f"cross={result['crossover_rate']}, "
            f"elit={result['elitism_size']}"
        )
        config_groups[key].append(result)
    
    # Calculate statistics per configuration
    config_stats = {}
    
    for config_key, config_results in config_groups.items():
        if not config_results:
            continue
            
        fitnesses = [r['final_fitness'] for r in config_results]
        cut_points = [r['acceptable_cuts_count'] for r in config_results]
        times = [r['execution_time'] for r in config_results]
        balances = [r['balance_max_diff'] for r in config_results]
        
        # Filter time outliers (some values are incorrect)
        valid_times = [t for t in times if t < 1000]  # Filter abnormally high times
        
        config_stats[config_key] = {
            'n_trials': len(config_results),
            'avg_fitness': statistics.mean(fitnesses),
            'std_fitness': statistics.stdev(fitnesses) if len(fitnesses) > 1 else 0,
            'max_fitness': max(fitnesses),
            'min_fitness': min(fitnesses),
            'avg_cut_points': statistics.mean(cut_points),
            'max_cut_points': max(cut_points),
            'avg_time': statistics.mean(valid_times) if valid_times else statistics.mean(times),
            'min_time': min(valid_times) if valid_times else min(times),
            'avg_balance': statistics.mean(balances),
            'best_result': max(config_results, key=lambda r: r['final_fitness']),
            'results': config_results
        }
    
    return {
        'by_config': config_stats,
        'all_results': results
    }


def find_best_configs(analysis: dict[str, Any]) -> dict[str, Any]:
    """Find the best configurations according to different criteria."""
    
    config_stats = analysis['by_config']
    
    best_configs = {
        'highest_fitness': None,
        'most_cut_points': None,
        'best_balance': None,
        'fastest': None,
        'best_overall': None  # Balance between fitness and time
    }
    
    best_fitness = -float('inf')
    most_cuts = -1
    best_bal = float('inf')
    fastest_time = float('inf')
    best_score = -float('inf')
    
    for config_key, stats in config_stats.items():
        # Best fitness
        if stats['max_fitness'] > best_fitness:
            best_fitness = stats['max_fitness']
            best_configs['highest_fitness'] = (config_key, stats)
        
        # Most cut points
        if stats['max_cut_points'] > most_cuts:
            most_cuts = stats['max_cut_points']
            best_configs['most_cut_points'] = (config_key, stats)
        
        # Best balance (lower difference)
        if stats['avg_balance'] < best_bal:
            best_bal = stats['avg_balance']
            best_configs['best_balance'] = (config_key, stats)
        
        # Fastest (valid time)
        valid_times = [r['execution_time'] for r in stats['results'] if r['execution_time'] < 1000]
        if valid_times:
            avg_time = statistics.mean(valid_times)
            if avg_time < fastest_time:
                fastest_time = avg_time
                best_configs['fastest'] = (config_key, stats)
        
        # Best overall (normalized fitness - normalized time)
        # Use average fitness and average valid time
        valid_times = [r['execution_time'] for r in stats['results'] if r['execution_time'] < 1000]
        if valid_times and stats['avg_fitness'] > 0:
            # Score = fitness / time (higher is better)
            score = stats['avg_fitness'] / (statistics.mean(valid_times) + 1)
            if score > best_score:
                best_score = score
                best_configs['best_overall'] = (config_key, stats)
    
    return best_configs


def print_analysis(results_file: Path):
    """Print the analysis of results."""
    
    print("\n" + "="*80)
    print("HYPERPARAMETER OPTIMIZATION RESULTS ANALYSIS")
    print("="*80)
    
    # Load results
    results = load_json_results(results_file)
    print(f"\nTotal executions analyzed: {len(results)}")
    
    # Analyze
    analysis = analyze_results(results)
    best_configs = find_best_configs(analysis)
    
    config_stats = analysis['by_config']
    print(f"Unique configurations tested: {len(config_stats)}")
    
    # Best fitness
    if best_configs['highest_fitness']:
        config_key, stats = best_configs['highest_fitness']
        print("\n" + "="*80)
        print("🏆 HIGHEST FITNESS")
        print("="*80)
        print(f"Configuration: {config_key}")
        print(f"Average fitness: {stats['avg_fitness']:.2f} ± {stats['std_fitness']:.2f}")
        print(f"Maximum fitness: {stats['max_fitness']:.2f}")
        print(f"Average cut points: {stats['avg_cut_points']:.1f} (max: {stats['max_cut_points']})")
        print(f"Average balance: {stats['avg_balance']:.1f}")
        print(f"Average time: {stats['avg_time']:.2f}s")
        
        best_result = stats['best_result']
        print(f"\nBest individual result:")
        print(f"  Fitness: {best_result['final_fitness']:.2f}")
        print(f"  Cut points: {best_result['acceptable_cuts_count']}")
        print(f"  Balance: {best_result['balance_max_diff']}")
        print(f"  Time: {best_result['execution_time']:.2f}s")
    
    # Most cut points
    if best_configs['most_cut_points']:
        config_key, stats = best_configs['most_cut_points']
        print("\n" + "="*80)
        print("✂️  MOST CUT POINTS")
        print("="*80)
        print(f"Configuration: {config_key}")
        print(f"Average cut points: {stats['avg_cut_points']:.1f}")
        print(f"Maximum cut points: {stats['max_cut_points']}")
        print(f"Average fitness: {stats['avg_fitness']:.2f}")
        print(f"Average balance: {stats['avg_balance']:.1f}")
        print(f"Average time: {stats['avg_time']:.2f}s")
    
    # Best balance
    if best_configs['best_balance']:
        config_key, stats = best_configs['best_balance']
        print("\n" + "="*80)
        print("⚖️  BEST BALANCE")
        print("="*80)
        print(f"Configuration: {config_key}")
        print(f"Average balance: {stats['avg_balance']:.1f}")
        print(f"Average fitness: {stats['avg_fitness']:.2f}")
        print(f"Average cut points: {stats['avg_cut_points']:.1f}")
        print(f"Average time: {stats['avg_time']:.2f}s")
    
    # Fastest
    if best_configs['fastest']:
        config_key, stats = best_configs['fastest']
        print("\n" + "="*80)
        print("⚡ FASTEST")
        print("="*80)
        print(f"Configuration: {config_key}")
        print(f"Average time: {stats['avg_time']:.2f}s")
        print(f"Minimum time: {stats['min_time']:.2f}s")
        print(f"Average fitness: {stats['avg_fitness']:.2f}")
        print(f"Average cut points: {stats['avg_cut_points']:.1f}")
    
    # Best overall
    if best_configs['best_overall']:
        config_key, stats = best_configs['best_overall']
        print("\n" + "="*80)
        print("🌟 BEST OVERALL CONFIGURATION (Fitness/Time Balance)")
        print("="*80)
        print(f"Configuration: {config_key}")
        print(f"Average fitness: {stats['avg_fitness']:.2f} ± {stats['std_fitness']:.2f}")
        print(f"Average cut points: {stats['avg_cut_points']:.1f}")
        print(f"Average balance: {stats['avg_balance']:.1f}")
        print(f"Average time: {stats['avg_time']:.2f}s")
        print(f"Trials performed: {stats['n_trials']}")
        
        # Extract hyperparameter values
        best_result = stats['best_result']
        print(f"\n📋 RECOMMENDED HYPERPARAMETERS:")
        print(f"  • Population: {best_result['population_size']}")
        print(f"  • Generations: {best_result['generations']}")
        print(f"  • Mutation Rate: {best_result['mutation_rate']}")
        print(f"  • Crossover Rate: {best_result['crossover_rate']}")
        print(f"  • Elitism: {best_result['elitism_size']}")
        print(f"  • Early stopping patience: {best_result['early_stopping_patience']}")
    
    # Analysis by individual parameter
    print("\n" + "="*80)
    print("📊 ANALYSIS BY PARAMETER")
    print("="*80)
    
    # Population analysis
    print("\n📈 Population:")
    pop_groups = defaultdict(list)
    for result in results:
        pop_groups[result['population_size']].append(result)
    
    for pop_size in sorted(pop_groups.keys()):
        group_results = pop_groups[pop_size]
        fitnesses = [r['final_fitness'] for r in group_results]
        valid_times = [r['execution_time'] for r in group_results if r['execution_time'] < 1000]
        cut_points = [r['acceptable_cuts_count'] for r in group_results]
        
        print(f"  Population {pop_size:3d}: Fitness={statistics.mean(fitnesses):7.1f}, "
              f"Cut points={statistics.mean(cut_points):4.1f}, "
              f"Time={statistics.mean(valid_times) if valid_times else 0:.1f}s "
              f"(n={len(group_results)})")
    
    # Mutation rate analysis
    print("\n🔄 Mutation Rate:")
    mut_groups = defaultdict(list)
    for result in results:
        mut_groups[result['mutation_rate']].append(result)
    
    for mut_rate in sorted(mut_groups.keys()):
        group_results = mut_groups[mut_rate]
        fitnesses = [r['final_fitness'] for r in group_results]
        valid_times = [r['execution_time'] for r in group_results if r['execution_time'] < 1000]
        cut_points = [r['acceptable_cuts_count'] for r in group_results]
        
        print(f"  Mutation {mut_rate:.2f}: Fitness={statistics.mean(fitnesses):7.1f}, "
              f"Cut points={statistics.mean(cut_points):4.1f}, "
              f"Time={statistics.mean(valid_times) if valid_times else 0:.1f}s "
              f"(n={len(group_results)})")
    
    # Crossover rate analysis
    print("\n🔀 Crossover Rate:")
    cross_groups = defaultdict(list)
    for result in results:
        cross_groups[result['crossover_rate']].append(result)
    
    for cross_rate in sorted(cross_groups.keys()):
        group_results = cross_groups[cross_rate]
        fitnesses = [r['final_fitness'] for r in group_results]
        valid_times = [r['execution_time'] for r in group_results if r['execution_time'] < 1000]
        cut_points = [r['acceptable_cuts_count'] for r in group_results]
        
        print(f"  Crossover {cross_rate:.2f}: Fitness={statistics.mean(fitnesses):7.1f}, "
              f"Cut points={statistics.mean(cut_points):4.1f}, "
              f"Time={statistics.mean(valid_times) if valid_times else 0:.1f}s "
              f"(n={len(group_results)})")
    
    # Elitism analysis
    print("\n👑 Elitism:")
    elit_groups = defaultdict(list)
    for result in results:
        elit_groups[result['elitism_size']].append(result)
    
    for elit_size in sorted(elit_groups.keys()):
        group_results = elit_groups[elit_size]
        fitnesses = [r['final_fitness'] for r in group_results]
        valid_times = [r['execution_time'] for r in group_results if r['execution_time'] < 1000]
        cut_points = [r['acceptable_cuts_count'] for r in group_results]
        
        print(f"  Elitism {elit_size}: Fitness={statistics.mean(fitnesses):7.1f}, "
              f"Cut points={statistics.mean(cut_points):4.1f}, "
              f"Time={statistics.mean(valid_times) if valid_times else 0:.1f}s "
              f"(n={len(group_results)})")
    
    print("\n" + "="*80)


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analyze hyperparameter optimization results"
    )
    parser.add_argument(
        '--file',
        type=str,
        default='optimization_results/medium/medium_tournament_results.json',
        help='Path to JSON results file'
    )
    
    args = parser.parse_args()
    
    results_file = Path(args.file)
    
    if not results_file.exists():
        print(f"❌ Error: File not found {results_file}")
        return
    
    print_analysis(results_file)


if __name__ == "__main__":
    main()

