# AI Coding Instructions

You are working on the Raspberry Pi Zero W MAX7219 Photobooth Display project.

## 1. Source of Truth

Read:

```text
Raspberry Pi Zero W MAX7219 Photobooth Display.md
```

before making architectural changes.

`Raspberry Pi Zero W MAX7219 Photobooth Display.md` defines what the application should ultimately do.

Read:

```text
Development Roadmap.md
```

to determine the current development phase.

---

# 2. Work Only on the Current Phase

Do not implement future phases unless required by the current phase.

If the current phase is Phase 4, do not start building:

- Web UI
- Authentication
- systemd
- Networking UI

unless explicitly requested.

---

# 3. Inspect Before Changing

Before modifying code:

1. Inspect the existing project.
2. Identify which files are involved.
3. Understand the existing behavior.
4. Make a short plan.
5. Then modify the code.

Do not assume the project has the structure described in the specification if the actual files differ.

---

# 4. Keep the Architecture Simple

Preferred Python structure:

```text
app.py
display.py
config.py
web.py
```

Do not create new Python modules unless there is a clear reason.

Do not create:

```text
display/
renderer/
effects/
controllers/
managers/
services/
helpers/
utils/
```

just for organizational purposes.

A small amount of duplication is preferable to unnecessary abstraction.

---

# 5. File Responsibilities

### app.py

Application coordination and shared state.

### display.py

Everything related to MAX7219 and LED display behavior.

### config.py

JSON settings, presets, validation, persistence.

### web.py

Flask, web pages, browser sessions, PIN, web controls.

Keep these responsibilities clear.

---

# 6. Do Not Rewrite Working Code

If existing functionality works:

**preserve it.**

When adding a feature:

- Make the smallest reasonable change.
- Do not rewrite unrelated code.
- Do not rename files/classes/functions without a reason.
- Do not change architecture merely for style.

If a major architectural change appears necessary, explain why before doing it.

---

# 7. Avoid AI Loops

Never repeatedly modify code without testing.

Use this cycle:

```text
Understand
   ↓
Plan
   ↓
Change
   ↓
Run
   ↓
Test
   ↓
Inspect result
   ↓
Fix
```

If the same problem remains after several attempts, stop and explain the problem instead of repeatedly changing unrelated code.

---

# 8. Keep the Pi Simple

Do not add unnecessary:

- databases
- cloud services
- APIs
- frameworks
- dependencies
- background services
- network services

Use Raspberry Pi OS facilities where appropriate.

Wi-Fi is managed by NetworkManager.

Hostname discovery is handled by Avahi.

Application recovery is handled by systemd.

---

# 9. Display Rules

MAX7219 wiring:

```text
DIN → GPIO10 / MOSI
CLK → GPIO11 / SCLK
CS  → GPIO8 / CE0
```

The display uses a separate 5V supply with common ground.

Do not assume the physical matrix orientation.

Verify it during hardware testing.

Do not show the IP address on the LED display during normal startup.

---

# 10. Non-Blocking Operation

Do not use long blocking delays for normal operation.

Avoid:

```python
time.sleep(10)
```

for display state transitions.

Use timestamps, timers, or state tracking.

The display and web interface must be able to operate concurrently.

---

# 11. Configuration Safety

Configuration files are:

```text
data/settings.json
data/presets.json
```

Always:

- Validate input.
- Use defaults when configuration is invalid.
- Preserve configuration versioning.
- Write files safely.
- Avoid losing valid configuration because of one bad value.

Never allow malformed user input to crash the application.

---

# 12. Testing

After meaningful changes:

- Run Python syntax checks.
- Start the application.
- Test the changed feature.
- Test the most closely related existing feature.

For hardware changes, provide a simple physical test.

Do not claim something works unless it was actually tested or clearly state that it could not be tested.

---

# 13. Do Not Invent Requirements

If the specification does not define something important, do not silently invent a complicated solution.

Prefer:

1. Simple implementation.
2. Existing project conventions.
3. Ask the user when the decision significantly affects architecture.

---

# 14. Completion Report

After each phase, briefly report:

### Implemented

What was completed.

### Files Changed

List every created/modified file.

### Dependencies

List new dependencies.

### Setup Changes

Mention:

- SPI
- systemd
- OS configuration
- permissions
- network configuration

when applicable.

### Test Result

State exactly what was tested.

### User Test

Give simple instructions for the user.
Provide linux command if needed.

### Known Limitations

State what remains unfinished.

### Next Phase

State the next roadmap phase.

Then STOP.

Do not begin the next phase automatically.

---

# 15. Most Important Rule

**Do not optimize the architecture while implementing a feature.**

The goal is a reliable, understandable Raspberry Pi appliance.

Prefer:

```text
simple + working
```

over:

```text
clever + abstract
```

If a solution requires many new files or layers, reconsider whether the design is becoming unnecessarily complicated.