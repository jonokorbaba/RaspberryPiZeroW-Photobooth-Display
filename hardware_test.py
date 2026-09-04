#!/usr/bin/env python3
"""
Phase 1 - Hardware Proof
Raspberry Pi Zero W + MAX7219 4-in-1 (32x8) LED Matrix

This script exists only to prove the hardware works. It is NOT the
final application. Phase 2 will move display logic into display.py.

What this tests, in order:
  1. SPI / MAX7219 initialization
  2. Each of the 4 matrices individually (orientation + wiring check)
  3. Static text across the full 32x8 area
  4. Basic scrolling text

Wiring (hardware SPI, per AI_Coding_Instructions.md / spec):
  DIN -> GPIO10 (SPI0 MOSI)
  CLK -> GPIO11 (SPI0 SCLK)
  CS  -> GPIO8  (SPI0 CE0)
  VCC -> separate regulated 5V supply
  GND -> common ground with the Pi

Before running:
  1. Enable SPI:  sudo raspi-config -> Interface Options -> SPI -> Enable
     (or: sudo raspi-config nonint do_spi 0)
  2. Reboot if SPI was just enabled.
  3. Install dependencies:  pip install -r requirements.txt
  4. Confirm the device exists:  ls /dev/spidev0.0

Run:
  python3 hardware_test.py

NOTE ON ORIENTATION:
  BLOCK_ORIENTATION and ROTATE below are starting guesses, not confirmed
  values. The spec explicitly says physical orientation must be verified
  on real hardware, not assumed. If test 2 (individual matrices) shows
  the numbers upside-down, mirrored, or in the wrong left-to-right
  order, adjust BLOCK_ORIENTATION (try 0, -90, or 90) and/or ROTATE
  (0-3) and rerun.
"""

import sys
import time

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT
from luma.led_matrix.device import max7219


CASCADED = 4              # four 8x8 matrices = 32x8 total
BLOCK_ORIENTATION = -90   # UNCONFIRMED - verify during hardware testing
ROTATE = 0                # UNCONFIRMED - verify during hardware testing
CONTRAST = 64              # 0-255, moderate brightness for bring-up


def init_device():
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(
        serial,
        cascaded=CASCADED,
        block_orientation=BLOCK_ORIENTATION,
        rotate=ROTATE,
    )
    device.contrast(CONTRAST)
    return device


def test_individual_matrices(device):
    """Light up each 8x8 block one at a time with its number (1-4)."""
    print("\n[TEST 2] Individual matrices (left to right = 1,2,3,4)")
    for i in range(CASCADED):
        with canvas(device) as draw:
            x_start = i * 8
            text(draw, (x_start + 2, 0), str(i + 1),
                 fill="white", font=proportional(CP437_FONT))
        print(f"  Matrix {i + 1} of {CASCADED} should now show '{i + 1}'")
        time.sleep(2)
    device.clear()
    device.show()


def test_static_text(device, message="TEST"):
    print(f"\n[TEST 3] Static text: '{message}'")
    with canvas(device) as draw:
        text(draw, (0, 0), message, fill="white", font=proportional(CP437_FONT))
    time.sleep(3)
    device.clear()
    device.show()


def test_scroll_text(device, message="SAY CHEESE! ", delay=0.05):
    print(f"\n[TEST 4] Scrolling text: '{message.strip()}'")
    show_message(
        device,
        message,
        fill="white",
        font=proportional(CP437_FONT),
        scroll_delay=delay,
    )


def main():
    print("Phase 1 - Hardware Proof")
    print("=" * 40)

    print("\n[TEST 1] Initializing MAX7219 over SPI...")
    try:
        device = init_device()
    except Exception as e:
        print(f"[ERROR] Could not initialize MAX7219: {e}")
        print("Check: SPI enabled, wiring (DIN=GPIO10, CLK=GPIO11, CS=GPIO8),")
        print("common ground, and separate 5V supply for the display.")
        sys.exit(1)
    print("[OK] MAX7219 initialized.")

    try:
        test_individual_matrices(device)
        test_static_text(device, "TEST")
        test_static_text(device, "1234")
        test_scroll_text(device, "SAY CHEESE! HAVE FUN! ")
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    finally:
        device.clear()
        device.show()
        print("\n[DONE] Display cleared. Phase 1 test sequence complete.")


if __name__ == "__main__":
    main()
