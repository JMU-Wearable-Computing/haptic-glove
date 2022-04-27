import socket
from pynput import keyboard
import numpy as np
from haptic_mapping import *

TCP_IP = "192.168.1.4"
TCP_IP = "172.16.1.4"

#TCP_IP = "192.168.50.170"

TCP_PORT = 8888

pFactor = 1.0

motors = np.array([np.array([0.0,1.0,0.0]), np.array([0.0,-1.0,0.0]), np.array([-1.0,0.0,0.0]), np.array([1.0,0.0,0.0])]) #standard position
motors_UD = np.array([np.array([0.0,-1.0,0.0]), np.array([0.0,1.0,0.0]), np.array([1.0,0.0,0.0]), np.array([-1.0,0.0,0.0])]) #upside down
motors_R = np.array([np.array([1.0,0.0,0.0]), np.array([-1.0,0.0,0.0]), np.array([0.0,1.0,0.0]), np.array([0.0,-1.0,0.0])]) #rolled right
motors_L = np.array([np.array([-1.0,0.0,0.0]), np.array([1.0,0.0,0.0]), np.array([0.0,-1.0,0.0]), np.array([0.0,1.0,0.0])]) #rolled left
current_motors = motors

def get_acceleration():
    accel_data = np.array([0.0,0.0,0.0])
    accel_norm = np.array([0.0,0.0,0.0])
    accel_mapped = np.array([0,0,0])
    s.send('accel\n'.encode('ascii'))
        #time.sleep(0.1)
    msg = s.recv(4096).decode("ascii").split('\r')[0].split('\n')[0]
    try: 
        msg_split = msg.split(',')
        msg_split = np.array(msg_split)
        msg_split = msg_split.astype(float)
        accel_data = msg_split
        accel_norm = accel_data / np.linalg.norm(accel_data)
        x_dat = accel_norm[0]
        y_dat = accel_norm[1]
        z_dat = accel_norm[2]
        accel_norm[0] = round(x_dat,2)
        accel_norm[1] = round(y_dat,2)
        accel_norm[2] = round(z_dat,2)                    
        #print(accel_norm)
    except:
        None
    return accel_data, accel_norm

def make_message(vect):
    return f'/{vect[0]}/{vect[1]}/{vect[2]}/{vect[3]}\n'

C = np.array([0.0,0.0,0.0]) #Current Pos
G = np.array([0.0,0.0,0.0]) # Goal Pos

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
 
mode = "pull"

pattern = '118'
if mode == "pull":
    commands = {'up':np.array([0.0,pFactor,0.0]), 'down':np.array([0.0,-pFactor,0.0]), 'left':np.array([-pFactor,0.0,0.0]), 'right':np.array([pFactor,0.0,0.0])}

if mode == "push":    
    commands = {'up':np.array([0.0,-pFactor,0.0]), 'down':np.array([0.0,pFactor,0.0]), 'left':np.array([pFactor,0.0,0.0]), 'right':np.array([-pFactor,0.0,0.0])}

vector = commands['up']
board = keyboard.Controller()

 
def on_press(key):
    if key == keyboard.Key.esc:
        return False  # stop listener
    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys
 
    if k in ['up', 'down', 'left', 'right']:  # keys of interest
        global vector
        vector = commands[k]
        #for i in range(0,1):
            #s.send(make_message(find_intensity_array(C, commands[k], current_motors, norm=True)).encode('ascii'))
            #recieved = s.recv(64).decode('ASCII')
            #print(recieved)
    if k == 'space':
        vector = np.array([0.0,0.0,100.0])
            
 
    if k == 'q':    
        return False  # stoplistener; remove this if want more keys
 
listener = keyboard.Listener(on_press=on_press)
listener.start()  # start to listen on a separate thread
while True:

    accel_data, accel_norm = get_acceleration()
    #print(accel_norm)
    
    if (accel_norm[1] > 0.7):
        current_motors = motors
    elif (accel_norm[1] < -0.7):
        current_motors = motors_UD
    elif (accel_norm[0] > 0.7 ):
        current_motors = motors_L
    elif (accel_norm[0] < -0.7 ):
        current_motors = motors_R
    print(make_message(find_intensity_array(C, vector, current_motors, norm=True)).encode('ascii'))
    s.send(make_message(find_intensity_array(C, vector, current_motors, norm=True)).encode('ascii'))
listener.join()  # remove if main thread is polling self.keysup messsage
 
 
