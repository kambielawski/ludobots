import time
import pickle
import os

from ageFitnessPareto import AgeFitnessPareto

def Get_Constants_AFPO_Emp():
    return {
        'generations': 5,
        'target_population_size': 10,
        'objective': 'emp_fitness',
        'batching': True,
        'batch_size': 10
    }

def Get_Constants_AFPO_Fit():
    return {
        'generations': 5,
        'target_population_size': 10,
        'objective': 'tri_fitness', 
        'batching': True,
        'batch_size': 10
    }

class Experiment:
    def __init__(self, experiment_directory='', N_runs=10):
        if experiment_directory: # Continue existing experiment
            self.pickle_file = f'{experiment_directory}/evo_runs.pickle'
        else: # Initialize a new experiment
            # 1. Create a new experiment directory
            timestr = time.strftime('%b%d_%I_%M')
            self.experiment_directory = f'experiments/exp_{timestr}' 
            os.system(f'mkdir {self.experiment_directory}')
            os.system(f'mkdir {self.experiment_directory}/best_robots')
            os.system(f'mkdir {self.experiment_directory}/quadruped')
            os.system(f'mkdir {self.experiment_directory}/best_robots/pareto_front')
            os.system(f'cp robots/body_quadruped.urdf {self.experiment_directory}')
            os.system(f'cp world.sdf {self.experiment_directory}')

            # 2. Print experiment information to file
            info_file = open(f'{self.experiment_directory}/info.txt', 'w')
            info_file.write(str(Get_Constants_AFPO_Emp()) + '\n')
            info_file.write(str(Get_Constants_AFPO_Fit()))
            info_file.close()
            
            # 3. Initialize N_runs AFPO objects and pickle them
            treatment_1 = { i: AgeFitnessPareto(Get_Constants_AFPO_Emp(), run_id=(i+1), dir=f'{self.experiment_directory}') for i in range(N_runs) }
            treatment_2 = { i: AgeFitnessPareto(Get_Constants_AFPO_Fit(), run_id=(N_runs+i+1), dir=f'{self.experiment_directory}') for i in range(N_runs) }
            self.evo_runs = { 'emp_fitness': treatment_1,
                              'tri_fitness': treatment_2 }
            self.pickle_file = f'{self.experiment_directory}/evo_runs.pickle'
            with open(self.pickle_file, 'wb') as pklFileHandle:
                pickle.dump(self.evo_runs, pklFileHandle)
    
    def Run_One_Generation(self):
        # 1. Unpickle previous generation
        with open(self.pickle_file, 'rb') as pickle_file:
            self.evo_runs = pickle.load(pickle_file)

        # 2. Compute a single generation for all runs
        for treatment in self.evo_runs:
            for run in self.evo_runs[treatment]:
                self.evo_runs[treatment][run].Evolve_One_Generation()

        # 3. Pickle runs
        with open(self.pickle_file, 'wb') as pklFileHandle:
            pickle.dump(self.evo_runs, pklFileHandle, protocol=pickle.HIGHEST_PROTOCOL)

        # 4. Run t-test and print relevant information
        self.Print_Statistics()

    def Print_Statistics(self):
        print('Donezo with generation')
