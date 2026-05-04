import csv
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "results.csv")

STARTING_RATING = 1500
K_FACTOR = 20


def load_matches():
    """Load historical match results from the CSV file."""
    matches = []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            matches.append(row)

    # Dates are stored as YYYY-MM-DD, so sorting the date strings works.
    matches.sort(key=lambda match: match["date"])
    return matches


def calculate_expected_score(team_rating, opponent_rating):
    """Calculate the expected Elo score for one team."""
    return 1 / (1 + math.pow(10, (opponent_rating - team_rating) / 400))


def update_elo_ratings():
    """Build Elo ratings by replaying every historical match."""
    ratings = {}
    matches = load_matches()

    for match in matches:
        home_team = match["home_team"]
        away_team = match["away_team"]

        # Some future scheduled matches have "NA" scores.
        # Elo ratings should only be updated with matches that have final scores.
        if match["home_score"] == "NA" or match["away_score"] == "NA":
            continue

        home_score = float(match["home_score"])
        away_score = float(match["away_score"])

        # Step 1: Get each team's current rating.
        # If a team has never appeared before, start it at STARTING_RATING.
        home_rating = ratings.get(home_team, STARTING_RATING)
        away_rating = ratings.get(away_team, STARTING_RATING)

        # Step 2: Calculate each team's expected score.
        # A stronger team has an expected score closer to 1.
        # A weaker team has an expected score closer to 0.
        home_expected = calculate_expected_score(home_rating, away_rating)
        away_expected = calculate_expected_score(away_rating, home_rating)

        # Step 3: Convert the real match result into Elo scores.
        # Win = 1.0, draw = 0.5, loss = 0.0.
        if home_score > away_score:
            home_actual = 1.0
            away_actual = 0.0
        elif home_score < away_score:
            home_actual = 0.0
            away_actual = 1.0
        else:
            home_actual = 0.5
            away_actual = 0.5

        # Step 4: Calculate each team's rating change.
        # Rating change = K_FACTOR * (actual score - expected score).
        # Teams gain more points for surprising wins and lose more for surprising losses.
        home_change = K_FACTOR * (home_actual - home_expected)
        away_change = K_FACTOR * (away_actual - away_expected)

        # Step 5: Save the updated ratings back into the dictionary.
        ratings[home_team] = home_rating + home_change
        ratings[away_team] = away_rating + away_change

    return ratings


# Build ratings once when this module is loaded.
# predict_match() can then reuse these ratings without recomputing them each time.
ELO_RATINGS = update_elo_ratings()


def predict_match(team1, team2):
    """Return win probabilities for two teams using their Elo ratings."""
    team1_rating = ELO_RATINGS.get(team1, STARTING_RATING)
    team2_rating = ELO_RATINGS.get(team2, STARTING_RATING)

    team1_probability = calculate_expected_score(team1_rating, team2_rating)
    team2_probability = 1 - team1_probability

    return {
        "team1": team1,
        "team2": team2,
        "team1_win_probability": team1_probability,
        "team2_win_probability": team2_probability,
    }


if __name__ == "__main__":
    print("Top 10 Elo-rated teams:")

    top_teams = sorted(
        ELO_RATINGS.items(),
        key=lambda team_rating: team_rating[1],
        reverse=True,
    )[:10]

    for rank, (team, rating) in enumerate(top_teams, start=1):
        print(f"{rank}. {team}: {rating:.1f}")

    print("\nSample prediction:")
    result = predict_match("Brazil", "Argentina")
    print(f"{result['team1']} vs {result['team2']}")
    print(f"{result['team1']}: {result['team1_win_probability']:.2%}")
    print(f"{result['team2']}: {result['team2_win_probability']:.2%}")
