"""
Script para probar diferentes configuraciones del algoritmo genético.
Prueba con diferentes números de jugadores y documenta los resultados.
"""

from src.genetic_algorithm import GeneticAlgorithm, validate_solution, detect_cut_points
from src.printer import print_results
import time


def test_configuration(n_players, n_matches, generations=100, population_size=50):
    """
    Prueba una configuración específica del algoritmo.
    
    Args:
        n_players: Número de jugadores
        n_matches: Número de partidos a generar
        generations: Número de generaciones
        population_size: Tamaño de la población
    
    Returns:
        Diccionario con los resultados
    """
    print(f"\n{'='*70}")
    print(f"TESTING: {n_players} players, {n_matches} matches")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    ga = GeneticAlgorithm(
        n_players=n_players,
        n_matches=n_matches,
        population_size=population_size,
        generations=generations,
        mutation_rate=0.1,
        crossover_rate=0.8,
        elitism_size=2,
        weight_balance=100.0,
        weight_opponent_rep=10.0,
        weight_team_rep=10.0,
        weight_waiting=5.0,
        weight_early_cut=50.0,
        n_jobs=-1,
        early_stopping_patience=15
    )
    
    best_calendar = ga.run(verbose=False)
    
    elapsed_time = time.time() - start_time
    
    # Validar solución
    is_valid, quality, message = validate_solution(best_calendar)
    
    # Detectar puntos de corte
    perfect_cuts, acceptable_cuts = detect_cut_points(best_calendar)
    
    # Calcular balance
    matches_per_player = best_calendar.get_matches_per_player()
    match_counts = list(matches_per_player.values())
    max_matches = max(match_counts)
    min_matches = min(match_counts)
    balance_diff = max_matches - min_matches
    
    # Calcular fitness final
    final_fitness = ga.best_fitness_history[-1]
    
    results = {
        'n_players': n_players,
        'n_matches': n_matches,
        'is_valid': is_valid,
        'quality': quality,
        'perfect_cuts': len(perfect_cuts),
        'acceptable_cuts': len(acceptable_cuts),
        'first_perfect_cut': perfect_cuts[0] if perfect_cuts else None,
        'first_acceptable_cut': acceptable_cuts[0] if acceptable_cuts else None,
        'balance_diff': balance_diff,
        'final_fitness': final_fitness,
        'generations_run': len(ga.best_fitness_history),
        'elapsed_time': elapsed_time
    }
    
    # Mostrar resultados
    print(f"\n✓ Resultados:")
    print(f"  • Válido: {is_valid}")
    print(f"  • Calidad: {quality}")
    print(f"  • Puntos de corte perfectos: {len(perfect_cuts)}")
    print(f"  • Puntos de corte aceptables: {len(acceptable_cuts)}")
    if perfect_cuts:
        print(f"  • Primer corte perfecto: match {perfect_cuts[0]} ({perfect_cuts[0]/n_matches*100:.1f}%)")
    if acceptable_cuts:
        print(f"  • Primer corte aceptable: match {acceptable_cuts[0]} ({acceptable_cuts[0]/n_matches*100:.1f}%)")
    print(f"  • Diferencia de balance: {balance_diff} partidos")
    print(f"  • Fitness final: {final_fitness:.2f}")
    print(f"  • Generaciones ejecutadas: {results['generations_run']}")
    print(f"  • Tiempo: {elapsed_time:.2f}s")
    
    return results


def main():
    """
    Ejecuta pruebas con diferentes configuraciones.
    """
    print("="*70)
    print("PRUEBAS DE CONFIGURACIÓN - ALGORITMO GENÉTICO".center(70))
    print("="*70)
    
    configurations = [
        # (n_players, n_matches, generations, population_size)
        (4, 10, 50, 30),   # Pequeño
        (5, 15, 50, 30),   # Pequeño-medio
        (6, 20, 75, 40),   # Medio
        (7, 30, 100, 50),  # Medio-grande
        (8, 40, 100, 50),  # Grande
    ]
    
    all_results = []
    
    for config in configurations:
        n_players, n_matches, generations, population_size = config
        results = test_configuration(n_players, n_matches, generations, population_size)
        all_results.append(results)
    
    # Resumen final
    print(f"\n{'='*70}")
    print("RESUMEN DE RESULTADOS".center(70))
    print(f"{'='*70}\n")
    
    print(f"{'Jugadores':<10} {'Partidos':<10} {'Calidad':<12} {'Cortes P':<10} {'Cortes A':<10} {'Balance':<10} {'Tiempo':<10}")
    print("-" * 70)
    
    for r in all_results:
        print(f"{r['n_players']:<10} {r['n_matches']:<10} {r['quality']:<12} "
              f"{r['perfect_cuts']:<10} {r['acceptable_cuts']:<10} "
              f"{r['balance_diff']:<10} {r['elapsed_time']:.1f}s")
    
    print(f"\n{'='*70}")
    print("ANÁLISIS".center(70))
    print(f"{'='*70}\n")
    
    valid_count = sum(1 for r in all_results if r['is_valid'])
    excellent_count = sum(1 for r in all_results if r['quality'] == 'EXCELLENT')
    good_count = sum(1 for r in all_results if r['quality'] == 'GOOD')
    
    print(f"✓ Soluciones válidas: {valid_count}/{len(all_results)}")
    print(f"✓ Calidad EXCELLENT: {excellent_count}/{len(all_results)}")
    print(f"✓ Calidad GOOD o mejor: {good_count + excellent_count}/{len(all_results)}")
    
    avg_perfect_cuts = sum(r['perfect_cuts'] for r in all_results) / len(all_results)
    avg_acceptable_cuts = sum(r['acceptable_cuts'] for r in all_results) / len(all_results)
    
    print(f"\n✓ Promedio de cortes perfectos: {avg_perfect_cuts:.1f}")
    print(f"✓ Promedio de cortes aceptables: {avg_acceptable_cuts:.1f}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

