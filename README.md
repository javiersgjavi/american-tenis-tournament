# American Padel Tournament - Genetic Algorithm

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-178%20passing-brightgreen.svg)](tests/)
[![Code style: Clean](https://img.shields.io/badge/code%20style-clean-black.svg)](https://github.com/psf/black)

An optimized calendar generator for American-style padel tournaments using genetic algorithms. The system creates balanced match schedules that minimize repetitions and maximize flexibility through strategic cut points. Supports **multiple courts** for simultaneous matches.

## 🎯 Features

- **Genetic Algorithm Optimization**: Evolves tournament calendars to maximize quality
- **Multiple Courts Support**: Simultaneous matches on multiple courts with round-based scheduling
- **Balance Optimization**: Ensures all players play similar number of matches
- **Cut Points Detection**: Identifies optimal stopping points for flexible tournament lengths
- **Repetition Minimization**: Reduces team and opponent repetitions
- **Waiting Time Optimization**: Minimizes idle rounds for players
- **Distribution Analysis**: Ensures uniform spacing of cut points
- **Hyperparameter Optimization**: Tools to find optimal GA parameters
- **Parallel Processing**: Multi-core support for faster execution
- **Early Stopping**: Automatic convergence detection
- **Comprehensive Testing**: 178 tests covering all functionality

## 📋 Requirements

- Python 3.10+
- uv (package manager)

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/american-tenis-tournament.git
cd american-tenis-tournament

# Install dependencies using uv
uv sync
```

## 💻 Usage

### Basic Usage

```bash
# Run with default parameters (7 players, 50 matches)
uv run python main.py
```

### Custom Configuration

Edit `main.py` to customize parameters:

```python
# Tournament parameters
N_PLAYERS = 8           # Number of players
N_ROUNDS = 10           # Number of rounds to play
N_COURTS = 2            # Number of courts (default: 1)
# Total matches = N_ROUNDS × N_COURTS

# Genetic Algorithm parameters
POPULATION_SIZE = 100   # Size of the population
GENERATIONS = 200       # Number of generations to evolve
MUTATION_RATE = 0.1     # Probability of mutation (0.0 to 1.0)
CROSSOVER_RATE = 0.8    # Probability of crossover (0.0 to 1.0)
ELITISM_SIZE = 2        # Number of best individuals to preserve
EARLY_STOPPING_PATIENCE = 20  # Stop if no improvement for N generations

# Fitness weights
WEIGHT_BALANCE = 100.0      # Most important - balance matches per player
WEIGHT_OPPONENT_REP = 10.0  # Medium - minimize opponent repetitions
WEIGHT_TEAM_REP = 10.0      # Medium - minimize team repetitions
WEIGHT_WAITING = 5.0        # Low-medium - minimize waiting rounds
WEIGHT_EARLY_CUT = 50.0     # High - incentivize early cut points
```

### Multiple Courts

With multiple courts, matches are grouped into **rounds** where `N_COURTS` matches are played simultaneously:

```
📅 Round 1:
  🎾 Court 1 - Match 1: (A,B) vs (C,D)
  🎾 Court 2 - Match 2: (E,F) vs (G,H)

📅 Round 2:
  🎾 Court 1 - Match 3: (A,E) vs (B,F)
  🎾 Court 2 - Match 4: (C,G) vs (D,H)
```

**Minimum players per court configuration:**
- 1 court: 4 players minimum
- 2 courts: 8 players minimum  
- N courts: 4×N players minimum

### Hyperparameter Optimization

Find optimal parameters for your specific scenario:

```bash
# Run full optimization for all scenarios
uv run python run_hyperparameter_optimization.py

# Run quick optimization for medium tournaments
uv run python run_hyperparameter_optimization.py --quick --scenario medium

# Run optimization for specific scenario
uv run python run_hyperparameter_optimization.py --scenario small
uv run python run_hyperparameter_optimization.py --scenario large
```

Results are saved to `optimization_results/` directory in CSV and JSON formats.

## 🧪 Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_genetic_algorithm.py -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html
```

## 📊 Project Structure

```
american-tenis-tournament/
├── src/
│   ├── dataclasses.py              # Match and Calendar Pydantic models
│   ├── utils.py                    # Utility functions
│   ├── genetic_algorithm.py        # GA logic and fitness functions
│   ├── printer.py                  # Output formatting
│   └── hyperparameter_optimizer.py # Hyperparameter optimization tools
├── tests/
│   ├── test_match.py               # Tests for Match class
│   ├── test_calendar.py            # Tests for Calendar class
│   ├── test_fitness.py             # Tests for fitness functions
│   ├── test_genetic_algorithm.py   # Tests for GA
│   ├── test_cut_points.py          # Tests for cut points detection
│   ├── test_output.py              # Tests for output formatting
│   ├── test_main.py                # End-to-end tests
│   └── test_multiple_courts.py     # Tests for multiple courts functionality
├── docs_agent/
│   ├── agent.md                    # Project overview and concepts
│   ├── implementation.md           # Implementation details
│   ├── changelog.md                # Progress tracking
│   └── tests_info.md               # Test suite documentation
├── main.py                         # Main execution script
├── run_hyperparameter_optimization.py  # Hyperparameter optimization script
├── test_configurations.py          # Configuration testing script
└── README.md                       # This file
```

## 🎓 How It Works

### Chromosome Representation

Each calendar is represented as a matrix of shape `(N_MATCHES, 2 * N_PLAYERS)`:

```
Match vector: [team1_bits | team2_bits]
Example (7 players): [1,0,0,1,0,0,0, 0,1,1,0,0,0,0]
                      A B C D E F G   A B C D E F G
                      [  Team 1   ]   [  Team 2   ]
```

### Fitness Function

The fitness function combines multiple objectives:

1. **Balance Penalty** (weight: 100.0) - Most important
   - Penalizes uneven distribution of matches per player
   - Formula: `(max_matches - min_matches)²`

2. **Opponent Repetition Penalty** (weight: 10.0)
   - Penalizes repeated opponent pairings
   - Formula: `Σ(count - 1)²` for each opponent pair

3. **Team Repetition Penalty** (weight: 10.0)
   - Penalizes repeated team pairings
   - Formula: `Σ(count - 1)²` for each team pair

4. **Waiting Rounds Penalty** (weight: 5.0)
   - Penalizes long gaps between matches for players
   - Formula: `Σ(gap²)` for all players

5. **Early Cut Points Bonus** (weight: 50.0)
   - Rewards calendars with early and well-distributed cut points
   - Formula: `1000/(first_cut + 1) + count_bonuses + distribution_bonus`

### Genetic Operators

- **Selection**: Tournament selection (size: 3)
- **Crossover**: Single-point crossover (rate: 0.8)
- **Mutation**: Three operators - replace, swap, regenerate (rate: 0.1)
- **Elitism**: Preserves best 2 individuals

### Cut Points

A **cut point** is a position where the tournament can be stopped while maintaining balance:

- **Perfect cut**: All players have played exactly the same number of matches
- **Acceptable cut**: Maximum difference ≤ 1 match between players

The algorithm optimizes for:
1. Early first cut point
2. Maximum number of cut points
3. Uniform distribution of cut points

## 📈 Performance

### Typical Results (7 players, 30 matches)

- **Execution Time**: 30-40 seconds (with early stopping)
- **Quality**: ACCEPTABLE or better in 90%+ of runs
- **Balance**: Max difference ≤ 1 match between players
- **Cut Points**: 10-15 acceptable cut points
- **Distribution**: Well-distributed throughout calendar

### Recommended Configurations

**Small Tournaments (4-5 players, 10-20 matches):**
- Population: 50-75
- Generations: 100-150
- Time: < 5 seconds

**Medium Tournaments (6-7 players, 30-50 matches):**
- Population: 100-150
- Generations: 200-300
- Time: 30-60 seconds

**Large Tournaments (8-10 players, 60-100 matches):**
- Population: 150-200
- Generations: 300-500
- Time: 2-5 minutes

## 🔧 Configuration Testing

Test multiple configurations automatically:

```bash
uv run python test_configurations.py
```

This will test configurations for 4-8 players and provide detailed statistics.

## 📚 Documentation

Comprehensive documentation is available in the `docs_agent/` directory:

- **[agent.md](docs_agent/agent.md)**: Project overview, objectives, and algorithm concepts
- **[implementation.md](docs_agent/implementation.md)**: Technical implementation details and design decisions
- **[changelog.md](docs_agent/changelog.md)**: Complete development history and progress tracking
- **[tests_info.md](docs_agent/tests_info.md)**: Test suite documentation and coverage

## 🤝 Contributing

This project follows Test-Driven Development (TDD):

1. Write tests first (RED)
2. Implement code to pass tests (GREEN)
3. Refactor while keeping tests green (REFACTOR)

**Important**: Tests define the expected behavior. If a test fails, fix the code, not the test.

## 📝 Code Quality

- **Type Hints**: Full type annotations throughout
- **Pydantic Validation**: Automatic data validation
- **Clean Code**: Well-documented and organized
- **Testing**: 178 tests, 100% passing
- **English Only**: All code, comments, and documentation in English

## 🎯 Project Status

**Current Phase**: Phase 9 Complete - Multiple Courts Support ✅

**All Phases Completed:**
- ✅ Phase 1: Core Data Structures
- ✅ Phase 2: Fitness Function
- ✅ Phase 3: Genetic Algorithm
- ✅ Phase 4: Cut Points Detection
- ✅ Phase 5: Output Formatting
- ✅ Phase 6: Main Script and End-to-End Testing
- ✅ Phase 7: Testing and Optimization
- ✅ Phase 7.1: Enhanced Output and Distribution Optimization
- ✅ Phase 8: Hyperparameter Optimization
- ✅ Phase 9: Multiple Courts and Round-based Play

**Status**: Production Ready with Multiple Courts Support ✅

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

AI System for sports calendar generation

## 🙏 Acknowledgments

- Genetic Algorithms for optimization
- Pydantic for data validation
- pytest for testing framework
- tqdm for progress visualization
- joblib for parallelization

---

**Version**: 2.0  
**Last Updated**: 2025-12-31
