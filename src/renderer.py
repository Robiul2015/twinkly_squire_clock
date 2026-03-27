"""
Frame renderer for the Twinkly clock display.
Generates a 24x16 RGB frame (3 panels wide x 2 tall) from the current time.
Includes transition effects on minute and hour changes.
"""

import math
import random
import time
from datetime import datetime

from fonts import get_glyph, measure_text
from themes import scale_color, lerp_color
from effects import apply_effects, get_adaptive_colors, get_rainbow_colors

# High-contrast colors for the seconds blink indicator
_HIGH_CONTRAST_COLORS = [
    (255, 0, 0),       # Red
    (0, 255, 0),       # Green
    (0, 100, 255),     # Blue
    (255, 255, 0),     # Yellow
    (255, 0, 255),     # Magenta
    (0, 255, 255),     # Cyan
    (255, 128, 0),     # Orange
    (128, 255, 0),     # Lime
    (255, 0, 128),     # Hot pink
    (0, 255, 128),     # Spring green
    (128, 0, 255),     # Purple
    (255, 255, 255),   # White
]

WIDTH = 24
HEIGHT = 16

# Transition durations (seconds)
MINUTE_TRANSITION = 0.6    # Zoom-pulse on minute change
HOUR_TRANSITION = 1.2      # Burst flash on hour change


class TransitionState:
    """Tracks minute/hour changes and transition progress."""

    def __init__(self):
        self.last_minute = -1
        self.last_hour = -1
        self.minute_change_ts = 0.0  # When the last minute change happened
        self.hour_change_ts = 0.0

    def update(self, now, now_ts):
        """Check for minute/hour changes and record timestamps."""
        if self.last_minute == -1:
            # First frame — initialize without triggering transition
            self.last_minute = now.minute
            self.last_hour = now.hour
            return

        if now.minute != self.last_minute:
            self.minute_change_ts = now_ts
            self.last_minute = now.minute

        if now.hour != self.last_hour:
            self.hour_change_ts = now_ts
            self.last_hour = now.hour

    def get_minute_progress(self, now_ts):
        """Return 0.0-1.0 progress through minute transition, or -1 if inactive."""
        elapsed = now_ts - self.minute_change_ts
        if elapsed < MINUTE_TRANSITION:
            return elapsed / MINUTE_TRANSITION
        return -1

    def get_hour_progress(self, now_ts):
        """Return 0.0-1.0 progress through hour transition, or -1 if inactive."""
        elapsed = now_ts - self.hour_change_ts
        if elapsed < HOUR_TRANSITION:
            return elapsed / HOUR_TRANSITION
        return -1


# Global transition state (persists across frames)
_transition = TransitionState()


def create_frame():
    """Create an empty frame buffer (black)."""
    return [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]


def draw_char(frame, glyph, x, y, color):
    """Draw a single character glyph onto the frame at position (x, y)."""
    for row_idx, row in enumerate(glyph):
        py = y + row_idx
        if py < 0 or py >= HEIGHT:
            continue
        for col_idx, val in enumerate(row):
            px = x + col_idx
            if px < 0 or px >= WIDTH:
                continue
            if val:
                frame[py][px] = color


def draw_char_scaled(frame, glyph, cx, cy, color, scale):
    """Draw a glyph scaled around center point (cx, cy).

    scale=1.0 is normal, >1.0 is zoomed in, <1.0 is zoomed out.
    """
    glyph_h = len(glyph)
    glyph_w = len(glyph[0]) if glyph else 0

    for py in range(HEIGHT):
        for px in range(WIDTH):
            # Map display pixel back to glyph space
            gx = (px - cx) / scale + glyph_w / 2
            gy = (py - cy) / scale + glyph_h / 2
            gi = int(gy)
            gj = int(gx)
            if 0 <= gi < glyph_h and 0 <= gj < glyph_w:
                if glyph[gi][gj]:
                    frame[py][px] = color


def draw_text(frame, text, x, y, color, font_name="3x5", spacing=1):
    """Draw a string of text onto the frame."""
    cursor_x = x
    for ch in text:
        glyph = get_glyph(ch, font_name)
        draw_char(frame, glyph, cursor_x, y, color)
        cursor_x += len(glyph[0]) + spacing


def draw_text_centered(frame, text, y, color, font_name="3x5", spacing=1):
    """Draw text horizontally centered on the display."""
    w, _ = measure_text(text, font_name, spacing)
    x = (WIDTH - w) // 2
    draw_text(frame, text, x, y, color, font_name, spacing)


def _apply_minute_zoom(frame, progress):
    """Zoom-pulse effect: digits briefly scale up then back to normal.

    progress: 0.0 (start) to 1.0 (end)
    Phase 1 (0.0-0.4): scale from 1.0 to 1.4 (zoom in)
    Phase 2 (0.4-1.0): scale from 1.4 back to 1.0 (zoom out)
    Also adds a brief brightness boost.
    """
    if progress < 0.4:
        t = progress / 0.4
        scale = 1.0 + 0.4 * t
        bright = 1.0 + 0.5 * t
    else:
        t = (progress - 0.4) / 0.6
        scale = 1.4 - 0.4 * t
        bright = 1.5 - 0.5 * t

    cx = WIDTH / 2
    cy = HEIGHT / 2

    # Scale existing lit pixels outward from center
    original = [row[:] for row in frame]
    for y in range(HEIGHT):
        for x in range(WIDTH):
            frame[y][x] = (0, 0, 0)

    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Map back to source
            sx = int((x - cx) / scale + cx + 0.5)
            sy = int((y - cy) / scale + cy + 0.5)
            if 0 <= sy < HEIGHT and 0 <= sx < WIDTH:
                src = original[sy][sx]
                if src != (0, 0, 0):
                    frame[y][x] = scale_color(src, min(bright, 2.0))


