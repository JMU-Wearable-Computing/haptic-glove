import numpy as np
import math

#Find the normalized distance between two vectors
def find_distance(vector1, vector2, normalized=False):
    if normalized:
        vector1 = vector1 / np.linalg.norm(vector1)
        vector2 = vector2 / np.linalg.norm(vector2)
    diff = vector1 - vector2
    distance = np.linalg.norm(diff)
    return distance

#Map a variable with expected range in_min-in_max to range out_min-out_max
#Works like the map function in C++
def map_to_range(x, in_min, in_max, out_min, out_max, bounded=False):
    output = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if bounded:
        if output < out_min:
            output = out_min
        if output > out_max:
            output = out_max
    return output

#Like map but with an inverse relationship
def reverse_map_to_range(x, in_min, in_max, out_min, out_max, bounded=False):
    output = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if bounded:
        if output > out_min:
            output = out_min
        if output < out_max:
            output = out_max
    return output

#Generate array of vibration intensity for motors
#Uses current position of glove, the goal position, postions of motors on hand and acceleration (acceleration not implemented yet)
def find_intensity_array(current_pos, goal_pos, motor_positions, accel = np.array([0.0,0.0,0.0]), norm = True):
    #Normalize all vectors
    if norm:
        if ( np.linalg.norm(current_pos) != 0):
            current_pos = current_pos / np.linalg.norm(current_pos)
        if ( np.linalg.norm(goal_pos) != 0):
            goal_pos = goal_pos / np.linalg.norm(goal_pos)
        if ( np.linalg.norm(accel) != 0):
            accel = accel / np.linalg.norm(accel)

    #Calculate displacement to goal and find distance
    U = goal_pos - current_pos - accel
    D = np.linalg.norm(U)

    #Map the distance value to motor command values
    #I is the maximum that a single motor can be driven
    #I will be proportionaly distributed across motors that are closest to the displacement vector
    I = map_to_range(D, 0, 1, 150, 255,  bounded=True)

    motor_distance = [0.0,0.0,0.0,0.0]
    mapped = [0.0,0.0,0.0,0.0]

    #Find the distance between the displacement vector and motors
    #Calculate distributions of vibration to each motor
    for i in range(0, len(motor_positions)):
        motor_distance[i] = find_distance(U, motor_positions[i], normalized=norm)
        #Bound the proportion of vibration sent to a single motor
        mapped[i] = reverse_map_to_range(motor_distance[i], 0.0, math.sqrt(2), 1, .59, bounded=True)

    #Cast distributions of vibration to motors to a numpy array
    mapped = np.array(mapped)
    #Scale distribution by the global maximum vibration
    intensity = np.array(I * mapped).astype(int)
    return intensity

if __name__ == '__main__':
    C = np.array([0,0,0]) #Current Pos
    G = np.array([1,0,1]) # Goal Pos
    motors = np.array([np.array([0,0,1]), np.array([0,0,-1]), np.array([0,-1,0]), np.array([0,1,0])]) 
    intense = find_intensity_array(C, G, motors)