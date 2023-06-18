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

# Grab directory and metric to extract the robots from
parser = argparse.ArgumentParser()
parser.add_argument('dir', type=str)
parser.add_argument('metric', type=str)
args = parser.parse_args()

# Open up the directory and load the pickled runs
with open(f'{args.dir}/evo_runs.pickle', 'rb') as pf:
    evo_runs = pickle.load(pf)
    k = list(evo_runs.keys())[0]
    evo_runs = evo_runs[k]
    current_gen = evo_runs[0].currentGen

SAVE_DIRECTORY = f'top_{args.metric}_{current_gen}'

# Save the best of the bunch
for i, run in enumerate(evo_runs):
    print(f'=============\nrun {i}\n===============')
    evo_runs[run].Evolve_One_Generation() # AFPO object
    evo_runs[run].Save_Best(save_dir=SAVE_DIRECTORY, metric=args.metric)