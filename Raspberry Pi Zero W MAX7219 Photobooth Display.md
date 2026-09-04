# Raspberry Pi Zero W MAX7219 Photobooth Display

**Project Status:** Active Development  
**Hardware:** Raspberry Pi Zero W + MAX7219 4-in-1 32×8 LED matrix  
**OS:** Raspberry Pi OS Lite  
**Language:** Python 3  
**Interface:** Local web interface  
**Purpose:** Standalone Wi-Fi-controlled LED message display for a photobooth

---

# 1. Project Purpose

Build a small, reliable Raspberry Pi Zero W appliance that controls a MAX7219 4-in-1 32×8 LED matrix.

The device is an **independent photobooth display**.

It is not responsible for:

- Camera control
- Photo capture
- The photobooth application
- Gallery functions
- Photo processing
- Photobooth countdown synchronization

The display must continue operating independently even when the photobooth computer, browser, router, or Wi-Fi connection is unavailable.

The web interface exists only as a convenient local management interface.

---

# 2. Core Requirements

The finished device must:

- Drive all four 8×8 matrices through the MAX7219.
- Display text.
- Scroll text.
- Display static text.
- Support adjustable scrolling speed.
- Support adjustable message duration.
- Support adjustable brightness.
- Support left-to-right and right-to-left display direction.
- Support multiple display effects.
- Support Single, Playlist, and Random modes.
- Store settings persistently.
- Store editable message presets persistently.
- Allow custom text.
- Provide a local web interface.
- Protect normal controls with a PIN.
- Provide Display ON/OFF control.
- Provide system/status information.
- Automatically recover from application crashes.
- Continue displaying saved content without Wi-Fi.
- Require no cloud service or internet connection for normal operation.

---

# 3. Hardware

## 3.1 Raspberry Pi

Target hardware:

- Raspberry Pi Zero W
- Raspberry Pi OS Lite
- Python 3
- Hardware SPI

The Pi is dedicated to this application.

## 3.2 MAX7219

Display:

- MAX7219 driver
- Four 8×8 matrices
- Total resolution: 32×8

Physical arrangement:

```text
LEFT                                      RIGHT
┌────────┬────────┬────────┬────────┐
│  8×8   │  8×8   │  8×8   │  8×8   │
└────────┴────────┴────────┴────────┘
```

Text should normally read naturally from left to right.

The actual physical orientation of the installed module must be verified during hardware testing rather than assumed.

---

# 4. Wiring

Use Raspberry Pi hardware SPI.

| MAX7219 | Raspberry Pi Zero W |
|---|---|
| DIN | GPIO10 / SPI0 MOSI |
| CLK | GPIO11 / SPI0 SCLK |
| CS/LOAD | GPIO8 / SPI0 CE0 |
| VCC | Separate regulated 5V supply |
| GND | Common ground |

The MAX7219 display should use a suitable separate 5V supply.

Do not power the matrix from the Pi 5V rail unless the actual current requirement has been verified.

The Pi and MAX7219 must share a common ground.

---

# 5. Network

Wi-Fi is configured during Raspberry Pi OS installation.

The application must **not** implement its own Wi-Fi provisioning.

Use:

- NetworkManager for Wi-Fi
- Avahi/mDNS for local hostname discovery

Preferred address:

```text
http://photobooth-display.local
```

Do not implement:

- WiFiManager
- Custom Wi-Fi setup
- Cloud networking
- Internet dependency

The application must start and display normally even if Wi-Fi is unavailable.

When Wi-Fi becomes available again, the web interface should become accessible without restarting the application.

---

# 6. Software Structure

Keep the project intentionally small.

```text
/opt/photobooth-display/
│
├── app.py
├── display.py
├── config.py
├── web.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── app.js
│
├── data/
│   ├── settings.json
│   └── presets.json
│
├── requirements.txt
│
├── PROJECT.md
├── ROADMAP.md
└── AI_INSTRUCTIONS.md
```

## 6.1 `app.py`

`app.py` is the application coordinator.

It is responsible for:

- Application startup
- Shared application state
- Loading configuration
- Initializing the display
- Starting the display operation
- Starting the web server
- Coordinating shutdown/restart behavior

