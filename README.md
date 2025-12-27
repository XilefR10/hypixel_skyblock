# hypixel_skyblock

This repository contains a small Python automation script (macro.py) that simulates keyboard input to run a repeating movement/jumping sequence. It was created to automate repetitive in-game movements for testing or convenience.

**Macro Overview**
- **Script:** macro.py
- **What it does:** alternates holding movement keys and jump to simulate repeated movement. The script runs a sequence of hold/release actions in loops and prints logs to the console.

**Background**
The macro was written to automate a simple, repeatable input pattern (e.g., moving left while jumping, then moving right while jumping). It is intentionally simple and editable so you can adapt timings, keys, and loop count to your needs.

**Requirements**
- Python 3.8+ installed
- pynput package for sending keyboard events

Install the dependency:

	pip install pynput

**Usage**
1. Open a terminal in this folder.
2. Run the script:

	python macro.py

3. Focus the window you want to send keys to (the script sends OS-level key events to the active window).
4. Press F8 to start the sequence; press F8 again to stop it. The script prints simple logs while holding and releasing keys.

**Controls & Config**
- Toggle start/stop: F8
- Movement keys set at top of macro.py: key_a, key_d, key_w, and key_space.
- Loop count: change the num_loops variable.
- Timings: the script uses time.sleep() calls (currently 71s and 72s in each phase) — adjust these values to change how long each hold lasts.

**Customization**
- To change which keys are used, edit the key variables near the top of macro.py.
- To change how many times the sequence repeats, edit num_loops.
- To change phase durations, modify the time.sleep() values inside run_sequence().

**Notes & Safety**
- The script simulates real key presses and requires the target window to be focused.
- Many online games (including Hypixel) prohibit automation or macros. Using automation may violate terms of service and could lead to bans. Use responsibly and only where allowed.
- If key events do not work, ensure pynput is installed and the script is running with sufficient privileges. On Windows, running the script from an elevated prompt may help in some environments.

**Troubleshooting**
- No effect in-game: make sure the game window is focused, and try running the script as administrator.
- Errors importing pynput: run pip install pynput and verify the Python environment used to run the script matches the one where pynput is installed.

If you'd like, I can add a short example requirements.txt, add command-line options to configure timings, or make the script safer by adding a single-key emergency stop.