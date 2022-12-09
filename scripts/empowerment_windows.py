import os
import time
import numpy as np
import matplotlib.pyplot as plt
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

brain_file = './best_robots/quadruped/pf_brain_1111946350251605504.nndf'

def Run_Subprocess(window_size):
    sp = subprocess.Popen(['python3', 'simulate.py', 
                            'DIRECT', 
                            '0', 
                            brain_file, 
                            '../robots/body_quadruped', 
                            '--empowerment_window_size', str(window_size)],
                            stdout=subprocess.PIPE)

    stdout, stderr = sp.communicate()
    sp.wait()
    out_str = stdout.decode('utf-8')
    fitness_metrics = re.search('\(.+\)', out_str)[0].strip('()').split(' ')
    selection_metrics = {
        'displacement': float(fitness_metrics[0]),
        'empowerment': float(fitness_metrics[1]),
        'first_half_displacement': float(fitness_metrics[2]),
        'second_half_displacement': float(fitness_metrics[3]),
        'random': float(fitness_metrics[4])
    }
    return window_size, selection_metrics


emp_data = []
try:
    with ThreadPoolExecutor() as executor:
        futures = []
        # Start threads
        for window_size in np.arange(6,500,2):
            f = executor.submit(Run_Subprocess, window_size)
            futures.append(f)
        # Wait for all threads to be finished running
        while not all([f.done() for f in futures]):
            time.sleep(0.1)
        # Done executing, grab results
        print('done!')
        for f in futures:
            window_size, metrics = f.result()
            emp_data.append((window_size, metrics['empowerment']))
except Exception as err:
    os.system(f'echo {err} >> error_log.txt')

# emp = selection_metrics['empowerment']
# emp_data.append((window_size, emp))

plt.scatter(*zip(*emp_data))
plt.xlabel('History Length')
plt.ylabel('Empowerment')
plt.title('Coarse-grained actions, NPEET entropy estimation')
plt.savefig('empowerment_window_max.png')
print(emp_data)
    
