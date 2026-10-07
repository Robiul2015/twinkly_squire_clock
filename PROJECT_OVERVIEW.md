# Twinkly Squire Clock - Project Overview

## Architecture

A Docker-containerized Python app that renders a real-time HH:MM clock on Twinkly Squares LED panels (24x16 pixels, 384 LEDs across 6 panels in a 3x2 grid). Runs at 10 FPS.

```
config.yaml → Clock Main Loop (10 FPS)
                ├→ Render Frame (HH:MM + seconds dot)
                ├→ Apply Transitions (minute zoom / hour burst)
                ├→ Apply Theme Effects (background animations)
                └→ Convert to Bytes → Permutation Map → UDP v3 → Twinkly Device
```

---

## Files

| File | Purpose |
|---|---|
| `src/clock.py` | Main loop, config loading, brightness scheduling, lifecycle management |
| `src/renderer.py` | Frame generation, text drawing, transitions, seconds blink indicator |
| `src/themes.py` | 13 color themes, color utilities (hex_to_rgb, lerp, scale, hsv_to_rgb) |
| `src/effects.py` | 11+ background animation effects applied to black pixels |
| `src/fonts.py` | 4 pixel font definitions (3x5, 5x7, 5x7r, 5x7b) |
| `src/transport.py` | Twinkly device communication (REST API + UDP), LED coordinate mapping |
| `config/config.yaml` | Runtime config (hot-reloaded every 60s for theme changes) |
| `Dockerfile` | Python 3.12-slim container, copies src/ into image |
| `docker-compose.yml` | Host networking, auto-restart, mounts config/ as volume |

---

## Rendering Pipeline

1. **Get time** - `datetime.now()`, 12-hour format
2. **Create frame** - Empty 24x16 black grid
3. **Get colors** - From theme (static, adaptive, or rainbow)
4. **Draw HH:MM** - Using selected font (5x7 default), colon blinks 500ms on/off
5. **Draw seconds dot** - 2-pixel indicator below time, random high-contrast color per second, blinks 500ms on/off
6. **Apply transitions** - Hour burst (1.2s expanding ring + flash) or minute zoom (0.6s scale pulse)
7. **Apply effects** - Theme background animations on black pixels only
8. **Convert to bytes** - Flat RGB array in raster order
9. **Permutation map** - Remap raster positions to LED indices (handles Y-inversion + serpentine wiring)
10. **UDP push** - Send to Twinkly via xled library (port 7777, protocol v3)

---

## Themes (14 total)

| Theme | Hours | Minutes | Effect |
|---|---|---|---|
| `ocean_drift` | Cyan | Dark blue | Border wave (blue shades) |
| `ember_glow` | Orange | Red | Ember flicker on border |
| `neon_synthwave` | Magenta | Cyan | Gradient sweep (purple bg) |
| `minimal_white` | White | Light gray | Breathing brightness pulse |
| `aurora_borealis` | White | White | Shifting aurora color bands |
| `time_of_day` | Adaptive | Adaptive | Colors change by hour (dawn→day→dusk→night) |
| `sunset_boulevard` | Pale gold | Coral | Border wave (golden) |
| `cyberpunk_tokyo` | Hot pink | Lime | Pixel chase (purple bg) |
| `forest_canopy` | Green | Teal | Shimmer (light through leaves) |
| `lava_lamp` | Red | Orange | Slow morphing lava blobs |
| `ice_crystal` | Pale white | Light blue | Random sparkle flashes |
| `rainbow_shift` | Cycling | Cycling (120° offset) | Rainbow border + digit hue rotation |
| `green_lava` | Green | Teal | Lava blobs + shimmer combined |
| `matrix_terminal` | Phosphor green | Dim green | Falling code rain + scanlines |

---

## Effects

### Border Effects (edges only)
- **border_wave** - Slow color wave cycling along border pixels
- **ember_flicker** - Random flickering embers, brighter at bottom
- **pixel_chase** - Alternating colors racing around border
- **sparkle** - Random bright flashes (3% chance per pixel per frame)
- **shimmer** - Overlapping sine waves, organic feel
- **rainbow_border** - Continuous rainbow cycling

