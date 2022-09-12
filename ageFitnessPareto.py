import numpy as np
import copy

from solution import Solution
import constants as c

class AgeFitnessPareto():
    def __init__(self, constants):
        self.population = dict()
        self.nextAvailableId = 0
        self.constants = constants
        self.nGenerations = constants['generations']

        # create initial population randomly
        for i in range(self.constants['population_size']):
            self.population[i] = Solution(self.nextAvailableId)
            self.nextAvailableId += 1

    def Evolve(self):
        for currentGen in range(self.constants['generations']):
            print('===== Generation ' + str(currentGen) + ' =====')
            self.Evolve_One_Generation()

    def Evolve_One_Generation(self):
        self.Increment_Ages()
        self.Run_Solutions()
        self.Evaluate_Solutions()
        self.Reduce_Population()

    def Evaluate_Solutions(self):
        # after having run the solutions, we have access to the fitness
        # and the age; now we can determine a pareto front
        paretoFront = self.Pareto_Front()
        print(paretoFront)
        print([(s.Get_Age(), s.Get_Fitness(), s.Get_Empowerment()) for s in self.population.values()])
        pass

    def Reduce_Population(self):
        pass

    def Increment_Ages(self):
        for solnId in self.population:
            self.population[solnId].Increment_Age()

    def Run_Solutions(self):
        for solnId in self.population:
            # TODO: Check if the solution has already been run
            self.population[solnId].Start_Simulation()
        for solnId in self.population:
            self.population[solnId].Wait_For_Simulation_To_End()
    
    '''
    Returns IDs of the solutions that are Pareto optimal
    '''
    def Pareto_Front(self):
        paretoFront = []
        popSize = len(self.population)
        for i in range(popSize):
            iIsDominated = False
            for j in range(popSize):
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
        if self.population[j].Get_Robot_Empowerment() > self.population[i].Get_Robot_Empowerment():
            return False
        return True

    def Show_Best(self):
        pass