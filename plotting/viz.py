import csv
from ast import literal_eval
import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self):
        pass

    def Parse_Gen_Data(self, genDataFileName):
        f = open(genDataFileName, 'r')
        lines = f.readlines()
        genTupleStrings = [line.split('|') for line in lines]
        # Filter out empty strings
        genTupleStrings = list(map(lambda gen: list(filter(lambda tup: tup != '\n', gen)), genTupleStrings))
        # Turn tuple strings into literal tuples
        self.populationOverTime = list(map(lambda gen: list(map(lambda tup: literal_eval(tup), gen)), genTupleStrings))

    def Rainbow_Waterfall_Plot(self):
        '''
        Use population data over time to track lineages
        '''
        lineages = {} # Indexed by tuple (generation, root parent ID)

        # Setup lineages data structure
        for g, generation in enumerate(self.populationOverTime):
            for individual in generation:
                _, _, _, emp, lineage = individual
                if lineage in lineages:
                    # Only add to lineage list if fitness is higher for that gen
                    better_exists = False
                    for g_curr, e_curr in lineages[lineage]:
                        if g == g_curr:
                            if emp > e_curr:
                                lineages[lineage].remove((g_curr, e_curr))
                            else:
                                better_exists = True
                    if better_exists == False:
                        lineages[lineage].append((g, emp))
                else:
                    lineages[lineage] = [(g, emp)]

        # Plot each lineage as a line
        for lineage in lineages: 
            plt.step(*zip(*lineages[lineage]))
        plt.title('Lineages (N=25, G=120)')
        plt.xlabel('Generation')
        plt.ylabel('Empowerment')
        plt.savefig('./plots/rainbow_waterfall_emp_fitness.png')


    def Pareto_Front_Size_Plot(self, pfSizeFileName):
        f = open(pfSizeFileName, 'r')
        nums = [int(line) for line in f.readlines()]
        x = range(1, len(nums) + 1)
        
        plt.scatter(x, nums)
        plt.xlabel('Generation')
        plt.ylabel('Pareto Front Size')
        plt.savefig('pfsize.png')
            
    def Read_Run_File(self, runFileName):
        f = open(runFileName, 'r')
        reader = csv.reader(f, delimiter='|')
