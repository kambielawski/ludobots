import os

# from hillclimber import HillClimber
from parallelHillClimber import ParallelHillClimber

# hc = HillClimber()
hc = ParallelHillClimber()
hc.Evolve()
hc.Show_Best()



