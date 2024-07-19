
from hapticdriver import HapticDriver
import time

glove = HapticDriver(device_id=10, port=8888, acceleration=False, verbose=True)

glove.connect()

effect = 27
duration = 0.5

for i in range(0,5):

    # set motor 1 to effect 16 (1000 ms alert)
    glove.set_motors(['E', effect, 0, 0, 0, 0, 0, 0, 0])

    # sleep 1s
    time.sleep(duration)

    # set motor 2 to effect 16 (1000 ms alert)
    glove.set_motors(['E', 0, effect, 0, 0, 0, 0, 0, 0])

    # sleep 1s
    time.sleep(duration)

    # set motor 3 to effect 16 (1000 ms alert)
    glove.set_motors(['E', 0, 0, effect, 0, 0, 0, 0, 0])

    # sleep 1s
    time.sleep(duration)

    # set motor 4 to effect 16 (1000 ms alert)
    glove.set_motors(['E', 0, 0, 0, effect, 0, 0, 0, 0])

    # sleep 1s
    time.sleep(duration)


# disconnect from glove
glove.disconnect()

