### purpose of this code is to calculate joint angles from motion capture data

#importing libraries
import numpy as np
import math as math
import matplotlib.pyplot as plt

# loading up files
angle_data = np.loadtxt('joint_angle_test_data_006.csv', skiprows=7, delimiter=",")

# determining variables
time = angle_data[:, 1]
hand_x = angle_data[:, 5]
hand_y = angle_data[:, 6]
hand_z = angle_data[:, 7]
shoulder_x = angle_data[:, 8]
shoulder_y = angle_data[:, 9]
shoulder_z = angle_data[:, 10]
elbow_x = angle_data[:, 2]
elbow_y = angle_data[:, 3]
elbow_z = angle_data[:, 4]

angles_list = list()

# making vectors
for i in range(0, len(time)):
    elbow_hand_vector = list()

    elbow_hand_x = elbow_x[i] - hand_x[i]
    elbow_hand_y = elbow_y[i] - hand_y[i]
    elbow_hand_z = elbow_z[i] - hand_z[i]

    elbow_hand_vector.append(elbow_hand_x)
    elbow_hand_vector.append(elbow_hand_y)
    elbow_hand_vector.append(elbow_hand_z)

    elbow_shoulder_vector = list()

    elbow_shoulder_x = elbow_x[i] - shoulder_x[i]
    elbow_shoulder_y = elbow_y[i] - shoulder_y[i]
    elbow_shoulder_z = elbow_z[i] - shoulder_z[i]

    elbow_shoulder_vector.append(elbow_shoulder_x)
    elbow_shoulder_vector.append(elbow_shoulder_y)
    elbow_shoulder_vector.append(elbow_shoulder_z)

    elbow_hand_vector_mag = math.sqrt((elbow_hand_x ** 2) + (elbow_hand_y ** 2) + (elbow_hand_z ** 2))
    elbow_shoulder_vector_mag = math.sqrt((elbow_shoulder_x ** 2) + (elbow_shoulder_y ** 2) + (elbow_shoulder_z ** 2))

    dot_product = (elbow_hand_vector[0] * elbow_shoulder_vector[0]) + (elbow_hand_vector[1] * elbow_shoulder_vector[1]) + (elbow_hand_vector[2] * elbow_shoulder_vector[2])

    angle_radians = math.acos(dot_product / (elbow_hand_vector_mag * elbow_shoulder_vector_mag))
    angle_degrees = math.degrees(angle_radians)
    angles_list.append(angle_degrees)

# plotting
plt.plot(time, angles_list)
plt.xlabel('Time (s)')
plt.ylabel('Elbow Joint Angle (degrees)')
plt.title('Elbow Joint Angle Over Time')
plt.show()