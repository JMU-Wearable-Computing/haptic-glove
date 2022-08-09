from Python.haptic_mapping import *
from Python.helpers import *
import numpy as np
from pynput import keyboard
import socket
from threading import Thread
import time


# Glove object
# Supports versions with and without accelerometer
# Used for manual opperation and testing


class LocalizationDemo():

    def __init__(self, device_id, port, mode="pull", acceleration=False, verbose=False) -> None:
        # Initialize object variables
        self.connected = False
        self.device_id = device_id
        self.verbose = verbose
        # Automatically find glove IP with device_id
        self.TCP_IP = find_device_ip(self.device_id)
        self.TCP_PORT = port

    # Connect to the glove via TCP socket
    def connect(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.TCP_IP, self.TCP_PORT))
            self.connected = True

        except:
            if self.verbose:
                print(f'Failed to connect to ip {self.TCP_IP}')

    # Create a thread for reading keyboard input for a single glove
    # Default to arrow keys for control of glove
    def keyboard_thread(self, keys=['up', 'down', 'left', 'right']):
        listening_thread = Thread(target=self.__listen_keyboard, args=(keys,))
        listening_thread.start()

    # Begin listening to keyboard
    # Keys variable will override default key map
    def __listen_keyboard(self, keys=['up', 'down', 'left', 'right']):

        self.keys = keys
        self.board = keyboard.Controller()
        self.listener = keyboard.Listener(on_press=self.__on_press)
        self.listener.start()  # start to listen on a separate thread
        self.listening = True
        self.listener.join()  # remove if main thread is polling self.keysup messsage
        self.listening = False

    # Format message for transfer over TCP socket
    def make_message(self, vect):
        return f'/{vect[0]}/{vect[1]}/{vect[2]}/{vect[3]}\n'

    # Callback for keyboard presses
    def __on_press(self, key):

        special_key = False
        try:
            print('alphanumeric key {0} pressed'.format(key.char))

        except AttributeError:
            print('special key {0} pressed'.format(key))
            special_key = True

        if key == keyboard.Key.esc:
            print("Program ending.")
            return False
        vec = []
        if special_key:
            if key.name == 'up':
                print("Up Key detected! Do the motor thing!")
                vec = bytearray([255,0,0,0])
                print(vec)
            elif key.name == 'down':
                print("Down Key detected! Do the motor thing!")
                vec = bytearray([0,255,0,0])
                print(vec)
            elif key.name == 'right':
                print("Right Key detected! Do the motor thing!")
                vec = bytearray([0,0,255,0])
            elif key.name == 'left':
                print("Left Key detected! Do the motor thing!")
                vec = bytearray([0,0,0,255])
            else:
                print('Single key detected as ', key.name)
                vec = bytearray([0,0,0,0])
        else:  # Keys other than special keys
            if key.char == 'i':
                print("i Key detected! Do the motor thing!")
                vec = bytearray([255,255,0,0])
            else:
                print('Single key detected as ', key.char)
                vec = bytearray([0,0,0,0])

        ### create message to turn on two motors

        ### send the message to the glove

        glove.send_message(glove.make_message(vec))

        ### wait two seconds
        '''
        IMPORTANT NOTE: Polling here may block the system on Windows.
        See "The keyboard listener thread in https://pynput.readthedocs.io/en/latest/keyboard.html#monitoring-the-keyboard
        The solution may be to dispatch this wait to another thread
        '''
        current_time_in_ns = time.time_ns()
        duration_to_wait_in_ns = 5E9
        print('Beginning wait of ', duration_to_wait_in_ns / 1E9, 'seconds')
        while abs(time.time_ns() - current_time_in_ns) < duration_to_wait_in_ns:
            pass
        print('Waiting done!')

        ### create message to turn off two motors

        ### send message to glove

        glove.send_message(glove.make_message(bytearray([0,0,0,0])))

    # Send message to glove over TCP socket
    def send_message(self, message):
        if self.connected:
            self.s.send(bytes(message,'UTF-8'))
        else:
            print(f'Glove {self.device_id} not connected. Please run Glove.connect() method.')

    def set_ip_manual(self, ip):
        self.TCP_IP = ip

    # Set the maximum intensity of the motor outputs
    def set_power_factor(self, number):
        if number < 1.0 and number > 0.0:
            self.pFactor = number
        else:
            print(f'Power factor for glove {self.device_id} not in range. Power factor should be between 0 and 1')


if __name__ == '__main__':
    # Define glove
    glove = LocalizationDemo(4, 8888, acceleration=False, verbose=True)
    # Connect to glove
    glove.connect()
    # Setup keyboard listener
    glove.keyboard_thread()
