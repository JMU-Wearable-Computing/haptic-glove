"""Demo to show vibration functionality of two gloves

Author: Will Bradford
Version: 10/17/23
"""
from glove import Glove
import time

print('Welcome to the two glove demo!\n'
      'The program will cycle through various vibration combinations to test motor functionality.\n')

# Define gloves
# device_id will be different for every glove
# verbose=True prints out the intensity values message that is sent to the glove(s)
glove = Glove(device_id=2, port=8888, acceleration=False, verbose=True)
glove1 = Glove(device_id=4, port=8888, acceleration=False, verbose=True)

# Connect to gloves
glove.connect()
glove1.connect()

# Set first glove
glove.set_motors([3, -1])
time.sleep(2.0)

# Set both gloves
glove.set_motors([0.0, 0.8, 0.2])
glove1.set_motors([1, 0, 1])
time.sleep(2.0)

# Set both gloves
glove.set_motors([1, 1, 1, .5])
glove1.set_motors()
time.sleep(2.0)

# Set both gloves
glove.set_motors([.1, .32, 0, 1])
glove1.set_motors([0, .5, 0, 1.0, 3, 2, -5, .6])
