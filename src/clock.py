"""
Main loop for the Twinkly Squares wall clock.
Connects to the device and continuously renders/pushes clock frames.
"""

import logging
import os
import signal
import sys
import time
from datetime import datetime, date

import yaml
from astral import LocationInfo
from astral.sun import sun

from renderer import render_clock_frame, frame_to_bytes
from themes import get_theme, list_themes
from transport import TwinklyTransport

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("clock")

DEFAULT_CONFIG = {
    "twinkly_ip": "192.168.1.100",
    "theme": "ocean_drift",
    "brightness": 80,
    "fps": 10,
    "night_brightness": 20,
    "night_start": 22,           # 10 PM
    "location": {
        "name": "Sydney",
        "region": "Australia",
        "latitude": 51.4934,
        "longitude": 0.0,
        "timezone": "Australia/Sydney",
    },
    "brightness_schedule": {8: 80, 20: 50},
}


def load_config():
    """Load config from YAML, falling back to defaults."""
    for path in [
        "/app/config/config.yaml",
        os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml"),
    ]:
        try:
            with open(path, "r") as f:
                user_config = yaml.safe_load(f) or {}
                logger.info("Config loaded from %s", path)
                return {**DEFAULT_CONFIG, **user_config}
        except FileNotFoundError:
            continue
    logger.info("No config file found, using defaults")
    return dict(DEFAULT_CONFIG)


def get_sunrise_hour(config):
    """Calculate today's sunrise hour for the configured location."""
    try:
        loc_cfg = config.get("location", {})
        city = LocationInfo(
            loc_cfg.get("name", "Sydney"),
            loc_cfg.get("region", "Australia"),
            loc_cfg.get("timezone", "Australia/Sydney"),
            loc_cfg.get("latitude", 51.4934),
            loc_cfg.get("longitude", 0.0),
        )
        s = sun(city.observer, date=date.today(), tzinfo=city.timezone)
        sunrise_hour = s["sunrise"].hour
        logger.info("Today's sunrise: %s (hour %d)", s["sunrise"].strftime("%H:%M"), sunrise_hour)
        return sunrise_hour
    except Exception as e:
        logger.warning("Sunrise calculation failed: %s. Defaulting to 6 AM.", e)
        return 6


def apply_brightness_schedule(transport, config, now):
    """Set brightness based on time-of-day with sunrise-aware night dimming.

    10 PM to sunrise: night_brightness (default 20%)
    After sunrise: follows brightness_schedule
    """
    current_hour = now.hour
    night_start = config.get("night_start", 22)
    night_brightness = config.get("night_brightness", 20)
    sunrise_hour = get_sunrise_hour(config)

    # Check if we're in the night window (10 PM -> sunrise)
    is_night = current_hour >= night_start or current_hour < sunrise_hour

    if is_night:
        transport.set_brightness(night_brightness)
        logger.info("Night mode: brightness %d%% (until sunrise ~%d:00)",
                     night_brightness, sunrise_hour)
        return

    # Daytime: use the schedule
    schedule = config.get("brightness_schedule")
    if not schedule:
        transport.set_brightness(config.get("brightness", 80))
        return

    brightness = config.get("brightness", 80)
    for hour_str, val in sorted(schedule.items(), key=lambda x: int(x[0])):
        if int(hour_str) <= current_hour:
            brightness = val
    transport.set_brightness(brightness)


class ClockRunner:
    """Runs the clock display loop with graceful shutdown."""

    def __init__(self):
        self.running = True
        self.transport = None

    def handle_signal(self, signum, _frame):
        logger.info("Received signal %d, shutting down...", signum)
        self.running = False

    def run(self):
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)

        config = load_config()
        logger.info("Theme: %s | Target: %s | FPS: %d",
                     config["theme"], config["twinkly_ip"], config["fps"])
        logger.info("Available themes: %s", [t[0] for t in list_themes()])

        try:
            theme = get_theme(config["theme"])
        except ValueError as e:
            logger.error(str(e))
            sys.exit(1)

        self.transport = TwinklyTransport(
            config["twinkly_ip"],
            skip_mapping=config.get("skip_mapping", False),
        )

        retry_delay = 5
        while self.running and not self.transport.connect():
            logger.warning("Retrying in %ds...", retry_delay)
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)

        if not self.running:
            return

        logger.info("Clock running!")
        apply_brightness_schedule(self.transport, config, datetime.now())

        tick_count = 0
        frame_interval = 1.0 / config["fps"]
        last_brightness_hour = -1

        while self.running:
            loop_start = time.monotonic()
            try:
                now = datetime.now()

                if now.hour != last_brightness_hour:
                    apply_brightness_schedule(self.transport, config, now)
                    last_brightness_hour = now.hour

                # Hot-reload theme from config every 60 seconds
                if tick_count > 0 and tick_count % (config["fps"] * 60) == 0:
                    new_config = load_config()
                    if new_config["theme"] != config["theme"]:
                        try:
                            theme = get_theme(new_config["theme"])
                            config = new_config
                            logger.info("Theme switched to: %s", config["theme"])
                        except ValueError as e:
                            logger.warning("Invalid theme: %s", e)

                font = config.get("font", "5x7")
                frame = render_clock_frame(theme, now=now, tick_count=tick_count, font_name=font)
                self.transport.push_frame(frame_to_bytes(frame))
                tick_count += 1

            except Exception as e:
                logger.error("Render error: %s", e, exc_info=True)

            elapsed = time.monotonic() - loop_start
            sleep_time = frame_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

        logger.info("Shutting down...")
        if self.transport:
            self.transport.disconnect()
        logger.info("Goodbye!")


if __name__ == "__main__":
    ClockRunner().run()
