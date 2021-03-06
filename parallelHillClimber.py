import numpy as np
import copy
import os

from solution import Solution
import constants as c

class ParallelHillClimber:
    def __init__(self, constants):
        self.constants = constants
        self.parents = dict()
        self.nextAvailableId = 0

        # create initial population of Solutions
        for i in range(self.constants['population_size']):
            self.parents[i] = Solution(self.nextAvailableId)
            self.nextAvailableId += 1

    def __del__(self):
        os.system("rm world_*.sdf && rm brain_*.nndf && rm fitness_*.txt")

    def Evolve(self):
        for currGen in range(self.constants['generations']):
            print("===============\nGENERATION " + str(currGen) + "\n===============\n")
            self.Evaluate(self.parents)
            self.Evolve_For_One_Generation()

    def Evolve_For_One_Generation(self):
        self.Spawn()
        self.Mutate()
        self.Evaluate(self.children)
        self.Select()
        # self.Print_Population_Fitness()
        self.Print_Best_Fitness()
        self.Save_Best()
        # cleanup 
        os.system("rm world_*.sdf && rm brain_*.nndf && rm fitness_*.txt")
            

    def Show_Best(self):
        best_solution = self.Get_Best_Solution()
        print("Fitness: ", best_solution.Get_Fitness())
        best_solution.Start_Simulation(runMode="GUI")
        best_solution.Wait_For_Simulation_To_End()

    def Save_Best(self):
        best_solution = self.Get_Best_Solution()
        best_id = best_solution.Get_ID()
        os.system("mv brain_" + str(best_id) + ".nndf best_brain.nndf")

    def Get_Best_Solution(self):
        best_fitness=-np.inf
        best_parent=-1
        for i in self.parents.keys():
            if self.parents[i].fitness > best_fitness:
                best_parent = i
                best_fitness = self.parents[i].fitness
        return self.parents[best_parent]

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
            if self.children[i].fitness > self.parents[i].fitness:
                self.parents[i] = self.children[i]
    
    def Evaluate(self, solutions):
        for s in solutions.keys():
            solutions[s].Start_Simulation()
        for s in solutions.keys():
            solutions[s].Wait_For_Simulation_To_End()

    def Print_Population_Fitness(self):
        for i in self.parents.keys():
            print("Parent fitness: ", str(self.parents[i].fitness), "; Child fitness: ", str(self.children[i].fitness))

    def Print_Best_Fitness(self):
        print("Best fitness: ", self.Get_Best_Solution().Get_Fitness())

