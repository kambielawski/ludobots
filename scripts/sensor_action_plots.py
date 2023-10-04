import pickle
from collections import Counter
import argparse

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 

import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('plot_type', type=str)
parser.add_argument('brain_file', type=str)
parser.add_argument('body_file', type=str)
parser.add_argument('world_file', type=str)

args = parser.parse_args()
body_file = args.body_file
brain_file = args.brain_file
world_file = args.world_file

def Simulate_Brain(brain_file, 
                   body_file='./robots/body_quadruped.urdf', 
                   world_file='./task_environments/world.sdf'):
    # Simulate and store simulations
    print(f'Simulating brain from file {brain_file}')
    os.system(f'python3 simulate.py DIRECT 0 {brain_file} {body_file} --objects_file {world_file} --pickle_sim True')
    with open('transient.pkl', 'rb') as pf:
        sim = pickle.load(pf)

    # Create sensor/action pairs and rank sizes
    robot = sim.robots[0]
    return robot.actionz, robot.sensorz

def Simulate_Directory(dir, body_file='./robots/body_quadruped.urdf'):
    all_sa_pairs = {}
    for file in os.listdir(dir):
        sa_pairs = Simulate_Brain(f'{dir}/{file}', body_file)
        all_sa_pairs[file] = sa_pairs

    return all_sa_pairs

def Plot_Brains(all_sa_pairs, color='red', label=None):
    print(f'color: {color}, label: {label}')
    ranksizes = []
    # Count and aggregate into rank/sizes
    for brain in all_sa_pairs:
        print(brain)
        pair_counts = Counter(all_sa_pairs[brain])
        size = sorted(pair_counts.values(), reverse=True)
        rank = range(1,len(size)+1)
        ranksizes.append((rank, size))

    # Plot rank sizes
    print(len(ranksizes))
    for i, (rank, size) in enumerate(ranksizes):
        if label and i == 0:
            plt.plot(np.log10(rank),np.log10(size), color=color, alpha=0.3, label=label)
        else:
            plt.plot(np.log10(rank),np.log10(size), color=color, alpha=0.3)
    plt.xlabel('Log(Rank)')
    plt.ylabel('Log(Number of sensor/action pairs)')
    
def log_plot(data, xlabel, ylabel):
    counts = Counter(data)
    size = sorted(counts.values(), reverse=True)
    rank = range(1, len(size) + 1)
    plt.scatter(rank, size)
    # plt.scatter(np.log10(rank), np.log10(size))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

actions, sensors = Simulate_Brain(brain_file, body_file, world_file)
if args.plot_type == 'sa_pairs':
    sa_pairs = [(a, s) for a in actions for s in sensors]
    Plot_Brains({0: sa_pairs}, color='blue', label='')
elif args.plot_type == 'action':
    log_plot(actions, xlabel='Rank', ylabel='Number of actions')
elif args.plot_type == 'sensor':
    log_plot(sensors, xlabel='Rank', ylabel='Number of sensors')

plt.legend()
plt.show()