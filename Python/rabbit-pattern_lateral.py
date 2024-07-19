
from hapticdriver import HapticDriver
import time

glove = HapticDriver(device_id=10, port=8888, acceleration=False, verbose=True)

glove.connect()

for i in range(0,5):

    # set motor 1 to effect 16 (1000 ms alert)
    glove.set_motors(['E', 1, 0, 0, 0, 0, 0, 0, 0])

    # sleep 1s
    time.sleep(0.5)

    # set motor 2 to effect 16 (1000 ms alert)
    glove.set_motors(['E', 0, 1, 0, 0, 0, 0, 0, 0])

    # sleep 1s
    time.sleep(0.25)

    # set motor 3 to effect 16 (1000 ms alert)
    glove.set_motors(['E', 0, 0, 1, 0, 0, 0, 0, 0])

    # sleep 1s
    time.sleep(0.25)

    # set motor 4 to effect 16 (1000 ms alert)
    glove.set_motors(['E', 0, 0, 0, 1, 0, 0, 0, 0])

    # sleep 1s
    time.sleep(0.5)

    # set motor 4 to effect 16 (1000 ms alert)
    glove.set_motors(['E', 0, 0, 0, 1, 0, 0, 0, 0])

    # sleep 1s
    time.sleep(0.5)

    # set motor 3 to effect 16 (1000 ms alert)
    glove.set_motors(['E', 0, 0, 1, 0, 0, 0, 0, 0])

    # sleep 1s
    time.sleep(0.25)

    # set motor 2 to effect 16 (1000 ms alert)
    glove.set_motors(['E', 0, 1, 0, 0, 0, 0, 0, 0])

    # sleep 1s
    time.sleep(0.25)

    # set motor 1 to effect 16 (1000 ms alert)
    glove.set_motors(['E', 1, 0, 0, 0, 0, 0, 0, 0])

    # sleep 1s
    time.sleep(0.5)


# disconnect from glove
glove.disconnect()