def _apply_hour_burst(frame, progress):
    """Burst flash: bright ring expands outward from center then fades.

    progress: 0.0 (start) to 1.0 (end)
    """
    cx = WIDTH / 2
    cy = HEIGHT / 2
    max_radius = max(WIDTH, HEIGHT)

    # Ring expands outward
    ring_radius = progress * max_radius
    ring_width = 2.5

    # Flash brightness fades out
    flash_bright = 1.0 - progress * 0.8

    # Brief full-screen white flash at the very start
    if progress < 0.08:
        flash_alpha = 1.0 - (progress / 0.08)
        for y in range(HEIGHT):
            for x in range(WIDTH):
                r, g, b = frame[y][x]
                w = int(255 * flash_alpha * 0.6)
                frame[y][x] = (min(255, r + w), min(255, g + w), min(255, b + w))
        return

    # Expanding ring
    for y in range(HEIGHT):
        for x in range(WIDTH):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            ring_dist = abs(dist - ring_radius)
            if ring_dist < ring_width:
                intensity = (1.0 - ring_dist / ring_width) * flash_bright
                if intensity > 0:
                    r, g, b = frame[y][x]
                    boost = int(200 * intensity)
                    frame[y][x] = (min(255, r + boost), min(255, g + boost), min(255, b + boost))

    # Also boost all existing digit pixels briefly
    if progress < 0.3:
        digit_boost = 1.0 + (1.0 - progress / 0.3) * 0.8
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if frame[y][x] != (0, 0, 0):
                    frame[y][x] = scale_color(frame[y][x], min(digit_boost, 2.0))


def render_clock_frame(theme, now=None, tick_count=0, font_name="5x7"):
    """Render a complete clock frame with transition effects."""
    if now is None:
        now = datetime.now()
    now_ts = time.time()

    # Track minute/hour changes
    _transition.update(now, now_ts)

    colors = theme["colors"]
    if theme.get("effects", {}).get("adaptive"):
        colors = get_adaptive_colors(theme, now.hour)

    # 12-hour format
    hour_12 = now.hour % 12 or 12
    hh_str = f"{hour_12:2d}"
    mm_str = f"{now.minute:02d}"
    colon_visible = (now.microsecond < 500000)

    frame = create_frame()

    # Colors
    rainbow = get_rainbow_colors(theme, now_ts)
    hours_color = rainbow["hours"] if rainbow else colors["hours"]
    minutes_color = rainbow["minutes"] if rainbow else colors["minutes"]

    if rainbow:
        colon_color = rainbow["colon"]
    else:
        colon_color = colors["colon"]
        r, g, b = colon_color
        if r * 0.299 + g * 0.587 + b * 0.114 < 100:
            colon_color = (255, 255, 255)

    # Draw HH:MM centered
    row_y = 5
    two_digit = (hh_str[0] != " ")

    if two_digit:
        x = 0
        draw_char(frame, get_glyph(hh_str[0], font_name), x, row_y, hours_color)
        x += 6
    else:
        x = 3

    draw_char(frame, get_glyph(hh_str[1], font_name), x, row_y, hours_color)
    x += 5

    colon_x = x
    if colon_visible:
        draw_char(frame, get_glyph(":", font_name), x, row_y, colon_color)
    x += 2

    draw_char(frame, get_glyph(mm_str[0], font_name), x, row_y, minutes_color)
    x += 6
    draw_char(frame, get_glyph(mm_str[1], font_name), x, row_y, minutes_color)

    # Seconds blink indicator — random high-contrast color each second
    # Positioned below the colon, at the bottom of the display
    blink_on = (now.microsecond < 500000)
    if blink_on:
        rng = random.Random(now.second + now.minute * 60 + now.hour * 3600)
        sec_color = rng.choice(_HIGH_CONTRAST_COLORS)
        frame[row_y + 8][colon_x] = sec_color

    # Apply transition effects
    hour_progress = _transition.get_hour_progress(now_ts)
    minute_progress = _transition.get_minute_progress(now_ts)

    if hour_progress >= 0:
        # Hour burst takes priority
        _apply_hour_burst(frame, hour_progress)
    elif minute_progress >= 0:
        _apply_minute_zoom(frame, minute_progress)

    # Apply theme background effects
    apply_effects(frame, WIDTH, HEIGHT, theme, now_ts, tick_count)

    return frame


def frame_to_bytes(frame):
    """Convert a 2D frame buffer to flat RGB bytes in raster order."""
    data = bytearray()
    for row in frame:
        for r, g, b in row:
            data.append(r)
            data.append(g)
            data.append(b)
    return bytes(data)
