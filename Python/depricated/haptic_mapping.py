import numpy as np
import math



if __name__ == '__main__':
    C = np.array([0,0,0]) #Current Pos
    G = np.array([1,0,1]) # Goal Pos
    motors = np.array([np.array([0,0,1]), np.array([0,0,-1]), np.array([0,-1,0]), np.array([0,1,0])]) 
    intense = find_intensity_array(C, G, motors)