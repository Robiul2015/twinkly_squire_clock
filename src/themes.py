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


def hsv_to_rgb(h, s, v):
    """Convert HSV (h=0-360, s=0-1, v=0-1) to RGB tuple."""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


# ---------------------------------------------------------------------------
# Original themes
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# New themes
# ---------------------------------------------------------------------------

LEAF_HORIZON = {
    "name": "Leaf Horizon",
    "description": "Soothing green palette that shifts through the day, dawn to night",
    "colors": {
        "background": hex_to_rgb("#050A06"),
        "hours": hex_to_rgb("#8EDFA6"),
        "minutes": hex_to_rgb("#71B284"),
        "seconds": hex_to_rgb("#47704F"),
        "colon": hex_to_rgb("#A0E8B4"),
        "ampm": hex_to_rgb("#386B48"),
        "date": hex_to_rgb("#2A4F35"),
        "border": hex_to_rgb("#050A06"),
    },
    "effects": {
        "adaptive": True,
        "periods": [
            (6, "mint_dawn", "#45B892", "#060C08", 0.70),
            (9, "fresh_leaf", "#3FBE57", "#050A06", 0.85),
            (16, "mossy_gold", "#9FB35A", "#0A0A04", 0.75),
            (19, "forest_dusk", "#2F7A52", "#060B08", 0.45),
            (22, "deep_pine", "#2E5A3E", "#020503", 0.12),
        ],
    },
}

SUNSET_BOULEVARD = {
    "name": "Sunset Boulevard",
    "description": "Warm golden hour gradient",
    "colors": {
        "background": (0, 0, 0),
        "hours": hex_to_rgb("#FFE0B0"),
        "minutes": hex_to_rgb("#FF7755"),
        "seconds": hex_to_rgb("#CC4422"),
        "colon": hex_to_rgb("#FFAA00"),
        "ampm": hex_to_rgb("#CC6633"),
        "date": hex_to_rgb("#884422"),
        "border": hex_to_rgb("#110500"),
    },
    "effects": {
        "border_wave": True,
        "wave_speed": 0.03,
        "wave_colors": [
            hex_to_rgb("#1A0800"),
            hex_to_rgb("#220A04"),
            hex_to_rgb("#180610"),
            hex_to_rgb("#140412"),
            hex_to_rgb("#1A0800"),
        ],
    },
}

CYBERPUNK_TOKYO = {
    "name": "Cyberpunk Tokyo",
    "description": "Hot pink on deep purple, high contrast",
    "colors": {
        "background": hex_to_rgb("#06000A"),
        "hours": hex_to_rgb("#FF1493"),
        "minutes": hex_to_rgb("#AAFF00"),
        "seconds": hex_to_rgb("#FF0066"),
        "colon": (255, 255, 255),
        "ampm": hex_to_rgb("#AA00FF"),
        "date": hex_to_rgb("#6600AA"),
        "border": hex_to_rgb("#06000A"),
    },
    "effects": {
        "pixel_chase": True,
        "chase_speed": 0.15,
        "chase_colors": [
            hex_to_rgb("#FF1493"),
            hex_to_rgb("#00FFCC"),
        ],
    },
}

FOREST_CANOPY = {
    "name": "Forest Canopy",
    "description": "Natural greens, calming",
    "colors": {
        "background": (0, 0, 0),
        "hours": hex_to_rgb("#33FF66"),
        "minutes": hex_to_rgb("#00CC77"),
        "seconds": hex_to_rgb("#009955"),
        "colon": hex_to_rgb("#88FF00"),
        "ampm": hex_to_rgb("#228844"),
        "date": hex_to_rgb("#116633"),
        "border": hex_to_rgb("#001A05"),
    },
    "effects": {
        "shimmer": True,
        "shimmer_colors": [
            hex_to_rgb("#001A05"),
            hex_to_rgb("#002A08"),
            hex_to_rgb("#00220A"),
            hex_to_rgb("#001808"),
        ],
        "shimmer_speed": 0.04,
        "shimmer_density": 0.3,
    },
}

LAVA_LAMP = {
    "name": "Lava Lamp",
    "description": "Slow-morphing warm color blobs",
    "colors": {
        "background": (0, 0, 0),
        "hours": hex_to_rgb("#FF2200"),
        "minutes": hex_to_rgb("#FF8800"),
        "seconds": hex_to_rgb("#CC4400"),
        "colon": hex_to_rgb("#FFDD00"),
        "ampm": hex_to_rgb("#AA4400"),
        "date": hex_to_rgb("#882200"),
        "border": (0, 0, 0),
    },
    "effects": {
        "lava": True,
        "lava_speed": 0.02,
        "lava_colors": [
            hex_to_rgb("#220000"),
            hex_to_rgb("#331100"),
            hex_to_rgb("#221000"),
            hex_to_rgb("#110800"),
            hex_to_rgb("#2A0500"),
        ],
    },
}

