import numpy as np
import copy
import os
import time
from sys import platform
from concurrent.futures import ThreadPoolExecutor

from solution import Solution
from history import RunHistory

OS_MV = 'move' if platform == 'win32' else 'mv'
OS_RM = 'del' if platform == 'win32' else 'rm'

class AgeFitnessPareto():
    def __init__(self, constants, run_id=1, dir='.'):
        self.population = dict()
        self.nGenerations = constants['generations']
        self.targetPopSize = constants['target_population_size']
        self.batch_size = constants['batch_size']
        self.robot_constants = {
            'empowerment_window_size': constants['empowerment_window_size'],
            'motor_measure': constants['motor_measure'],
            'objectives': constants['objectives']
        }
        self.history = RunHistory(constants, dir=dir)
        self.currentGen = 0
        self.dir = dir
        self.run_id = run_id

    def __del__(self):
        pass
    
    '''
    Main Evolve loop for a single run
    '''
    def Evolve(self):
        while self.currentGen < self.nGenerations:
            print('===== Generation ' + str(self.currentGen) + ' =====')
            self.Evolve_One_Generation()
            if self.currentGen == self.nGenerations:
                # self.Save_Emp()
                # self.Save_Best()
                self.Write_Gen_Statistics()
            # self.Clean_Directory()

    '''
    Single generation process
    '''
    def Evolve_One_Generation(self):
        # 1. Reproduce
        if self.currentGen == 0:
            # Initialize random population
            for _ in range(self.targetPopSize):
                rand_id = self.Get_Available_Id()
                self.population[rand_id] = Solution(rand_id, (0, rand_id), constants=self.robot_constants, dir=self.dir)
        else:
            self.Increment_Ages()
            self.Extend_Population(self.currentGen)

        # 2. Simulate
        self.Run_Solutions()

        # 3. Cull population
        self.Reduce_Population()

        # 4. Analyze and run statistics
        pf = self.Pareto_Front()
        # self.Save_Pareto_Front(pf)
        self.Run_Gen_Statistics(self.currentGen, pf)
        self.currentGen += 1

    '''
    Breed parents, mutate, and add a random individual
    '''
    def Extend_Population(self, genNumber):
        # 1. Breed
        # - do tournament selection |pop| times 
        for _ in range(self.targetPopSize):
            parent = self.Tournament_Select()
            child = copy.deepcopy(self.population[parent])
            # - create mutated children from the tournament winners
            child.Mutate()
            rand_id = self.Get_Available_Id()
            child.Set_ID(rand_id)
            child.Reset_Simulated()
            self.population[rand_id] = child

        # 2. Add a random individual
        rand_id = self.Get_Available_Id()
        self.population[rand_id] = Solution(rand_id, (genNumber, rand_id), self.robot_constants, dir=self.dir)

    '''
    Tournament selection to decide which individuals reproduce
    '''
    def Tournament_Select(self):
        p1 = np.random.choice(list(self.population.keys()))
        p2 = np.random.choice(list(self.population.keys()))
        while p2 == p1:
            p2 = np.random.choice(list(self.population.keys()))

        # Tournament winner based only on primary objective (first listed)
        if self.population[p1].Get_Primary_Objective() > self.population[p2].Get_Primary_Objective():
            return p1
        else:
            return p2

    '''
    Remove dominated individuals until target population size is reached
    '''
    def Reduce_Population(self):
        pf_size = len(self.Pareto_Front())
        print(pf_size)
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
        def Run_One_Solution_Async(solnId):
            return self.population[solnId].Run_Simulation()

        try:
            with ThreadPoolExecutor() as executor:
                futures = []
                # Start threads
                for solnId in self.population:
                    if not self.population[solnId].Has_Been_Simulated():
                        f = executor.submit(Run_One_Solution_Async, solnId)
                        futures.append(f)
                # Wait for all threads to be finished running
                while not all([f.done() for f in futures]):
                    time.sleep(0.1)
        except Exception as err:
            os.system(f'echo {err} >> {self.dir}/error_log.txt')

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
        return self.population[i].Dominates_Other(self.population[j])

    def Run_Gen_Statistics(self, genNumber, pf):
        '''
        Sends data for bookkeeping in RunHistory class

        genNumber is an int representing which generation the data is from
        pf is a dict of the Pareto Front solutions for the generation
        '''
        pfData = [{
            'id': self.population[s].Get_ID(),
            'age': self.population[s].Get_Age(),
            'metrics': self.population[s].selection_metrics,
            'lineage': self.population[s].Get_Lineage()
        } for s in pf]
        popData = [{
            'id': self.population[s].Get_ID(),
            'age': self.population[s].Get_Age(),
            'metrics': self.population[s].selection_metrics,
            'lineage': self.population[s].Get_Lineage()
        } for s in self.population]
        
        self.history.Population_Data(genNumber, popData)
        self.history.Pareto_Front_Data(genNumber, pfData)

    def Write_Gen_Statistics(self):
        self.history.Write_Pareto_Front_File()

    def Get_Available_Id(self):
        return hash(np.random.random())

    def Clean_Directory(self):
        # Remove the rest
        os.system(OS_RM + ' ' + self.dir + '/brain_*.nndf')
        os.system(OS_RM + ' ' + self.dir + '/body_quadruped_*.urdf') 
        os.system(OS_RM + ' ' + self.dir + '/world_*.sdf')

    def Save_Emp(self):
        pop_data = self.population
        max_emp_id = -1
        max_emp = -1
        for id in pop_data:
            emp = pop_data[id].selection_metrics['empowerment']
            if emp > max_emp:
                max_emp_id = id
                max_emp = emp
        # Save highest empowerment
        os.system(OS_MV + f' ./brain_{max_emp_id}.nndf best_robots/empowered/brain_{max_emp_id}.nndf')

    def Save_Pop(self):
        os.system(f'mkdir {self.dir}/gen_{self.currentGen}')
        for id in self.population:
            os.system(OS_MV + f' {self.dir}/brain_{id}.nndf {self.dir}/gen_{self.currentGen}/brain_{id}.nndf')

    def Save_Pareto_Front(self, pf):
        # Remove current pareto front files
        os.system(f'rm {self.dir}/pareto_front/run_{self.run_id}/*')
        
        # Save active pareto front
        os.system(f'cp {self.dir}/brain_' + '{' + ','.join([str(id) for id in pf]) + '}' + f'.nndf {self.dir}/pareto_front/run_{self.run_id}')

    def Save_Best(self, pareto_front_dir='pareto_front', metric='displacement'):
        pf = self.Pareto_Front()
        
        max_id = max([(self.population[id].selection_metrics[metric], id) for id in pf])[1]

        # Save Pareto-front brains
        # for id in pf:
        if os.path.exists(f'{self.dir}/brain_{max_id}.nndf'):
            os.system(OS_MV + f' {self.dir}/brain_{max_id}.nndf {self.dir}/best_robots/{pareto_front_dir}/pf_brain_{max_id}.nndf')

    def Save_Best_Simulation(self):
        pass

    