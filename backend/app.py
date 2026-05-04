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
from simulator import run_simulations


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


if __name__ == "__main__":
    app.run(debug=True)
