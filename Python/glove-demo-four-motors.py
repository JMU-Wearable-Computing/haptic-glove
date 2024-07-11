"""
Demo program to activate four individual motors in sequence. Targeted at v2.0 board.

Jason Forsyth (7/11/2024)
"""
from hapticdriver import HapticDriver
import time

glove = HapticDriver(device_id=10, port=8888, acceleration=False, verbose=True)

glove.connect()

# set motor 1 to effect 16 (1000 ms alert)
glove.set_motors(['E', 16, 0, 0, 0, 0, 0, 0, 0])

# sleep 1s
time.sleep(1)

# set motor 2 to effect 16 (1000 ms alert)
glove.set_motors(['E', 0, 16, 0, 0, 0, 0, 0, 0])

# sleep 1s
time.sleep(1)

# set motor 3 to effect 16 (1000 ms alert)
glove.set_motors(['E', 0, 0, 16, 0, 0, 0, 0, 0])

# sleep 1s
time.sleep(1)

# set motor 4 to effect 16 (1000 ms alert)
glove.set_motors(['E', 0, 0, 0, 16, 0, 0, 0, 0])

# sleep 1s
time.sleep(1)

# disconnect from glove
glove.disconnect()

