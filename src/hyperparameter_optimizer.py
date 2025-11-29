"""
Hyperparameter Optimization Module for American Padel Tournament Genetic Algorithm.

This module provides tools to systematically test different hyperparameter combinations
and analyze their impact on solution quality and execution time.

Author: AI System
Date: 2025-11-29
"""

import time
import json
import csv
from pathlib import Path
from typing import Any
from dataclasses import dataclass, asdict
import numpy as np
from src.genetic_algorithm import GeneticAlgorithm
from src.dataclasses import Calendar


@dataclass
class HyperparameterConfig:
    """Configuration for a single hyperparameter test run."""
    
    # Problem parameters
    n_players: int
    n_matches: int
    
    # GA parameters
    population_size: int
    generations: int
    mutation_rate: float
    crossover_rate: float
    elitism_size: int
    early_stopping_patience: int | None
    
    # Fitness weights
    weight_balance: float
    weight_opponent_rep: float
    weight_team_rep: float
    weight_waiting: float
    weight_early_cut: float
    
    # Execution parameters
    n_jobs: int = 1
    random_seed: int | None = None
    
    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    @classmethod
    def default(cls, n_players: int = 7, n_matches: int = 30) -> 'HyperparameterConfig':
        """Create default configuration."""
        return cls(
            n_players=n_players,
            n_matches=n_matches,
            population_size=100,
            generations=200,
            mutation_rate=0.1,
            crossover_rate=0.8,
            elitism_size=2,
            early_stopping_patience=20,
            weight_balance=100.0,
            weight_opponent_rep=10.0,
            weight_team_rep=10.0,
            weight_waiting=5.0,
            weight_early_cut=50.0,
            n_jobs=1,
            random_seed=None
        )


@dataclass
class OptimizationResult:
    """Results from a single optimization run."""
    
    # Configuration
    config: HyperparameterConfig
    
    # Solution quality metrics
    final_fitness: float
    balance_max_diff: int
    perfect_cuts_count: int
    acceptable_cuts_count: int
    first_cut_position: int | None
    first_cut_percentage: float | None
    distribution_std_dev: float | None
    
    # Performance metrics
    execution_time: float
    generations_run: int
    converged_early: bool
    
    # Validation
    is_valid: bool
    quality_level: str
    
    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        result = {
            'final_fitness': self.final_fitness,
            'balance_max_diff': self.balance_max_diff,
            'perfect_cuts_count': self.perfect_cuts_count,
            'acceptable_cuts_count': self.acceptable_cuts_count,
            'first_cut_position': self.first_cut_position,
            'first_cut_percentage': self.first_cut_percentage,
            'distribution_std_dev': self.distribution_std_dev,
            'execution_time': self.execution_time,
            'generations_run': self.generations_run,
            'converged_early': self.converged_early,
            'is_valid': self.is_valid,
            'quality_level': self.quality_level,
        }
        result.update(self.config.to_dict())
        return result


