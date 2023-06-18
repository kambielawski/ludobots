import argparse
import pickle

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 

from robot import Robot
from simulation import Simulation
from plotting.run_plotter import RunPlotter
import numpy as np
import matplotlib.pyplot as plt


'''
USAGE: 
- generate two Simulation() object pickles using sim.Pickle_Sim('pf_file_name.pkl')
- execute this file with those two file names as args:
    - python3 compare_log_plots.py sim1.pkl sim2.pkl
'''

dir_random = './best_robots/random_robots'
dir_empowered = './best_robots/empowered_only'
dir_displacement = './best_robots/displacement_only'

display_map = {
    './best_robots/random_robots': {'name': 'Random', 'color': 'red'},
    './best_robots/empowered_only': {'name': 'Empowered', 'color': 'blue'},
    './best_robots/displacement_only': {'name': 'Displacement', 'color': 'green'}
}

treatments = [dir_random, dir_empowered, dir_displacement]

sims = {t: [] for t in treatments}

SAVE_PATH = 'sa_pairs_save.pkl'
if os.path.exists(f'./{SAVE_PATH}'):
    with open(SAVE_PATH, 'rb') as pf:
        ranksizes = pickle.load(pf)
else:
    # Simulate and store simulations
    for dir in treatments:
        print(f'Simulating {dir}')
        for file in os.listdir(dir):
            os.system(f'python3 simulate.py DIRECT 0 {dir}/{file} ./robots/body_quadruped.urdf')
            with open('transient.pkl', 'rb') as pf:
                sim = pickle.load(pf)
                sims[dir].append(sim)

    # Create sensor/action pairs and rank sizes
    ranksizes = {t: [] for t in treatments}
    for dir in sims:
        for sim in sims[dir]:
            robot = sim.robots[0]
            pairs = {}
            for a in robot.actionz:
                for s in robot.sensorz:
                    pair = (a,s)
                    if pair in pairs:
                        pairs[pair] += 1
                    else:
                        pairs[pair] = 1

            size = sorted(pairs.values(), reverse=True)
            rank = range(1,len(size)+1)

            ranksizes[dir].append((rank, size))

    with open('sa_pairs_save.pkl', 'wb') as pf:
        pickle.dump(ranksizes, pf)
        print('SA pairs Pickle saved')

# Now combine and plot the confidence intervals
for t in ranksizes: # Random, empowered, displacement
    all_ys = []
    for i, (xs, ys) in enumerate(ranksizes[t]):
        all_ys.append(ys)
        if i == 0:
            plt.scatter(np.log10(xs), np.log10(ys), color=display_map[t]['color'], alpha=0.2, label=display_map[t]['name'])
        else:
            plt.scatter(np.log10(xs), np.log10(ys), color=display_map[t]['color'], alpha=0.05)
    print([len(ys) for ys in all_ys])
plt.xlabel('Log(Rank)')
plt.ylabel('Log(SA pair occurrences)')
plt.legend()
plt.title('Locomotion')
plt.show()
