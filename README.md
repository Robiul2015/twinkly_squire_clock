# Twinkly Squares Wall Clock

A live wall clock running on Twinkly Squares LED panels, driven by a Python script in Docker.

![Display](https://img.shields.io/badge/display-24x16_RGB-blue) ![Python](https://img.shields.io/badge/python-3.12-green) ![Docker](https://img.shields.io/badge/docker-compose-blue)

## Hardware

- **Twinkly Squares Starter Pack** — 1 master + 5 extension panels
- **Layout:** 3 wide x 2 tall = 24x16 pixels (384 RGB LEDs)
- **Host:** Synology DS720+ NAS (Docker) or any Linux machine

## How It Works

A Python script generates clock frames at 10 FPS and pushes them to the Twinkly device over UDP using the `xled` library. The LED layout coordinates are read from the device API and used to build a pixel permutation map that accounts for the serpentine wiring of each panel.

```
Docker Container (Python)
  └── Render 24x16 frame (HH:MM, 5x7 font, 12h format)
  └── Apply permutation map (raster → LED index)
  └── UDP push to Twinkly (port 7777, protocol v3)
```

## Themes

Switch themes by editing `config/config.yaml` — hot-reloaded every 60 seconds.

| Theme | Description |
|-------|-------------|
| `ocean_drift` | Calm cyan-blue with slow wave border animation |
| `ember_glow` | Warm fireplace with flickering ember border |
| `neon_synthwave` | Retro 80s magenta/cyan with gradient sweep |
| `minimal_white` | Clean white with subtle breathing effect |
| `aurora_borealis` | Shifting green/purple aurora background |
| `time_of_day` | Adaptive — gold morning, white day, blue night, dim red sleep |

## Quick Start

### Prerequisites

- Twinkly Squares connected to WiFi and set up via the Twinkly mobile app
- Docker host on the same local network

### Deploy

1. Clone this repo:
   ```bash
   git clone https://github.com/Robiul2015/twinkly_squire_clock.git
   cd twinkly_squire_clock
   ```

2. Edit `config/config.yaml` with your Twinkly IP address:
   ```yaml
   twinkly_ip: "192.168.1.100"
   theme: "ocean_drift"
   ```

3. Set your timezone in `docker-compose.yml`:
   ```yaml
   environment:
     - TZ=Australia/Sydney
   ```

4. Build and run:
   ```bash
   docker compose build
   docker compose up -d
   ```

5. Check logs:
   ```bash
   docker compose logs -f
   ```

### Synology NAS

1. Install **Container Manager** from Package Center
2. Enable SSH in **Control Panel > Terminal & SNMP**
3. Copy files to `/volume1/docker/twinkly-clock/`
4. SSH in and run `docker compose up -d`

## Configuration

All settings in `config/config.yaml`:

```yaml
twinkly_ip: "192.168.1.100"    # Device IP
theme: "ocean_drift"           # Active theme
brightness: 80                 # Default brightness (0-100)
fps: 10                        # Frames per second

# Auto-dim by time of day
brightness_schedule:
  6: 60      # 6 AM
  8: 80      # 8 AM
  20: 50     # 8 PM
  23: 15     # 11 PM
```

## Project Structure

```
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── config/
│   └── config.yaml
└── src/
    ├── clock.py        # Main loop
    ├── effects.py      # Background animations
    ├── fonts.py        # 3x5 and 5x7 pixel fonts
    ├── renderer.py     # Frame generation
    ├── themes.py       # Color theme definitions
    └── transport.py    # Twinkly connection and LED mapping
```

## Adding a Custom Theme

Edit `src/themes.py` and add a new dict:

```python
MY_THEME = {
    "name": "My Theme",
    "description": "Custom colors",
    "colors": {
        "background": (0, 0, 0),
        "hours": (255, 255, 255),
        "minutes": (200, 200, 200),
        "seconds": (100, 100, 100),
        "colon": (255, 255, 255),
        "ampm": (80, 80, 80),
        "date": (60, 60, 60),
        "border": (0, 0, 0),
    },
    "effects": {},  # Or add border_wave, aurora, etc.
}
```

Register it in the `THEMES` dict and set `theme: "my_theme"` in config.

## Technical Details

- **Protocol:** Twinkly real-time UDP v3 (port 7777) with REST auth (port 80)
- **Auth:** `hw_address=None` bypasses challenge-response validation for newer firmware
- **Y-axis:** Inverted in Twinkly coordinates (Y=0 is physical bottom)
- **Panels:** Serpentine wiring varies per panel; layout API provides exact LED coordinates
- **Reconnection:** Auto-reconnects with exponential backoff on failure
- **Graceful shutdown:** SIGTERM sets device back to movie mode

## Dependencies

- [xled](https://github.com/scrool/xled) — Twinkly control library
- [Pillow](https://pillow.readthedocs.io/) — Image processing
- [PyYAML](https://pyyaml.org/) — Configuration

## License

MIT
