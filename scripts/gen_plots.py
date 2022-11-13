import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from ageFitnessPareto import AgeFitnessPareto

import pickle
import argparse
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--dir', required=True, type=str)
args = parser.parse_args()

def generateGenerationFiles(evo_runs):
    t1, t2 = evo_runs.keys()
    t1_runs = evo_runs[t1]
    t2_runs = evo_runs[t2]
    all_runs = t1_runs | t2_runs
    print(all_runs)

    for run_id in all_runs:
        run = all_runs[run_id]
        run.plotter.Write_Generation_Data_To_File(run.targetPopSize, 
                                                run.currentGen, 
                                                run.objective, 
                                                id=run_id)
        
def paretoFrontLinePlot(evo_runs):
    pass


with open(f'{args.dir}/evo_runs.pickle', 'rb') as pickleFile:
    evo_runs = pickle.load(pickleFile)

generateGenerationFiles(evo_runs)