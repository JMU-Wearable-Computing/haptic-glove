import socket
from haptic_mapping import *
import random
import time
from threading import Thread
import numpy as np
import ast

TCP_IP = "172.16.1.4"
#TCP_IP = "172.16.1.3"
#TCP_IP = "192.168.50.170"

TCP_PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

accel_data = np.array([1.0,1.0,1.0])
accel_norm = np.array([1.0,1.0,1.0])
accel_mapped = np.array([0,0,0])

# def get_accel():
#     try:
#         while True:
#             try:
#                 global accel_data
#                 global accel_norm

#                 s.send('accel\n'.encode('ascii'))
#                 #time.sleep(0.1)
#                 recv_time = time.time()
#                 msg = s.recv(4096).decode("ascii").split('\r')[0].split('\n')[0]
#                 try: 
#                     msg_split = msg.split(',')
#                     msg_split = np.array(msg_split)
#                     msg_split = msg_split.astype(float)
#                     accel_data = msg_split
#                     accel_norm = accel_data / np.linalg.norm(accel_data)
#                     x_dat = accel_norm[0]
#                     y_dat = accel_norm[1]
#                     z_dat = accel_norm[2]
#                     accel_norm[0] = round(x_dat,2)
#                     accel_norm[1] = round(y_dat,2)
#                     accel_norm[2] = round(z_dat,2)                    
#                     #print(accel_norm)
#                 except:
#                     None
#                     #print('acceleration fail')
#                 #print(msg)
#                 #print(accel_data)
#                 recv_time = time.time() - recv_time
#                 #print(f'Time to recieve message: {recv_time} seconds')
#             except:
#                 print("No message to be recieved.")
#             #time.sleep(0.5)
#     except:
#         None


def make_message(vect):
    return f'/{vect[0]}/{vect[1]}/{vect[2]}/{vect[3]}\n'

def get_acceleration():
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

try: 
    #accel_thread = Thread(target=get_accel)
    #accel_thread.start()

    C = np.array([0.0,0.0,0.0]) #Current Pos
    G = np.array([1.0,0.0,0.0]) # Goal Pos

    #motors = np.array([np.array([0.0,1.0,0.0]), np.array([0.0,-1.0,0.0]), np.array([-1.0,0.0,0.0]), np.array([1.0,0.0,0.0])]) #array of motor positions
    motors_UD = np.array([np.array([0.0,-1.0,0.0]), np.array([0.0,1.0,0.0]), np.array([1.0,0.0,0.0]), np.array([-1.0,0.0,0.0])])
    #motors_L = np.array([np.array([1.0,0.0,0.0]), np.array([-1.0,0.0,0.0]), np.array([0.0,1.0,0.0]), np.array([0.0,-1.0,0.0])])
    #motors_R = np.array([np.array([-1.0,0.0,0.0]), np.array([1.0,0.0,0.0]), np.array([0.0,-1.0,0.0]), np.array([0.0,1.0,0.0])])
    current_motors = motors_UD
    while True:

        get_acceleration()
        print(accel_data)
        print(accel_norm)
        
        # if (accel_norm[1] > 0.7):
        #     current_motors = motors
        # elif (accel_norm[1] < -0.7):
        #     current_motors = motors_UD
        # elif (accel_norm[0] > 0.7 ):
        #     current_motors = motors_R
        # elif (accel_norm[0] < -0.7 ):
        #     current_motors = motors_L


        #G = np.array([0,random.uniform(-2,2),random.uniform(-2,2)]) # Goal Position
        G = np.array([0.0,1.0,0.0]) - accel_data # Goal Position
        intensity = find_intensity_array(C, G, current_motors, norm=True) 

        print(G, intensity)
        message = make_message(intensity)

        send_time = time.time()
        for i in range(0,2):
            s.send(message.encode('ascii'))
        send_time = time.time() - send_time
        #print(f'Time to send message: {send_time} seconds')
        time.sleep(0.1)
    
except KeyboardInterrupt:
    print ('KeyboardInterrupt exception is caught')


    