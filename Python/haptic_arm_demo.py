##### on left arm
# motor 1 needs to be placed on the top of the wrist
# motor 2 is the front part of forearm
# motor 3 is mid-forearm(little further to elbow maybe)
# motor 4 is on back part of forearm
# motor 8 needs to be on the outer wrist
# motor 6 needs to be on bottom of wrist
# motor 7 needs to be on inner wrist

# importing libraries
from hapticdriver import HapticDriver
import time
import sys


# defining lateral movement functions
def lateral_backward():
    for i in range(0, 5):
        # set motor 1 to effect 1 (strong click - 100%)
        glove.set_motors(['E', 1, 0, 0, 0, 0, 0, 0, 0])

        # for 0.5s
        time.sleep(0.5)

        # set motor 2 to effect 1 (strong click - 100%)
        glove.set_motors(['E', 0, 1, 0, 0, 0, 0, 0, 0, ])

        # for 0.25s
        time.sleep(0.25)

        # set motor 3 to effect 1 (strong click - 100%)
        glove.set_motors(['E', 0, 0, 1, 0, 0, 0, 0, 0])

        # for 0.25s
        time.sleep(0.25)

        # set motor 4 to effect 1 (strong click - 100%)
        glove.set_motors(['E', 0, 0, 0, 1, 0, 0, 0, 0])

        # for 0.5s
        time.sleep(0.5)

    # stop motors
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])

    return


def lateral_forward():
    for i in range(0, 5):
        # set motor 4 to effect 1 (strong click - 100%)
        glove.set_motors(['E', 0, 0, 0, 1, 0, 0, 0, 0])

        # for 0.5s
        time.sleep(0.5)

        # set motor 3 to effect 1 (strong click - 100%)
        glove.set_motors(['E', 0, 0, 1, 0, 0, 0, 0, 0])

        # for 0.25s
        time.sleep(0.25)

        # set motor 2 to effect 1 (strong click - 100%)
        glove.set_motors(['E', 0, 1, 0, 0, 0, 0, 0, 0, ])

        # for 0.25s
        time.sleep(0.25)

        # set motor 1 to effect 1 (strong click - 100%)
        glove.set_motors(['E', 1, 0, 0, 0, 0, 0, 0, 0])

        # for 0.5s
        time.sleep(0.5)

    # stop motors
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])

    return


def counter_clockwise_rotation():
    for i in range(0, 5):
        # set motor 1 to effect 27 (short double click strong 1 - 100%)
        glove.set_motors(['E', 27, 0, 0, 0, 0, 0, 0, 0])

        # for 0.5s
        time.sleep(0.5)

        # set motor 8 to effect 27 (short double click strong 1 - 100%)
        glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 27])

        # for 0.5s
        time.sleep(0.5)

        # set motor 6 to effect 27 (short double click strong 1 - 100%)
        glove.set_motors(['E', 0, 0, 0, 0, 0, 27, 0, 0])

        # for 0.5s
        time.sleep(0.5)

        # set motor 7 to effect 27 (short double click strong 1 - 100%)
        glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 27, 0])

        # for 0.5s
        time.sleep(0.5)

    # stop motors
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])

    return


def clockwise_rotation():
    for i in range(0, 5):
        # set motor 1 to effect 27 (short double click strong 1 - 100%)
        glove.set_motors(['E', 27, 0, 0, 0, 0, 0, 0, 0])

        # for 0.5s
        time.sleep(0.5)

        # set motor 7 to effect 27 (short double click strong 1 - 100%)
        glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 27, 0])

        # for 0.5s
        time.sleep(0.5)

        # set motor 6 to effect 27 (short double click strong 1 - 100%)
        glove.set_motors(['E', 0, 0, 0, 0, 0, 27, 0, 0])

        # for 0.5s
        time.sleep(0.5)

        # set motor 8 to effect 27 (short double click strong 1 - 100%)
        glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 27])

        # for 0.5s
        time.sleep(0.5)

    # stop motors
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])

    return

def motors_off():
    # turn all motors off
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
    return

# connect to glove
glove = HapticDriver(device_id=21, port=8888, acceleration=False, verbose=True)

success = glove.connect()
if success is False:
    print('Could not connect to glove. Exiting.')
    sys.exit(-1)
else:
    print('Connected to glove!')


# program loop
key = ''
while key != 'q':
    print('Enter key command.')
    print('End key for command (q to quit): ')
    key = input()
    print('Key '+str(key)+ ' was pressed...')

    if key == 'a':
        lateral_forward()
    elif key == 's':
        lateral_backward()
    elif key == 'd':
        counter_clockwise_rotation()
    elif key == 'f':
        clockwise_rotation()
    elif key == 'p':
        motors_off()

    motors_off()

#disconnecting glove
glove.disconnect()

