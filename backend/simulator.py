import random

try:
    from predictor import predict_match
except ModuleNotFoundError:
    from backend.predictor import predict_match


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

GROUPS = {
    "A": ["Argentina", "Brazil", "France", "England"],
    "B": ["Spain", "Germany", "Portugal", "Netherlands"],
    "C": ["Croatia", "Belgium", "Uruguay", "Japan"],
    "D": ["Morocco", "United States", "Mexico", "Canada"],
}


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
    # Shuffle the bracket each tournament so the simulation is not tied to
    # one fixed set of quarterfinal matchups. This makes the results more realistic.
    teams = TEAMS.copy()
    random.shuffle(teams)

    quarterfinal_winners = [
        simulate_match(teams[0], teams[1]),
        simulate_match(teams[2], teams[3]),
        simulate_match(teams[4], teams[5]),
        simulate_match(teams[6], teams[7]),
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


def simulate_group_stage(group_teams):
    """Simulate one round-robin group and return sorted standings."""
    standings = {}

    for team in group_teams:
        standings[team] = {
            "points": 0,
            "wins": 0,
            "losses": 0,
            "matches_played": 0,
        }

    # Round robin: each team plays every other team once.
    # The i < j loop prevents duplicate matchups.
    for i in range(len(group_teams)):
        for j in range(i + 1, len(group_teams)):
            team1 = group_teams[i]
            team2 = group_teams[j]
            winner = simulate_match(team1, team2)

            if winner == team1:
                loser = team2
            else:
                loser = team1

            standings[winner]["points"] += 3
            standings[winner]["wins"] += 1
            standings[winner]["matches_played"] += 1

            standings[loser]["losses"] += 1
            standings[loser]["matches_played"] += 1

    # The random number breaks ties without always favoring input order.
    sorted_standings = sorted(
        standings.items(),
        key=lambda team_standing: (
            team_standing[1]["points"],
            team_standing[1]["wins"],
            random.random(),
        ),
        reverse=True,
    )

    return sorted_standings


def get_all_teams(groups):
    """Return every team from every group."""
    teams = []

    for group_teams in groups.values():
        teams.extend(group_teams)

    return teams


def get_default_advancing_count(groups):
    """Top 2 teams from each group advance by default."""
    return len(groups) * 2


def qualify_teams(groups, total_advancing_teams):
    """Select top 2 from each group plus best 3rd-place teams if needed."""
    base_qualifiers = []
    third_place_teams = []

    for group_name in sorted(groups):
        standings = simulate_group_stage(groups[group_name])

        base_qualifiers.append(standings[0][0])
        base_qualifiers.append(standings[1][0])

        third_place_team = standings[2]
        third_place_teams.append(
            {
                "team": third_place_team[0],
                "points": third_place_team[1]["points"],
                "wins": third_place_team[1]["wins"],
                "tie_break": random.random(),
            }
        )

    extra_spots = total_advancing_teams - len(base_qualifiers)

    sorted_third_place_teams = sorted(
        third_place_teams,
        key=lambda team: (team["points"], team["wins"], team["tie_break"]),
        reverse=True,
    )

    additional_qualifiers = [
        team["team"] for team in sorted_third_place_teams[:extra_spots]
    ]

    qualified_teams = base_qualifiers + additional_qualifiers

    if len(qualified_teams) != total_advancing_teams:
        raise ValueError("Qualified team count does not match knockout size.")

    return qualified_teams


def simulate_knockout_rounds(qualified_teams):
    """Simulate knockout rounds until one champion remains."""
    teams = qualified_teams.copy()

    # Shuffle once to create a simple neutral bracket.
    random.shuffle(teams)

    while len(teams) > 1:
        next_round = []

        for i in range(0, len(teams), 2):
            winner = simulate_match(teams[i], teams[i + 1])
            next_round.append(winner)

        teams = next_round

    return teams[0]


def simulate_one_tournament(custom_groups=None, total_advancing_teams=None):
    """Simulate group stage, qualification, knockout rounds, and final."""
    groups = custom_groups or GROUPS
    advancing_count = total_advancing_teams or get_default_advancing_count(groups)
    qualified_teams = qualify_teams(groups, advancing_count)

    return simulate_knockout_rounds(qualified_teams)


def run_full_simulations(custom_groups=None, total_advancing_teams=None, seed=None):
    """Run many full tournament simulations and return championship probabilities."""
    if seed is not None:
        random.seed(seed)

    groups = custom_groups or GROUPS
    teams = get_all_teams(groups)
    advancing_count = total_advancing_teams or get_default_advancing_count(groups)

    championship_wins = {}

    for team in teams:
        championship_wins[team] = 0

    for _ in range(NUM_SIMULATIONS):
        champion = simulate_one_tournament(groups, advancing_count)
        championship_wins[champion] += 1

    championship_probabilities = {}

    for team, wins in championship_wins.items():
        championship_probabilities[team] = wins / NUM_SIMULATIONS

    return championship_probabilities


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
