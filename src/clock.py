"""
Main loop for the Twinkly Squares wall clock.
Connects to the device and continuously renders/pushes clock frames.
"""

import logging
import os
import signal
import sys
import time
from datetime import datetime

import yaml

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
    "brightness_schedule": {6: 60, 8: 80, 20: 50, 23: 15},
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


def apply_brightness_schedule(transport, config, current_hour):
    """Set brightness based on time-of-day schedule."""
    schedule = config.get("brightness_schedule")
    if not schedule:
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
        apply_brightness_schedule(self.transport, config, datetime.now().hour)

        tick_count = 0
        frame_interval = 1.0 / config["fps"]
        last_brightness_hour = -1

        while self.running:
            loop_start = time.monotonic()
            try:
                now = datetime.now()

                if now.hour != last_brightness_hour:
                    apply_brightness_schedule(self.transport, config, now.hour)
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

                frame = render_clock_frame(theme, now=now, tick_count=tick_count)
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
