import os

# from hillclimber import HillClimber
from parallelHillClimber import ParallelHillClimber
from ageFitnessPareto import AgeFitnessPareto
import constants as c

def Get_Constants_AFPO():
    return {
<<<<<<< HEAD
        'generations': 800,
=======
        'generations': 5,
>>>>>>> 13c10d0ea6d223f0acc8c1a9dc287363a56c4148
        'target_population_size': 200,
        'batching': True,
        'batch_size': 10
    }

def Get_Constants_HillClimber():
    return {
        'generations': c.NUMBER_OF_GENERATIONS,
        'population_size': c.POPULATION_SIZE
    }

# Age-Fitness Pareto Optimization
afpo = AgeFitnessPareto(Get_Constants_AFPO())
afpo.Evolve()
# afpo.Show_Best()

# # HILLCLIMBER
# hc = ParallelHillClimber(Get_Constants_HillClimber())
# hc.Evolve()
# hc.Show_Best()



