import pandas as pd
from hapticdriver import HapticDriver
import time

# reading file
skeleton_data = pd.read_csv('quadrant_skeleton.csv')

# defining variables
time = skeleton_data.iloc[:, [0]]
x = skeleton_data.iloc[:, [1]]
y = skeleton_data.iloc[:, [2]]
z = skeleton_data.iloc[:, [3]]

# converting variable lists into numpy
time_np = time.to_numpy()
x_np = x.to_numpy()
y_np = y.to_numpy()
z_np = z.to_numpy()

# connecting glove
glove = HapticDriver(device_id=10, port=8888, acceleration=False, verbose=True)

glove.connect()

# creating loop
for i in range(len(x_np)):
    if x_np[i] > 0 and z_np[i] > 0:
        glove.set_motors(['E', 1, 0, 0, 0, 0, 0, 0, 0])
        time.sleep(1)
    elif x_np[i] > 0 and z_np[i] < 0:
        glove.set_motors(['E', 0, 1, 0, 0, 0, 0, 0, 0])
        time.sleep(1)
    elif x_np[i] < 0 and z_np[i] < 0:
        glove.set_motors(['E', 0, 0, 1, 0, 0, 0, 0, 0])
        time.sleep(1)
    elif x_np[i] < 0 and z_np[i] > 0:
        glove.set_motors(['E', 0, 0, 0, 1, 0, 0, 0, 0])
        time.sleep(1)

# disconnect from glove
glove.disconnect