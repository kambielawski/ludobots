import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Plotter:
    def __init__(self, constants):
        self.constants = constants
        self.populationOverTime = {}
        self.paretoFrontOverTime = {}

    def Population_Data(self, genNumber, population):
        self.populationOverTime[genNumber] = population

    def Pareto_Front_Data(self, genNumber, paretoFront):
        self.paretoFrontOverTime[genNumber] = paretoFront

    def Plot_Gen_Fitness(self):
        plt.figure(1)
        gen_fitness = [(g, i[2]) for g in self.populationOverTime for i in self.populationOverTime[g]]
        plt.scatter(*zip(*gen_fitness))
        plt.xlabel('Generation Number')
        plt.ylabel('Fitness (displacement)')
        plt.title('Generation vs. Fitness (G={g}, N={n})'.format(
                    g=self.constants['generations'], n=self.constants['target_population_size']))
        plt.savefig('./plots/gen_fitness.png')

    def Plot_Age_Fitness(self):
        plt.figure(2)
        age_fitness = [(i[1], i[2]) for g in self.populationOverTime for i in self.populationOverTime[g]]
        plt.scatter(*zip(*age_fitness))
        plt.xlabel('Age')
        plt.ylabel('Fitness (displacement)')
        plt.title('Age vs. Fitness (G={g}, N={n})'.format(
                    g=self.constants['generations'], n=self.constants['target_population_size']))
        plt.savefig('./plots/age_fitness.png')

    def Plot_Gen_Fitness_PF(self):
        plt.figure(3)
        gen_fitness = [(g, i[2]) for g in self.populationOverTime for i in self.populationOverTime[g]]
        pf_points = [(g, i[2]) for g in self.paretoFrontOverTime for i in self.paretoFrontOverTime[g]]
        # for g in self.paretoFrontOverTime:
        #     for i in self.paretoFrontOverTime[g]:
        #         plt.annotate(str(i[1]) + ', e:' + str(round(i[3], 3)), xy=(g, i[2]))
        plt.scatter(*zip(*gen_fitness), label="Individuals")
        plt.scatter(*zip(*pf_points), label="Pareto Front Individuals")
        plt.xlabel('Generation Number')
        plt.ylabel('Fitness (displacement)')
        plt.title('Generation vs. Fitness, Pareto Front (G={g}, N={n})'.format(
                    g=self.constants['generations'], n=self.constants['target_population_size']))
        plt.legend()
        plt.savefig('./plots/gen_fitness_pf.png')

    def Plot_Age_Fitness_PF(self):
        plt.figure(4)
        age_fitness = [(i[1], i[2]) for g in self.populationOverTime for i in self.populationOverTime[g]]
        pf_points = [(i[1], i[2]) for g in self.paretoFrontOverTime for i in self.paretoFrontOverTime[g]]
        plt.scatter(*zip(*age_fitness), label="Individuals")
        plt.scatter(*zip(*pf_points), label="Pareto Front Individuals")
        plt.xlabel('Age')
        plt.ylabel('Fitness (displacement)')
        plt.title('Age vs. Fitness, Pareto Front (G={g}, N={n})'.format(g=self.constants['generations'], n=self.constants['target_population_size']))
        plt.legend()
        plt.savefig('./plots/age_fitness_pf.png')