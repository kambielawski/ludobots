import sys
import os
import time
import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv) < 2: 
    print('Usage: python3 empowerment_window.py <brain file> <body file>')
    exit(1)
else:
    brain_file = sys.argv[1]

emp_data = []
for window_size in np.arange(6, 500, 2):
    os.system('cd .. && python3 simulate.py DIRECT 0 ' + brain_file + ' body_quadruped.urdf ' + str(window_size))

    while not os.path.exists('../fitness_0.txt'):
        time.sleep(0.01)

    f_file = open('../fitness_0.txt')
    fitness, emp = f_file.readlines()[0].split(' ')
    emp = float(emp)
    emp_data.append((window_size, emp))
    f_file.close()

plt.scatter(*zip(*emp_data))
plt.xlabel('Window Size')
plt.ylabel('Average Empowerment')
plt.title('Coarse-grained actions, NPEET entropy estimation')
plt.savefig('empowerment_window.png')
print(emp_data)
    
