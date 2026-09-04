# Development Roadmap

This document controls implementation order.

**Do not skip ahead.**

Each phase must be completed and tested before moving to the next phase.

---

# Phase 1 — Hardware Proof

Implement only:

- Raspberry Pi environment
- Hardware SPI
- MAX7219 connection
- Basic initialization
- Simple text
- Basic scrolling

Wiring:

```text
DIN = GPIO10
CLK = GPIO11
CS  = GPIO8
```

Verify:

- All four matrices work.
- Text is readable.
- Physical orientation is correct.
- Scrolling works.
- Display power is stable.

Do NOT implement in this phase:

- Web
- PIN
- Presets
- JSON configuration
- Advanced effects
- systemd

---

# Phase 2 — Clean Display Module

Create:

```text
display.py
```

Move display-related functionality into this module.

Implement:

- MAX7219 initialization
- Text rendering
- Scrolling
- Basic display state

Goal:

`display.py` owns the hardware.

Do not add web functionality.

---

# Phase 3 — Display Controls

Add:

- Brightness
- Scroll speed
- Message duration
- Direction

Test each independently.

Do not add the web interface yet.

---

# Phase 4 — Display Modes

Add:

- Single mode
- Playlist mode
- Random mode

Use simple internal application state.

Avoid unnecessary classes/modules.

Test:

- Single message playback
- Multiple messages playback
- Playlist sequence order
- Random selection (avoid immediate repeat where practical)


---


# Phase 5 — Persistent Configuration

Create:

```text
config.py
data/settings.json
data/presets.json
```

Implement:

- Load settings
- Save settings
- Defaults
- Validation
- Version number
- Safe writes
- Configuration recovery
- Persistent storage

Test:

1. Change settings.
2. Restart application.
3. Confirm settings remain.
4. Corrupt settings intentionally.
5. Confirm safe defaults load.


---

# Phase 6 — Basic Web Interface

Create:

```text
web.py
templates/
static/
```

Implement:

- Main page
- Preset selection
- Custom text
- Display mode
- Scroll speed
- Message duration
- Brightness
- Direction
- Effect
- Preview
- Save
- Display ON/OFF

The display must continue operating when the browser closes.

---

# Phase 7 — Networking

Configure/verify:

- NetworkManager
- Avahi
- `photobooth-display.local`

The application must not manage Wi-Fi credentials.

Test from:

- iPhone
- iPad
- Desktop

Also test:

1. Disconnect Wi-Fi.
2. Confirm display continues.
3. Restore Wi-Fi.
4. Confirm web interface returns.

---

# Phase 8 — Authentication

Implement:

- PIN login
- Browser session
- Logout
- PIN change
- Failed login handling

Do not redesign the web interface.

---

# Phase 9 — System Page

Add:

- Application version
- Uptime
- Wi-Fi status
- Hostname
- IP
- MAX7219 status
- Brightness
- CPU
- Memory
- Temperature
- Storage

Add:

- Display test
- Application restart
- Raspberry Pi reboot
- Factory reset

Factory reset must require confirmation.

---

# Phase 10 — systemd Daemonization

Create:

```text
display-controller.service
```

Configure:

- Automatic startup
- Automatic restart after crash
- Normal Linux logging (journalctl)

Test:

1. Start service.
2. Reboot Pi.
3. Confirm application starts.
4. Force application failure.
5. Confirm systemd restarts it.

---

# Phase 11 — Reliability and Polish

Perform:

- Power-loss testing
- Long-duration testing
- Configuration corruption testing
- Wi-Fi loss testing
- Router-off testing
- Repeated web requests
- Repeated setting changes
- Display ON/OFF testing
- Touch-screen/mobile testing

Fix reliability problems before adding features.

---

# Development Rule

After each phase:

1. Stop.
2. Test.
3. Report.
4. Wait for confirmation.

Do not automatically continue to the next phase.