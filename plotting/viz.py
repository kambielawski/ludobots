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
