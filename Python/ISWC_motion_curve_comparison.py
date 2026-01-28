# the purpose of this code is to compare motion curves

# importing libraries
import os
import numpy as np
import math as math
import matplotlib.pyplot as plt

# creating a function
def elbow_angle_calculation(filename):
    # loading the data
    # build a path relative to this script so the function works from any cwd
    base_dir = os.path.dirname(__file__)
    filepath = os.path.join(base_dir, "Sammy_MOCAP_Manipulated", filename)
    # use genfromtxt to handle empty cells and fill them with 0.0
    try:
        raw_data = np.genfromtxt(filepath, skip_header=7, delimiter=',', filling_values=0.0)
    except OSError:
        # helpful error if file is missing
        raise FileNotFoundError(f"Data file not found: {filepath}")

    # handle empty files or unexpected shapes returned by genfromtxt
    if raw_data is None or raw_data.size == 0:
        # return empty time and angle array for this file
        return np.array([]), np.array([])
    if raw_data.ndim == 1:
        # single row -> make it 2D so indexing works; if too few columns, treat as empty
        if raw_data.size < 10:
            return np.array([]), np.array([])
        raw_data = raw_data.reshape(1, -1)
    # if there are fewer columns than expected, pad with zeros
    if raw_data.ndim == 2 and raw_data.shape[1] < 10:
        cols = raw_data.shape[1]
        new = np.zeros((raw_data.shape[0], 10))
        new[:, :cols] = raw_data
        raw_data = new

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
        # construct vectors from coordinates (empty cells were filled with 0.0 above)
        elbow_hand_x = elbow_x[i] - hand_x[i]
        elbow_hand_y = elbow_y[i] - hand_y[i]
        elbow_hand_z = elbow_z[i] - hand_z[i]

        elbow_shoulder_x = elbow_x[i] - shoulder_x[i]
        elbow_shoulder_y = elbow_y[i] - shoulder_y[i]
        elbow_shoulder_z = elbow_z[i] - shoulder_z[i]

        elbow_hand_vector_mag = math.sqrt((elbow_hand_x ** 2) + (elbow_hand_y ** 2) + (elbow_hand_z ** 2))
        elbow_shoulder_vector_mag = math.sqrt(
            (elbow_shoulder_x ** 2) + (elbow_shoulder_y ** 2) + (elbow_shoulder_z ** 2))

        # handle cases where one or both vectors have zero length (e.g., missing markers)
        if elbow_hand_vector_mag == 0 or elbow_shoulder_vector_mag == 0:
            angle_degrees = 0.0
        else:
            dot_product = (elbow_hand_x * elbow_shoulder_x) + (elbow_hand_y * elbow_shoulder_y) + (elbow_hand_z * elbow_shoulder_z)
            denom = elbow_hand_vector_mag * elbow_shoulder_vector_mag
            cos_theta = dot_product / denom
            # clamp to valid domain for acos to avoid numerical errors
            cos_theta = max(-1.0, min(1.0, cos_theta))
            angle_radians = math.acos(cos_theta)
            angle_degrees = math.degrees(angle_radians)

        angles_list.append(angle_degrees)

    # convert angles list to numpy array for consistent plotting
    return time, np.array(angles_list)

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
plots_dir = os.path.join(os.path.dirname(__file__), 'plots')
os.makedirs(plots_dir, exist_ok=True)
plt.savefig(os.path.join(plots_dir, 'lateral_pulldowns_good.png'))
plt.close()

# plotting with variable data as well as 'good' trials
plt.plot(s_lp_1_time, s_lp_1_ea, label='Trial 1')
plt.plot(s_lp_2_time, s_lp_2_ea, label='Trial 2')
plt.plot(s_lp_3_time, s_lp_3_ea, label='Trial 3')
if getattr(s_lp_v_time, 'size', 0) > 0:
    plt.plot(s_lp_v_time, s_lp_v_ea, label='Variable Trial')
else:
    print('Warning: Sammy_LatPulls_Variable.csv contained no data; skipping variable trial on lateral pulldowns plot')
