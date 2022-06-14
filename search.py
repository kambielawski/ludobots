import os

# from hillclimber import HillClimber
from parallelHillClimber import ParallelHillClimber
import constants as c

def Get_Constants():
    return {
        'generations': c.NUMBER_OF_GENERATIONS,
        'population_size': c.POPULATION_SIZE
    }

# hc = HillClimber()
hc = ParallelHillClimber(Get_Constants())
hc.Evolve()
hc.Show_Best()