ICE_CRYSTAL = {
    "name": "Ice Crystal",
    "description": "Cold whites and pale blues, elegant",
    "colors": {
        "background": (0, 0, 0),
        "hours": hex_to_rgb("#EEFFFF"),
        "minutes": hex_to_rgb("#88CCFF"),
        "seconds": hex_to_rgb("#5599CC"),
        "colon": (255, 255, 255),
        "ampm": hex_to_rgb("#6699AA"),
        "date": hex_to_rgb("#446677"),
        "border": (0, 0, 0),
    },
    "effects": {
        "sparkle": True,
        "sparkle_color": (180, 220, 255),
        "sparkle_chance": 0.03,
    },
}

RAINBOW_SHIFT = {
    "name": "Rainbow Shift",
    "description": "Digits cycle through the full spectrum",
    "colors": {
        "background": (0, 0, 0),
        "hours": (255, 0, 0),
        "minutes": (0, 255, 0),
        "seconds": (0, 0, 255),
        "colon": (255, 255, 255),
        "ampm": (128, 128, 128),
        "date": (64, 64, 64),
        "border": (0, 0, 0),
    },
    "effects": {
        "rainbow": True,
        "rainbow_speed": 6.0,
        "rainbow_border": True,
    },
}

MATRIX_TERMINAL = {
    "name": "Matrix Terminal",
    "description": "Phosphor-green terminal with scanlines and falling code rain",
    "colors": {
        "background": (0, 0, 0),
        "hours": hex_to_rgb("#39FF6A"),
        "minutes": hex_to_rgb("#1FCC50"),
        "seconds": hex_to_rgb("#0E7A30"),
        "colon": hex_to_rgb("#AFFFC0"),
        "ampm": hex_to_rgb("#167A36"),
        "date": hex_to_rgb("#0B4A20"),
        "border": (0, 0, 0),
    },
    "effects": {
        "matrix_rain": True,
        "rain_color": hex_to_rgb("#17C94A"),
        "rain_speed": 4.5,
        "rain_trail": 5,
        "scanlines": True,
        "scanline_color": hex_to_rgb("#021407"),
        "scanline_period": 3,
    },
}

GREEN_LAVA = {
    "name": "Green Lava",
    "description": "Forest canopy digits with green lava blob background",
    "colors": {
        "background": (0, 0, 0),
        "hours": hex_to_rgb("#33FF66"),
        "minutes": hex_to_rgb("#00CC77"),
        "seconds": hex_to_rgb("#009955"),
        "colon": hex_to_rgb("#88FF00"),
        "ampm": hex_to_rgb("#228844"),
        "date": hex_to_rgb("#116633"),
        "border": hex_to_rgb("#001A05"),
    },
    "effects": {
        "lava": True,
        "lava_speed": 0.02,
        "lava_colors": [
            hex_to_rgb("#001A05"),
            hex_to_rgb("#002A0A"),
            hex_to_rgb("#003A10"),
            hex_to_rgb("#00220C"),
            hex_to_rgb("#001808"),
        ],
        "shimmer": True,
        "shimmer_colors": [
            hex_to_rgb("#001A05"),
            hex_to_rgb("#002A08"),
            hex_to_rgb("#00220A"),
            hex_to_rgb("#001808"),
        ],
        "shimmer_speed": 0.04,
        "shimmer_density": 0.3,
    },
}

# ---------------------------------------------------------------------------
# Theme registry
# ---------------------------------------------------------------------------

THEMES = {
    "ocean_drift": OCEAN_DRIFT,
    "ember_glow": EMBER_GLOW,
    "neon_synthwave": NEON_SYNTHWAVE,
    "minimal_white": MINIMAL_WHITE,
    "aurora_borealis": AURORA_BOREALIS,
    "time_of_day": TIME_OF_DAY,
    "sunset_boulevard": SUNSET_BOULEVARD,
    "cyberpunk_tokyo": CYBERPUNK_TOKYO,
    "forest_canopy": FOREST_CANOPY,
    "lava_lamp": LAVA_LAMP,
    "ice_crystal": ICE_CRYSTAL,
    "rainbow_shift": RAINBOW_SHIFT,
    "green_lava": GREEN_LAVA,
    "matrix_terminal": MATRIX_TERMINAL,
    "leaf_horizon": LEAF_HORIZON,
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
