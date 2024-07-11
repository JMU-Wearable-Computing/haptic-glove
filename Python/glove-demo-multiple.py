"""Demo to show vibration functionality of two or more gloves

Author: Will Bradford
Version: 4/16/24
"""
from glove import Glove
import time

print('Welcome to the multiple glove demo!\n'
      'The program will cycle through various vibration combinations to test motor functionality.\n')

# Define glove
# device_id will be different for every glove
# verbose=True prints out the intensity values message that is sent to the glove
glove = Glove(device_id=10, port=8888, acceleration=False, verbose=True)
glove2 = Glove(device_id=11, port=8888, acceleration=False, verbose=True)
# glove3 = Glove(device_id=12, port=8888, acceleration=False, verbose=True)

# Connect to glove
glove.connect()
glove2.connect()
# glove3.connect()

# Number of seconds to activate each time (edit as desired)
time_activated = 30

glove.set_motors(['E', 64, 64])
glove2.set_motors(['E', 64, 64])
# glove3.set_motors(['E', 64, 64])
time.sleep(time_activated)

glove.set_motors(['E', 78, 78, 78, 78, 78, 78, 78, 78])
glove2.set_motors(['E', 78, 78, 78, 78, 78, 78, 78, 78])
# glove3.set_motors(['E', 78, 78, 78, 78, 78, 78, 78, 78])
time.sleep(time_activated)

glove.set_motors(['E', 11, 0, -1, 1234, -1234, 46, 0, 64])
glove2.set_motors(['E', 11, 0, -1, 1234, -1234, 46, 0, 64])
# glove3.set_motors(['E', 11, 0, -1, 1234, -1234, 46, 0, 64])
time.sleep(time_activated)

# disconnected from glove and stop accelerometer thread
glove.disconnect()
glove2.disconnect()

