# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

American Tennis Tournament is a genetic algorithm-based calendar generator for "Americano" style doubles tournaments (tennis, padel, pickleball). The goal is to create match schedules where everyone plays with everyone while minimizing partner/opponent repetition and balancing match distribution.

## Commands

```bash
# Install dependencies
uv sync

# Run CLI tournament generator
uv run python main.py

# Run Streamlit web interface
uv run streamlit run streamlit_app.py

# Run all tests (178 tests)
uv run pytest tests/ -v

# Run single test file
uv run pytest tests/test_fitness.py -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Format code
black <files>
```

## Architecture

**Core Package (`src/`):**
- `dataclasses.py` - Pydantic models: `Match` (4 players, 2 teams) and `Calendar` (complete schedule with multi-court support)
- `genetic_algorithm.py` - `GeneticAlgorithm` class with fitness functions, selection, crossover, mutation, and early stopping
- `printer.py` - Output formatting and export (CSV for Excel, TXT for human-readable reports)
- `utils.py` - Match generation and validation utilities

**Entry Points:**
- `main.py` - CLI with configurable tournament and GA parameters
- `streamlit_app.py` - Mobile-friendly web UI

**Fitness Function Components:**
1. Round conflict penalty (hard constraint for multi-court)
2. Balance penalty (match distribution across players)
3. Opponent repetition penalty
4. Team repetition penalty
5. Waiting time penalty
6. Early cut point bonus

## Key Concepts

**Cut Points:** Moments in the schedule where all players have played exactly the same number of matches - useful for fair tournament breaks.

**Multiple Courts:** With N courts, N matches play simultaneously per round. Minimum players = 4 × N_COURTS.

**One-Hot Encoding:** Matches represented as binary vectors with exactly 4 ones (2 per team).

## Configuration (in main.py)

```python
# Tournament parameters
N_PLAYERS = 10           # Number of players
N_ROUNDS = 10            # Number of rounds
N_COURTS = 2             # Simultaneous courts (min 4×N_COURTS players)

# GA parameters
POPULATION_SIZE = 100
GENERATIONS = 200
MUTATION_RATE = 0.2      # High for exploration
CROSSOVER_RATE = 0.8
ELITISM_SIZE = 2
N_JOBS = -1              # Parallel: -1 = all cores
EARLY_STOPPING_PATIENCE = 50

# Fitness weights
WEIGHT_BALANCE = 100.0   # Highest priority
WEIGHT_OPPONENT_REP = 10.0
WEIGHT_TEAM_REP = 10.0
WEIGHT_WAITING = 5.0
WEIGHT_EARLY_CUT = 75.0  # High bonus for early cut points
```

## Output Files

Generated in `outputs/`:
- `tournament_calendar.csv` - Match schedule for Excel
- `tournament_results.txt` - Human-readable report with statistics and cut points
