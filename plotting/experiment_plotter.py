import pickle
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st

class ExperimentPlotter:
    def __init__(self):
        self.experiments = {}

    def Load_Experiment(self, pickle_file_path, exp_name):
        with open(pickle_file_path, 'rb') as pickle_file:
            runs = pickle.load(pickle_file)
            self.experiments[exp_name] = runs

    def Plot(self, experiments, objectives=['displacement']):
        pass

    def Plot_Combined_Top_Fitness(self, experiment_names):
        for exp_name in experiment_names:
            self.Plot_Top_Fitness_CI(self.experiments[exp_name])
        plt.legend()
        plt.show()

    def Plot_Top_Fitness_CI(self, experiment):
        for treatment in experiment.keys():
            means, confs = self.Get_Top_Fitness_Mean_CI(experiment[treatment])
            plt.plot(range(len(means)), means, label=treatment)
            plt.fill_between(range(len(means)), means-confs, means+confs, alpha=0.3)

        plt.xlabel('Generation')
        plt.ylabel('Top fitness (95% CI)')
    
    def Get_Top_Fitness_Mean_CI(self, runs):
        # Create a list of all runs' series of top fitness individuals
        top_fitness = []
        for afpo in runs:
            top_fit_series = runs[afpo].history.Get_Top_Metric_Over_Generations('displacement')
            top_fitness.append(top_fit_series)

        # The average top fitness for each generation, over all N evo runs
        grouped_by_generation = list(zip(*top_fitness))
        top_fitness_averages = [np.mean([x[1] for x in gen]) for gen in grouped_by_generation]

        confidence_intervals = [st.t.interval(0.95, len(gen)-1, loc=top_fitness_averages[i], scale=st.sem(gen)) for i, gen in enumerate(grouped_by_generation)]
        confidence_intervals = [(ci[1][1] - ci[0][1])/2 for ci in confidence_intervals]
        
        return np.array(top_fitness_averages), np.array(confidence_intervals)
