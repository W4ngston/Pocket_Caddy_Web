"""
Pocket Caddy core logic - ported from CLI to web-ready functions.
All input/output is now handled by app.py (Flask), not print/input.
"""

ELEVATION = 0.00116  # Adjustment per foot of elevation change (Trackman data)
WIND_LOSS = 2        # Yards lost per mph of headwind (PGA Tour data)
WIND_GAIN = 1        # Yards gained per mph of tailwind (PGA Tour data)

CLUB_ORDER = ["D", "W", "H", "3", "4", "5", "6", "7", "8", "9", "PW", "SW", "60"]

FILE_NAME = "club_distances.txt"


def load_club_distances():
    """Load club distances from file. Creates file with defaults if missing."""
    try:
        with open(FILE_NAME, "r") as f:
            lines = f.readlines()
            club_distances = {}
            for line in lines:
                club, distance = line.strip().split(":")
                club_distances[club.upper()] = int(distance) if distance != "None" else None
    except FileNotFoundError:
        club_distances = {club: None for club in CLUB_ORDER}
        save_club_distances(club_distances)
    return club_distances


def save_club_distances(club_distances):
    """Save club distances dictionary to file."""
    with open(FILE_NAME, "w") as f:
        for club, distance in club_distances.items():
            f.write(f"{club}:{distance}\n")


def update_club(club, distance):
    """Update a single club's distance. Returns updated dict or raises ValueError."""
    club = club.upper()
    if club not in CLUB_ORDER:
        raise ValueError(f"'{club}' is not a valid club.")
    distance = int(distance)
    if distance <= 0:
        raise ValueError("Distance must be a positive number.")
    club_distances = load_club_distances()
    club_distances[club] = distance
    save_club_distances(club_distances)
    return club_distances


def elevation_adjustment(distance_to_pin, pin_elevation):
    """Returns yardage adjustment for elevation change."""
    return int(distance_to_pin * (ELEVATION * pin_elevation))


def wind_adjustment(wind):
    """Returns yardage adjustment for wind (positive = headwind, negative = tailwind)."""
    if wind > 0:
        return int(wind * WIND_LOSS)
    else:
        return int(wind * WIND_GAIN)


def recommend_club(distance_to_pin, wind, pin_elevation):
    """
    Given shot conditions, returns the recommended club and adjusted distance.
    Raises ValueError on bad input, RuntimeError if no clubs are set.
    """
    if distance_to_pin <= 0:
        raise ValueError("Distance to pin must be a positive number.")

    adjusted = distance_to_pin + wind_adjustment(wind) + elevation_adjustment(distance_to_pin, pin_elevation)

    club_distances = load_club_distances()
    valid_clubs = {club: dist for club, dist in club_distances.items() if dist is not None}

    if not valid_clubs:
        raise RuntimeError("No club distances set. Please add your distances first.")

    best_club, best_dist = min(valid_clubs.items(), key=lambda x: abs(x[1] - adjusted))

    return {
        "adjusted_distance": adjusted,
        "recommended_club": best_club,
        "club_typical_distance": best_dist,
    }
