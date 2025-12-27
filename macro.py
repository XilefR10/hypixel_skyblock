import threading
import time
from pynput import keyboard

# Initialize the keyboard controller
kb_controller = keyboard.Controller()

# Define keys
key_a = 'a'
key_d = 'd'
key_w = 'w'
key_space = keyboard.Key.space

# Toggle flag
start_sequence = False

# Loop count
num_loops = 6

# Hold and release helpers
def hold_key(key):
    kb_controller.press(key)
    print(f"Holding {key}")

def release_key(key):
    kb_controller.release(key)
    print(f"Releasing {key}")

# The sequence function
def run_sequence():
    global start_sequence
    for i in range(num_loops):
        if not start_sequence:
            break  # stop if sequence is toggled off
        print(f"Loop {i+1}/{num_loops}")

        # Hold A, W, Space
        hold_key(key_a)
        hold_key(key_w)
        hold_key(key_space)
        time.sleep(71)
        if not start_sequence:
            break

        # Release A
        release_key(key_a)
        time.sleep(0.5)
        if not start_sequence:
            break

        # Hold D, W, Space
        hold_key(key_d)
        hold_key(key_w)
        hold_key(key_space)
        time.sleep(72)
        if not start_sequence:
            break

        # Release D
        release_key(key_d)
        time.sleep(0.5)

    # Release all keys at the end
    release_key(key_a)
    release_key(key_d)
    release_key(key_w)
    release_key(key_space)
    print("Sequence completed or stopped.")

# Listener for F8 toggle
def on_press(key):
    global start_sequence
    try:
        if key == keyboard.Key.f8:
            if not start_sequence:
                start_sequence = True
                print("Starting sequence...")
                threading.Thread(target=run_sequence, daemon=True).start()
            else:
                start_sequence = False
                print("Stopping sequence...")
    except AttributeError:
        pass

# Start the listener
with keyboard.Listener(on_press=on_press) as listener:
    print("Press F8 to start/stop the sequence.")
    listener.join()
