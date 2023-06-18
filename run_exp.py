import os
import argparse
from experiment import Experiment

############# ARGUMENT PARSING #############

parser = argparse.ArgumentParser()
parser.add_argument('--dir', required=False, default='', help='Experiment ID')
parser.add_argument('--exp', required=False, default='', help='Experiment file')
args = parser.parse_args()

############# ERROR CHECKING #############

# Either an experiment directory XOR an experiment file needs to be specified
if (not args.dir and not args.exp) or (args.dir and args.exp):
    raise OSError('Either an experiment directory OR an experiment file needs to be specified.')

# An experiment directory, if specified, needs to exist
if args.dir and not os.path.exists(args.dir):
    raise ValueError('Can\'t find experiment "' + args.exp_id + '"')

# Experiments need to have an 'evo_runs.pickle' file if directory is specified
if args.dir and not os.path.exists(f'{args.dir}/evo_runs.pickle'):
    raise OSError('Experiment directory does not contain an evo_runs.pickle file')

# Check for existence of the experiment specification
if args.exp and not os.path.exists(args.exp):
    raise OSError(f'Experiment file {args.exp} does not exist')

############# RUN EXPERIMENT(S) #############

if args.dir:   # Continue running existing experiment
    exp = Experiment(args.dir)
elif args.exp: # Start new experiment with experiment specification file
    exp = Experiment(None, args.exp)

g = 1
while True:
    print(f'\n\n========== \n Generation {g} \n ==========\n\n')
    exp.Run_One_Generation()
    g += 1

