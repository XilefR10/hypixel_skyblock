# prototype.py — README

This document explains the purpose, structure, and usage of `prototype.py` — a small, opinionated prototype refactor of the original `macro.py` into a state-machine controller.

**Background**
- Goal: move from a single repeating loop to a state-machine design so the macro can run discrete behaviours (FARMING, PEST_CHECK, PEST_KILL, SELL, IDLE) and decide when to switch.
- Benefits: easier to extend, safer to stop, fewer stuck-key bugs, clearer separation of concerns for farming / pest handling / UI actions.

**High-level design**
- `SkyblockMacro` class: central controller that owns keyboard & mouse controllers, runtime state, and a thread-safe main loop.
- States: `IDLE`, `FARMING`, `PEST_CHECK`, `PEST_KILL`, `SELL`.
- Control: start/stop via toggle key (F8) and emergency stop (Esc). The class exposes `start()` and `stop()` helpers.

**Key functions (methods)**
- `__init__()` — sets up controllers, default durations, pest-check timer, and threading primitives.
- `press(key)` / `release(key)` — safe wrappers around keyboard actions.
- `stop_all()` — releases movement/jump keys and mouse button to avoid stuck inputs.
- `farm_melons()` — encapsulated farming behaviour (presses movement + jump, sleeps for configured durations, releases keys).
- `should_kill_pests()` — timer-based pest detector placeholder (returns True when timer expires).
- `kill_pests()` — generic pest-killing behaviour (stops movement + issues repeated left-clicks).
- `sell_items()` — placeholder for UI-driven selling (opens inventory; abstracted UI sequence goes here).
- `run()` — main state-machine loop; checks `self.state` and executes corresponding state method, then transitions.
- `start()` / `stop()` — thread-safe entry/exit for the run loop; `stop()` also calls `stop_all()`.

**Usage**
1. Install dependency:

```bash
pip install pynput
```

2. Run the prototype (from repository root):

```bash
python prototype.py
```

3. Controls while running:
- Press `F8` to toggle start/stop (starts in `FARMING` when started).
- Press `Esc` for an immediate emergency stop (releases keys).

**Configuration & customization**
- Change durations at the top of the `SkyblockMacro` instance (`farm_left_duration`, `farm_right_duration`, `pest_check_interval`).
- Replace the `should_kill_pests()` timer with an OCR/OpenCV-based detector (see notes below) to detect in-game chat or HUD messages.
- Add more states (e.g., `VISITORS`) by adding a method for the behaviour and a transition in `run()`.

**Safety & notes**
- This is a prototype: it intentionally avoids hardcoded screen coordinates and complex vision logic.
- Many online servers disallow automation; using macros may violate server rules and result in bans. Use responsibly and only where permitted.
- `pynput` sends OS-level events; ensure the target window is focused when testing.
- If keys do not take effect, try running the script with elevated privileges.

**Extending the prototype**
- Replace timer pest checks with screenshot + OCR (Tesseract) or OpenCV-based template matching for robust detection.
- Add recovery behaviours (e.g., on unexpected disconnect or UI state mismatch).
- Add configuration via CLI arguments or a small `config.json` to adjust timings without editing source.

If you want, I can add a `requirements.txt`, implement an OCR-based `should_kill_pests()` proof-of-concept, or add a CLI for runtime configuration. For reference, the running prototype is `prototype.py` at the repository root.