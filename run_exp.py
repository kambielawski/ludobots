import os
import argparse
from experiment import Experiment

parser = argparse.ArgumentParser()
parser.add_argument('-experiment_directory', required=False, default='', help='Experiment ID')
args = parser.parse_args()

# An experiment directory, if specified, needs to exist
if args.experiment_directory and not os.path.exists(args.experiment_directory):
    raise ValueError('Can\'t find experiment "' + args.exp_id + '"')

# Experiments need to have an 'evo_runs.pickle' file
if args.experiment_directory and not os.path.exists(f'{args.experiment_directory}/evo_runs.pickle'):
    raise OSError('Experiment directory does not contain an evo_runs.pickle file')

exp = Experiment(args.experiment_directory)

g = 1
while True:
    print(f'\n\n========== \n Generation {g} \n ==========\n\n')
    exp.Run_One_Generation()
    t = exp.Run_T_Test()
    # Check if t is cool, blow up the universe if it is 