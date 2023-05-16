import os
import argparse
from experiment import Experiment

############# ARGUMENT PARSING #############

parser = argparse.ArgumentParser()
parser.add_argument('--dir', required=False, default='', help='Experiment ID')
args = parser.parse_args()

# An experiment directory, if specified, needs to exist
if args.dir and not os.path.exists(args.dir):
    raise ValueError('Can\'t find experiment "' + args.exp_id + '"')

# Experiments need to have an 'evo_runs.pickle' file if directory is specified
if args.dir and not os.path.exists(f'{args.dir}/evo_runs.pickle'):
    raise OSError('Experiment directory does not contain an evo_runs.pickle file')

############# RUN EXPERIMENT(S) #############

exp = Experiment(args.dir)

g = 1
while True:
    print(f'\n\n========== \n Generation {g} \n ==========\n\n')
    exp.Run_One_Generation()
    g += 1