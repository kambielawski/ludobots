import pickle
import argparse
from ageFitnessPareto import AgeFitnessPareto

parser = argparse.ArgumentParser()
parser.add_argument('--dir')
args = parser.parse_args()

with open(args.dir + '/evo_runs.pickle', 'rb') as pf:
    evo_runs = pickle.load(pf)

print('Current generation: ' + str(evo_runs['emp_fitness'][0].currentGen))