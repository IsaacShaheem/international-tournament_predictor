import os
import sys

from flask import Flask, jsonify, request
from flask_cors import CORS


# backend/app.py lives outside the src folder.
# These paths let Python import predictor.py and simulator.py from src.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FOLDER = os.path.join(PROJECT_ROOT, "src")
BACKEND_FOLDER = os.path.dirname(os.path.abspath(__file__))

for folder in [SRC_FOLDER, BACKEND_FOLDER]:
    if folder not in sys.path:
        sys.path.insert(0, folder)

from predictor import predict_match
from simulator import get_default_advancing_count, run_full_simulations, run_simulations


# Create the Flask app.
app = Flask(__name__)

# Enable CORS so a React frontend can call this API from another port.
CORS(app)


@app.route("/api/predict", methods=["GET"])
def predict():
    """Return match win probabilities for two teams."""
    team1 = request.args.get("team1")
    team2 = request.args.get("team2")

    # Both teams are required because predict_match needs two inputs.
    if not team1 or not team2:
        return jsonify({"error": "Please provide team1 and team2 query parameters."}), 400

    prediction = predict_match(team1, team2)
    return jsonify(prediction)


@app.route("/api/simulate", methods=["GET"])
def simulate():
    """Run tournament simulations and return championship win counts."""
    results = run_simulations()
    return jsonify(results)


def validate_groups(groups):
    """Validate and label frontend groups as A, B, C, and D."""
    if not isinstance(groups, list) or len(groups) != 4:
        return None, "Please provide exactly 4 groups."

    group_labels = ["A", "B", "C", "D"]
    labeled_groups = {}
    seen_teams = set()

    for index, group in enumerate(groups):
        if not isinstance(group, list) or len(group) != 4:
            return None, "Each group must contain exactly 4 teams."

        cleaned_group = []

        for team in group:
            if not isinstance(team, str) or not team.strip():
                return None, "Team names must be non-empty strings."

            cleaned_team = team.strip()
            normalized_team = cleaned_team.lower()

            if normalized_team in seen_teams:
                return None, "Team names must not be duplicated."

            seen_teams.add(normalized_team)
            cleaned_group.append(cleaned_team)

        labeled_groups[group_labels[index]] = cleaned_group

    return labeled_groups, None


def is_power_of_two(number):
    """Return True when number is 4, 8, 16, 32, etc."""
    return number > 0 and number & (number - 1) == 0


def validate_total_advancing_teams(total_advancing_teams, groups):
    """Validate the requested knockout size."""
    if total_advancing_teams is None:
        return get_default_advancing_count(groups), None

    if not isinstance(total_advancing_teams, int):
        return None, "total_advancing_teams must be an integer."

    if not is_power_of_two(total_advancing_teams):
        return None, "total_advancing_teams must be a power of 2."

    base_qualifiers = len(groups) * 2
    max_qualifiers = base_qualifiers + len(groups)

    if total_advancing_teams < base_qualifiers:
        return None, "total_advancing_teams is too small for the number of groups."

    if total_advancing_teams > max_qualifiers:
        return None, "total_advancing_teams is too large for the number of groups."

    return total_advancing_teams, None


def validate_seed(seed):
    """Validate optional seed value for reproducible simulations."""
    if seed is None:
        return None, None

    if not isinstance(seed, int):
        return None, "seed must be an integer."

    return seed, None


@app.route("/api/simulate-full", methods=["GET", "POST"])
def simulate_full():
    """Run full tournament simulations and return championship probabilities."""
    if request.method == "POST":
        if not request.is_json:
            return jsonify({"error": "Request body must be JSON."}), 400

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({"error": "Request JSON must be an object."}), 400

        groups = data.get("groups")
        labeled_groups, error = validate_groups(groups)

        if error:
            return jsonify({"error": error}), 400

        total_advancing_teams, error = validate_total_advancing_teams(
            data.get("total_advancing_teams"),
            labeled_groups,
        )

        if error:
            return jsonify({"error": error}), 400

        seed, error = validate_seed(data.get("seed"))

        if error:
            return jsonify({"error": error}), 400

        results = run_full_simulations(labeled_groups, total_advancing_teams, seed)
        return jsonify(results)

    results = run_full_simulations()
    return jsonify(results)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