Do not put all display, web, and configuration implementation into this file.

Think of `app.py` as the **brain**, not the entire application.

---

## 6.2 `display.py`

`display.py` contains everything related to the MAX7219 and LED display.

It owns:

- MAX7219 initialization
- SPI communication
- Matrix orientation
- Text rendering
- Font handling
- Scrolling
- Static display
- Effects
- Brightness
- Direction
- Display ON/OFF
- Startup messages
- Message playback
- Single mode
- Playlist mode
- Random mode
- Animation timing

Other modules must not directly manipulate MAX7219 hardware.

A single `Display`/`DisplayManager` class is acceptable if useful.

Do not create separate modules merely for individual effects or rendering unless the project later becomes large enough to justify them.

---

## 6.3 `config.py`

`config.py` owns persistent configuration.

It handles:

- Loading settings
- Saving settings
- Default settings
- Validation
- Configuration versioning
- Loading presets
- Saving presets
- Preset validation
- Safe JSON writes
- Recovery from malformed configuration

It may contain one or more small classes if useful, but avoid unnecessary abstraction.

It must not contain:

- HTML
- Flask routes
- MAX7219 code

---

## 6.4 `web.py`

`web.py` contains the local Flask web interface.

It handles:

- Flask application
- Login/PIN
- Browser session
- Main control page
- Settings controls
- Preset controls
- Custom text
- Display ON/OFF
- Preview
- Save
- System/status page
- Restart
- Reboot
- Factory reset

The web layer communicates with application/display/configuration objects.

It must **not** directly manipulate MAX7219 hardware.

---

# 7. Application Architecture

Use this simple relationship:

```text
                     app.py
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
        display.py            config.py
             ▲                   ▲
             │                   │
             └──────── web.py ───┘
```

More precisely:

```text
Web browser
     │
     ▼
   web.py
     │
     ▼
   app.py
     │
 ┌───┴────┐
 ▼        ▼
display  config
```

Rules:

1. `web.py` does not access MAX7219 hardware directly.
2. `display.py` does not know about HTTP or HTML.
3. `config.py` does not know about HTML.
4. Do not create unnecessary layers between these files.
5. Prefer simple function/class interfaces.
6. Do not introduce additional Python modules unless there is a demonstrated need.

---

# 8. Display Behavior

## 8.1 Startup

Startup should follow:

```text
POWER ON
   ↓
STARTING...
   ↓
DISPLAY INIT
   ↓
PHOTOBOOTH
DISPLAY
   ↓
NORMAL DISPLAY
```

Startup messages are temporary.

Do not display the IP address during normal startup.

Do not wait for Wi-Fi before entering normal display operation.

---

# 9. Display Modes

## Single

Display one selected message continuously.

## Playlist

Display selected messages in a fixed sequence.

Example:

```text
SAY CHEESE!
      ↓
SMILE!
      ↓
HAVE FUN!
      ↓
MAKE A MEMORY!
```

## Random

Select enabled messages randomly.

Avoid immediately repeating the same message when practical.

---

# 10. Message Timing

Scrolling speed and message duration are separate controls.

### Scroll speed

Controls how quickly text moves.

### Message duration

Controls how long a message remains the active message before another message is selected.

Example:

```text
Scroll speed = FAST
Message duration = 10 seconds
```

means the message moves quickly but remains the active message for 10 seconds.

For static messages, duration still determines when the next message is selected.

Avoid long blocking `sleep()` calls for normal operation.

Use timing/state logic.

---

# 11. Effects

The display engine should support effects without requiring major architectural changes.

Initial effects may include:

- Scroll
- Static

Do not implement every possible effect immediately.

Start with the simplest useful effects and add others later.

---

# 12. Direction

Support:

- Left to right
- Right to left

The default direction must be selected after testing the actual physical matrix orientation.

Do not assume the electrical orientation matches the physical orientation.

---

# 13. Brightness

Use the MAX7219 hardware intensity control.

Brightness must be adjustable from the web interface.

Do not use software PWM unless there is a specific technical reason.

---

# 14. Display ON/OFF

The web interface must provide a prominent Display ON/OFF control.

When OFF:

- LEDs are turned off.
- Raspberry Pi continues running.
- Wi-Fi continues running.
- Web server continues running.
- Settings remain intact.

