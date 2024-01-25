"""Module to define a haptic glove class.

Version: 10/17/23
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

def map_to_range(x, in_min, in_max, out_min, out_max, bounded=False):
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

def reverse_map_to_range(x, in_min, in_max, out_min, out_max, bounded=False):
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
    I = map_to_range(D, 0, 1, 150, 255,  bounded=True)

    motor_distance = [0.0,0.0,0.0,0.0]
    mapped = [0.0,0.0,0.0,0.0]

    # Find the distance between the displacement vector and motors
    # Calculate distributions of vibration to each motor
    for i in range(0, len(motor_positions)):
        motor_distance[i] = find_distance(U, motor_positions[i], normalized=norm)
        # Bound the proportion of vibration sent to a single motor
        mapped[i] = reverse_map_to_range(motor_distance[i], 0.0, math.sqrt(2), 1, .59, bounded=True)

    # Cast distributions of vibration to motors to a numpy array
    mapped = np.array(mapped)
    # Scale distribution by the global maximum vibration
    intensity = np.array(I * mapped).astype(int)
    return intensity

class Glove:
    """
    Glove object
    Supports versions with and without accelerometer
    Used for manual operation and testing
    """

    pFactor = 1.0  # Power factor scales maximum intensity of motor vibrations

    num_motors = 4  # Number of motors on glove

    # Motor coordinate arrays that will be switched between based on acceleration data
    motors = np.array([np.array([0.0, pFactor, 0.0]), np.array([0.0, -pFactor, 0.0]), np.array([-pFactor, 0.0, 0.0]),
                       np.array([pFactor, 0.0, 0.0])])  # standard position
    motors_UD = np.array([np.array([0.0, -pFactor, 0.0]), np.array([0.0, pFactor, 0.0]), np.array([pFactor, 0.0, 0.0]),
                          np.array([-pFactor, 0.0, 0.0])])  # upside down
    motors_R = np.array([np.array([pFactor, 0.0, 0.0]), np.array([-pFactor, 0.0, 0.0]), np.array([0.0, pFactor, 0.0]),
                         np.array([0.0, -pFactor, 0.0])])  # rolled right
    motors_L = np.array([np.array([-pFactor, 0.0, 0.0]), np.array([pFactor, 0.0, 0.0]), np.array([0.0, -pFactor, 0.0]),
                         np.array([0.0, pFactor, 0.0])])  # rolled left

    def __init__(self, device_id, port, acceleration=False, verbose=False) -> None:
        # Initialize object variables
        self.connected = False
        self.device_id = device_id
        self.verbose = verbose
        # Automatically find glove IP with device_id
        # self.TCP_IP = find_device_ip(self.device_id)

        # remove automatic lookup to avoid error when multiple NICs are present
        # IP is hard coded to 172.16.1.X based upon Apple AirPort router
        self.TCP_IP = "172.16.1." + str(device_id)
        self.TCP_PORT = port
        self.acceleration = acceleration
        # If using accelerometer, initialize acceleration vectors
        if acceleration:
            self.accel_data = np.array([0.0, 0.0, 0.0])
            self.accel_norm = np.array([0.0, 1.0, 0.0])
        # Set initial conditions
        self.current_vector = np.array([0.0, 1.0, 0.0])
        self.glove_position = np.array([0.0, 0.0, 0.0])
        # Set default motors
        self.current_motors = self.motors

    def connect(self):
        """Connect to the glove via TCP socket"""
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.TCP_IP, self.TCP_PORT))
            self.connected = True
            # If using accelerometer, spawn thread and tell it to read constantly
            if self.acceleration:
              self.accel_loop = True
              self.acceleration_thread = Thread(target=self.__get_acceleration).start()
        except:
            if self.verbose:
                print(f'Failed to connect to ip {self.TCP_IP}')

    # Send a message to the glove and retrieve response containing accelerometer reading
    def __get_acceleration(self):
        while self.accel_loop:
            if self.connected:
                if self.acceleration:
                    # Send message "accel"
                    self.s.send('accel\n'.encode('ascii'))
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
                            self.accel_norm = self.accel_data / np.linalg.norm(self.accel_data)
                            # TODO: Possible numpy version of rounding acceleration to improve program performance?
                            x_dat = self.accel_norm[0]
                            y_dat = self.accel_norm[1]
                            z_dat = self.accel_norm[2]
                            # normalize acceleration vector
                            self.accel_norm[0] = round(x_dat, 2)
                            self.accel_norm[1] = round(y_dat, 2)
                            self.accel_norm[2] = round(z_dat, 2)

                            # Change the coordinates of motors based on orientation of hand
                            if self.accel_norm[1] > 0.7:
                                self.current_motors = self.motors
                            elif self.accel_norm[1] < -0.7:
                                self.current_motors = self.motors_UD
                            elif self.accel_norm[0] > 0.7:
                                self.current_motors = self.motors_L
                            elif self.accel_norm[0] < -0.7:
                                self.current_motors = self.motors_R
                            # Send new message to glove
                            intensity_array = find_intensity_array(self.glove_position, self.current_vector, self.current_motors, norm=True)
                            self.communicate_message(intensity_array)
                        # TODO: investigate why this SLEEP is here
                        time.sleep(0.1)
                    except Exception as e:
                        if self.verbose:
                            print(f'Error communicating with glove. {e}')
                else:
                    if self.verbose:
                        print(f'Glove {self.device_id} not setup for acceleration.')
            else:
                if self.verbose:
                    print(f'Glove {self.device_id} not connected. Please run Glove.connect() method.')

    def __make_message(self, vect):
        """Format message for transfer over TCP socket

        :param vect: Vector to send to glove
        """
        return f'/{vect[0]}/{vect[1]}/{vect[2]}/{vect[3]}\n'

    def __send_message(self, message):
        """Send message to glove over TCP socket

        :param message: Message to send
        """
        if self.connected:
            self.s.send(message)
        else:
            print(f'Glove {self.device_id} not connected. Please run Glove.connect() method.')

    def communicate_message(self, vect):
        """Make and send a message

        :param vect: Vector to send to glove
        :return: Message that is sent
        """
        message = self.__make_message(vect).encode('ascii')
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

    def set_motors(self, intensities=[]):
        """Set the intensity of each motor. The order of the intensities array corresponds to the motor numbers

        :param intensities: An array of floats [0,1] to indicate the intensity of each motor
        """

        # Turn into NumPy array
        raw_intensities = np.array(intensities)

        # Append array of floating point zeros of length num_motors
        if raw_intensities.size < self.num_motors:
            raw_intensities = np.append(raw_intensities, np.zeros(self.num_motors))

        # Truncate to length of num_motors (undoes part of previous step if intensities parameter is not empty)
        if raw_intensities.size > self.num_motors:
            raw_intensities = raw_intensities[:self.num_motors]

        # Map 0-1 to 150-255
        mapped_list = [map_to_range(val, 0, 1, 150, 255, True) for val in raw_intensities]

        # Turn into NumPy array
        mapped_intensities = np.array(mapped_list).astype(int)

        # Make and send message to glove
        self.communicate_message(mapped_intensities)