# RaspberryPiZeroW-Photobooth-Display
Standalone Wi-Fi-controlled LED message display for a photobooth using MAX7219

Phase 1 — Hardware Proof (SPI init, MAX7219 connection, basic text, basic scrolling — no web, no config, no systemd per the roadmap)
User Test

install raspbian OS lite
SSH into the pi

On the Pi:
  sudo raspi-config nonint do_spi 0   # enable SPI if not already
  sudo reboot
  pip install -r requirements.txt
  python3 hardware_test.py

Watch for: each matrix showing its number 1–4 in order, "TEST" and "1234" displaying statically, then the scrolling message. If orientation looks wrong (mirrored/upside-down/reversed order), tell me what you see and I'll adjust BLOCK_ORIENTATION/ROTATE at the top of the file.

Phase 2 — Clean Display Module (create display.py, move this logic into it as a proper module)
