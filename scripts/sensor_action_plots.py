import pickle
from collections import Counter

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 

import numpy as np
import matplotlib.pyplot as plt

def Simulate_Brain(brain_file, body_file='./robots/body_quadruped.urdf'):
    # Simulate and store simulations
    print(f'Simulating brain from file {brain_file}')
    os.system(f'python3 simulate.py DIRECT 0 {brain_file} {body_file} --pickle_sim True')
    with open('transient.pkl', 'rb') as pf:
        sim = pickle.load(pf)

    # Create sensor/action pairs and rank sizes
    robot = sim.robots[0]
    sa_pairs = [(a, s) for a in robot.actionz for s in robot.sensorz]

    return sa_pairs


    # pair_counts = Counter(pairs)

    # size = sorted(pair_counts.values(), reverse=True)
    # rank = range(1,len(size)+1)

    # ranksizes.append((rank, size))

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
    


# sa_pairs_dis = Simulate_Directory('./experiments/May26_02_54_quadruped_displacement-empowerment_mA_n30p100w500/top_displacement_95')
# sa_pairs_emp = Simulate_Directory('./experiments/May26_02_54_quadruped_displacement-empowerment_mA_n30p100w500/top_empowerment_188')
sa_pairs_disemp = Simulate_Directory('experiments/May31_07_29_quadruped_boxdisplacement-empowerment_mA_n30p100w500/top_boxdisplacement_210')
sa_pairs_dis = Simulate_Directory('experiments/May28_09_05_quadruped_boxdisplacement_mA_n30p100w500/top_boxdisplacement_405')
sa_pairs_rand = Simulate_Directory('./best_robots/random_robots')
Plot_Brains(sa_pairs_dis, color='blue', label='Displacement')
Plot_Brains(sa_pairs_disemp, color='red', label='Displacement+Empowerment')
Plot_Brains(sa_pairs_rand, color='green', label='Random')
plt.title('Evolved Quadruped Sensor/Action Pairs, Box Displacement')
plt.legend()
plt.show()