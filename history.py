"""Stores data from a single run of an experiment."""
import matplotlib.pyplot as plt

class RunHistory:
    """Stores data from a single run of an experiment."""
    def __init__(self, constants=None, dir='.'):
        self.constants = {} if constants==None else constants
        self.populationOverTime = {}
        self.paretoFrontOverTime = {}
        self.paretoFrontSizeOverTime = []
        self.fignum = 0
        self.dir = dir

    def Population_Data(self, genNumber, population):
        """Stores the population at a given generation number."""
        self.populationOverTime[genNumber] = population

    def Pareto_Front_Data(self, genNumber, paretoFront):
        """Stores the pareto front at a given generation number."""
        self.paretoFrontOverTime[genNumber] = paretoFront
        self.paretoFrontSizeOverTime.append(len(paretoFront))

    def Write_Pareto_Front_File(self):
        """Writes the pareto front data to a file."""
        f = open(f'{self.dir}/data/pf_size.txt', 'w')
        for n in self.paretoFrontSizeOverTime:
            f.write(str(n) + '\n')

    def Get_Top_Metric_Over_Generations(self, selection_metric):
        """Returns the top fitness value from each generation."""
        keyfunc = lambda x: x['metrics'][selection_metric]

        best = []
        for gen, pop in self.populationOverTime.items():
            best_metric = sorted(pop, key=keyfunc, reverse=True)
            best.append((gen, keyfunc(best_metric[0])))
        return best

    def Get_Population_Data(self):
        """Returns the population data."""
        return self.populationOverTime

    def Plot_Pareto_Front_Size(self):
        """Plots the pareto front size over time."""
        plt.figure(self.fignum)
        self.fignum += 1

        plt.scatter(range(1,len(self.paretoFrontSizeOverTime)+1), self.paretoFrontSizeOverTime)
        plt.axhline(y=self.constants['target_population_size'], color='red', linestyle='dotted')
        plt.xlabel('Generation Number')
        plt.ylabel('Pareto front size')
        plt.title('Pareto Front Size over time')
        plt.savefig('./plotting/plots/pf_size_over_time.png')
