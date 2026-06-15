"""
app.py - Flask web server for Pocket Caddy.
Serves the HTML interface and handles requests from the browser.
"""

from flask import Flask, render_template, request, jsonify
from Pocket_Caddy import (
    load_club_distances,
    update_club,
    recommend_club,
    CLUB_ORDER,
)

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")


@app.route("/api/clubs", methods=["GET"])
def get_clubs():
    """Return all club distances in order."""
    distances = load_club_distances()
    # Return as ordered list so the UI can display them in club order
    ordered = [{"club": club, "distance": distances.get(club)} for club in CLUB_ORDER]
    return jsonify(ordered)


@app.route("/api/clubs", methods=["POST"])
def set_club():
    """Update a single club's distance."""
    data = request.get_json()
    club = data.get("club", "").strip().upper()
    distance = data.get("distance")

    try:
        updated = update_club(club, distance)
        ordered = [{"club": c, "distance": updated.get(c)} for c in CLUB_ORDER]
        return jsonify({"success": True, "clubs": ordered})
    except (ValueError, TypeError) as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/recommend", methods=["POST"])
def get_recommendation():
    """Return a club recommendation based on shot conditions."""
    data = request.get_json()
    try:
        distance = int(data.get("distance", 0))
        wind = int(data.get("wind", 0))
        elevation = int(data.get("elevation", 0))
        result = recommend_club(distance, wind, elevation)
        return jsonify({"success": True, **result})
    except (ValueError, TypeError) as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"success": False, "error": str(e)}), 422


if __name__ == "__main__":
    app.run(debug=True)
