import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from ageFitnessPareto import AgeFitnessPareto
import numpy as np

import scipy.stats as st
import pickle
import matplotlib.pyplot as plt

COLORS = ['red', 'blue', 'yellow', 'green', 'orange', 'purple']

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

def plotMetric95CI(experiment_dirs, metric):
    # Load each evo_runs object from pickled file in experiment directory
    loaded_data = []
    for exp_dir in experiment_dirs:
        print(exp_dir)
        with open(f'{exp_dir}/evo_runs.pickle', 'rb') as pickleFile:
            evo_runs = pickle.load(pickleFile)
            loaded_data.append(evo_runs)

    # Plot each line from each loaded data
    for i, evo_runs in enumerate(loaded_data):
        exp_label = list(loaded_data[i].keys())[0]
        t1_avg_best, t1_conf_int = getMetric95CI(evo_runs[exp_label], metric)
        # Plotting
        plt.plot(range(len(t1_avg_best)), t1_avg_best, label=exp_label, color=COLORS[i])
        plt.fill_between(range(len(t1_avg_best)), t1_avg_best-t1_conf_int, t1_avg_best+t1_conf_int, color=COLORS[i], alpha=0.3)
    
    plt.title(metric)
    plt.xlabel('Generation')
    plt.ylabel(f'{metric} (95% CI)')
    plt.legend()
    # plt.savefig(f'{args.dir}/plots/95CI_gen{len(t1_avg_best)}_fit_{time.time()}.png')
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

# plotWindowSizes([
#     'experiments/exp_Mar03_05_05',
#     'experiments/exp_Mar01_10_08',
#     'experiments/exp_Mar04_11_21',
# ], 'boxdisplacement')

plotMetric95CI(['./experiments/Jun19_06_32_biped_boxdisplacement_mA_n30p100w500',
                './experiments/Jun20_09_22_biped_boxdisplacement-empowerment_mA_n30p100w500'], 'boxdisplacement')
