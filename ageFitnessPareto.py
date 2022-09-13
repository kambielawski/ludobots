import numpy as np
import copy
import os
from sys import platform

from solution import Solution
import constants as c

class AgeFitnessPareto():
    def __init__(self, constants):
        self.population = dict()
        self.nextAvailableId = 0
        self.nGenerations = constants['generations']
        self.targetPopSize = constants['target_population_size']

        # Create initial population randomly
        for i in range(self.targetPopSize):
            self.population[i] = Solution(self.nextAvailableId)
            self.nextAvailableId += 1

    def __del__(self):
        if platform == 'win32':
            os.system("del world_*.sdf && del brain_*.nndf && del fitness_*.txt && del tmp_*.txt")
        else:
            os.system("rm world_*.sdf && rm brain_*.nndf && rm fitness_*.txt && rm tmp_*.txt")
    
    def Evolve(self):
        self.Run_Solutions()
        for currentGen in range(self.nGenerations):
            print('===== Generation ' + str(currentGen) + ' =====')
            self.Evolve_One_Generation()

    def Evolve_One_Generation(self):
        self.Increment_Ages()
        self.Extend_Population()
        self.Run_Solutions()
        self.Reduce_Population()
        pf = self.Pareto_Front()
        # print([(s.Get_ID(), s.Get_Age(), s.Get_Fitness(), s.Get_Empowerment()) for s in self.population.values()])
        print(pf)
        print([(self.population[s].Get_ID(), self.population[s].Get_Age(), 
                self.population[s].Get_Fitness(), self.population[s].Get_Empowerment()) for s in pf])
    
    '''
    Breed parents, mutate, and add a random individual
    '''
    def Extend_Population(self):
        # 1. Breed
        # - do tournament selection |pop| times 
        for i in range(self.targetPopSize):
            parent = self.Tournament_Select()
            child = copy.deepcopy(self.population[parent])
            # - create mutated children from the tournament winners
            child.Mutate()
            child.Set_ID(self.nextAvailableId)
            child.Reset_Simulated()
            self.population[self.nextAvailableId] = child
            self.nextAvailableId += 1

        # 2. Add a random individual
        self.population[self.nextAvailableId] = Solution(self.nextAvailableId)
        self.nextAvailableId += 1

    def Tournament_Select(self):
        p1 = np.random.choice(list(self.population.keys()))
        p2 = np.random.choice(list(self.population.keys()))
        while p2 == p1:
            p2 = np.random.choice(list(self.population.keys()))
        
        # Tournament winner based only on fitness? Primary objective? 
        if self.population[p1].Get_Fitness() > self.population[p2].Get_Fitness():
            return p1
        else:
            return p2

    '''
    Remove dominated individuals until target population size is reached
    '''
    def Reduce_Population(self):
        # Remove individuals until target population is reached
        while len(self.population) > self.targetPopSize:
            i1 = np.random.choice(list(self.population.keys()))
            i2 = np.random.choice(list(self.population.keys()))
            while i2 == i1:
                i2 = np.random.choice(list(self.population.keys()))

            if self.Dominates(i1, i2): # i1 dominates
                self.population.pop(i2)
            elif self.Dominates(i2, i1): # i2 dominates
                self.population.pop(i1)

    def Increment_Ages(self):
        for solnId in self.population:
            self.population[solnId].Increment_Age()

    def Run_Solutions(self):
        for solnId in self.population:
            if not self.population[solnId].Has_Been_Simulated():
                self.population[solnId].Start_Simulation()
        for solnId in self.population:
            if not self.population[solnId].Has_Been_Simulated():
                self.population[solnId].Wait_For_Simulation_To_End()
    
    '''
    Returns IDs of the solutions that are Pareto optimal
    '''
    def Pareto_Front(self):
        paretoFront = []
        for i in self.population:
            iIsDominated = False
            for j in self.population:
                if i != j and self.Dominates(j,i): # does j dominate i? 
                    iIsDominated = True
                    break 
            if not iIsDominated:
                paretoFront.append(i)
        return paretoFront

    '''
    Returns True if solution i dominates solution j (else False)
    '''
    def Dominates(self, i, j):
        if self.population[j].Get_Age() < self.population[i].Get_Age():
            return False
        if self.population[j].Get_Fitness() > self.population[i].Get_Fitness():
            return False
        if self.population[j].Get_Empowerment() > self.population[i].Get_Empowerment():
            return False
        return True

    def Show_Best(self):
        pass