OFF is a temporary runtime state.

Do not save the OFF state to persistent configuration.

After reboot, normal startup occurs.

---

# 15. Presets

Presets are reusable messages.

A preset contains at minimum:

```text
id
name
text
category
enabled
```

Example:

```json
{
  "id": "say_cheese",
  "name": "Say Cheese",
  "text": "SAY CHEESE!",
  "category": "Photobooth",
  "enabled": true
}
```

Categories/occasions must not be a fixed hard-coded list.

Examples include:

- Photobooth
- Birthday
- Wedding
- Holiday
- Durga Puja
- Anniversary
- Company Event
- Halloween
- Christmas
- Custom Event

The user should be able to create and use their own categories.

The interface should eventually support:

- Add preset
- Edit preset
- Delete preset
- Select preset
- Enable/disable preset
- Assign category

---

# 16. Initial Presets

The application may ship with common messages such as:

```text
SAY CHEESE!
SMILE!
PHOTO TIME!
STRIKE A POSE!
MAKE A MEMORY!
HAVE FUN!
LOOK HERE!
GET READY!
ONE MORE!
BEST PHOTO EVER!
```

Optional humorous messages:

```text
DON'T BLINK!
ACT NATURAL!
NO PRESSURE!
BLAME THE CAMERA.
THAT WAS AWKWARD.
WE NEED A RETAKE!
YOU LOOK FAMOUS!
PROOF YOU WERE HERE!
FUN DETECTED!
```

These are starter data only and must be editable.

---

# 17. Custom Text

Provide a web interface text field for custom messages.

Custom text must use the same display controls as presets.

Validate input.

Unsupported characters must be handled safely.

Do not allow invalid input to crash the application.

Initial font requirements:

- Simple/default font
- No custom font system
- No Bengali-specific font
- No advanced Unicode requirements

---

# 18. Playlist

Users can select multiple messages.

Example:

```text
☑ SAY CHEESE!
☑ SMILE!
☐ HAPPY BIRTHDAY!
☑ HAVE FUN!
☑ MAKE A MEMORY!
```

Playlist mode uses deterministic order.

Random mode selects enabled messages randomly.

---

# 19. Persistent Storage

Use local JSON files:

```text
data/settings.json
data/presets.json
```

Example settings:

```json
{
  "config_version": 1,
  "display_mode": "playlist",
  "scroll_speed": 5,
  "message_duration": 10,
  "brightness": 8,
  "effect": "scroll",
  "direction": "right_to_left",
  "playlist": [
    "say_cheese",
    "smile",
    "have_fun"
  ]
}
```

Configuration must survive:

- Application restart
- Raspberry Pi reboot

Use safe file-writing practices to reduce corruption risk during power loss.

Configuration files must contain a version number.

If configuration is malformed:

```text
CONFIG ERROR
DEFAULTS LOADED
```

The application should continue using safe defaults where possible.

---

# 20. Web Interface

The web interface is local only.

Requirements:

- Mobile friendly
- Touch friendly
- Works on iPhone
- Works on iPad
- Works on desktop browsers
- No external CDN
- No cloud dependency
- No internet dependency

Preferred address:

```text
http://photobooth-display.local
```

The display must continue working if the browser is closed.

---

# 21. Main Web Page

The main page should provide:

```text
PHOTOBOOTH DISPLAY

Current Message
[ SAY CHEESE! ]

Preset
[ SAY CHEESE! ▼ ]

Custom Text
[________________]

Mode
○ Single
● Playlist
○ Random

Scroll Speed
SLOW ─────●──── FAST

Message Duration
1 sec ─────●──── 60 sec

Brightness
LOW ─────────●── HIGH

Effect
[ Scroll ▼ ]

Direction
[ Right to Left ▼ ]

[ PREVIEW ]     [ SAVE ]

       [ DISPLAY OFF ]
```

The exact visual design may evolve.

Functionality is more important than visual complexity.

---

# 22. System Page

Provide a system/status page.

Information may include:

```text
Application
Version
Uptime

Wi-Fi
Status
SSID
Signal

Network
Hostname

Display
MAX7219 status
Brightness
Mode

System
CPU
Memory
Temperature
Storage
```

