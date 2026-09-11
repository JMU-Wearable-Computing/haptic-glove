#### motor placement
# motor 1: left trapezius muscle (upper back) near armpit level
# motor 2: right trapezius muscle (upper back) near armpit level
    # motor 3: left latissmus dorsi muscle (midback) - Motor 3 is unavailable
# motor 4: (right) latissimus dorsi muscle (midback) - Motor 4 will be placed mid-lower back
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

        # stop motors temporarily
        glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])

        #sleep for 1s
        time.sleep(1)

    # stop motors
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
    return

def r_elbow_tap():
    for i in range(0, 3):
        # set motor 5 to effect 44 (long double sharp click 1 - 100%)
        glove.set_motors(['E', 0, 0, 0, 0, 0, 44, 0, 0])

        # sleep for 1s
        time.sleep(1)

        # stop motors temporarily
        glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])

        #sleep for 1s
        time.sleep(1)

    # stop motors
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
    return

def l_wrist_tap():
    for i in range(0, 3):
        # set motor 5 to effect 44 (long double sharp click 1 - 100%)
        glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 44, 0])

        # sleep for 1s
        time.sleep(1)

        # stop motors temporarily
        glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])

        #sleep for 1s
        time.sleep(1)

    # stop motors
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
    return

def r_wrist_tap():
    for i in range(0, 3):
        # set motor 5 to effect 44 (long double sharp click 1 - 100%)
        glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 44])

        # sleep for 1s
        time.sleep(1)

        # stop motors temporarily
        glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])

        #sleep for 1s
        time.sleep(1)

    # stop motors
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
    return

def trap_muscle_tap():
    for i in range(0,3):
        for i in range(0,3):
            # set motor 1 to effect 44 (long double sharp click 1 - 100%)
            glove.set_motors(['E',44, 44, 0, 0, 0, 0, 0, 0])

            # sleep for 1s
            time.sleep(1)

            # stop motors temporarily
            glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])

            # sleep for 1s
            time.sleep(1)
    
        # sleep for 1s
        time.sleep(1)

        # stop motors
        glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])

        # keep motors stopped for 4s
        time.sleep(4)

    return
        

def lat_muscle_tap():
    for i in range(0,3):
        for i in range(0,3):
            # set motor 1 to effect 44 (long double sharp click 1 - 100%)
            glove.set_motors(['E', 0, 0, 0, 44, 0, 0, 0, 0])

            # sleep for 1s
            time.sleep(1)

            # stop motors temporarily
            glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])

            # sleep for 1s
            time.sleep(1)
    
        # sleep for 1s
        time.sleep(1)

        # stop motors
        glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])

        # keep motors stopped for 4s
        time.sleep(4)

    return



def motors_off():
    # turn all motors off
    glove.set_motors(['E', 0, 0, 0, 0, 0, 0, 0, 0])
    return

# connect to glove
glove = HapticDriver(device_id=10, port=8888, acceleration=False, verbose=True)

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

    if key == 'le':
        l_elbow_tap()
    elif key == 're':
        r_elbow_tap()
    elif key == 'lw':
        l_wrist_tap()
    elif key == 'rw': 
        r_wrist_tap()
    elif key == 'trap': 
        trap_muscle_tap()
    elif key == 'lat':
        lat_muscle_tap()
    elif key == 'stop':
        motors_off()

    motors_off()

#disconnecting glove
glove.disconnect()