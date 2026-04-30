# World Cup Prediction & Simulation Engine

## Overview

This project predicts international soccer match outcomes and simulates World Cup-style knockout tournaments. It uses historical match results to build simple Elo ratings, then runs Monte Carlo simulations to estimate championship probabilities.

The goal is to keep the project clear, readable, and practical as a portfolio piece for internship applications.

## Features

- Loads historical international match data from `data/results.csv`
- Builds Elo ratings from past match results
- Predicts win probabilities for two teams
- Simulates an 8-team knockout tournament
- Runs 10,000 Monte Carlo simulations
- Prints raw championship wins and championship percentages
- Includes a simple command-line interface for match predictions

## Methodology

### Elo Ratings

Each team starts with the same Elo rating. The model replays historical matches in date order and updates ratings after each match.

- Win = `1.0`
- Draw = `0.5`
- Loss = `0.0`

Teams gain more rating points for surprising wins and lose more points for surprising losses.

### Monte Carlo Simulation

The simulator uses the Elo-based match probabilities to choose winners with Python's `random` module. It repeats the tournament 10,000 times and counts how often each team wins the championship.

The tournament bracket is shuffled each simulation so results are not tied to one fixed set of quarterfinal matchups.

## Example Output

Match prediction:

```text
Brazil vs France
Brazil: 42.13%
France: 57.87%
```

Tournament simulation:

```text
Championship results after 10000 simulations:
Spain: 2231 wins, 22.31%
Argentina: 1984 wins, 19.84%
France: 1702 wins, 17.02%
```

## Technologies Used

- Python
- CSV data processing
- Elo rating system
- Monte Carlo simulation

## Future Improvements

- Add draw probabilities for group-stage simulations
- Simulate a full World Cup format with groups and knockout rounds
- Add home-field or neutral-site adjustments
- Compare model predictions against held-out historical matches
- Add charts for Elo ratings and tournament probabilities
