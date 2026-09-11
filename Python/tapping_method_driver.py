#### motor placement
# motor 1: left trapezius muscle (upper back) near armpit level
# motor 2: right trapezius muscle (upper back) near armpit level
# motor 3: left latissmus dorsi muscle (midback)
# motor 4: right latissimus dorsi muscle (midback)
# motor 5: left outer elbow
# motor 6: right outer elbow
# motor 7: left top wrist
# motor 8: right top wrist


# importing libraries 
from hapticdriver import HapticDriver
import time
import sys

def l_elbow_tap():
    for i in range(0, 3):
        # set motor 5 to effect 44 (long double sharp click 1 - 100%)
        glove.set_motors(['E', 0, 0, 0, 0, 44, 0, 0, 0])

        # sleep for 1s
        time.sleep(1)

    # stop motors
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])

# connect to glove
glove = HapticDriver(device_id=10, port=8888, acceleration=False, verbose=True)

success = glove.connect()
if success is False:
    print('Could not connect to glove. Exiting.')
    sys.exit(-1)
else:
    print('Connected to glove!')

# program loop
l_elbow_tap()


        