class HyperparameterOptimizer:
    """
    Systematic hyperparameter optimization for the genetic algorithm.
    
    This class provides methods to:
    1. Test different hyperparameter configurations
    2. Run multiple trials per configuration
    3. Analyze results statistically
    4. Export results for further analysis
    """
    
    def __init__(self, output_dir: str = "optimization_results"):
        """
        Initialize optimizer.
        
        Args:
            output_dir: Directory to save results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: list[OptimizationResult] = []
    
    def run_single_trial(
        self,
        config: HyperparameterConfig,
        verbose: bool = False
    ) -> OptimizationResult:
        """
        Run a single trial with given configuration.
        
        Args:
            config: Hyperparameter configuration
            verbose: Whether to print progress
            
        Returns:
            OptimizationResult with metrics
        """
        # Create GA instance
        ga = GeneticAlgorithm(
            n_players=config.n_players,
            n_matches=config.n_matches,
            population_size=config.population_size,
            generations=config.generations,
            mutation_rate=config.mutation_rate,
            crossover_rate=config.crossover_rate,
            elitism_size=config.elitism_size,
            early_stopping_patience=config.early_stopping_patience,
            weight_balance=config.weight_balance,
            weight_opponent_rep=config.weight_opponent_rep,
            weight_team_rep=config.weight_team_rep,
            weight_waiting=config.weight_waiting,
            weight_early_cut=config.weight_early_cut,
            n_jobs=config.n_jobs
        )
        
        # Run optimization
        start_time = time.time()
        best_calendar = ga.run(verbose=verbose)
        execution_time = time.time() - start_time
        
        # Calculate metrics
        from src.genetic_algorithm import (
            calculate_fitness,
            detect_cut_points,
            validate_solution
        )
        
        # Validate solution
        is_valid, message, quality = validate_solution(best_calendar)
        
        final_fitness = calculate_fitness(
            best_calendar,
            config.weight_balance,
            config.weight_opponent_rep,
            config.weight_team_rep,
            config.weight_waiting,
            config.weight_early_cut
        )
        
        # Balance metrics
        matches_per_player = best_calendar.get_matches_per_player()
        counts = list(matches_per_player.values())
        balance_max_diff = max(counts) - min(counts)
        
        # Cut points metrics
        perfect_cuts, acceptable_cuts = detect_cut_points(best_calendar)
        perfect_cuts_count = len(perfect_cuts)
        acceptable_cuts_count = len(acceptable_cuts)
        
        first_cut_position = None
        first_cut_percentage = None
        if perfect_cuts:
            first_cut_position = perfect_cuts[0]
            first_cut_percentage = (first_cut_position / len(best_calendar)) * 100
        elif acceptable_cuts:
            first_cut_position = acceptable_cuts[0]
            first_cut_percentage = (first_cut_position / len(best_calendar)) * 100
        
        # Distribution metrics
        distribution_std_dev = None
        if len(acceptable_cuts) >= 2:
            gaps = [acceptable_cuts[i+1] - acceptable_cuts[i] 
                   for i in range(len(acceptable_cuts) - 1)]
            if gaps:
                avg_gap = sum(gaps) / len(gaps)
                variance = sum((g - avg_gap) ** 2 for g in gaps) / len(gaps)
                distribution_std_dev = variance ** 0.5
        
        # Check if converged early
        # Note: We assume full generations were run unless we modify GA to track this
        converged_early = False  # Placeholder - would need GA modification to track actual generations run
        generations_run = config.generations  # Assume all generations ran
        
        return OptimizationResult(
            config=config,
            final_fitness=final_fitness,
            balance_max_diff=balance_max_diff,
            perfect_cuts_count=perfect_cuts_count,
            acceptable_cuts_count=acceptable_cuts_count,
            first_cut_position=first_cut_position,
            first_cut_percentage=first_cut_percentage,
            distribution_std_dev=distribution_std_dev,
            execution_time=execution_time,
            generations_run=generations_run,
            converged_early=converged_early,
            is_valid=is_valid,
            quality_level=quality
        )
    
    def run_multiple_trials(
        self,
        config: HyperparameterConfig,
        n_trials: int = 5,
        verbose: bool = False
    ) -> list[OptimizationResult]:
        """
        Run multiple trials with same configuration.
        
        Args:
            config: Hyperparameter configuration
            n_trials: Number of trials to run
            verbose: Whether to print progress
            
        Returns:
            List of OptimizationResults
        """
        results = []
        for trial in range(n_trials):
            if verbose:
                print(f"\n{'='*60}")
                print(f"Trial {trial + 1}/{n_trials}")
                print(f"{'='*60}")
            
            # Use different seed for each trial if seed is set
            trial_config = config
            if config.random_seed is not None:
                trial_config = HyperparameterConfig(
                    **{**config.to_dict(), 'random_seed': config.random_seed + trial}
                )
            
            result = self.run_single_trial(trial_config, verbose=verbose)
            results.append(result)
            self.results.append(result)
            
            if verbose:
                print(f"\nTrial {trial + 1} Results:")
                print(f"  Fitness: {result.final_fitness:.2f}")
                print(f"  Quality: {result.quality_level}")
                print(f"  Time: {result.execution_time:.2f}s")
                print(f"  Cut points: {result.acceptable_cuts_count}")
        
        return results
    
    def test_population_sizes(
        self,
        base_config: HyperparameterConfig,
        sizes: list[int] = [50, 100, 150, 200, 250],
        n_trials: int = 3,
        verbose: bool = True
    ) -> list[OptimizationResult]:
        """Test different population sizes."""
        if verbose:
            print("\n" + "="*60)
            print("TESTING POPULATION SIZES")
            print("="*60)
        
        results = []
        for size in sizes:
            if verbose:
                print(f"\n--- Testing population_size = {size} ---")
            
            config = HyperparameterConfig(**{**base_config.to_dict(), 'population_size': size})
            trial_results = self.run_multiple_trials(config, n_trials, verbose=False)
            results.extend(trial_results)
            
            if verbose:
                self._print_summary(trial_results, f"Population Size {size}")
        
        return results
    
    def test_generation_counts(
        self,
        base_config: HyperparameterConfig,
        counts: list[int] = [100, 200, 300, 500],
        n_trials: int = 3,
        verbose: bool = True
    ) -> list[OptimizationResult]:
        """Test different generation counts."""
        if verbose:
            print("\n" + "="*60)
            print("TESTING GENERATION COUNTS")
            print("="*60)
        
        results = []
        for count in counts:
            if verbose:
                print(f"\n--- Testing generations = {count} ---")
            
            config = HyperparameterConfig(**{**base_config.to_dict(), 'generations': count})
            trial_results = self.run_multiple_trials(config, n_trials, verbose=False)
            results.extend(trial_results)
            
            if verbose:
                self._print_summary(trial_results, f"Generations {count}")
        
        return results
    
    def test_mutation_rates(
        self,
        base_config: HyperparameterConfig,
        rates: list[float] = [0.05, 0.1, 0.15, 0.2],
        n_trials: int = 3,
        verbose: bool = True
    ) -> list[OptimizationResult]:
        """Test different mutation rates."""
        if verbose:
            print("\n" + "="*60)
            print("TESTING MUTATION RATES")
            print("="*60)
        
        results = []
        for rate in rates:
            if verbose:
                print(f"\n--- Testing mutation_rate = {rate} ---")
            
            config = HyperparameterConfig(**{**base_config.to_dict(), 'mutation_rate': rate})
            trial_results = self.run_multiple_trials(config, n_trials, verbose=False)
            results.extend(trial_results)
            
            if verbose:
                self._print_summary(trial_results, f"Mutation Rate {rate}")
        
        return results
    
    def test_crossover_rates(
        self,
        base_config: HyperparameterConfig,
        rates: list[float] = [0.6, 0.7, 0.8, 0.9],
        n_trials: int = 3,
        verbose: bool = True
    ) -> list[OptimizationResult]:
        """Test different crossover rates."""
        if verbose:
            print("\n" + "="*60)
            print("TESTING CROSSOVER RATES")
            print("="*60)
        
        results = []
        for rate in rates:
            if verbose:
                print(f"\n--- Testing crossover_rate = {rate} ---")
            
            config = HyperparameterConfig(**{**base_config.to_dict(), 'crossover_rate': rate})
            trial_results = self.run_multiple_trials(config, n_trials, verbose=False)
            results.extend(trial_results)
            
            if verbose:
                self._print_summary(trial_results, f"Crossover Rate {rate}")
        
        return results
    
    def test_elitism_sizes(
        self,
        base_config: HyperparameterConfig,
        sizes: list[int] = [1, 2, 3, 5],
        n_trials: int = 3,
        verbose: bool = True
    ) -> list[OptimizationResult]:
        """Test different elitism sizes."""
        if verbose:
            print("\n" + "="*60)
            print("TESTING ELITISM SIZES")
            print("="*60)
        
        results = []
        for size in sizes:
            if verbose:
                print(f"\n--- Testing elitism_size = {size} ---")
            
            config = HyperparameterConfig(**{**base_config.to_dict(), 'elitism_size': size})
            trial_results = self.run_multiple_trials(config, n_trials, verbose=False)
            results.extend(trial_results)
            
            if verbose:
                self._print_summary(trial_results, f"Elitism Size {size}")
        
        return results
    
    
    def _print_summary(self, results: list[OptimizationResult], title: str) -> None:
        """Print summary statistics for a set of results."""
        if not results:
            return
        
        fitness_values = [r.final_fitness for r in results]
        times = [r.execution_time for r in results]
        cuts = [r.acceptable_cuts_count for r in results]
        balance = [r.balance_max_diff for r in results]
        
        print(f"\n{title} Summary:")
        print(f"  Fitness:    {np.mean(fitness_values):8.2f} ± {np.std(fitness_values):6.2f}")
        print(f"  Time:       {np.mean(times):8.2f}s ± {np.std(times):6.2f}s")
        print(f"  Cut points: {np.mean(cuts):8.1f} ± {np.std(cuts):6.1f}")
        print(f"  Balance:    {np.mean(balance):8.1f} ± {np.std(balance):6.1f}")
        
        # Quality distribution
        quality_counts = {}
        for r in results:
            quality_counts[r.quality_level] = quality_counts.get(r.quality_level, 0) + 1
        print(f"  Quality:    {dict(quality_counts)}")
    
    def export_to_csv(self, filename: str = "hyperparameter_results.csv") -> None:
        """Export all results to CSV file."""
        filepath = self.output_dir / filename
        
        if not self.results:
            print("No results to export.")
            return
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.results[0].to_dict().keys())
            writer.writeheader()
            for result in self.results:
                writer.writerow(result.to_dict())
        
        print(f"\nResults exported to: {filepath}")
    
    def export_to_json(self, filename: str = "hyperparameter_results.json") -> None:
        """Export all results to JSON file."""
        filepath = self.output_dir / filename
        
        data = [result.to_dict() for result in self.results]
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\nResults exported to: {filepath}")
    
    def get_best_configuration(
        self,
        metric: str = 'final_fitness'
    ) -> tuple[HyperparameterConfig, OptimizationResult]:
        """
        Get the best configuration based on a metric.
        
        Args:
            metric: Metric to optimize ('final_fitness', 'execution_time', etc.)
            
        Returns:
            Tuple of (best_config, best_result)
        """
        if not self.results:
            raise ValueError("No results available. Run tests first.")
        
        if metric == 'execution_time':
            # For time, lower is better
            best_result = min(self.results, key=lambda r: r.execution_time)
        else:
            # For other metrics, higher is better
            best_result = max(self.results, key=lambda r: getattr(r, metric))
        
        return best_result.config, best_result
    
    def analyze_results(self) -> dict[str, Any]:
        """
        Analyze all results and provide summary statistics.
        
        Returns:
            Dictionary with analysis results
        """
        if not self.results:
            return {"error": "No results available"}
        
        analysis = {
            "total_runs": len(self.results),
            "fitness": {
                "mean": float(np.mean([r.final_fitness for r in self.results])),
                "std": float(np.std([r.final_fitness for r in self.results])),
                "min": float(np.min([r.final_fitness for r in self.results])),
                "max": float(np.max([r.final_fitness for r in self.results])),
            },
            "execution_time": {
                "mean": float(np.mean([r.execution_time for r in self.results])),
                "std": float(np.std([r.execution_time for r in self.results])),
                "min": float(np.min([r.execution_time for r in self.results])),
                "max": float(np.max([r.execution_time for r in self.results])),
            },
            "cut_points": {
                "mean": float(np.mean([r.acceptable_cuts_count for r in self.results])),
                "std": float(np.std([r.acceptable_cuts_count for r in self.results])),
                "min": int(np.min([r.acceptable_cuts_count for r in self.results])),
                "max": int(np.max([r.acceptable_cuts_count for r in self.results])),
            },
            "balance": {
                "mean": float(np.mean([r.balance_max_diff for r in self.results])),
                "std": float(np.std([r.balance_max_diff for r in self.results])),
                "min": int(np.min([r.balance_max_diff for r in self.results])),
                "max": int(np.max([r.balance_max_diff for r in self.results])),
            },
            "quality_distribution": {},
            "success_rate": 0.0,
        }
        
        # Quality distribution
        for result in self.results:
            level = result.quality_level
            analysis["quality_distribution"][level] = \
                analysis["quality_distribution"].get(level, 0) + 1
        
        # Success rate (EXCELLENT or GOOD)
        successful = sum(1 for r in self.results 
                        if r.quality_level in ["EXCELLENT", "GOOD"])
        analysis["success_rate"] = (successful / len(self.results)) * 100
        
        return analysis
    
    def print_analysis(self) -> None:
        """Print detailed analysis of all results."""
        analysis = self.analyze_results()
        
        if "error" in analysis:
            print(analysis["error"])
            return
        
        print("\n" + "="*60)
        print("HYPERPARAMETER OPTIMIZATION ANALYSIS")
        print("="*60)
        
        print(f"\nTotal runs: {analysis['total_runs']}")
        
        print("\n📊 FITNESS:")
        print(f"  Mean:    {analysis['fitness']['mean']:8.2f}")
        print(f"  Std Dev: {analysis['fitness']['std']:8.2f}")
        print(f"  Range:   [{analysis['fitness']['min']:.2f}, {analysis['fitness']['max']:.2f}]")
        
        print("\n⏱️  EXECUTION TIME:")
        print(f"  Mean:    {analysis['execution_time']['mean']:8.2f}s")
        print(f"  Std Dev: {analysis['execution_time']['std']:8.2f}s")
        print(f"  Range:   [{analysis['execution_time']['min']:.2f}s, {analysis['execution_time']['max']:.2f}s]")
        
        print("\n✂️  CUT POINTS:")
        print(f"  Mean:    {analysis['cut_points']['mean']:8.1f}")
        print(f"  Std Dev: {analysis['cut_points']['std']:8.1f}")
        print(f"  Range:   [{analysis['cut_points']['min']}, {analysis['cut_points']['max']}]")
        
        print("\n⚖️  BALANCE:")
        print(f"  Mean:    {analysis['balance']['mean']:8.1f}")
        print(f"  Std Dev: {analysis['balance']['std']:8.1f}")
        print(f"  Range:   [{analysis['balance']['min']}, {analysis['balance']['max']}]")
        
        print("\n🏆 QUALITY DISTRIBUTION:")
        for level, count in analysis['quality_distribution'].items():
            percentage = (count / analysis['total_runs']) * 100
            print(f"  {level:12s}: {count:3d} ({percentage:5.1f}%)")
        
        print(f"\n✅ SUCCESS RATE: {analysis['success_rate']:.1f}% (EXCELLENT or GOOD)")
        print("="*60)

