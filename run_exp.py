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

# while True:
exp.Run_One_Generation()