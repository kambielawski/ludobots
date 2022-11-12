import os
import csv
from ast import literal_eval
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Plotter:
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

    def Write_Generation_Data_To_File(self, popsize, gens, obj, id=1):
        '''
        Writes generation data to a file (one generation per line)
        '''
        print(f'Creating file {self.dir}/data/gen_data_{id}.txt')
        f = open(f'{self.dir}/data/gen_data_{id}.txt', 'a')
        f.write(f'n={popsize},g={gens},obj={obj}\n')
        for g in self.populationOverTime:
            for individual in self.populationOverTime[g]:
                f.write(str(individual) + '|')
            f.write('\n')

    def Print_Top_Fitness(self):
        if self.objective == 'tri_fitness':
            keyfunc = lambda x:x[2][1]
        elif self.objective == 'emp_fitness':
            keyfunc = lambda x:x[2]
        else:
            raise ValueError("Invalid objective")
        sortedRobots = sorted(self.populationOverTime[-1], key=keyfunc, reverse=True)
        print(sortedRobots[:10])

    '''
    Parses generation data into self.populationOverTime data structure
    from a given text file
    '''
    def Parse_Gen_Data(self, genDataFileName):
        f = open(genDataFileName, 'r')

        # parse first line to grab run information
        n, g, objective = [a.split('=')[1].strip('\n') for a in f.readline().split(',')]
        self.popSize = int(n)
        self.totalGens = int(g)
        self.objective = objective

        # parse & process remaining generation data
        lines = f.readlines()
        genTupleStrings = [line.split('|') for line in lines]
        # Filter out empty strings
        genTupleStrings = list(map(lambda gen: list(filter(lambda tup: tup != '\n', gen)), genTupleStrings))
        # Turn tuple strings into literal tuples
        self.populationOverTime = list(map(lambda gen: list(map(lambda tup: literal_eval(tup), gen)), genTupleStrings))

        return self.populationOverTime

    def Get_Population_Data(self):
        return self.populationOverTime

    # TODO: Separate empowerment & fitness plots
    def Rainbow_Waterfall_Plot(self, yaxis='fitness'):
        '''
        Use population data over time to track lineages
        '''
        if self.objective == 'tri_fitness' and yaxis == 'empowerment':
            raise ValueError("Can't plot empowerment under tri-fitness conditions")

        lineages = {} # Indexed by tuple (generation, root parent ID)

        # Setup lineages data structure
        for g, generation in enumerate(self.populationOverTime):
            for individual in generation:
                _, _, fitness, empowerment, lineage = individual

                # Select metric we're looking at
                if self.objective == 'tri_fitness':
                    metric = fitness[1]
                elif self.objective == 'emp_fitness':
                    if yaxis == 'fitness':
                        metric = fitness
                    elif yaxis == 'empowerment':
                        metric = empowerment

                if not metric:
                    raise ValueError("Invalid objective or yaxis value")
            
                if lineage in lineages:
                    # Only add to lineage list if fitness is higher for that gen
                    better_exists = False
                    for g_curr, m in lineages[lineage]:
                        if g == g_curr:
                            if empowerment > metric:
                                lineages[lineage].remove((g_curr, m))
                            else:
                                better_exists = True

                    # Add the current individual to the current max lineage
                    if better_exists == False:
                        lineages[lineage].append((g, metric))
                else:
                    lineages[lineage] = [(g, metric)]

        # Plot each lineage as a line
        for lineage in lineages: 
            plt.step(*zip(*lineages[lineage]))
        plt.title('Lineages (N={}, G={})'.format(self.popSize, self.totalGens))
        plt.xlabel('Generation')
        plt.ylabel('{}'.format((yaxis)))
        plt.savefig('./plots/rainbow_waterfall_{metric}_n{popsize}g{gens}_{objective}.png'
                    .format(metric=yaxis, popsize=self.popSize, gens=self.totalGens, objective=self.objective))

    def Plot_Pareto_Front_Size_From_File(self, pfSizeFileName):
        f = open(pfSizeFileName, 'r')
        nums = [int(line) for line in f.readlines()]
        x = range(1, len(nums) + 1)
        
        plt.scatter(x, nums)
        plt.xlabel('Generation')
        plt.ylabel('Pareto Front Size')
        plt.savefig('pfsize.png')

    def Plot_Pareto_Front_Size(self):
        plt.figure(self.fignum)
        self.fignum += 1

        plt.scatter(range(1,len(self.paretoFrontSizeOverTime)+1), self.paretoFrontSizeOverTime)
        plt.axhline(y=self.constants['target_population_size'], color='red', linestyle='dotted')
        plt.xlabel('Generation Number')
        plt.ylabel('Pareto front size')
        plt.title('Pareto Front Size over time')
        plt.savefig('./plotting/plots/pf_size_over_time.png')

    def Plot_Gen_Fitness(self):
        plt.figure(self.fignum)
        self.fignum += 1

        gen_fitness = [(g, i[2]) for g in self.populationOverTime for i in self.populationOverTime[g]]
        plt.scatter(*zip(*gen_fitness))
        plt.xlabel('Generation Number')
        plt.ylabel('Fitness (displacement)')
        plt.title('Generation vs. Fitness (G={g}, N={n})'.format(
                    g=self.constants['generations'], n=self.constants['target_population_size']))
        plt.savefig('./plotting/plots/gen_fitness.png')

    def Plot_Age_Fitness(self):
        plt.figure(self.fignum)
        self.fignum += 1
        
        age_fitness = [(i[1], i[2]) for g in self.populationOverTime for i in self.populationOverTime[g]]
        plt.scatter(*zip(*age_fitness))
        plt.xlabel('Age')
        plt.ylabel('Fitness (displacement)')
        plt.title('Age vs. Fitness (G={g}, N={n})'.format(
                    g=self.constants['generations'], n=self.constants['target_population_size']))
        print(os.getcwd())
        plt.savefig('./plotting/plots/age_fitness.png')

    def Plot_Gen_Fitness_PF(self):
        plt.figure(self.fignum)
        self.fignum += 1

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
        plt.savefig('./plotting/plots/gen_fitness_pf.png')

    def Plot_Age_Fitness_PF(self):
        plt.figure(self.fignum)
        self.fignum += 1
        
        age_fitness = [(i[1], i[2]) for g in self.populationOverTime for i in self.populationOverTime[g]]
        pf_points = [(i[1], i[2]) for g in self.paretoFrontOverTime for i in self.paretoFrontOverTime[g]]
        plt.scatter(*zip(*age_fitness), label="Individuals")
        plt.scatter(*zip(*pf_points), label="Pareto Front Individuals")
        plt.xlabel('Age')
        plt.ylabel('Fitness (displacement)')
        plt.title('Age vs. Fitness, Pareto Front (G={g}, N={n})'.format(g=self.constants['generations'], n=self.constants['target_population_size']))
        plt.legend()
        plt.savefig('./plotting/plots/age_fitness_pf.png')