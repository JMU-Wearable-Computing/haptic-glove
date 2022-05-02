import numpy as np
import math

def find_distance(vector1, vector2, normalized=False):
    if normalized:
        vector1 = vector1 / np.linalg.norm(vector1)
        vector2 = vector2 / np.linalg.norm(vector2)
    diff = vector1 - vector2
    distance = np.linalg.norm(diff)
    return distance

def orient_motor(motor_position, acceleration):
    #TODO
    print("Not implemented")

def map_to_range(x, in_min, in_max, out_min, out_max, bounded=False):
    output = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if bounded:
        if output < out_min:
            output = out_min
        if output > out_max:
            output = out_max
    return output

def reverse_map_to_range(x, in_min, in_max, out_min, out_max, bounded=False):
    output = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if bounded:
        if output > out_min:
            output = out_min
        if output < out_max:
            output = out_max
    return output


def find_intensity_array(current_pos, goal_pos, motor_positions, accel = np.array([0.0,0.0,0.0]), norm = True):
    U = goal_pos - current_pos
    D = np.linalg.norm(U)
    
    if norm:
        if ( np.linalg.norm(current_pos) != 0):
            current_pos = current_pos / np.linalg.norm(current_pos)
        if ( np.linalg.norm(goal_pos) != 0):
            goal_pos = goal_pos / np.linalg.norm(goal_pos)
        if ( np.linalg.norm(accel) != 0):
            accel = accel / np.linalg.norm(accel)

    #print(current_pos, goal_pos, accel)

    U = goal_pos - current_pos - accel
    #print(f'Displacement vector: {U}')

    #D = np.linalg.norm(U)
    #print(f'Distance from goal: {D}')

    I = map_to_range(D, 0, 1, 150, 255,  bounded=True)
    #print(f'Distance adjusted to range: {I}')

    motor_distance = [0.0,0.0,0.0,0.0]
    mapped = [0.0,0.0,0.0,0.0]

    for i in range(0, len(motor_positions)):
        motor_distance[i] = find_distance(U, motor_positions[i], normalized=norm)
        mapped[i] = reverse_map_to_range(motor_distance[i], 0.0, math.sqrt(2), 1, .59, bounded=True)

    mapped = np.array(mapped)

    #print(f'Motor distances : {motor_distance}')
    #print(f'Motor intensity proportions: {mapped}')

    intensity = np.array(I * mapped).astype(int)
    #print(f'Motor intensity array: {intensity}')
    return intensity

if __name__ == '__main__':

    C = np.array([0,0,0]) #Current Pos
    G = np.array([1,0,1]) # Goal Pos
    motors = np.array([np.array([0,0,1]), np.array([0,0,-1]), np.array([0,-1,0]), np.array([0,1,0])]) 

    intense = find_intensity_array(C, G, motors)