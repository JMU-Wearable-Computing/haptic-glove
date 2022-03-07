import socket
from haptic_mapping import *
import random
import time

TCP_IP = "172.16.1.2"
#TCP_IP = "172.16.1.3"
#TCP_IP = "192.168.50.170"

TCP_PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))


def make_message(vect):
    return f'/{vect[0]}/{vect[1]}/{vect[2]}/{vect[3]}\n'


C = np.array([0,0,0]) #Current Pos
G = np.array([0,1,1]) # Goal Pos
motors = np.array([np.array([0,0,1]), np.array([0,0,-1]), np.array([0,-1,0]), np.array([0,1,0])]) #array of motor positions

for i in range(0,100):
    G = np.array([0,random.uniform(-2,2),random.uniform(-2,2)]) # Goal Position
    
    intensity = find_intensity_array(C, G, motors)
    print(G, intensity)
    intensity= [150,100,100,100]
    #intensity= [255,255,100,100]
    message = make_message(intensity)

    for i in range(0,10):
        s.send(message.encode('ascii'))
    
    time.sleep(2)

    