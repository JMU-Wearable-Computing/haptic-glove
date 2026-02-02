# importing libraries
import numpy as np
import math as math
import matplotlib.pyplot as plt

# loading up the file
file = np.loadtxt('skeleton_joint_angle2.csv', skiprows=7, delimiter = ',')

# defining variables
time = file[:, 1]
r_shoulder_x = file[:, 5]
r_shoulder_y = file[:, 6]
r_shoulder_z = file[:, 7]
r_elbow_x = file[:, 8]
r_elbow_y = file[:, 9]
r_elbow_z = file[:, 10]
r_wrist_x = file[:, 11]
r_wrist_y = file[:, 12]
r_wrist_z = file[:, 13]
l_shoulder_x = file[:, 2]
l_shoulder_y = file[:, 3]
l_shoulder_z = file[:, 4]
r_front_hip_x = file[:, 17]
r_front_hip_y = file[:, 18]
r_front_hip_z = file[:, 19]
r_back_hip_x = file[:, 14]
r_back_hip_y = file[:, 15]
r_back_hip_z = file[:, 16]

elbow_angles_list = list()
armpit_angles_list = list()
chest_shoulder_angles_list = list()

# making vectors
for i in range(0, len(time)):
    # finding average of hip markers
    r_hip_x = (r_front_hip_x[i] + r_back_hip_x[i]) / 2
    r_hip_y = (r_front_hip_y[i] + r_back_hip_y[i]) / 2
    r_hip_z = (r_front_hip_z[i] + r_back_hip_z[i]) / 2

    # for elbow to wrist
    elbow_hand_vector = list()

    elbow_wrist_x = r_elbow_x[i] - r_wrist_x[i]
    elbow_wrist_y = r_elbow_y[i] - r_wrist_y[i]
    elbow_wrist_z = r_elbow_z[i] - r_wrist_z[i]

    elbow_hand_vector.append(elbow_wrist_x)
    elbow_hand_vector.append(elbow_wrist_y)
    elbow_hand_vector.append(elbow_wrist_z)

    # for elbow to shoulder
    elbow_shoulder_vector = list()

    elbow_shoulder_x = r_elbow_x[i] - r_shoulder_x[i]
    elbow_shoulder_y = r_elbow_y[i] - r_shoulder_y[i]
    elbow_shoulder_z = r_elbow_z[i] - r_shoulder_z[i]

    elbow_shoulder_vector.append(elbow_shoulder_x)
    elbow_shoulder_vector.append(elbow_shoulder_y)
    elbow_shoulder_vector.append(elbow_shoulder_z)

    # for left shoulder to right shoulder vector
    l_r_shoulder_vector = list()

    l_r_shoulder_x = l_shoulder_x[i] - r_shoulder_x[i]
    l_r_shoulder_y = l_shoulder_y[i] - r_shoulder_y[i]
    l_r_shoulder_z = l_shoulder_z[i] - r_shoulder_z[i]

    l_r_shoulder_vector.append(l_r_shoulder_x)
    l_r_shoulder_vector.append(l_r_shoulder_y)
    l_r_shoulder_vector.append(l_r_shoulder_z)

    # for hip to shoulder
    hip_shoulder_vector = list()

    hip_shoulder_x = r_hip_x[i] - r_shoulder_x[i]
    hip_shoulder_y = r_hip_y[i] - r_shoulder_y[i]
    hip_shoulder_z = r_hip_z[i] - r_shoulder_z[i]

    hip_shoulder_vector.append(hip_shoulder_x)
    hip_shoulder_vector.append(hip_shoulder_y)
    hip_shoulder_vector.append(hip_shoulder_z)


    # determining vector magnitudes
    elbow_wrist_mag = math.sqrt((elbow_wrist_x ** 2) + (elbow_wrist_y ** 2) + (elbow_wrist_z ** 2))
    elbow_shoulder_mag = math.sqrt((elbow_shoulder_x ** 2) + (elbow_shoulder_y ** 2) + (elbow_shoulder_z ** 2))
    l_r_shoulder_mag = math.sqrt((l_r_shoulder_x ** 2) + (l_r_shoulder_y ** 2) + (l_r_shoulder_z ** 2))
    hip_shoulder_mag = math.sqrt((hip_shoulder_x ** 2) + (hip_shoulder_y ** 2) + (hip_shoulder_z ** 2))

    # finding the angles
    dot_product_elbow = (elbow_wrist_x * elbow_shoulder_x) + (elbow_wrist_y * elbow_shoulder_y) + (elbow_wrist_z * elbow_shoulder_z)
    elbow_angle = math.degrees(math.acos(dot_product_elbow / (elbow_wrist_mag * elbow_shoulder_mag)))

    dot_product_armpit = (hip_shoulder_x * elbow_shoulder_x) + (hip_shoulder_y * elbow_shoulder_y) + (hip_shoulder_z * elbow_shoulder_z)
    armpit_angle = math.degrees(math.acos(dot_product_armpit / (hip_shoulder_mag * elbow_shoulder_mag)))

    dot_product_chest_shoulder = (l_r_shoulder_x * elbow_shoulder_x) + (l_r_shoulder_y * elbow_shoulder_y) + (l_r_shoulder_z * elbow_shoulder_z)
    chest_shoulder_angle = math.degrees(math.acos(dot_product_armpit / (l_r_shoulder_mag * elbow_shoulder_mag)))

    # adding angle to angle list
    elbow_angles_list.append(elbow_angle)
    armpit_angles_list.append(armpit_angle)
    chest_shoulder_angles_list.append(chest_shoulder_angle)

# plotting
plt.plot(time, elbow_angles_list)
plt.xlabel('Time (s)')
plt.ylabel('Elbow Joint Angle (degrees)')
plt.title('Elbow Joint Angle Over Time')
plt.show()

plt.plot(time, armpit_angles_list)
plt.xlabel('Time (s)')
plt.ylabel('Armpit Joint Angle (degrees)')
plt.title('Armpit Joint Angle Over Time')
plt.show()

plt.plot(time, chest_shoulder_angles_list)
plt.xlabel('Time (s)')
plt.ylabel('Chest to Shoulder Joint Angle (degrees)')
plt.title('Chest to Shoulder Joint Angle Over Time')
plt.show()

# TODO
# empty cells are being taken as spaces which can't be converted into numbers. retake data and see what happens