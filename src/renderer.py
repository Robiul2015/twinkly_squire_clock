"""
Frame renderer for the Twinkly clock display.
Generates a 24x16 RGB frame (3 panels wide x 2 tall) from the current time.
"""

import time
from datetime import datetime

from fonts import get_glyph, measure_text
from effects import apply_effects, get_adaptive_colors

WIDTH = 24
HEIGHT = 16


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


def render_clock_frame(theme, now=None, tick_count=0):
    """Render a complete clock frame — HH:MM centered on display."""
    if now is None:
        now = datetime.now()
    now_ts = time.time()

    colors = theme["colors"]
    if theme.get("effects", {}).get("adaptive"):
        colors = get_adaptive_colors(theme, now.hour)

    # 12-hour format
    hour_12 = now.hour % 12 or 12
    hh_str = f"{hour_12:2d}"
    mm_str = f"{now.minute:02d}"
    colon_visible = (now.microsecond < 500000)

    frame = create_frame()

    hours_color = colors["hours"]
    minutes_color = colors["minutes"]
    colon_color = colors["colon"]

    # HH:MM in 5x7 font, centered on 24x16 display
    # Vertically: (16 - 7) / 2 -> row 5
    # Horizontally: 2-digit=24px (x=0), 1-digit=18px (x=3)
    row_y = 5
    two_digit = (hh_str[0] != " ")

    if two_digit:
        x = 0
        draw_char(frame, get_glyph(hh_str[0], "5x7"), x, row_y, hours_color)
        x += 6
    else:
        x = 3

    draw_char(frame, get_glyph(hh_str[1], "5x7"), x, row_y, hours_color)
    x += 5

    if colon_visible:
        draw_char(frame, get_glyph(":", "5x7"), x, row_y, colon_color)
    x += 2

    draw_char(frame, get_glyph(mm_str[0], "5x7"), x, row_y, minutes_color)
    x += 6
    draw_char(frame, get_glyph(mm_str[1], "5x7"), x, row_y, minutes_color)

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
