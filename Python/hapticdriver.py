"""Module to define a haptic glove class.

Version: 4/25/24
"""
import math
import numpy as np
import socket
from threading import Thread
import time


def find_distance(vector1, vector2, normalized=False):
    """Find the normalized distance between two vectors

    :param vector1: First vector
    :param vector2: Second vector
    :param normalized: Whether to normalize vectors first
    """
    if normalized:
        vector1 = vector1 / np.linalg.norm(vector1)
        vector2 = vector2 / np.linalg.norm(vector2)
    diff = vector1 - vector2
    distance = np.linalg.norm(diff)
    return distance

def map_to_range(x, in_min, in_max, out_min, out_max, bounded=False): # TODO: Can this be removed for glove 2.0?
    """Map a variable with expected range in_min-in_max to range out_min-out_max. Works like the map function in C++

    :param x: Number to map
    :param in_min: Minimum of input range
    :param in_max: Maximum of input range
    :param out_min: Minimum of output range
    :param out_max: Maximum of output range
    :param bounded: Whether to strictly bound input value to output range
    """
    output = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if bounded:
        if output < out_min:
            output = out_min
        if output > out_max:
            output = out_max
    return output

def reverse_map_to_range(x, in_min, in_max, out_min, out_max, bounded=False): #TODO: Can this be removed for glove 2.0?
    """Inversely map a variable with expected range in_min-in_max to range out_min-out_max.

    :param x: Number to map
    :param in_min: Minimum of input range
    :param in_max: Maximum of input range
    :param out_min: Minimum of output range
    :param out_max: Maximum of output range
    :param bounded: Whether to strictly bound input value to output range
    """
    output = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if bounded:
        if output > out_min:
            output = out_min
        if output < out_max:
            output = out_max
    return output

def find_intensity_array(current_pos, goal_pos, motor_positions, accel = np.array([0.0,0.0,0.0]), norm = True):
    """Generate array of vibration intensity for motors. (acceleration not implemented yet)

    :param current_pos: Current position of glove
    :param goal_pos: Goal position of glove
    :param motor_positions: Position of motors on the hand
    :param accel: acceleration
    :param norm: Whether to normalize vectors first
    """
    # Normalize all vectors
    if norm:
        if np.linalg.norm(current_pos) != 0:
            current_pos = current_pos / np.linalg.norm(current_pos)
        if np.linalg.norm(goal_pos) != 0:
            goal_pos = goal_pos / np.linalg.norm(goal_pos)
        if np.linalg.norm(accel) != 0:
            accel = accel / np.linalg.norm(accel)

    # Calculate displacement to goal and find distance
    U = goal_pos - current_pos - accel
    D = np.linalg.norm(U)

    # Map the distance value to motor command values
    # I is the maximum that a single motor can be driven
    # I will be proportionally distributed across motors that are closest to the displacement vector
    I = map_to_range(D, 0, 1, 150, 255,  bounded=True) # TODO: See comments at function creation

    motor_distance = [0.0,0.0,0.0,0.0]
    mapped = [0.0,0.0,0.0,0.0]

    # Find the distance between the displacement vector and motors
    # Calculate distributions of vibration to each motor
    for i in range(0, len(motor_positions)):
        motor_distance[i] = find_distance(U, motor_positions[i], normalized=norm)
        # Bound the proportion of vibration sent to a single motor
        mapped[i] = reverse_map_to_range(motor_distance[i], 0.0, math.sqrt(2), 1, .59, bounded=True) # TODO: See comments at function creation

    # Cast distributions of vibration to motors to a numpy array
    mapped = np.array(mapped)
    # Scale distribution by the global maximum vibration
    intensity = np.array(I * mapped).astype(int)
    return intensity

