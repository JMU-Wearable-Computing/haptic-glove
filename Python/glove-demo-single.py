"""Demo to show vibration functionality of one glove

Author: Will Bradford
Version: 4/25/24
"""
from glove import Glove
import time

print('Welcome to the single glove demo!\n'
      'The program will cycle through various vibration combinations to test motor functionality.\n')

# Define glove
# device_id will be different for every glove
# acceleration=True activates the accelerometer for the entire time that the Python script is running
# verbose=True prints out the message that is sent to the glove
#glove = Glove(device_id=10, port=8888, acceleration=False, verbose=True)
glove = Glove(device_id=10, port=8888, acceleration=True, verbose=True)

# Connect to glove (Arduino does not register a connection until a message is sent.
# Meaning, Arduino doesn't register a connection until glove.set_motors() or glove.communicate_message() is called)
glove.connect()

# Number of seconds to activate each time (edit as desired)
time_activated = 3

glove.set_motors(['E', 10])
time.sleep(time_activated)

glove.set_motors(['E'])
time.sleep(time_activated)

glove.set_motors(['E', 9, 9, 9, 9, 9, 9, 9, 9])

glove.set_motors(['E', 64, 0, 0, 64, 0, 0, 0, 64])
time.sleep(time_activated)

# Kill the accelerometer loop so the program ends
glove.accel_loop = False
