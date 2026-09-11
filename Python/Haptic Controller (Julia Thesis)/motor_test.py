import time
import sys
import os
from datetime import datetime

# Add parent directory to path for hapticdriver import
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from hapticdriver import HapticDriver
import threading
from pynput import keyboard

def motor_1_activate():
    glove.set_motors(['E', 44, 0, 0, 0, 0, 0, 0, 0])
    time.sleep(1)
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
    return

def motor_2_activate(): 
    glove.set_motors(['E', 0, 44, 0, 0, 0, 0, 0, 0])
    time.sleep(1)
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
    return

def motor_3_activate(): 
    glove.set_motors(['E', 0, 0, 44, 0, 0, 0, 0, 0])
    time.sleep(1)
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
    return

def motor_4_activate(): 
    glove.set_motors(['E', 0, 0, 0, 44, 0, 0, 0, 0])
    time.sleep(1)
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
    return

def motor_5_activate(): 
    glove.set_motors(['E', 0, 0, 0, 0, 44, 0, 0, 0])
    time.sleep(1)
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
    return

def motor_6_activate(): 
    glove.set_motors(['E', 0, 0, 0, 0, 0, 44, 0, 0])
    time.sleep(1)
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
    return

def motor_7_activate(): 
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 44, 0])
    time.sleep(1)
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
    return

def motor_8_activate(): 
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 44])
    time.sleep(1)
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
    return

def motors_off():
    # turn all motors off
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
    return

#connect to glove
glove = HapticDriver(device_id=10, port=8888, acceleration=False, verbose=True)

success = glove.connect()
if success is False:
    print('Could not connect to glove. Exiting.')
    sys.exit(-1)
else:
    print('Connected to glove!')

# main loop
key = ''
while key != 'q':
    print('Enter key command.')
    print('End key for command (q to quit): ')
    key = input()
    print('Key '+str(key)+ ' was pressed...')

    if key == '1': 
        motor_1_activate()
    elif key == '2':
        motor_2_activate()
    elif key == '3':
        motor_3_activate()
    elif key == '4':
        motor_4_activate()
    elif key == '5':
        motor_5_activate()
    elif key == '6':
        motor_6_activate()
    elif key == '7':
        motor_7_activate()
    elif key == '8':
        motor_8_activate()
    elif key == 'q': 
        motors_off()
        print('Quitting...')

# disconnect from glove
glove.disconnect()
print('Disconnected from glove.')