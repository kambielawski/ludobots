import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 

import numpy as np
import pickle
import argparse
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--dir', required=True, type=str)
args = parser.parse_args()

def empowerment_distribution(runs):
    all_populations_empowerments = []
    for run in runs:
        for individual in runs[run].population.values():
            # if not individual.Has_Been_Simulated():
            all_populations_empowerments.append(individual.Get_Empowerment())

    print(all_populations_empowerments)
    plt.hist(all_populations_empowerments)
    plt.show()

with open(f'{args.dir}/evo_runs.pickle', 'rb') as pickleFile:
    evo_runs = pickle.load(pickleFile)

t1,t2 = evo_runs.keys()
print(t1, t2)
print(list(evo_runs[t1][1].population.values())[1].objectives)
print(list(evo_runs[t2][1].population.values())[1].objectives)
exit(1)

empowerment_distribution(evo_runs[t1])
empowerment_distribution(evo_runs[t2])