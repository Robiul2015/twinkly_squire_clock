"""
Background and decorative effects for the Twinkly clock display.
Each effect modifies the frame buffer in place, only touching black pixels.
"""

import math
import random

from themes import lerp_color, scale_color, hex_to_rgb


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


def _apply_border_wave(frame, width, height, effects, now_ts):
    """Slow color wave along border pixels."""
    wave_colors = effects.get("wave_colors", [(0, 17, 51)])
    speed = effects.get("wave_speed", 0.05)
    num_colors = len(wave_colors)

    border = []
    for x in range(width):
        border.append((0, x))
        border.append((height - 1, x))
    for y in range(1, height - 1):
        border.append((y, 0))
        border.append((y, width - 1))

    for i, (y, x) in enumerate(border):
        if frame[y][x] == (0, 0, 0):
            phase = (now_ts * speed + i * 0.15) % num_colors
            idx = int(phase)
            frac = phase - idx
            frame[y][x] = lerp_color(
                wave_colors[idx % num_colors],
                wave_colors[(idx + 1) % num_colors],
                frac,
            )


def _apply_ember_flicker(frame, width, height, effects, tick_count):
    """Random flickering ember effect on border pixels."""
    ember_colors = effects.get("ember_colors", [(17, 2, 0)])

    border = []
    for x in range(width):
        border.append((0, x))
        border.append((height - 1, x))
    for y in range(1, height - 1):
        border.append((y, 0))
        border.append((y, width - 1))

    for y, x in border:
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
                frac = pos - idx
                c = lerp_color(colors[idx], colors[min(idx + 1, num - 1)], frac)
                row_factor = 0.08 + 0.04 * math.sin(y * 0.5 + now_ts * 0.3)
                frame[y][x] = scale_color(c, row_factor)
