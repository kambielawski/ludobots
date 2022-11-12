import time
import pickle
import os
import threading

from ageFitnessPareto import AgeFitnessPareto

def Get_Constants_AFPO_Emp():
    return {
        'generations': 5,
        'target_population_size': 10,
        'objective': 'emp_fitness',
        'batching': True,
        'batch_size': 5
    }

def Get_Constants_AFPO_Fit():
    return {
        'generations': 5,
        'target_population_size': 10,
        'objective': 'tri_fitness', 
        'batching': True,
        'batch_size': 5
    }

class Experiment:
    def __init__(self, experiment_directory='', N_runs=30):
        print('EXP: experiment directory: ', experiment_directory)
        if experiment_directory: # Continue existing experiment
            self.pickle_file = f'{experiment_directory}/evo_runs.pickle'
        else: # Initialize a new experiment
            # 1. Create a new experiment directory
            timestr = time.strftime('%b%d_%I_%M')
            self.experiment_directory = f'experiments/exp_{timestr}' 
            os.system(f'mkdir {self.experiment_directory}')
            os.system(f'mkdir {self.experiment_directory}/data')
            os.system(f'mkdir {self.experiment_directory}/plots')
            os.system(f'mkdir {self.experiment_directory}/best_robots')
            os.system(f'mkdir {self.experiment_directory}/best_robots/quadruped')
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
    
    def Thread_Func(self, treatment, run):
        self.evo_runs[treatment][run].Evolve_One_Generation()

    def Run_One_Generation(self):
        t_start = time.time()
        self.threads = []
        # 1. Unpickle previous generation
        with open(self.pickle_file, 'rb') as pickle_file:
            self.evo_runs = pickle.load(pickle_file)

        # 2. Compute a single generation for all runs
        for treatment in self.evo_runs:
            for run in self.evo_runs[treatment]:
                t = threading.Thread(target=self.Thread_Func, args=[treatment, run])
                t.start()
                self.threads.append(t)

        for t in self.threads:
            t.join()

        for treatment in self.evo_runs:
            for run in self.evo_runs[treatment]:
                self.evo_runs[treatment][run].Clean_Directory()
    
        # 3. Pickle runs
        with open(self.pickle_file, 'wb') as pklFileHandle:
            pickle.dump(self.evo_runs, pklFileHandle, protocol=pickle.HIGHEST_PROTOCOL)

        t_end = time.time()
        self.one_gen_time = t_end - t_start
        self.Print_GenTime_To_File()
        # 4. Run t-test and print relevant information
        self.Print_Statistics()

    def Run_T_Test(self):
        return 1

    def Print_GenTime_To_File(self):
        f = open('gen_timing.txt', 'a')
        f.write(f'\ngeneration time: ' + str(self.one_gen_time))
        f.close()

    def Print_Statistics(self):
        print('Donezo with generation')
