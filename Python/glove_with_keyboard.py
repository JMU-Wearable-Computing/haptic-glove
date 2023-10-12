from haptic_mapping import *
import numpy as np
from pynput import keyboard
from threading import Thread
import time
from refactored_glove import Glove


def keyboard_thread():
    """
    Create a thread for reading keyboard input for two gloves
    :return:
    """
    listening_thread = Thread(target=listen_keyboard)
    listening_thread.start()


def listen_keyboard(mode="pull"):
    """
    Begin listening to keyboard
    :param mode: Whether motors "push" or "pull" user to target
    :return:
    """

    # Global variables are a workaround since these were previously attributes of glove class
    global commands
    global commands1
    global keys
    global keys1

    pFactor = glove.get_power_factor()
    pFactor1 = glove1.get_power_factor()

    if mode == "pull":
        commands = {keys[0]: np.array([0.0, pFactor, 0.0]), keys[1]: np.array([0.0, -pFactor, 0.0]),
                    keys[2]: np.array([-pFactor, 0.0, 0.0]), keys[3]: np.array([pFactor, 0.0, 0.0])}
        commands1 = {keys1[0]: np.array([0.0, pFactor1, 0.0]), keys1[1]: np.array([0.0, -pFactor1, 0.0]),
                     keys1[2]: np.array([-pFactor1, 0.0, 0.0]), keys1[3]: np.array([pFactor1, 0.0, 0.0])}
    elif mode == "push":
        commands = {keys[0]: np.array([0.0, -pFactor, 0.0]), keys[1]: np.array([0.0, pFactor, 0.0]),
                    keys[2]: np.array([pFactor, 0.0, 0.0]), keys[3]: np.array([-pFactor, 0.0, 0.0])}
        commands1 = {keys1[0]: np.array([0.0, pFactor1, 0.0]), keys1[1]: np.array([0.0, -pFactor1, 0.0]),
                     keys1[2]: np.array([-pFactor1, 0.0, 0.0]), keys1[3]: np.array([pFactor1, 0.0, 0.0])}

    #self.board = keyboard.Controller()
    listener = keyboard.Listener(on_press=on_press)
    listener.start()  # start to listen on a separate thread
    listener.join()  # remove if main thread is polling self.keysup message


def on_press(key):
    """
    Callback for keyboard presses
    :param key: Key that is pressed
    :return:
    """

    # Global variables are a workaround since these were previously attributes of glove class
    global keys
    global keys1

    # Stop listener
    if key == keyboard.Key.esc:
        return False

    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys

    # Stop all motors but keep listener open
    if k == 'space':
        glove.current_vector = np.array([0.0, 0.0, 1.0])
        glove1.current_vector = np.array([0.0, 0.0, 1.0])

    # Stop listener; remove this if you want more keys
    elif k == 'q':
        if glove.acceleration:
            glove.accel_loop = False
        if glove1.acceleration:
            glove1.accel_loop = False

        return False

    # Check if pressed key is for first glove
    if k in keys:  # keys of interest
        glove.current_vector = commands[k]

        # If not using accelerometer, send message on keypress
        if not glove.acceleration:
            key_intensity = find_intensity_array(glove.glove_position, glove.current_vector, glove.current_motors, norm=True)
            key_message = glove.make_message(key_intensity).encode('ascii')
            print(key_message)
            glove.send_message(key_message)

        time.sleep(.05)

    # Check if pressed key is for second glove
    elif k in keys1:  # keys of interest
        glove1.current_vector = commands1[k]

        # If not using accelerometer, send message on keypress
        if not glove1.acceleration:
            key_intensity = find_intensity_array(glove1.glove_position, glove1.current_vector, glove1.current_motors, norm=True)
            key_message = glove1.make_message(key_intensity).encode('ascii')
            print(key_message)
            glove1.send_message(key_message)

        time.sleep(.05)


if __name__ == '__main__':
    print('Welcome to the two glove haptic demo!\n\n'
          'Press "esc" to stop the keyboard listener.\n'
          'Press "q" to stop the keyboard listener and quit the program.\n'
          'Press the space bar to stop all motors but keep the listener open.')

    # Mode sets whether the vibrations tells use to move away or towards vibration
    commands = None
    commands1 = None

    # Define gloves
    glove = Glove(device_id=2, port=8888, acceleration=True, verbose=False)
    glove1 = Glove(device_id=4, port=8888, acceleration=True, verbose=False)

    # Keys to use for the gloves
    keys = ['a', 's', 'd', 'f']
    keys1 = ['h', 'j', 'k', 'l']

    # Connect to gloves
    glove.connect()
    glove1.connect()

    # Setup keyboard listeners
    keyboard_thread()
