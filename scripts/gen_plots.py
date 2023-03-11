import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from ageFitnessPareto import AgeFitnessPareto
import numpy as np

import scipy.stats as st
import pickle
import argparse
import matplotlib.pyplot as plt
import time

# TODO: generalize these functions to take any objective.

parser = argparse.ArgumentParser()
parser.add_argument('--dir', required=True, type=str)
args = parser.parse_args()

def getMetric95CI(runs, metric):
    best = []

    for afpo in runs:
        best_over_generations = runs[afpo].history.Get_Top_Metric_Over_Generations(metric)
        best.append(best_over_generations)

    grouped_by_generation = list(zip(*best))
    top_averages = [np.mean([x[1] for x in gen]) for gen in grouped_by_generation]
    confidence_intervals = [st.t.interval(0.95, len(gen)-1, loc=top_averages[i], scale=st.sem(gen)) for i, gen in enumerate(grouped_by_generation)]
    confidence_intervals = [(ci[1][1] - ci[0][1])/2 for ci in confidence_intervals]
    return np.array(top_averages), np.array(confidence_intervals)

def plotMetric95CI(evo_runs, metric):
    t1, t2 = evo_runs.keys()
    t1_avg_best, t1_conf_int = getMetric95CI(evo_runs[t1], metric)
    t2_avg_best, t2_conf_int= getMetric95CI(evo_runs[t2], metric)

    # Plotting
    plt.plot(range(len(t1_avg_best)), t1_avg_best, label=t1 + '_t1', color='Red')
    plt.plot(range(len(t2_avg_best)), t2_avg_best, label=t2 + '_t2', color='Blue')
    # plt.plot(range(len(t1_avg_best)), t1_avg_best, label='window_125', color='Red')
    # plt.plot(range(len(t2_avg_best)), t2_avg_best, label='window_500', color='Blue')
    plt.fill_between(range(len(t1_avg_best)), t1_avg_best-t1_conf_int, t1_avg_best+t1_conf_int, color='Red', alpha=0.3)
    plt.fill_between(range(len(t2_avg_best)), t2_avg_best-t2_conf_int, t2_avg_best+t2_conf_int, color='Blue', alpha=0.3)
    plt.title(metric)
    plt.xlabel('Generation')
    plt.ylabel(f'{metric} (95% CI)')
    plt.legend()
    plt.savefig(f'{args.dir}/plots/95CI_gen{len(t1_avg_best)}_fit_{time.time()}.png')
    plt.show()

def plotWindowSizes(experiments, metric):
    for exp in experiments:
        with open(f'{exp}/evo_runs.pickle', 'rb') as pickleFile:
            evo_runs = pickle.load(pickleFile)
            t1, t2 = evo_runs.keys()
            t1_avg_best, t1_conf_int = getMetric95CI(evo_runs[t1], metric)
            t2_avg_best, t2_conf_int= getMetric95CI(evo_runs[t2], metric)
            if exp == 'experiments/exp_Mar01_10_08':
                plt.plot(range(len(t1_avg_best)), t1_avg_best, label='window_125')
                plt.plot(range(len(t2_avg_best)), t2_avg_best, label='window_500')
            else:
                plt.plot(range(len(t1_avg_best)), t1_avg_best, label=t1)
                plt.plot(range(len(t2_avg_best)), t2_avg_best, label=t2)
            plt.fill_between(range(len(t1_avg_best)), t1_avg_best-t1_conf_int, t1_avg_best+t1_conf_int, color='Red', alpha=0.1)
            plt.fill_between(range(len(t2_avg_best)), t2_avg_best-t2_conf_int, t2_avg_best+t2_conf_int, color='Blue', alpha=0.1)
    plt.title(metric)
    plt.xlabel('Generation')
    plt.ylabel(f'{metric} (95% CI)')
    plt.legend()
    plt.savefig(f'./window_sizes.png')
    plt.show()

# with open(f'{args.dir}/evo_runs.pickle', 'rb') as pickleFile:
#     evo_runs = pickle.load(pickleFile)

plotWindowSizes([
    'experiments/exp_Mar03_05_05',
    'experiments/exp_Mar01_10_08',
    'experiments/exp_Mar04_11_21',
], 'box_displacement')

# boxDisplacementPlot(evo_runs)
# paretoFrontLinePlot(evo_runs)
# empowermentPlot(evo_runs)

# plotMetric95CI(evo_runs, 'empowerment')
# plotMetric95CI(evo_runs, 'displacement')
# plotMetric95CI(evo_runs, 'box_displacement')
# plotMetric95CI(evo_runs, 'first_half_box_displacement')
# plotMetric95CI(evo_runs, 'box_displacement')
