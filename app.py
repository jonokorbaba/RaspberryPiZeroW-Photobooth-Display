#!/usr/bin/env python3
"""
app.py

Application entry point. Coordinates the application and holds shared
application state.

Phase 5 - Persistent Configuration. Settings (brightness, scroll speed,
message duration, direction, mode, messages) now load from
data/settings.json via config.py instead of being hardcoded. Change
the file (or a value in it), restart the app, and the change persists.
Corrupt the file and the app recovers to safe defaults instead of
crashing - see config.py for the recovery logic.

Run:
  python3 app.py
"""

import sys

import config
from display import Display


def new_state(mode="single", messages=None, single_message=None):
    """Build a fresh application state dict for a given mode."""
    messages = messages if messages else list(config.DEFAULT_MESSAGES)
    return {
        "mode": mode,
        "messages": messages,
        "single_message": single_message or messages[0],
        "current_index": 0,
        "last_random_index": None,
    }


def get_next_message(state):
    """
    Return the next message to display, given the current mode.

    single:   always the same configured message.
    playlist: cycles through messages in order, wrapping around.
    random:   picks a random message, avoiding an immediate repeat
              where more than one message is available.
    """
    mode = state["mode"]
    messages = state["messages"]

    if mode == "single":
        return state["single_message"]

    if mode == "playlist":
        idx = state["current_index"]
        msg = messages[idx]
        state["current_index"] = (idx + 1) % len(messages)
        return msg

    if mode == "random":
        if len(messages) == 1:
            return messages[0]  # can't avoid repeat with only one message
        import random
        idx = random.randrange(len(messages))
        while idx == state.get("last_random_index"):
            idx = random.randrange(len(messages))
        state["last_random_index"] = idx
        return messages[idx]

    raise ValueError(f"Unknown mode: {mode}")


def test_single_mode(display):
    print("\n[TEST] Single mode")
    state = new_state(mode="single", messages=config.DEFAULT_MESSAGES, single_message=config.DEFAULT_MESSAGES[0])
    for i in range(3):
        msg = get_next_message(state)
        print(f"  Playback {i + 1}: '{msg}'")
        display.scroll_text(msg)


def test_playlist_mode(display):
    print("\n[TEST] Playlist mode")
    state = new_state(mode="playlist", messages=config.DEFAULT_MESSAGES)
    shown = []
    for i in range(len(config.DEFAULT_MESSAGES) * 2):
        msg = get_next_message(state)
        shown.append(msg)
        print(f"  Playback {i + 1}: '{msg}'")
        display.scroll_text(msg)
    expected = config.DEFAULT_MESSAGES + config.DEFAULT_MESSAGES
    if shown != expected:
        print(f"  [WARNING] Playlist order did not match expected sequence: {shown}")
    else:
        print("  Playlist order verified correct (matches source list, wraps correctly)")


def test_random_mode(display):
    print("\n[TEST] Random mode")
    state = new_state(mode="random", messages=config.DEFAULT_MESSAGES)
    shown = []
    for i in range(6):
        msg = get_next_message(state)
        shown.append(msg)
        print(f"  Playback {i + 1}: '{msg}'")
        display.scroll_text(msg)
    repeats = [a for a, b in zip(shown, shown[1:]) if a == b]
    if repeats:
        print(f"  [WARNING] Immediate repeat detected: {repeats}")
    else:
        print("  No immediate repeats across", len(shown), "picks")


def main():
    print("Phase 5 - Persistent Configuration Test")
    print("=" * 40)

    settings = config.load_settings()
    print("\n[OK] Settings loaded from data/settings.json:")
    for key, value in settings.items():
        print(f"    {key}: {value}")

    try:
        display = Display(
            contrast=settings["contrast"],
            scroll_speed=settings["scroll_speed"],
            message_duration=settings["message_duration"],
            direction=settings["direction"],
        )
    except Exception as e:
        print(f"\n[ERROR] Could not initialize display: {e}")
        print("Check: SPI enabled, wiring, common ground, separate 5V supply.")
        sys.exit(1)
    print("\n[OK] Display initialized from loaded settings")

    state = new_state(
        mode=settings["mode"],
        messages=settings["messages"],
        single_message=settings["single_message"],
    )

    try:
        print(f"\n[RUNNING] Configured mode: '{state['mode']}'")
        for i in range(4):
            msg = get_next_message(state)
            print(f"  Playback {i + 1}: '{msg}'")
            display.scroll_text(msg)
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    finally:
        display.clear()
        print("\n[DONE] Display cleared.")
        print(
            "\nTo test persistence: edit a value in data/settings.json "
            "(e.g. \"contrast\": 200) and rerun. To test corruption "
            "recovery: replace data/settings.json with invalid text and rerun - "
            "it should fall back to safe defaults instead of crashing."
        )


if __name__ == "__main__":
    main()



