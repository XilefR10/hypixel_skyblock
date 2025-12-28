import threading
import time
from pynput import keyboard, mouse
import pytesseract
from PIL import ImageGrab
import re


class SkyblockMacro:
    """State-machine controller for Hypixel Skyblock farming automation.

    This class manages a finite-state automation system for coordinating
    farming, pest detection, pest elimination, and selling actions in
    Hypixel Skyblock. It is thread-safe and designed for safe stopping
    with minimal risk of stuck key presses.

    Attributes:
        running (bool): Whether the macro loop is actively running.
        state (str): Current state (IDLE, FARMING, PEST_CHECK, PEST_KILL, SELL).
        kb (keyboard.Controller): pynput keyboard controller for input.
        mouse (mouse.Controller): pynput mouse controller for clicks.
        lock (threading.Lock): Thread-safe state access.
        farm_left_duration (float): Seconds to hold A+W+Space for left lane.
        farm_right_duration (float): Seconds to hold D+W+Space for right lane.
        pest_keywords (list): Keywords to search for in OCR text to detect pests.
        chat_crop_area (tuple): Screen bbox (left, top, right, bottom) for chat OCR.
        ocr_cooldown (float): Minimum seconds between OCR checks to reduce overhead.

    States:
        IDLE: No action; waiting for start signal.
        FARMING: Run farm_melons() behavior; transition to PEST_CHECK.
        PEST_CHECK: Check for pests via should_kill_pests(); transition to PEST_KILL or FARMING.
        PEST_KILL: Run kill_pests() behavior; transition to FARMING.
        SELL: Run sell_items() behavior; transition to IDLE.

    Example:
        macro = SkyblockMacro()
        macro.start()  # Press F8 to trigger this
        # ... macro runs farming/pest checks ...
        macro.stop()   # Press F8 again to stop
    """

    def __init__(self):
        """Initialize the SkyblockMacro controller with default settings.

        Sets up keyboard/mouse controllers, farming durations, OCR pest detection,
        and thread-safe state management.
        """
        # Keyboard and mouse input controllers
        self.kb = keyboard.Controller()
        self.mouse = mouse.Controller()

        # State and thread safety
        self.running = False
        self.state = "IDLE"
        self.lock = threading.Lock()  # Protects state transitions
        self.num_loops = 6  # Legacy; not currently used

        # Configurable farming durations (in seconds)
        self.farm_left_duration = 71  # Hold A+W+Space for left lane
        self.farm_right_duration = 72  # Hold D+W+Space for right lane

        # OCR-based pest detection configuration
        self.pest_detection_enabled = True
        self.pest_keywords = ["pest", "spawned", "has appeared"]  # Keywords to detect in chat
        self.chat_crop_area = (0, 0, 1920, 200)  # Screen region to capture for OCR (adjust for your UI)
        self.ocr_cooldown = 2  # Minimum seconds between OCR checks
        self.last_ocr_check = time.time()

        # Internal thread control
        self._stop_event = threading.Event()  # Signals to run() loop to exit

    # --- input helpers ---
    def press(self, key):
        """Press and hold a key safely.

        Args:
            key: pynput key object or string (e.g., 'a', keyboard.Key.space).
        """
        try:
            self.kb.press(key)
        except Exception:
            # Silently ignore errors to avoid crashes during rapid key events
            pass

    def release(self, key):
        """Release a held key safely.

        Args:
            key: pynput key object or string (e.g., 'a', keyboard.Key.space).
        """
        try:
            self.kb.release(key)
        except Exception:
            # Silently ignore errors; key may already be released
            pass

    def stop_all(self):
        """Release all held keys and mouse buttons to prevent stuck inputs.

        This is called on shutdown to ensure the game does not see any
        held keys after the macro exits.
        """
        # Release all movement and jump keys
        for k in ['a', 'd', 'w', keyboard.Key.space]:
            try:
                self.release(k)
            except Exception:
                pass
        # Release left mouse button if held (used during pest-killing)
        try:
            self.mouse.release(mouse.Button.left)
        except Exception:
            pass

    # --- state implementations ---
    def farm_melons(self):
        """Execute one farming cycle: left lane → right lane.

        Simulates moving left (A+W+Space), pausing, then moving right (D+W+Space).
        Durations are configurable via farm_left_duration and farm_right_duration.
        """
        print("FARMING: Farming melons...")

        # Left lane: hold A (left) + W (forward) + Space (jump)
        self.press('a')
        self.press('w')
        self.press(keyboard.Key.space)
        time.sleep(self.farm_left_duration)

        # Transition: release A, pause briefly to avoid jittering
        self.release('a')
        time.sleep(0.3)

        # Right lane: hold D (right) + W (forward) + Space (jump)
        self.press('d')
        time.sleep(self.farm_right_duration)

        # Release all keys to ensure a clean state
        self.release('d')
        self.release('w')
        self.release(keyboard.Key.space)

    def should_kill_pests(self):
        """Detect pests using OCR on chat area.

        Captures a screenshot of the chat region, runs Tesseract OCR,
        and searches for pest-related keywords. Returns True if any keyword
        is found; False otherwise. Respects cooldown to avoid overhead.

        Returns:
            bool: True if pests detected, False otherwise.
        """
        # Early exit if OCR detection is disabled
        if not self.pest_detection_enabled:
            return False

        # Cooldown check: avoid running OCR too frequently
        if time.time() - self.last_ocr_check < self.ocr_cooldown:
            return False

        # Update last check timestamp
        self.last_ocr_check = time.time()

        try:
            # Capture screenshot of chat region (customize bbox for your UI)
            screenshot = ImageGrab.grab(bbox=self.chat_crop_area)
            # Run Tesseract OCR on screenshot
            text = pytesseract.image_to_string(screenshot).lower()
            # Search for any pest keyword in the extracted text
            for keyword in self.pest_keywords:
                if keyword in text:
                    print(f"OCR: detected '{keyword}' in chat — pest found!")
                    return True
        except Exception as e:
            # Log OCR errors but continue (graceful degradation)
            print(f"OCR error: {e}")

        return False

    def kill_pests(self):
        """Execute pest-killing behavior: stop and attack repeatedly.

        Releases forward movement and performs repeated mouse clicks
        to attack nearby pests.
        """
        print("PEST_KILL: Killing pests (generic)...")
        # Stop forward movement to focus on combat
        self.release('w')
        # Perform repeated left-clicks to attack pests (generic approach)
        for _ in range(20):
            try:
                self.mouse.click(mouse.Button.left)
            except Exception:
                pass
            time.sleep(0.2)  # Small delay between clicks

    def sell_items(self):
        """Execute selling behavior (placeholder).

        Currently just opens inventory (E key). Real implementation would
        use OCR/image recognition to navigate UI and confirm sales.
        """
        print("SELL: Selling items (placeholder)")
        # Open inventory (E key) — UI actions are abstracted
        self.press('e')
        time.sleep(0.5)
        self.release('e')

    # --- main run loop (state machine) ---
    def run(self):
        """Main state-machine loop: executes behaviors based on current state.

        Runs until self.running is False or _stop_event is set.
        Ensures all keys are released on exit.
        """
        print("Macro run loop started")
        while self.running and not self._stop_event.is_set():
            # Safely read current state
            with self.lock:
                state = self.state

            # Execute behavior based on state and transition
            if state == "FARMING":
                # Perform one farming cycle, then check for pests
                self.farm_melons()
                with self.lock:
                    self.state = "PEST_CHECK"

            elif state == "PEST_CHECK":
                # Detect pests; switch to PEST_KILL or continue FARMING
                if self.should_kill_pests():
                    with self.lock:
                        self.state = "PEST_KILL"
                else:
                    with self.lock:
                        self.state = "FARMING"

            elif state == "PEST_KILL":
                # Kill detected pests, then resume farming
                self.kill_pests()
                with self.lock:
                    self.state = "FARMING"

            elif state == "SELL":
                # Execute selling logic, then go idle
                self.sell_items()
                with self.lock:
                    self.state = "IDLE"

            elif state == "IDLE":
                # Idle: sleep briefly to avoid busy-waiting
                time.sleep(0.5)

            # Brief sleep to allow state changes from other threads
            time.sleep(0.1)

        # Clean shutdown: release all keys before exiting
        self.stop_all()
        print("Run loop exiting")

    # --- control helpers ---
    def start(self):
        """Start the macro: begin the run loop in a daemon thread.

        Sets state to FARMING and spawns the background thread.
        Safe to call multiple times (idempotent).
        """
        with self.lock:
            if self.running:
                # Already running; skip
                return
            self.running = True
            self.state = "FARMING"  # Begin in farming state
            self._stop_event.clear()
        # Start run() in a background thread
        threading.Thread(target=self.run, daemon=True).start()

    def stop(self):
        """Stop the macro: halt the run loop and release all keys.

        Signals run() to exit and immediately releases held keys
        to prevent stuck inputs in the game.
        """
        with self.lock:
            self.running = False
            self.state = "IDLE"
        # Signal run() loop to stop
        self._stop_event.set()
        # Release all keys immediately
        self.stop_all()


# --- global macro instance and listener ---
# Global instance of the macro controller; shared with on_press() callback
macro = SkyblockMacro()


def on_press(key):
    """Global keyboard listener: handle macro toggle and emergency stop.

    F8: Start/stop the macro
    Esc: Emergency stop (forcefully release all keys)

    Args:
        key: pynput Key object from the listener.
    """
    try:
        if key == keyboard.Key.f8:
            # Toggle start/stop
            if not macro.running:
                print("Toggling: start")
                macro.start()
            else:
                print("Toggling: stop")
                macro.stop()

        elif key == keyboard.Key.esc:
            # Emergency stop: forcefully exit and release keys
            print("Emergency stop requested")
            macro.stop()
    except Exception:
        # Ignore key parsing errors
        pass


if __name__ == "__main__":
    """Entry point: start the keyboard listener and begin waiting for input."""
    print("Prototype macro loaded. Press F8 to start/stop; Esc to emergency-stop.")
    # Create and start a persistent keyboard listener
    with keyboard.Listener(on_press=on_press) as listener:
        # Block until listener is stopped (Ctrl+C)
        listener.join()
