"""
Background and decorative effects for the Twinkly clock display.
Each effect modifies the frame buffer in place, only touching black pixels.
"""

import math
import random

from themes import lerp_color, scale_color, hex_to_rgb, hsv_to_rgb


def apply_effects(frame, width, height, theme, now_ts, tick_count):
    """Apply all active effects for a theme to the frame buffer."""
    effects = theme.get("effects", {})

    if effects.get("border_wave"):
        _apply_border_wave(frame, width, height, effects, now_ts)
    if effects.get("ember_flicker"):
        _apply_ember_flicker(frame, width, height, effects, tick_count)
    if effects.get("gradient_sweep"):
        _apply_gradient_sweep(frame, width, height, effects, now_ts)
    if effects.get("aurora"):
        _apply_aurora(frame, width, height, effects, now_ts)
    if effects.get("pixel_chase"):
        _apply_pixel_chase(frame, width, height, effects, now_ts)
    if effects.get("shimmer"):
        _apply_shimmer(frame, width, height, effects, now_ts)
    if effects.get("lava"):
        _apply_lava(frame, width, height, effects, now_ts)
    if effects.get("sparkle"):
        _apply_sparkle(frame, width, height, effects, tick_count)
    if effects.get("rainbow_border"):
        _apply_rainbow_border(frame, width, height, effects, now_ts)


def get_rainbow_colors(theme, now_ts):
    """Return dynamically cycling colors for the rainbow theme."""
    effects = theme.get("effects", {})
    if not effects.get("rainbow"):
        return None
    speed = effects.get("rainbow_speed", 6.0)
    base_hue = (now_ts * 360 / speed) % 360
    return {
        "hours": hsv_to_rgb(base_hue, 1.0, 1.0),
        "minutes": hsv_to_rgb(base_hue + 120, 1.0, 1.0),
        "colon": hsv_to_rgb(base_hue + 60, 1.0, 1.0),
    }


def apply_seconds_pulse(color, theme, now_ts):
    """Return brightness-modulated color for pulsing effect."""
    effects = theme.get("effects", {})
    if not effects.get("seconds_pulse"):
        return color
    period = effects.get("pulse_period", 2.0)
    phase = (now_ts % period) / period * 2 * math.pi
    factor = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(phase))
    return scale_color(color, factor)


def apply_breathing(color, theme, now_ts):
    """Apply slow breathing brightness oscillation."""
    effects = theme.get("effects", {})
    if not effects.get("breathing"):
        return color
    lo = effects.get("breathing_min", 0.8)
    hi = effects.get("breathing_max", 1.0)
    period = effects.get("breathing_period", 4.0)
    phase = (now_ts % period) / period * 2 * math.pi
    factor = lo + (hi - lo) * (0.5 + 0.5 * math.sin(phase))
    return scale_color(color, factor)


def get_adaptive_colors(theme, hour):
    """Get colors adjusted for time-of-day adaptive theme."""
    effects = theme.get("effects", {})
    if not effects.get("adaptive"):
        return theme["colors"]

    periods = effects["periods"]
    colors = dict(theme["colors"])

    current_period = periods[-1]
    for i, period in enumerate(periods):
        next_hour = periods[i + 1][0] if i + 1 < len(periods) else periods[0][0] + 24
        if period[0] <= hour < next_hour:
            current_period = period
            break

    _, _, hours_hex, bg_hex, brightness = current_period
    base = hex_to_rgb(hours_hex)
    colors["hours"] = scale_color(base, brightness)
    colors["minutes"] = scale_color(base, brightness * 0.8)
    colors["seconds"] = scale_color(base, brightness * 0.5)
    colors["colon"] = scale_color(base, brightness * 0.9)
    colors["ampm"] = scale_color(base, brightness * 0.4)
    colors["date"] = scale_color(base, brightness * 0.3)
    colors["background"] = hex_to_rgb(bg_hex)
    colors["border"] = hex_to_rgb(bg_hex)
    return colors


# ---------------------------------------------------------------------------
# Effect implementations
# ---------------------------------------------------------------------------

def _get_border(width, height):
    """Return list of (y, x) border pixel positions."""
    border = []
    for x in range(width):
        border.append((0, x))
        border.append((height - 1, x))
    for y in range(1, height - 1):
        border.append((y, 0))
        border.append((y, width - 1))
    return border


def _apply_border_wave(frame, width, height, effects, now_ts):
    """Slow color wave along border pixels."""
    wave_colors = effects.get("wave_colors", [(0, 17, 51)])
    speed = effects.get("wave_speed", 0.05)
    num = len(wave_colors)

    for i, (y, x) in enumerate(_get_border(width, height)):
        if frame[y][x] == (0, 0, 0):
            phase = (now_ts * speed + i * 0.15) % num
            idx = int(phase)
            frame[y][x] = lerp_color(wave_colors[idx % num], wave_colors[(idx + 1) % num], phase - idx)


