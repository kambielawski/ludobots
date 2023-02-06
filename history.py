import os
import csv
from ast import literal_eval
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class RunHistory:
    def __init__(self, constants=None, dir='.'):
        self.constants = {} if constants==None else constants
        self.populationOverTime = {}
        self.paretoFrontOverTime = {}
        self.paretoFrontSizeOverTime = []
        self.fignum = 0
        self.dir = dir

    def Population_Data(self, genNumber, population):
        self.populationOverTime[genNumber] = population

    def Pareto_Front_Data(self, genNumber, paretoFront):
        self.paretoFrontOverTime[genNumber] = paretoFront
        self.paretoFrontSizeOverTime.append(len(paretoFront))

    def Write_Pareto_Front_File(self):
        f = open(f'{self.dir}/data/pf_size.txt', 'w')
        for n in self.paretoFrontSizeOverTime:
            f.write(str(n) + '\n')

    def Get_Top_Fitness(self):
        keyfunc = lambda x: x[2]
        sortedRobots = sorted(self.populationOverTime[-1], key=keyfunc, reverse=True)
        return sortedRobots

    def Get_Top_Fitness_Over_Generations(self):
        keyfunc = lambda x:x['metrics']['displacement']

        best_fitness = []
        for gen in self.populationOverTime:
            best_fit = sorted(self.populationOverTime[gen], key=keyfunc, reverse=True)
            best_fitness.append((gen, keyfunc(best_fit[0])))
        return best_fitness

    def Get_Top_Empowerment_Over_Generations(self):
        keyfunc = lambda x: x['metrics']['empowerment']

        best_empowerment = []
        for gen in self.populationOverTime:
            best_emp = sorted(self.populationOverTime[gen], key=keyfunc, reverse=True)
            best_empowerment.append((gen, keyfunc(best_emp[0])))
        return best_empowerment

    def Get_Top_Metric_Over_Generations(self, selectionMetric):
        keyfunc = lambda x: x['metrics'][selectionMetric]

        best = []
        for gen in self.populationOverTime:
            best_metric = sorted(self.populationOverTime[gen], key=keyfunc, reverse=True)
            best.append((gen, keyfunc(best_metric[0])))
        return best

    def Get_Population_Data(self):
        return self.populationOverTime

    def Plot_Pareto_Front_Size(self):
        plt.figure(self.fignum)
        self.fignum += 1

        plt.scatter(range(1,len(self.paretoFrontSizeOverTime)+1), self.paretoFrontSizeOverTime)
        plt.axhline(y=self.constants['target_population_size'], color='red', linestyle='dotted')
        plt.xlabel('Generation Number')
        plt.ylabel('Pareto front size')
        plt.title('Pareto Front Size over time')
        plt.savefig('./plotting/plots/pf_size_over_time.png')