class HapticDriver:
    """
    Glove object
    Supports versions with and without accelerometer
    Used for manual operation and testing
    """

    pFactor = 1.0  # Power factor scales maximum intensity of motor vibrations

    # Motor coordinate arrays that will be switched between based on acceleration data
    motors = np.array([np.array([0.0, pFactor, 0.0]), np.array([0.0, -pFactor, 0.0]), np.array([-pFactor, 0.0, 0.0]),
                       np.array([pFactor, 0.0, 0.0])])  # standard position
    motors_UD = np.array([np.array([0.0, -pFactor, 0.0]), np.array([0.0, pFactor, 0.0]), np.array([pFactor, 0.0, 0.0]),
                          np.array([-pFactor, 0.0, 0.0])])  # upside down
    motors_R = np.array([np.array([pFactor, 0.0, 0.0]), np.array([-pFactor, 0.0, 0.0]), np.array([0.0, pFactor, 0.0]),
                         np.array([0.0, -pFactor, 0.0])])  # rolled right
    motors_L = np.array([np.array([-pFactor, 0.0, 0.0]), np.array([pFactor, 0.0, 0.0]), np.array([0.0, -pFactor, 0.0]),
                         np.array([0.0, pFactor, 0.0])])  # rolled left

    def __init__(self, device_id, port, acceleration=False, verbose=True) -> None:
        # Initialize object variables
        self.connected = False
        self.device_id = device_id
        self.verbose = verbose
        # Automatically find glove IP with device_id
        # self.TCP_IP = find_device_ip(self.device_id)

        # TODO: remove automatic lookup to avoid error when multiple NICs are present
        # IP is hard coded to 172.16.1.X based upon Apple AirPort router
        self.TCP_IP = "172.16.1." + str(device_id)
        self.TCP_PORT = port
        self.acceleration = acceleration
        # If using accelerometer, initialize acceleration vectors
        if acceleration:
            self.accel_data = np.array([0.0, 0.0, 0.0, 0.0])
            #self.accel_norm = np.array([0.0, 1.0, 0.0])
        # Set initial conditions
        self.current_vector = np.array([0.0, 1.0, 0.0])
        self.glove_position = np.array([0.0, 0.0, 0.0])
        # Set default motors
        self.current_motors = self.motors

        # create global flag to indicate glove shutdown
        self.shutdown = False

    def connect(self):
        """Connect to the glove via TCP socket"""
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.settimeout(10)
            self.s.connect((self.TCP_IP, self.TCP_PORT))
            self.connected = True
            # If using accelerometer, spawn thread and tell it to read constantly
            if self.acceleration:
              self.accel_loop = True
              self.acceleration_thread = Thread(target=self.__get_acceleration).start()
        except:
            if self.verbose:
                print(f'Failed to connect to ip {self.TCP_IP}')
            return False

        return True

    def disconnect(self):

        # set shutdown flag to True
        self.shutdown = True

        # close socket
        self.s.close()

    # Send a message to the glove and retrieve response containing accelerometer reading
    def __get_acceleration(self): # TODO: Edit to where the user can turn this on/off within their Python script based on their application

        # this is a one time send
        self.s.send('A,1\n'.encode('ascii'))
        while self.accel_loop:

            # if correct socket available
            if self.connected:

                # if acceleration has been enabled
                if self.acceleration:
                    # Receive accelerometer reading
                    # TODO: adjust recv to recv_into so buffer is not allocated each time  https://docs.python.org/3/library/socket.html
                    msg = self.s.recv(4096).decode("ascii").split('\r')[0].split('\n')[0]
                    try:
                        # Check if message exists
                        if len(msg) > 0:
                            # Parse the acceleration message
                            msg_split = msg.split(',')
                            msg_split = np.array(msg_split)
                            msg_split = msg_split.astype(float)
                            self.accel_data = msg_split
                            # TODO: Possible numpy version of rounding acceleration to improve program performance?
                            '''x_dat = self.accel_data[0]
                            y_dat = self.accel_data[1]
                            z_dat = self.accel_data[2]'''
                            #print(self.accel_data) # Print out accel data to ensure that the thread is functioning
                        # TODO: investigate why this SLEEP is here. Cause you don't want to hammer the socket with
                        # data requests - JF
                        time.sleep(0.1)
                    except Exception as e:
                        if self.verbose:
                            print(f'Error communicating with glove. {e}')

                # warning if acceleration not enabled
                else:
                    if self.verbose:
                        print(f'Glove {self.device_id} not setup for acceleration. Accel thread shutting down.')

            # warning if no socket is present
            else:
                if self.verbose:
                    print(f'Glove {self.device_id} not connected. Please run Glove.connect() method. Accel thread shutting down.')
                    return

            # if global shut down initiated
            if self.shutdown:
                if self.verbose:
                    print(f'Shutting down acceleration thread')
                return

            # default yield at end of thread: https://docs.python.org/3/library/time.html#time.sleep
            time.sleep(0)

    def __make_message(self, vect, magic_byte):
        """Format message for transfer over TCP socket. Message can be variable length, up to a length of 8

        :param vect: Vector to send to glove
        :param magic_byte: Byte value to XOR with the checksum. Default is 0xff
        """

        # Create string for message. This allows for variable message length
        msg = ''

        # Add each effect ID to the message
        for effect_id in vect:
          msg += f'{effect_id},'

        # Create checksum to add to the end of the message
        checksum = 0

        # Turn each character into an integer and XOR each byte of the message together
        for char in msg:
            checksum ^= ord(char)

        # XOR the magic byte with the other bytes of the message
        checksum ^= magic_byte

        # Add integer version of the checksum and a newline character to the message
        # Note that the required comma before the checksum was added at the end of the above for loop
        msg += f'{checksum}\n'

        return msg

    def __send_message(self, message):
        """Send message to glove over TCP socket

        :param message: Message to send
        """
        if self.connected:
            self.s.send(message)
        else:
            print(f'Glove {self.device_id} not connected. Please run Glove.connect() method.')

    def communicate_message(self, msg_tup, magic_byte):
        """Make and send a message

        :param msg_tup: Tuple containing cmd letter and data contents to send to glove
        :param magic_byte: Byte value to XOR with the checksum. Default is 0xff
        :return: Message that is sent
        """
        # Create message string with cmd letter
        message = msg_tup[0]

        # If there is data to include in the message, include it
        if len(msg_tup) == 2:
            message += "," + self.__make_message(msg_tup[1], magic_byte)

        # Encode and send message
        message = message.encode('ascii')
        self.__send_message(message)
        if self.verbose:
            print(message)

        return message

    def set_ip_manual(self, ip):
        """Manually set glove IP"""
        self.TCP_IP = ip

    def set_power_factor(self, number):
        """Set the maximum intensity of the motor outputs"""
        if 1.0 > number > 0.0:
            self.pFactor = number
        else:
            print(f'Power factor for glove {self.device_id} not in range. Power factor should be between 0 and 1')

    def get_power_factor(self):
        """Get glove power factor"""
        return self.pFactor

    def set_motors(self, effects=[], magic_byte=0xff):
        """Set the playback effect of each motor. The order of the effects array corresponds to the motor numbers

        :param effects: A list containing a command letter followed by integers [-1,123] that indicate the desired playback effect of each motor
        :param magic_byte: Byte value to XOR with the checksum
        """

        # Remove and save command letter
        cmd_letter = effects.pop(0)

        # Turn into NumPy array
        raw_effects = np.array(effects)

        # Append array of floating point zeros of length 8
        if raw_effects.size < 8:
            raw_effects = np.append(raw_effects, np.zeros(8))

        # Truncate to length of 8 (undoes part of previous step if effects parameter is not empty)
        if raw_effects.size > 8:
            raw_effects = raw_effects[:8]

        # Turn into NumPy array
        final_effects = raw_effects.astype(int)

        # Make and send message to glove
        self.communicate_message((cmd_letter, final_effects), magic_byte)
