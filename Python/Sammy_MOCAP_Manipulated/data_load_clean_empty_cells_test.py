# testing function to clean up data and remove rows with empty cells for data analysis

# importing libaries
import numpy as np
import matplotlib.pyplot as plt
import math as math

def elbow_angle_calculation(filename):
    # loading the data
    original_file = open(filename)
    filepath = filename
    raw_data = np.loadtxt(filepath, skiprows=7, delimiter=',')
    # clearing data of empty cells
    non_empty_rows_indices = np.array([i for i, row in enumerate(raw_data) if all(cell != '' for cell in row)])
    cleaned_data = raw_data[non_empty_rows_indices]

    # defining variables
    time = cleaned_data[:, 0]
    shoulder_x = cleaned_data[:, 1]
    shoulder_y = cleaned_data[:, 2]
    shoulder_z = cleaned_data[:, 3]
    elbow_x = cleaned_data[:, 4]
    elbow_y = cleaned_data[:, 5]
    elbow_z = cleaned_data[:, 6]
    hand_x = cleaned_data[:, 7]
    hand_y = cleaned_data[:, 8]
    hand_z = cleaned_data[:, 9]

    # creating an empty list for elbow angle values
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
        elbow_shoulder_vector_mag = math.sqrt(
            (elbow_shoulder_x ** 2) + (elbow_shoulder_y ** 2) + (elbow_shoulder_z ** 2))

        dot_product = (elbow_hand_vector[0] * elbow_shoulder_vector[0]) + (
                    elbow_hand_vector[1] * elbow_shoulder_vector[1]) + (elbow_hand_vector[2] * elbow_shoulder_vector[2])

        angle_radians = math.acos(dot_product / (elbow_hand_vector_mag * elbow_shoulder_vector_mag))
        angle_degrees = math.degrees(angle_radians)
        angles_list.append(angle_degrees)

    return time, angles_list

[s_r_v_time, s_r_v_ea] = elbow_angle_calculation('Sammy_Rows_Variable.csv')
plt.plot(s_r_v_time, s_r_v_ea, label='Variable Data')
plt.xlabel('Time (s)')
plt.ylabel('Elbow Angle (degrees)')
plt.title('Elbow Angle Over Time for Variable Rows')
plt.legend()
plt.show()