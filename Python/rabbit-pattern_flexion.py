from hapticdriver import HapticDriver
import time

glove = HapticDriver(device_id=10, port=8888, acceleration=False, verbose=True)

glove.connect()

effect = 7
duration = 2

for i in range(0,5):
    glove.set_motors(['E', effect, 0, 0, 0, 0, 0, 0, 0])
    time.sleep(duration)

    glove.set_motors(['E', 0, effect, 0, 0, 0, 0, 0, 0])
    time.sleep(duration)

glove.disconnect()