### Fullscreen Effects (all black pixels)
- **gradient_sweep** - Horizontal gradient line sweeps top to bottom (30s period)
- **aurora** - Slow shifting color bands (60s cycle)
- **lava** - Two overlapping sine patterns create morphing blobs
- **matrix_rain** - Falling code-rain streaks, one per column, bright head with fading trail
- **scanlines** - Faint horizontal bands on every Nth row, CRT-style

### Color Effects (modify digit colors)
- **rainbow** - Digits cycle through HSV spectrum (6s rotation)
- **adaptive** - Colors and brightness change by time of day
- **breathing** - Sinusoidal brightness pulse (4s period)

---

## Fonts

| Font | Size | Style |
|---|---|---|
| `3x5` | 3×5 | Tom Thumb, minimal (used for small text) |
| `5x7` | 5×7 | Classic dot matrix, sharp corners (default) |
| `5x7r` | 5×7 | Rounded corners, softer appearance |
| `5x7b` | 5×7 | Bold, thick 2px strokes, maximum visibility |

---

## Transition Effects

### Minute Change - Zoom Pulse (0.6s)
- **Phase 1** (0-240ms): Scale 1.0x→1.4x, brightness boost 1.0x→1.5x
- **Phase 2** (240-600ms): Scale 1.4x→1.0x, brightness fades back to normal
- Digits expand outward from center then shrink back

### Hour Change - Burst Flash (1.2s)
- **Flash** (0-80ms): Full-screen white wash, fades out
- **Ring** (80-1200ms): Bright ring expands outward from center
- **Digit boost** (0-300ms): All digits brightened temporarily
- Hour transition takes priority if both trigger simultaneously

---

## Seconds Blink Indicator
- **Position**: 2-pixel dot centered below HH:MM (row y+8)
- **Blink**: Visible first 500ms of each second, off for remaining 500ms
- **Color**: Random from 12 high-contrast colors, seeded by current second (deterministic per second)
- **Palette**: Red, Green, Blue, Yellow, Magenta, Cyan, Orange, Lime, Hot Pink, Spring Green, Purple, White

---

## Brightness & Night Mode

### Night Mode
- **Night window**: `night_start` (default 22:00) until sunrise
- **Sunrise**: Calculated daily using Astral library for configured lat/long
- **Night brightness**: 5% (configurable)

### Daytime Schedule
- After sunrise, brightness follows `brightness_schedule` entries
- Finds highest hour ≤ current hour, applies that brightness
- Default: 95% from 8 AM, 60% from 8 PM

### Update Frequency
- Brightness rechecked every frame, but only updated when hour changes

---

## Transport & Twinkly Protocol

### REST API (Port 80)
- Authentication, device info, LED layout, mode setting, brightness

### UDP v3 (Port 7777)
- Real-time frame data (~1.2 KB per frame at 10 FPS)

### LED Mapping
- Y-axis is inverted (Twinkly Y=0 at bottom, renderer Y=0 at top)
- Serpentine wiring within panels (alternating row directions)
- Permutation map built from device-reported LED coordinates
- Auth token refreshed every 3600s; reconnects after 5 consecutive failures

---

## Configuration Reference

| Setting | Default | Description |
|---|---|---|
| `twinkly_ip` | `192.168.1.100` | Device IP address |
| `theme` | `ocean_drift` | Active theme (hot-reloaded) |
| `brightness` | 80 | Default brightness 0-100 |
| `fps` | 10 | Frames per second |
| `font` | `5x7` | Font: 5x7, 5x7r, 5x7b |
| `night_brightness` | 20 | Night brightness % |
| `night_start` | 22 | Night mode start (24h) |
| `location.*` | Sydney | Lat/long/timezone for sunrise calc |
| `brightness_schedule` | {8:80, 20:50} | Hour→brightness mapping |
| `skip_mapping` | false | Skip LED coordinate mapping |

---

## Docker Deployment

```bash
# Build and run
docker compose up -d --build

# View logs
docker logs -f twinkly-clock

# Restart after code changes
git pull && docker compose build && docker compose up -d

# Config changes only (no rebuild needed - mounted volume)
# Edit config/config.yaml, wait up to 60s for hot-reload
```
