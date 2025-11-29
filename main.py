"""
Main script for American Padel Tournament Calendar Generation.
This script runs the genetic algorithm and displays the results.
"""

from src.genetic_algorithm import GeneticAlgorithm, validate_solution
from src.printer import print_results


def main():
    """
    Main execution function for the tournament calendar generator.
    """
    # ========================================================================
    # CONFIGURATION PARAMETERS
    # ========================================================================
    
    print("="*70)
    print("AMERICAN PADEL TOURNAMENT - GENETIC ALGORITHM".center(70))
    print("="*70)
    
    # Tournament parameters
    N_PLAYERS = 7           # Number of players
    N_MATCHES = 50          # Number of matches to generate
    
    # Genetic Algorithm parameters
    POPULATION_SIZE = 100   # Size of the population
    GENERATIONS = 20       # Number of generations to evolve
    MUTATION_RATE = 0.1     # Probability of mutation (0.0 to 1.0)
    CROSSOVER_RATE = 0.8    # Probability of crossover (0.0 to 1.0)
    ELITISM_SIZE = 2        # Number of best individuals to preserve
    N_JOBS = -1             # Number of parallel jobs (-1 = all cores, 1 = sequential)
    
    # Fitness weights
    WEIGHT_BALANCE = 100.0      # Most important - balance matches per player
    WEIGHT_OPPONENT_REP = 10.0  # Medium - minimize opponent repetitions
    WEIGHT_TEAM_REP = 10.0      # Medium - minimize team repetitions
    WEIGHT_WAITING = 5.0        # Low-medium - minimize waiting rounds
    WEIGHT_EARLY_CUT = 50.0     # High - incentivize early cut points
    
    # ========================================================================
    # DISPLAY CONFIGURATION
    # ========================================================================
    
    print("\n📋 Configuration:")
    print(f"  • Players: {N_PLAYERS}")
    print(f"  • Matches to generate: {N_MATCHES}")
    print(f"  • Population size: {POPULATION_SIZE}")
    print(f"  • Generations: {GENERATIONS}")
    print(f"  • Mutation rate: {MUTATION_RATE}")
    print(f"  • Crossover rate: {CROSSOVER_RATE}")
    print(f"  • Elitism size: {ELITISM_SIZE}")
    print(f"  • Parallel jobs: {N_JOBS if N_JOBS > 0 else 'all CPU cores'}")
    
    print("\n⚖️  Fitness Weights:")
    print(f"  • Balance: {WEIGHT_BALANCE} (highest priority)")
    print(f"  • Opponent repetition: {WEIGHT_OPPONENT_REP}")
    print(f"  • Team repetition: {WEIGHT_TEAM_REP}")
    print(f"  • Waiting rounds: {WEIGHT_WAITING}")
    print(f"  • Early cut points: {WEIGHT_EARLY_CUT} (bonus)")
    
    # ========================================================================
    # INITIALIZE GENETIC ALGORITHM
    # ========================================================================
    
    print("\n" + "="*70)
    print("STARTING OPTIMIZATION".center(70))
    print("="*70 + "\n")
    
    ga = GeneticAlgorithm(
        n_players=N_PLAYERS,
        n_matches=N_MATCHES,
        population_size=POPULATION_SIZE,
        generations=GENERATIONS,
        mutation_rate=MUTATION_RATE,
        crossover_rate=CROSSOVER_RATE,
        elitism_size=ELITISM_SIZE,
        weight_balance=WEIGHT_BALANCE,
        weight_opponent_rep=WEIGHT_OPPONENT_REP,
        weight_team_rep=WEIGHT_TEAM_REP,
        weight_waiting=WEIGHT_WAITING,
        weight_early_cut=WEIGHT_EARLY_CUT,
        n_jobs=N_JOBS
    )
    
    # ========================================================================
    # RUN OPTIMIZATION
    # ========================================================================
    
    best_calendar = ga.run(verbose=True)
    
    # ========================================================================
    # VALIDATE SOLUTION
    # ========================================================================
    
    print("\n" + "="*70)
    print("VALIDATING SOLUTION".center(70))
    print("="*70 + "\n")
    
    is_valid, quality, message = validate_solution(best_calendar)
    
    if not is_valid:
        print("❌ Solution validation failed!")
        print(f"   Quality: {quality}")
        print(f"   Message: {message}")
        print("\n💡 Suggestions to improve:")
        print("   • Increase the number of generations (e.g., 500)")
        print("   • Increase population size (e.g., 200)")
        print("   • Adjust fitness weights")
        print("   • Try running the algorithm multiple times")
        return
    
    print(f"✓ Solution validated successfully!")
    print(f"  Quality: {quality}")
    print(f"  {message}")
    
    # ========================================================================
    # DISPLAY RESULTS
    # ========================================================================
    
    print("\n" + "="*70)
    print("FINAL RESULTS".center(70))
    print("="*70)
    
    print_results(
        calendar=best_calendar,
        title="AMERICAN PADEL TOURNAMENT - OPTIMIZED CALENDAR"
    )
    
    # ========================================================================
    # DISPLAY FITNESS EVOLUTION
    # ========================================================================
    
    print("\n" + "="*70)
    print("FITNESS EVOLUTION SUMMARY".center(70))
    print("="*70)
    
    if len(ga.best_fitness_history) > 0:
        initial_fitness = ga.best_fitness_history[0]
        final_fitness = ga.best_fitness_history[-1]
        improvement = final_fitness - initial_fitness
        
        print(f"\n  Initial fitness: {initial_fitness:.2f}")
        print(f"  Final fitness: {final_fitness:.2f}")
        print(f"  Total improvement: {improvement:.2f} ({(improvement/abs(initial_fitness)*100):.1f}%)")
        
        # Show some milestones
        milestones = [0, len(ga.best_fitness_history)//4, len(ga.best_fitness_history)//2, 
                     3*len(ga.best_fitness_history)//4, len(ga.best_fitness_history)-1]
        
        print("\n  Fitness milestones:")
        for i in milestones:
            gen = i + 1
            fitness = ga.best_fitness_history[i]
            print(f"    Generation {gen:3d}: {fitness:.2f}")
    
    print("\n" + "="*70)
    print("OPTIMIZATION COMPLETE".center(70))
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
