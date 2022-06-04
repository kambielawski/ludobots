import numpy as np
import copy

from solution import Solution
import constants as c

class HillClimber:
    def __init__(self):
        self.parent = Solution()

    def Evolve(self):
        self.parent.Evaluate()
        for currentGeneration in range(c.NUMBER_OF_GENERATIONS):
            self.Spawn()
            self.Mutate()
            self.child.Evaluate()
            self.Print_Fitness()
            self.Select()

    def Show_Best(self):
        self.parent.Evaluate(runMode="GUI")
        print("Best fitness: ", self.parent.fitness)

    def Spawn(self):
        self.child = copy.deepcopy(self.parent)

    def Mutate(self):
        self.child.Mutate()

    def Select(self):
        if self.child.fitness < self.parent.fitness:
            self.parent = self.child
    
    def Print_Fitness(self):
        print("Parent fitness: ", self.parent.fitness, "; Child fitness: ", self.child.fitness)


