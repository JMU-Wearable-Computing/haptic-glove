"""Demo to show vibration functionality of one glove

Author: Will Bradford
Version: 1/25/24
"""
from glove import Glove
import time

print('Welcome to the single glove demo!\n'
      'The program will cycle through various vibration combinations to test motor functionality.\n')


# Define glove
# device_id will be different for every glove
# verbose=True prints out the intensity values message that is sent to the glove
glove = Glove(device_id=4, num_motors=8, port=8888, acceleration=False, verbose=True)

# Connect to glove
glove.connect()

# Number of seconds to activate each time
time_activated = 3

glove.set_motors(['E', 10, 70, 64, 10, 10, 10, 10, 10])
time.sleep(time_activated)

#glove.set_motors(['E'])
#time.sleep(time_activated)

#glove.set_motors(['E', 10, 70, 64, 64, 64])
#time.sleep(time_activated)

#glove.set_motors([.1, .32, 0, 1])
#time.sleep(time_activated)