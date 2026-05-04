from backend.predictor import ELO_RATINGS, predict_match


def print_prediction(team1, team2):
    """Print match prediction probabilities in a clean format."""
    result = predict_match(team1, team2)

    print(f"{result['team1']} vs {result['team2']}")
    print(f"{result['team1']}: {result['team1_win_probability']:.2%}")
    print(f"{result['team2']}: {result['team2_win_probability']:.2%}")


if __name__ == "__main__":
    team1 = input("Enter first team: ").strip()
    team2 = input("Enter second team: ").strip()

    # Validate team names before predicting so users get a clear message
    # instead of silently using the default Elo rating for unknown teams.
    if team1 not in ELO_RATINGS or team2 not in ELO_RATINGS:
        print("One or both teams not found. Please enter valid international team names.")
    else:
        print_prediction(team1, team2)
