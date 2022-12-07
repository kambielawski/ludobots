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

parser = argparse.ArgumentParser()
parser.add_argument('--dir', required=True, type=str)
args = parser.parse_args()

def getAverageTopFitness(runs):
    # t2_runs = evo_runs[t2]
    t1_top_fits = []

    for afpo in runs:
        top_fit_series = runs[afpo].history.Get_Top_Fitness_Over_Generations()
        t1_top_fits.append(top_fit_series)

    # The average top fitness for each generation, over all N evo runs
    grouped_by_generation = list(zip(*t1_top_fits))
    print(grouped_by_generation[0])
    top_fitness_averages = [np.mean([x[1] for x in gen]) for gen in grouped_by_generation]
    confidence_intervals = [st.t.interval(0.95, len(gen)-1, loc=top_fitness_averages[i], scale=st.sem(gen)) for i, gen in enumerate(grouped_by_generation)]
    confidence_intervals = [(ci[1][1] - ci[0][1])/2 for ci in confidence_intervals]
    return np.array(top_fitness_averages), np.array(confidence_intervals)

def getAverageTopEmpowerment(runs):
    # t2_runs = evo_runs[t2]
    t1_top_emp = []

    for afpo in runs:
        top_emp_series = runs[afpo].history.Get_Top_Empowerment_Over_Generations()
        t1_top_emp.append(top_emp_series)

    # The average top fitness for each generation, over all N evo runs
    grouped_by_generation = list(zip(*t1_top_emp))
    print(grouped_by_generation[0])
    top_emp_averages = [np.mean([x[1] for x in gen]) for gen in grouped_by_generation]
    confidence_intervals = [st.t.interval(0.95, len(gen)-1, loc=top_emp_averages[i], scale=st.sem(gen)) for i, gen in enumerate(grouped_by_generation)]
    confidence_intervals = [(ci[1][1] - ci[0][1])/2 for ci in confidence_intervals]
    return np.array(top_emp_averages), np.array(confidence_intervals)

def paretoFrontLinePlot(evo_runs):
    t1, t2 = evo_runs.keys()

    # The average top fitness for each generation, over all N evo runs
    t1_avg_best, t1_conf_int = getAverageTopFitness(evo_runs[t1])
    t2_avg_best, t2_conf_int= getAverageTopFitness(evo_runs[t2])

    # Plotting
    plt.plot(range(len(t1_avg_best)), t1_avg_best, label=t1, color='Red')
    plt.plot(range(len(t2_avg_best)), t2_avg_best, label=t2, color='Blue')
    plt.fill_between(range(len(t1_avg_best)), t1_avg_best-t1_conf_int, t1_avg_best+t1_conf_int, color='Red', alpha=0.3)
    plt.fill_between(range(len(t2_avg_best)), t2_avg_best-t2_conf_int, t2_avg_best+t2_conf_int, color='Blue', alpha=0.3)
    plt.xlabel('Generation')
    plt.ylabel('Top fitness (95% CI)')
    plt.legend()
    plt.savefig(f'{args.dir}/data/95CI_gen{len(t1_avg_best)}_{time.time()}.png')
    plt.show()

def empowermentPlot(evo_runs):
    t1, t2 = evo_runs.keys()

    # The average top fitness for each generation, over all N evo runs
    t1_avg_best, t1_conf_int = getAverageTopEmpowerment(evo_runs[t1])
    t2_avg_best, t2_conf_int= getAverageTopEmpowerment(evo_runs[t2])

    # Plotting
    plt.plot(range(len(t1_avg_best)), t1_avg_best, label=t1, color='Red')
    plt.plot(range(len(t2_avg_best)), t2_avg_best, label=t2, color='Blue')
    plt.fill_between(range(len(t1_avg_best)), t1_avg_best-t1_conf_int, t1_avg_best+t1_conf_int, color='Red', alpha=0.3)
    plt.fill_between(range(len(t2_avg_best)), t2_avg_best-t2_conf_int, t2_avg_best+t2_conf_int, color='Blue', alpha=0.3)
    plt.xlabel('Generation')
    plt.ylabel('Top Empowerment (95% CI)')
    plt.legend()
    plt.savefig(f'{args.dir}/data/95CI_gen{len(t1_avg_best)}_{time.time()}.png')
    plt.show()

with open(f'{args.dir}/evo_runs.pickle', 'rb') as pickleFile:
    evo_runs = pickle.load(pickleFile)

paretoFrontLinePlot(evo_runs)
# empowermentPlot(evo_runs)