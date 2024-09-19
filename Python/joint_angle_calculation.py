### purpose of this code is to calculate joint angles from motion capture data

#importing libraries
import numpy as np
import math as math

# loading up files
angle_data = np.loadtxt('joint_angle_test_data.csv', skiprows=7, delimiter=",")

# determining variables
time = angle_data[:, 0]
hand_x = angle_data[:, 7]
hand_y = angle_data[:, 8]
hand_z = angle_data[:, 9]
shoulder_x = angle_data[:, 1]
shoulder_y = angle_data[:, 2]
shoulder_z = angle_data[:, 3]
elbow_x = angle_data[:, 4]
elbow_y = angle_data[:, 5]
elbow_z = angle_data[:, 6]

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
    print(angle_degrees)


   # for j in range(0, 3):
       # dot_product = 0
       # multiply = elbow_hand_vector[j] * elbow_shoulder_vector[j]
       # dot_product = dot_product + multiply

        #angle_radians = math.acos(dot_product / (elbow_hand_vector_mag * elbow_shoulder_vector_mag))
        #angle_degrees = math.degrees(angle_radians)
        #print(angle_degrees)