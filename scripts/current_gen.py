import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from ageFitnessPareto import AgeFitnessPareto

import pickle
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--dir')
args = parser.parse_args()

with open(args.dir + '/evo_runs.pickle', 'rb') as pf:
    evo_runs = pickle.load(pf)

for t in evo_runs:
    for run in evo_runs[t]:
        print('Current generation: ' + str(evo_runs[t][run].currentGen))