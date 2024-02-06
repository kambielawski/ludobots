import argparse
import pickle

from experiment import Trial

############# ARGUMENT PARSING #############

parser = argparse.ArgumentParser()
parser.add_argument('--file', required=True, default='', help='File path for pickled AFPO object')
args = parser.parse_args()

############# RUN EXPERIMENT(S) #############

with open(args.dir, 'rb') as pickle_file:
    trial : Trial = pickle.load(pickle_file)

trial.Run()