The IP address may appear on the system page.

Never show:

- Wi-Fi password
- PIN

The system page should provide:

- Display test
- Application restart
- Raspberry Pi reboot
- Factory reset
- Version
- Useful recent errors/status

Factory reset requires confirmation.

---

# 23. Authentication

Normal display controls require a PIN.

Expected flow:

```text
Open control page
       ↓
Enter PIN
       ↓
Correct PIN
       ↓
Access controls
```

Use a temporary browser session so the PIN does not need to be entered for every operation.

The PIN must be changeable from the authenticated interface.

Authentication is intended for a local network.

It is not intended to protect an internet-facing server.

---

# 24. Logging

Use normal Linux/systemd logging.

Useful events include:

```text
Application started
MAX7219 initialized
Settings loaded
Presets loaded
Web server started
Wi-Fi connected
Wi-Fi disconnected
Configuration saved
Display mode changed
Authentication failure
Display error
```

Avoid excessive logging.

Do not allow logs to unnecessarily fill the filesystem.

---

# 25. Reliability

The application must be designed as a small appliance.

Priority order:

1. Reliability
2. Simplicity
3. Maintainability
4. Easy troubleshooting
5. User experience
6. Persistent configuration
7. Recovery

The display must continue operating when:

- Wi-Fi is disconnected
- Router is offline
- Browser is closed
- Web interface is temporarily unavailable
- Photobooth computer is offline

---

# 26. Non-Blocking Operation

Normal display operation must not depend on long blocking delays.

Avoid:

```python
time.sleep(10)
```

for normal animation/state transitions.

Use timers and state tracking for:

- Scrolling
- Message rotation
- Effects
- Startup messages
- Wi-Fi monitoring

The display engine and web interface must operate concurrently.

---

# 27. Error Handling

Errors should be understandable.

Possible display messages:

```text
DISPLAY ERROR
CONFIG ERROR
SAVE FAILED
INVALID TEXT
```

Errors should not create permanent loops.

After a recoverable error, return to normal operation.

A bad settings file must not permanently prevent the application from starting.

---

# 28. systemd

The application will eventually run as:

```text
display-controller.service
```

systemd should:

- Start the application automatically
- Restart it after crashes
- Provide normal Linux logging

The service should not depend on Wi-Fi being available before starting.

---

# 29. Security

This is a local-network appliance.

Use reasonable security without over-engineering.

Required:

- PIN-protected controls
- Input validation
- No Wi-Fi password exposure
- No unnecessary secrets in source code
- No cloud services
- No external APIs

Do not build an unnecessary security framework.

---

# 30. Out of Scope

Do not implement unless explicitly requested:

- Camera control
- Photo capture
- Photobooth application
- Gallery software
- Photobooth countdown integration
- MQTT
- Cloud services
- External database
- External APIs
- Internet-dependent resources
- Remote internet access
- Custom Wi-Fi provisioning
- WiFiManager
- OTA firmware update system
- Bengali-specific fonts
- Custom font framework
- Complex home automation

---

# 31. Future Features

Possible future additions:

- Ambient-light sensor
- Automatic brightness
- Additional effects
- Additional fonts
- Preset import/export
- Configuration backup/restore
- Physical buttons
- Rotary encoder
- Additional matrix sizes
- Optional photobooth integration

These should only be considered after the core application is stable.

---

# 32. Definition of Done

The project is complete when the Pi can be installed on the photobooth and left running as an independent appliance.

Typical operation:

```text
POWER ON
   ↓
STARTING...
   ↓
DISPLAY INIT
   ↓
SAY CHEESE!
   ↓
SMILE!
   ↓
MAKE A MEMORY!
   ↓
...
```

The user can access:

```text
http://photobooth-display.local
```

and manage:

- Presets
- Custom text
- Playlist
- Random mode
- Scroll speed
- Message duration
- Brightness
- Direction
- Effects
- Display ON/OFF
- System diagnostics
- Application restart
- Raspberry Pi reboot
- Settings

If Wi-Fi disappears, the display continues operating.

If the application crashes, systemd restarts it.

The final product should feel like a **small dedicated appliance**, not a general-purpose Raspberry Pi computer.