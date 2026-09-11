#### motor placement
# motor 1: left trapezius muscle (upper back) near armpit level
# motor 2: right trapezius muscle (upper back) near armpit level
# motor 5: left outer elbow (on tricep)
# motor 6: right outer elbow (on tricep)
# motor 7: left top wrist
# motor 8: right top wrist

# importing libraries
import time
import sys
import os
from datetime import datetime

# Add parent directory to path for hapticdriver import
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from hapticdriver import HapticDriver
import threading
from pynput import keyboard

# Create log file for this session - logs to Julia's Thesis Data/muscle_logs
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(SCRIPT_DIR, '..', "Julia's Thesis Data", 'muscle_logs')
os.makedirs(LOG_DIR, exist_ok=True)
session_start = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
LOG_FILE = os.path.join(LOG_DIR, f'muscle_log_{session_start}.csv')

# Initialize log file with header
with open(LOG_FILE, 'w') as f:
    f.write('timestamp,key,command\n')

def log_command(key, command_name):
    """Log a command to the session log file with timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    with open(LOG_FILE, 'a') as f:
        f.write(f'{timestamp},{key},{command_name}\n')
    print(f'[LOGGED] {timestamp} - Key: {key}, Command: {command_name}')

# Event to signal pattern interruption
stop_event = threading.Event()
# Lock to prevent multiple patterns running simultaneously
pattern_lock = threading.Lock()
# Current pattern thread reference
current_thread = None

def interruptible_sleep(duration, interval=0.1):
    """Sleep that can be interrupted by stop_event."""
    elapsed = 0
    while elapsed < duration:
        if stop_event.is_set():
            return False  # Interrupted
        time.sleep(min(interval, duration - elapsed))
        elapsed += interval
    return True  # Completed normally

def trap_muscle_tap():
    for i in range(0, 3):
        if stop_event.is_set():
            break
        for j in range(0, 3):
            if stop_event.is_set():
                break
            glove.set_motors(['E', 44, 44, 0, 0, 0, 0, 0, 0])
            if not interruptible_sleep(1):
                break
            glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
            if not interruptible_sleep(1):
                break
        if stop_event.is_set():
            break
        if not interruptible_sleep(1):
            break
        glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
        if not interruptible_sleep(4):
            break
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])

def tri_muscle_tap():
    for i in range(0, 3):
        if stop_event.is_set():
            break
        for j in range(0, 3):
            if stop_event.is_set():
                break
            glove.set_motors(['E', 0, 0, 0, 0, 44, 44, 0, 0])
            if not interruptible_sleep(1):
                break
            glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
            if not interruptible_sleep(1):
                break
        if stop_event.is_set():
            break
        if not interruptible_sleep(1):
            break
        glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
        if not interruptible_sleep(4):
            break
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])

def motors_off():
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])

def run_pattern(pattern_func, pattern_name):
    """Run a pattern in a separate thread, interrupting any current pattern."""
    global current_thread
    
    # Signal current pattern to stop
    stop_event.set()
    
    # Wait for current pattern to finish
    if current_thread and current_thread.is_alive():
        current_thread.join(timeout=0.5)
    
    # Reset stop event and start new pattern
    stop_event.clear()
    
    def pattern_wrapper():
        with pattern_lock:
            print(f'Playing pattern: {pattern_name}')
            pattern_func()
            motors_off()
            print(f'Pattern {pattern_name} finished')
    
    current_thread = threading.Thread(target=pattern_wrapper, daemon=True)
    current_thread.start()

# Key mappings for single key presses
KEY_MAPPINGS = {
    '1': ('trap_muscle_tap', trap_muscle_tap),
    '2': ('tri_muscle_tap', tri_muscle_tap),
    '0': ('stop', motors_off),
}

running = True

def on_press(key):
    global running
    try:
        key_char = key.char
        if key_char == 'q':
            log_command(key_char, 'quit')
            print('\nQuitting...')
            stop_event.set()
            running = False
            return False  # Stop listener
        elif key_char in KEY_MAPPINGS:
            pattern_name, pattern_func = KEY_MAPPINGS[key_char]
            log_command(key_char, pattern_name)
            run_pattern(pattern_func, pattern_name)
    except AttributeError:
        # Special keys (shift, ctrl, etc.) - ignore
        pass

# connect to glove
glove = HapticDriver(device_id=10, port=8888, acceleration=False, verbose=True)

success = glove.connect()
if success is False:
    print('Could not connect to glove. Exiting.')
    sys.exit(-1)
else:
    print('Connected to glove!')

# Print instructions
print('\n--- Haptic Feedback Controller ---')
print('Press a key to trigger a pattern (patterns can be interrupted):')
print('  1 = Trap Muscle Tap')
print('  2 = Tri Muscle Tap')
print('  0 = Stop motors')
print('  q = Quit')
print('----------------------------------\n')

# Start keyboard listener
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

# Cleanup
stop_event.set()
if current_thread and current_thread.is_alive():
    current_thread.join(timeout=1)
motors_off()
glove.disconnect()
print('Disconnected from glove.')