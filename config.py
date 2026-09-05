"""
config.py

JSON settings and presets: load, save, defaults, validation, versioning,
safe (atomic) writes, and recovery from corrupted/missing files.

Phase 5 - Persistent Configuration.

Files:
  data/settings.json  - current display settings + mode + messages
  data/presets.json   - named presets (a small built-in starter set;
                         editing presets via the web UI comes later)

Design principle (AI_Coding_Instructions.md section 11 - Configuration
Safety): a single bad or missing field must never lose the rest of an
otherwise-valid config file. Validation happens field-by-field: any
invalid field falls back to its own default; every other valid field
is preserved untouched.
"""

import json
import os


CONFIG_VERSION = 1

DATA_DIR = "data"
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")
PRESETS_PATH = os.path.join(DATA_DIR, "presets.json")

DEFAULT_MESSAGES = ["SAY CHEESE!", "SMILE!", "HAVE FUN!", "PHOTOBOOTH"]

DEFAULT_SETTINGS = {
    "version": CONFIG_VERSION,
    "contrast": 64,
    "scroll_speed": 0.05,
    "message_duration": 3.0,
    "direction": "left",
    "mode": "single",
    "messages": list(DEFAULT_MESSAGES),
    "single_message": DEFAULT_MESSAGES[0],
}

DEFAULT_PRESETS = {
    "version": CONFIG_VERSION,
    "presets": {
        "Default": {
            "contrast": 64,
            "scroll_speed": 0.05,
            "message_duration": 3.0,
            "direction": "left",
        },
        "Bright & Fast": {
            "contrast": 200,
            "scroll_speed": 0.02,
            "message_duration": 2.0,
            "direction": "left",
        },
        "Dim & Slow": {
            "contrast": 20,
            "scroll_speed": 0.09,
            "message_duration": 4.0,
            "direction": "left",
        },
    },
}

MIN_SCROLL_SPEED = 0.005
MIN_MESSAGE_DURATION = 0.1
VALID_DIRECTIONS = ("left", "right")
VALID_MODES = ("single", "playlist", "random")
PRESET_FIELDS = ("contrast", "scroll_speed", "message_duration", "direction")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _atomic_write_json(path, data):
    """Write JSON safely: write to a temp file, then atomically replace
    the real file. A crash mid-write leaves the original file untouched
    rather than a half-written, corrupt one."""
    _ensure_data_dir()
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_settings(raw):
    """Validate a settings dict field-by-field, returning a fully valid
    settings dict. Missing/invalid fields fall back to defaults
    individually; valid fields are preserved."""
    if not isinstance(raw, dict):
        return dict(DEFAULT_SETTINGS)

    result = dict(DEFAULT_SETTINGS)

    version = raw.get("version")
    if isinstance(version, int):
        result["version"] = version

    contrast = raw.get("contrast")
    if _is_number(contrast):
        result["contrast"] = max(0, min(255, int(contrast)))

    scroll_speed = raw.get("scroll_speed")
    if _is_number(scroll_speed):
        result["scroll_speed"] = max(MIN_SCROLL_SPEED, float(scroll_speed))

    message_duration = raw.get("message_duration")
    if _is_number(message_duration):
        result["message_duration"] = max(MIN_MESSAGE_DURATION, float(message_duration))

    direction = raw.get("direction")
    if direction in VALID_DIRECTIONS:
        result["direction"] = direction

    mode = raw.get("mode")
    if mode in VALID_MODES:
        result["mode"] = mode

    messages = raw.get("messages")
    if isinstance(messages, list):
        cleaned = [m for m in messages if isinstance(m, str) and m.strip()]
        if cleaned:
            result["messages"] = cleaned

    single_message = raw.get("single_message")
    if isinstance(single_message, str) and single_message.strip():
        result["single_message"] = single_message
    elif result["single_message"] not in result["messages"]:
        # Keep cross-field consistency: if single_message wasn't valid and
        # the default doesn't exist in the (possibly custom) messages list,
        # fall back to the first real message instead of a dangling value.
        result["single_message"] = result["messages"][0]

    return result


def load_settings():
    """Load settings from disk. Handles a missing file, unreadable/corrupt
    JSON, and partially-invalid content. Always returns a fully valid
    settings dict, and writes a clean copy back to disk if recovery was
    needed (so the next load is clean too)."""
    if not os.path.exists(SETTINGS_PATH):
        settings = dict(DEFAULT_SETTINGS)
        save_settings(settings)
        return settings

    try:
        with open(SETTINGS_PATH, "r") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[config] WARNING: settings.json unreadable ({e}); using defaults.")
        settings = dict(DEFAULT_SETTINGS)
        save_settings(settings)
        return settings

    validated = _validate_settings(raw)
    if validated != raw:
        save_settings(validated)
    return validated


def save_settings(settings):
    """Validate then safely (atomically) write settings to disk."""
    validated = _validate_settings(settings)
    _atomic_write_json(SETTINGS_PATH, validated)
    return validated


def _validate_presets(raw):
    if not isinstance(raw, dict) or not isinstance(raw.get("presets"), dict):
        return {"version": CONFIG_VERSION, "presets": dict(DEFAULT_PRESETS["presets"])}

    presets = {}
    for name, values in raw["presets"].items():
        if not isinstance(name, str) or not name.strip() or not isinstance(values, dict):
            continue
        merged = _validate_settings({**DEFAULT_SETTINGS, **values})
        presets[name] = {field: merged[field] for field in PRESET_FIELDS}

    if not presets:
        presets = dict(DEFAULT_PRESETS["presets"])

    version = raw.get("version")
    if not isinstance(version, int):
        version = CONFIG_VERSION

    return {"version": version, "presets": presets}


def load_presets():
    """Load presets from disk, with the same recovery behavior as
    load_settings()."""
    if not os.path.exists(PRESETS_PATH):
        presets = dict(DEFAULT_PRESETS)
        save_presets(presets)
        return presets

    try:
        with open(PRESETS_PATH, "r") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[config] WARNING: presets.json unreadable ({e}); using defaults.")
        presets = dict(DEFAULT_PRESETS)
        save_presets(presets)
        return presets

    validated = _validate_presets(raw)
    if validated != raw:
        save_presets(validated)
    return validated


def save_presets(presets):
    """Validate then safely (atomically) write presets to disk."""
    validated = _validate_presets(presets)
    _atomic_write_json(PRESETS_PATH, validated)
    return validated
