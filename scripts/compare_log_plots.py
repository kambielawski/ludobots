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

parser = argparse.ArgumentParser()
parser.add_argument("sims", type=str)

args = parser.parse_args()

sim_strs = args.sims.split(',')

sims = dict()
for sim_str in sim_strs:
    with open(sim_str, 'rb') as pickle_file:
        sim = pickle.load(pickle_file)
    sims[sim_str] = sim

# ONLY ONE ROBOT! 
ranksizes = {}
for sim in sims:
    robot = sims[sim].robots[0]
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
    ranksizes[sim] = (rank, size)

for sim in ranksizes:
    rank, size = ranksizes[sim]
    plt.scatter(np.log10(rank), np.log10(size),label=sim, alpha=0.3)

plt.xlabel('Log(rank)')
plt.ylabel('Log(size)')
plt.legend()
plt.show()