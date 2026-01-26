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

**Status**: ❌ Attempted but Abandoned

**Description**:
Attempted to use numpy matrix operations instead of defaultdict and loops for calculating opponent/team repetition penalties.

**Expected Impact**: 15-25% faster
**Actual Impact**: Not achieved - reverted due to test failures

**Changes Attempted**:
- Tried replacing loops with numpy outer products
- Attempted matrix operations for counting pairs
- Multiple approaches to handle symmetric matrices

**Results**:
- **Multiple test failures** with incorrect penalty calculations
- Issues with double-counting in outer product operations
- Symmetric matrix handling proved more complex than anticipated
- **Reverted changes** to maintain code correctness
- Tests: ✅ All 204 tests passing after revert

**Lesson Learned**:
The repetition penalty logic involves complex pair counting with specific conditions (opponents vs teammates, avoiding self-pairs). The nested loop approach, while not vectorized, is correct and maintainable. Further optimization would require careful mathematical analysis to ensure correctness.

---

## Overall Progress

| Optimization | Status | Time (s) | Speedup vs Baseline | Cumulative Speedup |
|--------------|--------|----------|---------------------|-------------------|
| Baseline     | ✅     | 16.84    | 1.00x              | 1.00x             |
| Opt 1        | ✅     | 15.98    | 1.05x              | 1.05x             |
| Opt 3        | ✅     | 12.72    | 1.32x              | 1.32x             |
| Opt 2        | ✅     | 9.69     | 1.74x              | 1.74x             |
| Opt 4        | ❌     | N/A      | Reverted           | N/A               |

## Final Summary

**Total Performance Improvement**: 1.74x faster (42.4% reduction in execution time)
- Baseline: 16.84s ± 0.17s
- Final: 9.69s ± 0.08s
- Time saved: 7.15s per run

**Successful Optimizations**:
1. ✅ Pre-compute player indices (5.1% improvement)
2. ✅ Incremental cut point calculation (20.4% additional improvement)
3. ✅ Vectorize Calendar methods (23.8% additional improvement)

**Key Achievements**:
- Reduced time complexity from O(n²) to O(n) in cut point detection
- Eliminated Pydantic validation overhead in hot paths
- Leveraged numpy vectorization for player statistics
- Maintained 100% test coverage (all 204 tests passing)

**Next Steps**:
- Consider merging optimization branch to main
- Monitor performance in production scenarios
- Explore parallelization opportunities if further speedup needed
