"""
Color theme definitions for the Twinkly clock.
Add new themes by defining a dict and registering it in THEMES.
"""


def hex_to_rgb(hex_color):
    """Convert '#RRGGBB' to (R, G, B) tuple."""
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def lerp_color(c1, c2, t):
    """Linearly interpolate between two RGB tuples."""
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def scale_color(color, factor):
    """Scale an RGB color's brightness."""
    return (
        min(255, int(color[0] * factor)),
        min(255, int(color[1] * factor)),
        min(255, int(color[2] * factor)),
    )


OCEAN_DRIFT = {
    "name": "Ocean Drift",
    "description": "Calm, sophisticated, blue-dominant",
    "colors": {
        "background": (0, 0, 0),
        "hours": hex_to_rgb("#00AAFF"),
        "minutes": hex_to_rgb("#0066CC"),
        "seconds": hex_to_rgb("#004488"),
        "colon": hex_to_rgb("#00DDFF"),
        "ampm": hex_to_rgb("#006699"),
        "date": hex_to_rgb("#003366"),
        "border": hex_to_rgb("#001133"),
    },
    "effects": {
        "border_wave": True,
        "wave_speed": 0.05,
        "wave_colors": [
            hex_to_rgb("#001133"),
            hex_to_rgb("#002244"),
            hex_to_rgb("#001a3a"),
            hex_to_rgb("#000d22"),
        ],
    },
}

EMBER_GLOW = {
    "name": "Ember Glow",
    "description": "Warm, cozy, fireplace aesthetic",
    "colors": {
        "background": (0, 0, 0),
        "hours": hex_to_rgb("#FF6600"),
        "minutes": hex_to_rgb("#FF3300"),
        "seconds": hex_to_rgb("#CC2200"),
        "colon": hex_to_rgb("#FFAA00"),
        "ampm": hex_to_rgb("#993300"),
        "date": hex_to_rgb("#661100"),
        "border": hex_to_rgb("#110400"),
    },
    "effects": {
        "ember_flicker": True,
        "ember_colors": [
            hex_to_rgb("#110200"),
            hex_to_rgb("#220400"),
            hex_to_rgb("#331100"),
            hex_to_rgb("#441800"),
            hex_to_rgb("#221000"),
        ],
    },
}

NEON_SYNTHWAVE = {
    "name": "Neon Synthwave",
    "description": "Retro-futuristic, vibrant, 80s arcade",
    "colors": {
        "background": hex_to_rgb("#0A0014"),
        "hours": hex_to_rgb("#FF00FF"),
        "minutes": hex_to_rgb("#00FFFF"),
        "seconds": hex_to_rgb("#FF0088"),
        "colon": hex_to_rgb("#FFFF00"),
        "ampm": hex_to_rgb("#8800FF"),
        "date": hex_to_rgb("#4400AA"),
        "border": hex_to_rgb("#0A0014"),
    },
    "effects": {
        "gradient_sweep": True,
        "sweep_period": 30.0,
        "sweep_colors": [
            hex_to_rgb("#220044"),
            hex_to_rgb("#002233"),
        ],
    },
}

MINIMAL_WHITE = {
    "name": "Minimal White",
    "description": "Clean, modern, Scandinavian",
    "colors": {
        "background": (0, 0, 0),
        "hours": (255, 255, 255),
        "minutes": (204, 204, 204),
        "seconds": (102, 102, 102),
        "colon": (255, 255, 255),
        "ampm": (68, 68, 68),
        "date": (51, 51, 51),
        "border": (0, 0, 0),
    },
    "effects": {
        "breathing": True,
        "breathing_min": 0.80,
        "breathing_max": 1.00,
        "breathing_period": 4.0,
    },
}

AURORA_BOREALIS = {
    "name": "Aurora Borealis",
    "description": "Dynamic, colorful, natural",
    "colors": {
        "background": (0, 0, 0),
        "hours": (255, 255, 255),
        "minutes": (255, 255, 255),
        "seconds": hex_to_rgb("#88FFAA"),
        "colon": (255, 255, 255),
        "ampm": hex_to_rgb("#AAFFCC"),
        "date": hex_to_rgb("#66CC99"),
        "border": (0, 0, 0),
    },
    "effects": {
        "aurora": True,
        "aurora_speed": 60.0,
        "aurora_colors": [
            hex_to_rgb("#00FF66"),
            hex_to_rgb("#00CCAA"),
            hex_to_rgb("#6600CC"),
            hex_to_rgb("#0044FF"),
            hex_to_rgb("#00FF66"),
        ],
    },
}

TIME_OF_DAY = {
    "name": "Time-of-Day Adaptive",
    "description": "Changes with the actual time",
    "colors": {
        "background": (0, 0, 0),
        "hours": (255, 255, 255),
        "minutes": (204, 204, 204),
        "seconds": (136, 136, 136),
        "colon": (255, 255, 255),
        "ampm": (102, 102, 102),
        "date": (68, 68, 68),
        "border": (0, 0, 0),
    },
    "effects": {
        "adaptive": True,
        "periods": [
            (6, "morning", "#FFAA33", "#1A0500", 1.0),
            (10, "day", "#FFFFFF", "#000A14", 1.0),
            (16, "evening", "#FF6633", "#0A0005", 0.9),
            (20, "night", "#4488FF", "#000008", 0.7),
            (23, "sleep", "#220000", "#000000", 0.1),
        ],
    },
}

THEMES = {
    "ocean_drift": OCEAN_DRIFT,
    "ember_glow": EMBER_GLOW,
    "neon_synthwave": NEON_SYNTHWAVE,
    "minimal_white": MINIMAL_WHITE,
    "aurora_borealis": AURORA_BOREALIS,
    "time_of_day": TIME_OF_DAY,
}


def get_theme(name):
    """Retrieve a theme by key. Raises ValueError if not found."""
    theme = THEMES.get(name)
    if theme is None:
        raise ValueError(f"Unknown theme '{name}'. Available: {', '.join(THEMES)}")
    return theme


def list_themes():
    """Return list of (key, name, description) for all themes."""
    return [(k, t["name"], t["description"]) for k, t in THEMES.items()]
