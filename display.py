"""
display.py

Owns all MAX7219 / LED matrix hardware: initialization, text rendering,
scrolling (both directions), and basic display state (on/off, contrast,
scroll speed, message duration, direction).

Phase 3 - Display Controls.

Hardware values below are CONFIRMED on real hardware during Phase 1
testing (not guesses):
  BLOCK_ORIENTATION = -90
  ROTATE = 2
  Matrix order left-to-right = 1, 2, 3, 4 (correct with the above)

Wiring (hardware SPI):
  DIN -> GPIO10 (SPI0 MOSI)
  CLK -> GPIO11 (SPI0 SCLK)
  CS  -> GPIO8  (SPI0 CE0)

NOTE ON SCROLLING:
  luma.core.legacy.show_message() (used in Phases 1-2) only scrolls one
  direction. Supporting configurable direction (this phase) meant
  writing a small custom marquee: render the full message onto a wide
  offscreen image, then slide a device-width window across it, moving
  the window forward for one direction and backward for the other.
"""

import time

from PIL import Image, ImageDraw

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text as legacy_text
from luma.core.legacy.font import proportional, CP437_FONT
from luma.led_matrix.device import max7219


CASCADED = 4
BLOCK_ORIENTATION = -90
ROTATE = 2

DEFAULT_CONTRAST = 64
DEFAULT_SCROLL_SPEED = 0.05      # seconds between scroll frames
DEFAULT_MESSAGE_DURATION = 3.0   # seconds a static message is held
DEFAULT_DIRECTION = "left"       # "left" (text moves right-to-left) or "right"

MIN_SCROLL_SPEED = 0.005
MIN_MESSAGE_DURATION = 0.1

FONT = proportional(CP437_FONT)


class Display:
    """Owns the MAX7219 hardware and its current display settings."""

    def __init__(
        self,
        contrast=DEFAULT_CONTRAST,
        scroll_speed=DEFAULT_SCROLL_SPEED,
        message_duration=DEFAULT_MESSAGE_DURATION,
        direction=DEFAULT_DIRECTION,
    ):
        self._device = self._init_device()
        self.contrast_level = contrast
        self._device.contrast(self.contrast_level)
        self.scroll_speed = scroll_speed
        self.message_duration = message_duration
        self.direction = direction if direction in ("left", "right") else DEFAULT_DIRECTION
        self.is_on = True

    def _init_device(self):
        serial = spi(port=0, device=0, gpio=noop())
        return max7219(
            serial,
            cascaded=CASCADED,
            block_orientation=BLOCK_ORIENTATION,
            rotate=ROTATE,
        )

    # -- Rendering --------------------------------------------------------

    def show_text(self, message):
        """Display static text (no scrolling)."""
        with canvas(self._device) as draw:
            legacy_text(draw, (0, 0), message, fill="white", font=FONT)

    def scroll_text(self, message, speed=None, direction=None):
        """
        Scroll text across the display. Blocks until the scroll finishes.

        speed/direction optionally override the instance defaults for
        this call only; instance settings (self.scroll_speed,
        self.direction) are left unchanged.
        """
        speed = self.scroll_speed if speed is None else speed
        direction = self.direction if direction is None else direction
        if direction not in ("left", "right"):
            direction = self.direction

        image = self._render_scroll_image(message)
        device_width = self._device.width
        image_width = image.width

        if image_width <= device_width:
            # Message fits on the display already - just show it, no need
            # to scroll (also avoids an empty/invalid frame range below).
            self.show_text(message)
            return

        max_offset = image_width - device_width
        if direction == "left":
            offsets = range(0, max_offset + 1)
        else:  # "right"
            offsets = range(max_offset, -1, -1)

        for offset in offsets:
            frame = image.crop((offset, 0, offset + device_width, image.height))
            self._device.display(frame)
            time.sleep(speed)

    def _render_scroll_image(self, message):
        """
        Render `message` onto a wide offscreen image: one device-width of
        blank space before and after the text, so the message scrolls
        fully on and fully off the display.
        """
        device_width = self._device.width
        device_height = self._device.height
        text_width = sum(len(FONT[ord(ch)]) for ch in message)

        total_width = device_width + text_width + device_width
        image = Image.new(self._device.mode, (total_width, device_height))
        draw = ImageDraw.Draw(image)
        legacy_text(draw, (device_width, 0), message, fill="white", font=FONT)
        return image

    # -- Settings -----------------------------------------------------------

    def set_contrast(self, value):
        """Set brightness/contrast. Value is clamped to the valid 0-255 range."""
        try:
            value = int(value)
        except (TypeError, ValueError):
            return
        value = max(0, min(255, value))
        self.contrast_level = value
        self._device.contrast(value)

    def set_scroll_speed(self, seconds):
        """Set delay (in seconds) between scroll frames. Lower = faster."""
        try:
            seconds = float(seconds)
        except (TypeError, ValueError):
            return
        self.scroll_speed = max(MIN_SCROLL_SPEED, seconds)

    def set_message_duration(self, seconds):
        """Set how long (in seconds) a static message should be held by callers."""
        try:
            seconds = float(seconds)
        except (TypeError, ValueError):
            return
        self.message_duration = max(MIN_MESSAGE_DURATION, seconds)

    def set_direction(self, direction):
        """Set scroll direction: 'left' or 'right'. Invalid values are ignored."""
        if direction in ("left", "right"):
            self.direction = direction

    # -- State ----------------------------------------------------------

    def clear(self):
        """Blank the display output."""
        self._device.clear()
        self._device.show()

    def off(self):
        """Turn the display off (clears output, tracks state)."""
        self.clear()
        self.is_on = False

    def on(self):
        """Mark the display as on. Caller should follow with show_text/scroll_text."""
        self.is_on = True