plt.xlabel('Time (s)')
plt.ylabel('Elbow Joint Angle (degrees)')
plt.title('Lateral Pull Downs')
plt.legend()
plt.savefig(os.path.join(plots_dir, 'lateral_pulldowns_with_variable.png'))
plt.close()

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
plt.savefig(os.path.join(plots_dir, 'macarena.png'))
plt.close()

# use function to get time and elbow angles list for each trial of the bent over rows
[s_r_1_time, s_r_1_ea] = elbow_angle_calculation('Sammy_Rows_1.csv')
[s_r_2_time, s_r_2_ea] = elbow_angle_calculation('Sammy_Rows_2.csv')
[s_r_3_time, s_r_3_ea] = elbow_angle_calculation('Sammy_Rows_3.csv')
[s_r_v_time, s_r_v_ea] = elbow_angle_calculation('Sammy_Rows_Variable.csv')

# plotting 'good' trials of bent over rows
plt.plot(s_r_1_time, s_r_1_ea, label='Trial 1')
plt.plot(s_r_2_time, s_r_2_ea, label='Trial 2')
plt.plot(s_r_3_time, s_r_3_ea, label='Trial 3')
plt.xlabel('Time (s)')
plt.ylabel('Elbow Joint Angle (degrees)')
plt.title('Bent Over Rows')
plt.legend()
plt.savefig(os.path.join(plots_dir, 'rows_good.png'))
plt.close()

# plotting 'good' and variable trial of bent over rows
plt.plot(s_r_1_time, s_r_1_ea, label='Trial 1')
plt.plot(s_r_2_time, s_r_2_ea, label='Trial 2')
plt.plot(s_r_3_time, s_r_3_ea, label='Trial 3')
if getattr(s_r_v_time, 'size', 0) > 0:
    plt.plot(s_r_v_time, s_r_v_ea, label='Variable Trial')
else:
    print('Warning: Sammy_Rows_Variable.csv contained no data; skipping variable trial on rows plot')
plt.xlabel('Time (s)')
plt.ylabel('Elbow Joint Angle (degrees)')
plt.title('Bent Over Rows')
plt.legend()
plt.savefig(os.path.join(plots_dir, 'rows_with_variable.png'))
plt.close()

# use function to get time and elbow angles list for each trial of the woodchops
[s_w_1_time, s_w_1_ea] = elbow_angle_calculation('Sammy_Woodchops_1.csv')
[s_w_2_time, s_w_2_ea] = elbow_angle_calculation('Sammy_Woodchops_2.csv')
[s_w_3_time, s_w_3_ea] = elbow_angle_calculation('Sammy_Woodchops_3.csv')
[s_w_v_time, s_w_v_ea] = elbow_angle_calculation('Sammy_Woodchops_Variable.csv')

# plotting 'good' trials of woodchops
plt.plot(s_w_1_time, s_w_1_ea, label='Trial 1')
plt.plot(s_w_2_time, s_w_2_ea, label='Trial 2')
plt.plot(s_w_3_time, s_w_3_ea, label='Trial 3')
plt.xlabel('Time (s)')
plt.ylabel('Elbow Joint Angle (degrees)')
plt.title('Woodchops')
plt.legend()
plt.savefig(os.path.join(plots_dir, 'woodchops_good.png'))
plt.close()

# plotting 'good' and variable trials of woodchops
plt.plot(s_w_1_time, s_w_1_ea, label='Trial 1')
plt.plot(s_w_2_time, s_w_2_ea, label='Trial 2')
plt.plot(s_w_3_time, s_w_3_ea, label='Trial 3')
if getattr(s_w_v_time, 'size', 0) > 0:
    plt.plot(s_w_v_time, s_w_v_ea, label='Variable Trial')
else:
    print('Warning: Sammy_Woodchops_Variable.csv contained no data; skipping variable trial on woodchops plot')
plt.xlabel('Time (s)')
plt.ylabel('Elbow Joint Angle (degrees)')
plt.title('Woodchops')
plt.legend()
plt.savefig(os.path.join(plots_dir, 'woodchops_with_variable.png'))
plt.close()


# using dynamic time warping to compare trials
