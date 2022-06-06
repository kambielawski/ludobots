import numpy as np
import copy
import os

from solution import Solution
import constants as c

class ParallelHillClimber:
    def __init__(self):
        os.system("rm brain*.nndf && rm fitness*.txt")
        self.parents = dict()
        self.nextAvailableId = 0

        # create initial population of Solutions
        for i in range(c.POPULATION_SIZE):
            self.parents[i] = Solution(self.nextAvailableId)
            self.nextAvailableId += 1

    def Evolve(self):
        for currGen in range(c.NUMBER_OF_GENERATIONS):
            print("===============\nGENERATION " + str(currGen) + "\n===============\n")
            self.Evaluate(self.parents)
            self.Evolve_For_One_Generation()

    def Evolve_For_One_Generation(self):
        self.Spawn()
        self.Mutate()
        self.Evaluate(self.children)
        # self.Print_Fitness()
        self.Select()
            

    def Show_Best(self):
        best_fitness=np.inf
        best_parent=-1
        for i in self.parents.keys():
            if self.parents[i].fitness < best_fitness:
                best_parent = i
                best_fitness = self.parents[i].fitness
        self.parents[best_parent].Start_Simulation(runMode="GUI")
        print("Best fitness: ", best_fitness)

    def Spawn(self):
        self.children = dict()
        for c in self.parents.keys():
            self.children[c] = copy.deepcopy(self.parents[c])
            self.children[c].Set_ID(self.nextAvailableId)
            self.nextAvailableId += 1

    def Mutate(self):
        for child in self.children.keys():
            self.children[child].Mutate() 

    def Select(self):
        for i in self.children.keys():
            if self.children[i].fitness < self.parents[i].fitness:
                self.parents[i] = self.children[i]
    
    def Evaluate(self, solutions):
        for s in solutions.keys():
            solutions[s].Start_Simulation()
        for s in solutions.keys():
            solutions[s].Wait_For_Simulation_To_End()

    def Print_Fitness(self):
        for i in self.parents.keys():
            print("Parent fitness: ", self.parents[i].fitness, "; Child fitness: ", self.children[i].fitness + "\n")


