from glove import Glove
import numpy as np
import time

# Define gloves
glove = Glove(device_id=2, port=8888, acceleration=False, verbose=True)
glove1 = Glove(device_id=4, port=8888, acceleration=False, verbose=False)

# Connect to gloves
glove.connect()
glove1.connect()

#glove.current_vector = np.array([-1.0, -1.0, 1.0])

glove.set_motors([3, -1])
time.sleep(2.0)

glove.set_motors([0.0, 0.8, 0.2])
glove1.set_motors([1, 0, 1])
time.sleep(2.0)

glove.set_motors([1, 1, 1, .5])
time.sleep(2.0)

glove.set_motors([0, .5, 0, 1.0, 3, 2, -5, .6])
