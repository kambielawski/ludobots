import numpy as np
import copy
import os
from sys import platform

from solution import Solution
from plotter import Plotter

OS_MV = 'move' if platform == 'win32' else 'mv'
OS_RM = 'del' if platform == 'win32' else 'rm'

class AgeFitnessPareto():
    def __init__(self, constants):
        self.population = dict()
        self.nextAvailableId = 0
        self.nGenerations = constants['generations']
        self.targetPopSize = constants['target_population_size']
        self.plotter = Plotter(constants)

        # Create initial population randomly
        for i in range(self.targetPopSize):
            self.population[i] = Solution(self.nextAvailableId)
            self.nextAvailableId += 1

    def __del__(self):
        self.Clean_Directory()
    
    '''
    Main Evolve loop for a single run
    '''
    def Evolve(self):
        self.Run_Solutions()
        for currentGen in range(self.nGenerations):
            print('===== Generation ' + str(currentGen) + ' =====')
            self.Evolve_One_Generation(currentGen)
            if currentGen == self.nGenerations - 1:
                self.Save_Best()
                self.Plot_Gen_Animation()
            self.Clean_Directory()

    '''
    Single generation process
    '''
    def Evolve_One_Generation(self, genNumber):
        self.Increment_Ages()
        self.Extend_Population()
        self.Run_Solutions()
        self.Reduce_Population()
        pf = self.Pareto_Front()
        self.Run_Gen_Statistics(genNumber, pf)
        print(pf)
    
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
        pf_size = len(self.Pareto_Front())
        if pf_size >= self.targetPopSize:
            self.targetPopSize = pf_size
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

    def Dominates(self, i, j):
        '''
        Returns True if solution i dominates solution j (else False)
        '''
        if self.population[j].Get_Age() == self.population[i].Get_Age() and self.population[j].Get_Fitness() == self.population[i].Get_Fitness() and self.population[j].Get_Empowerment() == self.population[i].Get_Empowerment():
            return i > j
        elif self.population[i].Get_Age() <= self.population[j].Get_Age() and self.population[i].Get_Fitness() >= self.population[j].Get_Fitness() and self.population[i].Get_Empowerment() >= self.population[j].Get_Empowerment():
            return True
        else:
            return False

    def Run_Gen_Statistics(self, genNumber, pf):
        '''
        Sends data for bookkeeping in Plotter class

        genNumber is an int representing which generation the data is from
        pf is a dict of the Pareto Front solutions for the generation
        '''
        pfData = [(self.population[s].Get_ID(), self.population[s].Get_Age(), 
                   self.population[s].Get_Fitness(), self.population[s].Get_Empowerment()) for s in pf]
        popData = [(self.population[s].Get_ID(), self.population[s].Get_Age(), 
                    self.population[s].Get_Fitness(), self.population[s].Get_Empowerment()) for s in self.population]
        self.plotter.Population_Data(genNumber, popData)
        self.plotter.Pareto_Front_Data(genNumber, pfData)

    def Plot_Gen_Animation(self):
        '''
        Runs Plotter animation
        '''
        self.plotter.Plot_Age_Fitness()
        self.plotter.Plot_Gen_Fitness()
        self.plotter.Plot_Gen_Fitness_PF()
        self.plotter.Plot_Age_Fitness_PF()

    def Clean_Directory(self):
        pf = self.Pareto_Front()

        # Save Pareto-front brains
        for id in pf:
            if os.path.exists('brain_' + str(id) + '.nndf'):
                os.system(OS_MV + ' brain_{id}.nndf ./best_robots/pareto_front/pf_brain_{id}.nndf'.format(id=id))
        # Remove the rest
        os.system(OS_RM + ' world_*.sdf && ' + OS_RM + ' brain_*.nndf && ' + OS_RM + ' fitness_*.txt')
        # Remove old Pareto-front brains
        pf_files = os.listdir('./best_robots/pareto_front')
        for pf_id in [(int(filestr.split('.')[0].split('_')[2]), filestr) for filestr in pf_files]:
            if pf_id[0] not in pf:
                os.system(OS_RM + ' best_robots/pareto_front/{filestr}'.format(filestr=pf_id[1]))

    def Save_Best(self):
        pf = self.Pareto_Front()
        
        # Move over pareto front bests, then delete pareto_front dir
        for id in pf:
            os.system(OS_MV + ' best_robots/pareto_front/pf_brain_{id}.nndf best_robots/quadruped'.format(id=id))
        os.system(OS_RM + ' best_robots/pareto_front/*')