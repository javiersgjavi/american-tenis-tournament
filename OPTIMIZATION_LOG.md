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

## Optimization 2: Cache matches_per_player computation

**Status**: Pending

**Description**:
Pre-compute player statistics using vectorial numpy operations instead of iterating and creating Match objects repeatedly.

**Expected Impact**: 20-30% faster

**Changes**:
- Add `_precompute_player_stats()` method to Calendar
- Use cached results in fitness functions

**Results**:
- Time: TBD
- Speedup: TBD
- Tests: TBD

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

**Status**: Pending

**Description**:
Use numpy matrix operations instead of defaultdict and loops for calculating opponent/team repetition penalties.

**Expected Impact**: 15-25% faster

**Changes**:
- Replace loops with numpy outer products
- Use matrix operations for counting pairs

**Results**:
- Time: TBD
- Speedup: TBD
- Tests: TBD

---

## Overall Progress

| Optimization | Status | Time (s) | Speedup vs Baseline | Cumulative Speedup |
|--------------|--------|----------|---------------------|-------------------|
| Baseline     | ✅     | 16.84    | 1.00x              | 1.00x             |
| Opt 1        | ✅     | 15.98    | 1.05x              | 1.05x             |
| Opt 3        | ✅     | 12.72    | 1.32x              | 1.32x             |
| Opt 2        | ⏳     | -        | -                  | -                 |
| Opt 4        | ⏳     | -        | -                  | -                 |
