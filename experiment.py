import numpy as np
import time
import os

from parallelHillClimber import ParallelHillClimber
import constants as c

class Experiment:
    def __init__(self, expId):
        self.expId = expId
        self.xyVals = []
        self.trials = [(5, i) for i in range(2,7)]
        # self.trials = [(50,i) for i in range(2,21)]
        # self.trials = [(50, i) for i in range(2,50)]
        # self.trials = [(5,0)]

    def Run_One_Experiment(self, constants):
        start = time.clock_gettime(time.CLOCK_REALTIME)
        hc = ParallelHillClimber(constants)
        hc.Evolve()
        # hc.Show_Best()
        end = time.clock_gettime(time.CLOCK_REALTIME)
        runtime = (end-start)
        self.xyVals.append((constants['population_size'], runtime))
        self.Save_Values()

    def Run(self):
        for trial in self.trials:
            self.Run_One_Experiment({'generations': trial[0], 'population_size': trial[1]})

    def Save_Values(self):
        np.save('./data/exp_' + str(self.expId), self.xyVals)

exp = Experiment(2)
exp.Run()
os.system("python3 analyze.py ./data/exp_2.npy")
