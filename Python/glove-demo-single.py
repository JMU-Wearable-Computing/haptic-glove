"""Demo to show vibration functionality of one glove

Author: Will Bradford
Version: 4/25/24
"""
from hapticdriver import HapticDriver
import time

print('Welcome to the single glove demo!\n'
      'The program will cycle through various vibration combinations to test motor functionality.\n')

# Define glove
# device_id will be different for every glove
# port should be consistent with the port number in firmware-V2.ino. This is normally port=8888
# acceleration=True activates the accelerometer for the entire time that the Python script is running
# verbose=True prints out the message that is sent to the glove
# glove = Glove(device_id=10, port=8888, acceleration=False, verbose=True)
glove = HapticDriver(device_id=10, port=8888, acceleration=False, verbose=True)

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
time.sleep(time_activated)

glove.set_motors(['E', 64, 0, 0, 64, 0, 0, 0, 64])
time.sleep(time_activated)

glove.set_motors(['E', 47, 47, 47, 47, 47, 47, 47, 47])
time.sleep(30)

# disconnected from glove and stop accelerometer thread
glove.disconnect()
