# the purpose of this code is to compare motion curves

# importing libraries
import numpy as np
import math as math
import matplotlib.pyplot as plt

# creating a function
def elbow_angle_calculation(filename):
    # loading the data
    filepath = "Sammy_MOCAP_Manipulated/" + filename
    raw_data = np.loadtxt(filepath, skiprows=7, delimiter=',')

    # defining variables
    time = raw_data[:, 0]
    shoulder_x = raw_data[:, 1]
    shoulder_y = raw_data[:, 2]
    shoulder_z = raw_data[:, 3]
    elbow_x = raw_data[:, 4]
    elbow_y = raw_data[:, 5]
    elbow_z = raw_data[:, 6]
    hand_x = raw_data[:, 7]
    hand_y = raw_data[:, 8]
    hand_z = raw_data[:, 9]

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

# use function to get time and elbow angles list for each trial of lateral pull downs
[s_lp_1_time, s_lp_1_ea] = elbow_angle_calculation('Sammy_LatPulls_1.csv')
[s_lp_2_time, s_lp_2_ea] = elbow_angle_calculation('Sammy_LatPulls_2.csv')
[s_lp_3_time, s_lp_3_ea] = elbow_angle_calculation('Sammy_LatPulls_3.csv')
[s_lp_v_time, s_lp_v_ea] = elbow_angle_calculation('Sammy_LatPulls_Variable.csv')

# plotting with only 'good' trials
plt.plot(s_lp_1_time, s_lp_1_ea, label='Trial 1')
plt.plot(s_lp_2_time, s_lp_2_ea, label='Trial 2')
plt.plot(s_lp_3_time, s_lp_3_ea, label='Trial 3')
plt.xlabel('Time (s)')
plt.ylabel('Elbow Joint Angle (degrees)')
plt.title('Lateral Pull Downs')
plt.legend()
plt.show()

# plotting with variable data as well as 'good' trials
plt.plot(s_lp_1_time, s_lp_1_ea, label='Trial 1')
plt.plot(s_lp_2_time, s_lp_2_ea, label='Trial 2')
plt.plot(s_lp_3_time, s_lp_3_ea, label='Trial 3')
plt.plot(s_lp_v_time, s_lp_v_ea, label='Variable Trial')
plt.xlabel('Time (s)')
plt.ylabel('Elbow Joint Angle (degrees)')
plt.title('Lateral Pull Downs')
plt.legend()
plt.show()

# use function to get time and elbow angles list for each trial of macarena
[s_mac_000_time, s_mac_000_ea] = elbow_angle_calculation('Sammy_Macarena_000.csv')
[s_mac_001_time, s_mac_001_ea] = elbow_angle_calculation('Sammy_Macarena_001.csv')
[s_mac_002_time, s_mac_002_ea] = elbow_angle_calculation('Sammy_Macarena_002.csv')
[s_mac_003_time, s_mac_003_ea] = elbow_angle_calculation('Sammy_Macarena_003.csv')

# plotting macarena curves
plt.plot(s_mac_000_time, s_mac_000_ea)
plt.plot(s_mac_001_time, s_mac_001_ea)
plt.plot(s_mac_002_time, s_mac_002_ea)
plt.plot(s_mac_003_time, s_mac_003_ea)
plt.xlabel('Time (s)')
plt.ylabel('Elbow Joint Angle (degrees)')
plt.title('Macarena')
plt.show()

# use function to get time and elbow angles list for each trial of the bent over rows
[s_r_1_time, s_r_1_ea] = elbow_angle_calculation('Sammy_Rows_1.csv')
[s_r_2_time, s_r_2_ea] = elbow_angle_calculation('Sammy_Rows_2.csv')
[s_r_3_time, s_r_3_ea] = elbow_angle_calculation('Sammy_Rows_3.csv')
#[s_r_v_time, s_r_v_ea] = elbow_angle_calculation('Sammy_Rows_Variable.csv')

# plotting 'good' trials of bent over rows
plt.plot(s_r_1_time, s_r_1_ea, label='Trial 1')
plt.plot(s_r_2_time, s_r_2_ea, label='Trial 2')
plt.plot(s_r_3_time, s_r_3_ea, label='Trial 3')
plt.xlabel('Time (s)')
plt.ylabel('Elbow Joint Angle (degrees)')
plt.title('Bent Over Rows')
plt.legend()
plt.show()

# plotting 'good' and variable trial of bent over rows
plt.plot(s_r_1_time, s_r_1_ea, label='Trial 1')
plt.plot(s_r_2_time, s_r_2_ea, label='Trial 2')
plt.plot(s_r_3_time, s_r_3_ea, label='Trial 3')
#plt.plot(s_r_v_time, s_r_v_ea, label='Variable Trial')
plt.xlabel('Time (s)')
plt.ylabel('Elbow Joint Angle (degrees)')
plt.title('Bent Over Rows')
plt.legend()
plt.show()

# use function to get time and elbow angles list for each trial of the woodchops
#[s_w_1_time, s_w_1_ea] = elbow_angle_calculation('Sammy_Woodchops_1.csv')
#[s_w_2_time, s_w_2_ea] = elbow_angle_calculation('Sammy_Woodchops_2.csv')
#[s_w_3_time, s_w_3_ea] = elbow_angle_calculation('Sammy_Woodchops_3.csv')
#[s_w_v_time, s_w_v_ea] = elbow_angle_calculation('Sammy_Woodchops_Variable.csv')

# plotting 'good' trials of woodchops
#plt.plot(s_w_1_time, s_w_1_ea, label='Trial 1')
#plt.plot(s_w_2_time, s_w_2_ea, label='Trial 2')
#plt.plot(s_w_3_time, s_w_3_ea, label='Trial 3')
#plt.xlabel('Time (s)')
#plt.ylabel('Elbow Joint Angle (degrees)')
#plt.title('Woodchops')
#plt.legend()
#plt.show()

# plotting 'good' and variable trials of woodchops
#plt.plot(s_w_1_time, s_w_1_ea, label='Trial 1')
#plt.plot(s_w_2_time, s_w_2_ea, label='Trial 2')
#plt.plot(s_w_3_time, s_w_3_ea, label='Trial 3')
#plt.plot(s_w_v_time, s_w_v_ea, label='Variable Trial')
#plt.xlabel('Time (s)')
#plt.ylabel('Elbow Joint Angle (degrees)')
#plt.title('Woodchops')
#plt.legend()
#plt.show()

