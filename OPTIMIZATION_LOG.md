# Optimization Log

This document tracks all optimizations applied to the genetic algorithm and their performance impact.

## Baseline Performance

- **Date**: 2026-01-26
- **Branch**: optimization
- **Configuration**:
  - 10 players, 10 rounds, 2 courts
  - Population: 50, Generations: 50
  - 3 runs averaged

- **Results**:
  - Average time: **16.84s ± 0.17s**
  - Average fitness: 43841.95 ± 260.59
  - Tests: All passing (178 tests)

---

## Optimization 1: Pre-compute player indices from vectors

**Status**: ✅ Completed

**Description**:
Replace Match object creation with direct numpy operations to extract player indices from match vectors. This eliminates Pydantic validation overhead and reduces object creation.

**Expected Impact**: 30-50% faster
**Actual Impact**: 5.1% faster

**Changes**:
- Added `get_players_from_vector()` and `get_teams_from_vector()` utility functions
- Replaced Match object creation in:
  - `calculate_opponent_repetition_penalty()`
  - `calculate_team_repetition_penalty()`
  - `calculate_early_cut_bonus()`
  - `detect_cut_points()`

**Results**:
- Time: **15.98s ± 0.33s** (baseline: 16.84s)
- Speedup: **1.05x**
- Time saved: 0.86s (5.1% faster)
- Tests: ✅ All 204 tests passing

---

## Optimization 2: Vectorize Calendar methods

**Status**: ✅ Completed

**Description**:
Vectorize Calendar methods using numpy operations instead of iterating and creating Match objects. This includes `get_matches_per_player()`, `get_waiting_rounds_per_player()`, and `get_waiting_matches_per_player()`.

**Expected Impact**: 20-30% faster
**Actual Impact**: 23.8% faster (cumulative: 42.4% vs baseline)

**Changes**:
- Vectorized `get_matches_per_player()` using numpy sum operations on match arrays
- Modified `get_waiting_rounds_per_player()` to use `get_players_from_vector()`
- Modified `get_waiting_matches_per_player()` to use `get_players_from_vector()`
- Eliminated Match object creation in Calendar methods

**Results**:
- Time: **9.69s ± 0.08s** (vs 12.72s opt3, 16.84s baseline)
- Speedup: **1.74x** vs baseline
- Cumulative improvement: **42.4%**
- Tests: ✅ All 204 tests passing

---

## Optimization 3: Optimize calculate_early_cut_bonus()

**Status**: ✅ Completed

**Description**:
Calculate cut points incrementally instead of recounting from scratch for each round. This eliminates the O(n_rounds² × n_matches) complexity, making it O(n_matches).

**Expected Impact**: 40-60% faster
**Actual Impact**: 24.5% faster (cumulative: 32% vs baseline)

**Changes**:
- Refactored `calculate_early_cut_bonus()` to use incremental counting with numpy arrays
- Refactored `detect_cut_points()` similarly
- Changed from dict to numpy array for match counting
- Use numpy min/max operations instead of list conversions

**Results**:
- Time: **12.72s ± 0.13s** (vs 15.98s opt1, 16.84s baseline)
- Speedup: **1.32x** vs baseline
- Cumulative improvement: **24.5%**
- Tests: ✅ All 204 tests passing

---

## Optimization 4: Vectorize repetition penalties

**Status**: ✅ Completed (after careful mathematical analysis)

**Description**:
Vectorize opponent and team repetition penalties using numpy outer products and matrix operations. Initial attempt failed due to incorrect handling of symmetry and double-counting.

**Expected Impact**: 15-25% faster
**Actual Impact**: 5.1% faster (cumulative: 45.4% vs baseline)

**Changes**:
- **Opponent repetition**: Use outer(team1, team2) + outer(team2, team1) for symmetric opponent matrix
- **Team repetition**: Use outer(team1, team1) + outer(team2, team2) for teammate matrix
- Extract upper triangle (k=1) to avoid double counting
- Calculate penalty from non-zero counts: Σ(count - 1)²

**Key Insight**:
The challenge was handling matrix symmetry correctly:
- For opponents: Each match creates pairings between team1 and team2
- For teammates: Each team creates pairings within itself
- Only count upper triangle to avoid counting both (i,j) and (j,i)

**Results**:
- Time: **9.20s ± 0.20s** (vs 9.69s opt123, 16.84s baseline)
- Speedup: **1.83x** vs baseline
- Cumulative improvement: **45.4%**
- Tests: ✅ All 204 tests passing

**Lesson Learned**:
Complex optimizations require careful mathematical analysis. The first attempt failed because I didn't properly handle matrix symmetry. After analyzing the mathematics on paper and writing test cases, the vectorization succeeded.

---

## Overall Progress

| Optimization | Status | Time (s) | Speedup vs Baseline | Cumulative Speedup |
|--------------|--------|----------|---------------------|-------------------|
| Baseline     | ✅     | 16.84    | 1.00x              | 1.00x             |
| Opt 1        | ✅     | 15.98    | 1.05x              | 1.05x             |
| Opt 3        | ✅     | 12.72    | 1.32x              | 1.32x             |
| Opt 2        | ✅     | 9.69     | 1.74x              | 1.74x             |
| Opt 4        | ✅     | 9.20     | 1.83x              | 1.83x             |
| Opt 5-7      | ❌     | 10.00    | Reverted (slower)  | N/A               |

## Final Summary

**Total Performance Improvement**: 1.83x faster (45.4% reduction in execution time)
- Baseline: 16.84s ± 0.17s
- Final: 9.20s ± 0.20s
- Time saved: 7.64s per run (45.4% faster)

**Successful Optimizations**:
1. ✅ Pre-compute player indices (5.1% improvement)
2. ✅ Incremental cut point calculation (20.4% additional improvement)
3. ✅ Vectorize Calendar methods (23.8% additional improvement)
4. ✅ Vectorize repetition penalties (5.1% additional improvement)

**Key Achievements**:
- Reduced time complexity from O(n²) to O(n) in cut point detection
- Eliminated Pydantic validation overhead in hot paths
- Leveraged numpy vectorization for player statistics
- Vectorized repetition penalty calculations with outer products
- Maintained 100% test coverage (all 204 tests passing)

**Abandoned Optimizations**:
- Opt 5-7: Micro-optimizations that added numpy overhead for small data sizes

**Attempted but Abandoned Optimizations**:

## Optimization 5-7: Micro-optimizations (REVERTED)

**Status**: ❌ Abandoned - Made code slower

**Description**:
Attempted several micro-optimizations:
- Opt 5: Use `get_players_from_vector()` in `_generate_round_without_conflicts()`
- Opt 6: Use numpy min/max in `calculate_balance_penalty()`
- Opt 7: Vectorize `calculate_waiting_penalty()` with numpy

**Results**:
- Time: **10.00s ± 0.04s** (vs 9.69s previous)
- Performance: **3.2% SLOWER** (not faster!)
- **Reverted** all changes

**Lesson Learned**:
For small data sizes (10 players, few gaps), numpy array creation overhead exceeds benefits. Not all "vectorization" improves performance - measure first!

---

**Next Steps**:
- Retry vectorization of repetition penalties with better mathematical analysis
- Consider merging optimization branch to main
- Monitor performance in production scenarios