def _apply_ember_flicker(frame, width, height, effects, tick_count):
    """Random flickering ember effect on border pixels."""
    ember_colors = effects.get("ember_colors", [(17, 2, 0)])
    for y, x in _get_border(width, height):
        if frame[y][x] == (0, 0, 0):
            intensity = y / height
            base = random.choice(ember_colors)
            frame[y][x] = scale_color(base, 0.3 + 0.7 * intensity * random.uniform(0.5, 1.0))


def _apply_gradient_sweep(frame, width, height, effects, now_ts):
    """Horizontal gradient line that sweeps top-to-bottom."""
    period = effects.get("sweep_period", 30.0)
    colors = effects.get("sweep_colors", [(34, 0, 68), (0, 34, 51)])
    sweep_y = (now_ts % period) / period * height

    for y in range(height):
        dist = abs(y - sweep_y)
        if dist < 3:
            intensity = 1.0 - (dist / 3.0)
            for x in range(width):
                if frame[y][x] == (0, 0, 0):
                    t = x / max(1, width - 1)
                    frame[y][x] = scale_color(lerp_color(colors[0], colors[1], t), intensity * 0.5)


def _apply_aurora(frame, width, height, effects, now_ts):
    """Slowly shifting aurora bands across the background."""
    speed = effects.get("aurora_speed", 60.0)
    colors = effects.get("aurora_colors", [
        (0, 255, 102), (0, 204, 170), (102, 0, 204), (0, 68, 255), (0, 255, 102)
    ])
    num = len(colors)
    offset = (now_ts / speed) * width

    for y in range(height):
        for x in range(width):
            if frame[y][x] == (0, 0, 0):
                pos = ((x + offset) % width) / width * (num - 1)
                idx = int(pos)
                c = lerp_color(colors[idx], colors[min(idx + 1, num - 1)], pos - idx)
                row_factor = 0.08 + 0.04 * math.sin(y * 0.5 + now_ts * 0.3)
                frame[y][x] = scale_color(c, row_factor)


def _apply_pixel_chase(frame, width, height, effects, now_ts):
    """Alternating color pixels chase around the border."""
    speed = effects.get("chase_speed", 0.15)
    colors = effects.get("chase_colors", [(255, 20, 147), (0, 255, 204)])
    border = _get_border(width, height)

    offset = int(now_ts / speed) % len(border)
    for i, (y, x) in enumerate(border):
        if frame[y][x] == (0, 0, 0):
            idx = (i + offset) % (len(colors) * 3)
            color_idx = idx // 3 % len(colors)
            brightness = 0.15 + 0.25 * ((i + offset) % 6 < 3)
            frame[y][x] = scale_color(colors[color_idx], brightness)


def _apply_shimmer(frame, width, height, effects, now_ts):
    """Gentle shimmer on border pixels like light through leaves."""
    colors = effects.get("shimmer_colors", [(0, 26, 5)])
    speed = effects.get("shimmer_speed", 0.04)
    density = effects.get("shimmer_density", 0.3)

    for y, x in _get_border(width, height):
        if frame[y][x] == (0, 0, 0):
            # Use sin waves at different frequencies per pixel for organic feel
            val = math.sin(now_ts * speed * 10 + x * 1.7 + y * 2.3)
            if val > (1.0 - density * 2):
                bright = 0.3 + 0.7 * (val + 1) / 2
                base = colors[int(abs(val * 100)) % len(colors)]
                frame[y][x] = scale_color(base, bright)
            else:
                frame[y][x] = colors[0]


def _apply_lava(frame, width, height, effects, now_ts):
    """Slow-moving warm color blobs in the background."""
    speed = effects.get("lava_speed", 0.02)
    colors = effects.get("lava_colors", [(34, 0, 0), (51, 17, 0)])

    for y in range(height):
        for x in range(width):
            if frame[y][x] == (0, 0, 0):
                # Two overlapping sine patterns create blob-like shapes
                v1 = math.sin(x * 0.5 + now_ts * speed * 8) * math.cos(y * 0.7 + now_ts * speed * 6)
                v2 = math.sin((x + y) * 0.3 + now_ts * speed * 10)
                val = (v1 + v2) / 2
                if val > 0.1:
                    intensity = (val - 0.1) / 0.9
                    idx = int(abs(val * 50)) % len(colors)
                    frame[y][x] = scale_color(colors[idx], intensity * 0.5)


def _apply_sparkle(frame, width, height, effects, tick_count):
    """Random sparkle pixels that flash briefly like ice catching light."""
    color = effects.get("sparkle_color", (180, 220, 255))
    chance = effects.get("sparkle_chance", 0.03)

    for y, x in _get_border(width, height):
        if frame[y][x] == (0, 0, 0):
            if random.random() < chance:
                bright = random.uniform(0.4, 1.0)
                frame[y][x] = scale_color(color, bright)


def _apply_rainbow_border(frame, width, height, effects, now_ts):
    """Rainbow cycling on border pixels."""
    speed = effects.get("rainbow_speed", 6.0)
    border = _get_border(width, height)
    total = len(border)

    for i, (y, x) in enumerate(border):
        if frame[y][x] == (0, 0, 0):
            hue = ((now_ts * 360 / speed) + (i / total) * 360) % 360
            frame[y][x] = scale_color(hsv_to_rgb(hue, 1.0, 1.0), 0.25)
