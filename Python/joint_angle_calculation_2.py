# importing libraries
import numpy as np
import math as math
import matplotlib.pyplot as plt

# loading up data file
file = np.loadtxt('Val_Joint_Angles.csv', skiprows = 7, delimiter = ',')

# defining variables
time = file[:, 1]
wrist_x = file[:, 5]
wrist_y = file[:, 6]
wrist_z = file[:, 7]
elbow_x = file[:, 11]
elbow_y = file[:, 12]
elbow_z = file[:, 13]
shoulder_x = file[:, 2]
shoulder_y = file[:, 3]
shoulder_z = file[:, 4]
chest_x = file[:, 14]
chest_y = file[:, 15]
chest_z = file[:, 16]
hip_x = file[:, 8]
hip_y = file[:, 9]
hip_z = file[:, 10]

elbow_angle_list = list()
armpit_angle_list = list()
chest_shoulder_angle_list = list()

# making vectors and angles
for i in range(0, len(time)):
    # elbow to hand vector
    elbow_wrist_vector = list()

    elbow_wrist_x = wrist_x[i] - elbow_x[i]
    elbow_wrist_y = wrist_y[i] - elbow_y[i]
    elbow_wrist_z = wrist_z[i] - elbow_z[i]

    elbow_wrist_vector.append(elbow_wrist_x)
    elbow_wrist_vector.append(elbow_wrist_y)
    elbow_wrist_vector.append(elbow_wrist_z)


    # elbow to shoulder vector
    elbow_shoulder_vector = list()

    elbow_shoulder_x = shoulder_x[i] - elbow_x[i]
    elbow_shoulder_y = shoulder_y[i] - elbow_y[i]
    elbow_shoulder_z = shoulder_z[i] - elbow_z[i]

    elbow_shoulder_vector.append(elbow_shoulder_x)
    elbow_shoulder_vector.append(elbow_shoulder_y)
    elbow_shoulder_vector.append(elbow_shoulder_z)

    # chest to shoulder vector
    chest_shoulder_vector = list()

    chest_shoulder_x = chest_x[i] - shoulder_x[i]
    chest_shoulder_y = chest_y[i] - shoulder_y[i]
    chest_shoulder_z = chest_z[i] - shoulder_z[i]

    chest_shoulder_vector.append(chest_shoulder_x)
    chest_shoulder_vector.append(chest_shoulder_y)
    chest_shoulder_vector.append(chest_shoulder_z)

    # hip to shoulder vector
    shoulder_hip_vector = list()

    shoulder_hip_x = hip_x[i] - shoulder_x[i]
    shoulder_hip_y = hip_y[i] - shoulder_y[i]
    shoulder_hip_z = hip_z[i] - shoulder_z[i]

    shoulder_hip_vector.append(shoulder_hip_x)
    shoulder_hip_vector.append(shoulder_hip_y)
    shoulder_hip_vector.append(shoulder_hip_z)

    # finding vector magnitudes
    elbow_wrist_mag = math.sqrt((elbow_wrist_x ** 2) + (elbow_wrist_y ** 2) + (elbow_wrist_z ** 2))
    elbow_shoulder_mag = math.sqrt((elbow_shoulder_x ** 2) + (elbow_shoulder_y ** 2) + (elbow_shoulder_z ** 2))
    chest_shoulder_mag = math.sqrt((chest_shoulder_x ** 2) + (chest_shoulder_y ** 2) + (chest_shoulder_z ** 2))
    shoulder_hip_mag = math.sqrt((shoulder_hip_x ** 2) + (shoulder_hip_y ** 2) + (shoulder_hip_z ** 2))

    # finding elbow angle
    elbow_angle_dot_product = (elbow_wrist_vector[0] * elbow_shoulder_vector[0]) + (elbow_wrist_vector[1] * elbow_shoulder_vector[1]) + (elbow_wrist_vector[2] * elbow_shoulder_vector[2])
    elbow_angle = math.degrees(math.acos(elbow_angle_dot_product / (elbow_wrist_mag * elbow_shoulder_mag)))
    elbow_angle_list.append(elbow_angle)

    # finding angle of armpit
    armpit_angle_dot_product = (shoulder_hip_vector[0] * elbow_shoulder_vector[0]) + (shoulder_hip_vector[1] * elbow_shoulder_vector[1]) + (shoulder_hip_vector[2] * elbow_shoulder_vector[2])
    armpit_angle = math.degrees(math.acos(armpit_angle_dot_product / (shoulder_hip_mag * elbow_shoulder_mag)))
    armpit_angle_list.append(armpit_angle)

    # finding angle between arm and chest
    chest_shoulder_angle_dot_product = (chest_shoulder_vector[0] * elbow_shoulder_vector[0]) + (chest_shoulder_vector[1] * elbow_shoulder_vector[1]) + (chest_shoulder_vector[2] * elbow_shoulder_vector[2])
    chest_shoulder_angle = math.degrees(math.acos(chest_shoulder_angle_dot_product / (chest_shoulder_mag * elbow_shoulder_mag)))
    chest_shoulder_angle_list.append(chest_shoulder_angle)

# plotting
plt.plot(time, elbow_angle_list)
plt.xlabel('Time (s)')
plt.ylabel('Elbow Joint Angle (degrees)')
plt.title('Elbow Joint Angle Over Time')
plt.show()

plt.plot(time, armpit_angle_list)
plt.xlabel('Time (s)')
plt.ylabel('Armpit Joint Angle (degrees)')
plt.title('Armpit Joint Angle Over Time')
plt.show()

plt.plot(time, chest_shoulder_angle_list)
plt.xlabel('Time (s)')
plt.ylabel('Chest to Shoulder Joint Angle (degrees)')
plt.title('Chest to Shoulder Joint Angle Over Time')
plt.show()