import socket
from pynput import keyboard
import numpy as np
from haptic_mapping import *
from threading import Thread
import time

#Glove object
#Supports versions with and without accelerometer
#Used for manual opperation and testing
class Glove():
    pFactor = 1.0 #Power factor scales maximum intensity of motor vibrations

    #Motor coordinate arrays that will be switched between based on acceleration data
    motors = np.array([np.array([0.0,pFactor,0.0]), np.array([0.0,-pFactor,0.0]), np.array([-pFactor,0.0,0.0]), np.array([pFactor,0.0,0.0])]) #standard position
    motors_UD = np.array([np.array([0.0,-pFactor,0.0]), np.array([0.0,pFactor,0.0]), np.array([pFactor,0.0,0.0]), np.array([-pFactor,0.0,0.0])]) #upside down
    motors_R = np.array([np.array([pFactor,0.0,0.0]), np.array([-pFactor,0.0,0.0]), np.array([0.0,pFactor,0.0]), np.array([0.0,-pFactor,0.0])]) #rolled right
    motors_L = np.array([np.array([-pFactor,0.0,0.0]), np.array([pFactor,0.0,0.0]), np.array([0.0,-pFactor,0.0]), np.array([0.0,pFactor,0.0])]) #rolled left

    def __init__(self, device_id, ip, port, mode="pull", acceleration=False) -> None:
        #Initialize object variables
        self.connected = False
        self.device_id = device_id
        self.TCP_IP = ip
        self.TCP_PORT = port
        #mode sets whether the vibrations tells use to move away or towards vibration
        self.mode = mode
        self.acceleration = acceleration
        #If using accelerometer, initialize acceleration vectors
        if acceleration:
            self.accel_data = np.array([0.0,0.0,0.0])
            self.accel_norm = np.array([0.0,1.0,0.0])
        #Set initial conditions
        self.current_vector = np.array([0.0,0.0,0.0])
        self.glove_position = np.array([0.0,0.0,0.0])
        #Set default motors
        self.current_motors = self.motors

    #Connect to the glove via TCP socket
    def connect(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.TCP_IP, self.TCP_PORT))
            self.connected = True
        except:
            print(f'Failed to connect to ip {self.TCP_IP}')

    #Send a message to the glove and revieve response containing accelerometer reading
    def get_acceleration(self):
        if self.connected:
            if self.acceleration:
                #Send message "accel"
                self.s.send('accel\n'.encode('ascii'))
                #Recieve accelerometer reading
                msg = self.s.recv(4096).decode("ascii").split('\r')[0].split('\n')[0]
                try:
                    #Parse the acceleration message
                    msg_split = msg.split(',')
                    msg_split = np.array(msg_split)
                    msg_split = msg_split.astype(float)
                    self.accel_data = msg_split
                    self.accel_norm = self.accel_data / np.linalg.norm(self.accel_data)
                    x_dat = self.accel_norm[0]
                    y_dat = self.accel_norm[1]
                    z_dat = self.accel_norm[2]
                    #normalize acceleration vector
                    self.accel_norm[0] = round(x_dat,2)
                    self.accel_norm[1] = round(y_dat,2)
                    self.accel_norm[2] = round(z_dat,2)    
                    #Change the coordinates of motors based on orrientation of hand                
                    if (self.accel_norm[1] > 0.7):
                        self.current_motors = self.motors
                    elif (self.accel_norm[1] < -0.7):
                        self.current_motors = self.motors_UD
                    elif (self.accel_norm[0] > 0.7 ):
                        self.current_motors = self.motors_L
                    elif (self.accel_norm[0] < -0.7 ):
                        self.current_motors = self.motors_R
                except:
                    print('Error communicating with glove.')
                else:
                    print(f'Glove {self.device_id} not setup for acceleration.')
        else:
            print(f'Glove {self.device_id} not connected. Please run Glove.connect() method.')

    #Create a thread for reading keyboard input for a single glove\
    #Default to arrow keys for control of glove
    def keyboard_thread(self, keys = ['up', 'down', 'left', 'right']):
        listening_thread = Thread(target=self.listen_keyboard, args = (keys,))
        listening_thread.start()

    #Begin listening to keyboard
    def listen_keyboard(self, keys = ['up', 'down', 'left', 'right']):
        if self.mode == "pull":
            self.commands = {keys[0]:np.array([0.0,self.pFactor,0.0]), keys[1]:np.array([0.0,-self.pFactor,0.0]), keys[2]:np.array([-self.pFactor,0.0,0.0]), keys[3]:np.array([self.pFactor,0.0,0.0])}
        if self.mode == "push":    
            self.commands = {keys[0]:np.array([0.0,-self.pFactor,0.0]), keys[1]:np.array([0.0,self.pFactor,0.0]), keys[2]:np.array([self.pFactor,0.0,0.0]), keys[3]:np.array([-self.pFactor,0.0,0.0])}
        
        self.keys = keys
        self.board = keyboard.Controller()
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()  # start to listen on a separate thread
        self.listening = True
        self.listener.join()  # remove if main thread is polling self.keysup messsage
        self.listening = False

    #Format message for transfer over TCP socket
    def make_message(self, vect):
        return f'/{vect[0]}/{vect[1]}/{vect[2]}/{vect[3]}\n'

    #Callback for keyboard presses
    def on_press(self, key):
        if key == keyboard.Key.esc:
            return False  # stop listener
        try:
            k = key.char  # single-char keys
        except:
            k = key.name  # other keys
        if k in self.keys:  # keys of interest
            self.current_vector = self.commands[k]
            self.get_acceleration()
            print(self.make_message(find_intensity_array(self.glove_position, self.current_vector, self.current_motors, norm=True)))
            self.send_message(self.make_message(find_intensity_array(self.glove_position, self.current_vector, self.current_motors, norm=True)).encode('ascii'))
            time.sleep(.05)
        if k == 'space':
            self.current_vector = np.array([0.0,0.0,0.0])
        #Press q or esc to stop listening to keyboard
        if k == 'q':    
            return False  # stoplistener; remove this if want more keys

    #Send message to glove over TCP socket
    def send_message(self, message):
        if self.connected:
            self.s.send(message)
        else:
            print(f'Glove {self.device_id} not connected. Please run Glove.connect() method.')

    #Set the maximum intensity of the motor outputs
    def set_power_factor(self, number):
        if number < 1.0 and number > 0.0:
            self.pFactor = number
        else:
            print(f'Power factor for glove {self.device_id} not in range. Power factor should be between 0 and 1')
        

if __name__ == '__main__':
    glove = Glove(0, '192.168.50.4', 8888)
    glove.keyboard_thread()
    glove1 = Glove(1, '192.168.50.2', 8888)
    glove1.keyboard_thread( keys= ['w','a','s','d'])