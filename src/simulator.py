import random

try:
    from predictor import predict_match
except ModuleNotFoundError:
    from src.predictor import predict_match


random.seed(42)

TEAMS = [
    "Argentina",
    "Brazil",
    "France",
    "England",
    "Spain",
    "Germany",
    "Portugal",
    "Netherlands",
]

NUM_SIMULATIONS = 10000


def simulate_match(team1, team2):
    """Simulate one knockout match and return the winning team."""
    prediction = predict_match(team1, team2)
    team1_win_probability = prediction["team1_win_probability"]

    # random.random() returns a number between 0 and 1.
    # If that number is below team1's win probability, team1 wins.
    # Otherwise, team2 wins.
    if random.random() < team1_win_probability:
        return team1

    return team2


def simulate_tournament():
    """Simulate one 8-team knockout tournament and return the champion."""
    quarterfinal_winners = [
        simulate_match(TEAMS[0], TEAMS[1]),
        simulate_match(TEAMS[2], TEAMS[3]),
        simulate_match(TEAMS[4], TEAMS[5]),
        simulate_match(TEAMS[6], TEAMS[7]),
    ]

    semifinal_winners = [
        simulate_match(quarterfinal_winners[0], quarterfinal_winners[1]),
        simulate_match(quarterfinal_winners[2], quarterfinal_winners[3]),
    ]

    champion = simulate_match(semifinal_winners[0], semifinal_winners[1])
    return champion


def run_simulations():
    """Run many tournament simulations and count how often each team wins."""
    championship_wins = {}

    for team in TEAMS:
        championship_wins[team] = 0

    for _ in range(NUM_SIMULATIONS):
        champion = simulate_tournament()
        championship_wins[champion] += 1

    return championship_wins


def print_results(championship_wins):
    """Print raw championship wins and championship percentages."""
    print(f"Championship results after {NUM_SIMULATIONS} simulations:")

    sorted_results = sorted(
        championship_wins.items(),
        key=lambda team_result: team_result[1],
        reverse=True,
    )

    for team, wins in sorted_results:
        percentage = (wins / NUM_SIMULATIONS) * 100
        print(f"{team}: {wins} wins, {percentage:.2f}%")


if __name__ == "__main__":
    results = run_simulations()
    print_results(results)
