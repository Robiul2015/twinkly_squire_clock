"""
Transport layer for Twinkly Squares over the local network.
Handles connection, authentication, LED layout mapping, and UDP frame pushing.
"""

import logging
import time
from io import BytesIO

import xled

logger = logging.getLogger(__name__)

AUTH_REFRESH_INTERVAL = 3600  # Re-authenticate every hour
MAX_FAILURES = 5
FAILURE_BACKOFF = 30  # Seconds to wait after repeated failures


class TwinklyTransport:
    """Manages the connection to a Twinkly device and pushes frames."""

    def __init__(self, ip_address, skip_mapping=False):
        self.ip_address = ip_address
        self.skip_mapping = skip_mapping
        self.control = None
        self.led_count = 0
        self.permutation_map = None
        self._last_auth_time = 0
        self._consecutive_failures = 0

    def connect(self):
        """Authenticate, read device info and layout, set real-time mode."""
        try:
            logger.info("Connecting to Twinkly at %s", self.ip_address)
            # hw_address=None skips challenge-response validation
            # which fails on newer Twinkly firmware
            self.control = xled.ControlInterface(self.ip_address)

            info = self.control.get_device_info()
            info_data = info.data if hasattr(info, "data") else info
            if isinstance(info_data, dict):
                self.led_count = info_data.get("number_of_led", 384)
                product = info_data.get("product_code", "unknown")
                fw = info_data.get("fw_version", "unknown")
            else:
                self.led_count = 384
                product = fw = "unknown"

            logger.info("Connected: %s, fw %s, %d LEDs", product, fw, self.led_count)

            if self.skip_mapping:
                logger.info("skip_mapping=True, using identity mapping")
                self.permutation_map = list(range(self.led_count))
            else:
                self._read_layout()

            self.control.set_mode("rt")
            self._last_auth_time = time.time()
            self._consecutive_failures = 0
            logger.info("Real-time mode active")
            return True

        except Exception as e:
            logger.error("Failed to connect: %s", e)
            self.control = None
            return False

    def _read_layout(self):
        """Read LED layout coordinates and build the pixel permutation map.

        Twinkly returns (x, y) for each LED index. We sort unique X/Y values
        to determine column/row indices, with Y-axis inverted (Y=0 is physical
        bottom, Y=1 is physical top — confirmed by diagnostic).
        """
        try:
            layout_resp = self.control.get_led_layout()
            layout_data = layout_resp.data if hasattr(layout_resp, "data") else layout_resp
            coords = layout_data.get("coordinates", []) if isinstance(layout_data, dict) else []

            if not coords:
                logger.warning("No layout coordinates. Using identity mapping.")
                self.permutation_map = list(range(self.led_count))
                return

            from renderer import WIDTH, HEIGHT

            xs_unique = sorted(set(round(c["x"], 6) for c in coords))
            ys_unique = sorted(set(round(c["y"], 6) for c in coords))

            logger.info("Layout: %d LEDs, %dx%d grid", len(coords), len(xs_unique), len(ys_unique))

            x_to_col = {x: i for i, x in enumerate(xs_unique)}
            # Y-axis inverted: smallest Y = bottom row, largest Y = top row
            y_to_row = {y: (len(ys_unique) - 1 - i) for i, y in enumerate(ys_unique)}

            raster_to_led = list(range(self.led_count))
            mapped = 0
            for led_idx, coord in enumerate(coords):
                col = x_to_col.get(round(coord["x"], 6))
                row = y_to_row.get(round(coord["y"], 6))
                if col is not None and row is not None:
                    raster_pos = row * WIDTH + col
                    if 0 <= raster_pos < len(raster_to_led):
                        raster_to_led[raster_pos] = led_idx
                        mapped += 1

            logger.info("Mapped %d of %d pixels", mapped, WIDTH * HEIGHT)
            self.permutation_map = raster_to_led

        except Exception as e:
            logger.warning("Could not read layout: %s. Using identity.", e)
            self.permutation_map = list(range(self.led_count))

    def push_frame(self, raster_bytes):
        """Push a single RGB frame to the device via UDP."""
        if self.control is None:
            return False

        if time.time() - self._last_auth_time > AUTH_REFRESH_INTERVAL:
            logger.info("Refreshing auth token")
            try:
                self.control.set_mode("rt")
                self._last_auth_time = time.time()
            except Exception:
                if not self.connect():
                    return False

        try:
            if self.permutation_map:
                permuted = bytearray(self.led_count * 3)
                for raster_pos in range(min(len(self.permutation_map), self.led_count)):
                    led_idx = self.permutation_map[raster_pos]
                    src = raster_pos * 3
                    dst = led_idx * 3
                    if src + 3 <= len(raster_bytes) and dst + 3 <= len(permuted):
                        permuted[dst:dst + 3] = raster_bytes[src:src + 3]
                frame_data = bytes(permuted)
            else:
                frame_data = raster_bytes

            self.control.set_rt_frame_socket(
                BytesIO(frame_data), version=3, leds_number=self.led_count
            )
            self._consecutive_failures = 0
            return True

        except Exception as e:
            self._consecutive_failures += 1
            logger.warning("Frame push failed (%d/%d): %s",
                           self._consecutive_failures, MAX_FAILURES, e)
            if self._consecutive_failures >= MAX_FAILURES:
                logger.error("Too many failures, reconnecting in %ds", FAILURE_BACKOFF)
                time.sleep(FAILURE_BACKOFF)
                self.connect()
            return False

    def set_brightness(self, value):
        """Set device brightness (0-100)."""
        if self.control is None:
            return
        try:
            self.control.set_brightness(value)
            logger.info("Brightness set to %d%%", value)
        except Exception as e:
            logger.warning("Failed to set brightness: %s", e)

    def disconnect(self):
        """Set device back to movie mode and disconnect."""
        if self.control is None:
            return
        try:
            self.control.set_mode("movie")
            logger.info("Device set back to movie mode")
        except Exception as e:
            logger.warning("Disconnect cleanup failed: %s", e)
        self.control = None
