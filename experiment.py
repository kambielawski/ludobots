import time
import pickle
import os
import threading
import constants as c

from ageFitnessPareto import AgeFitnessPareto

def Get_Constants_AFPO_T1():
    return {
        'name': 'window_50',
        'generations': 999,
        'target_population_size': 100,
        'motor_measure': 'DESIRED_ANGLE', # 'VELOCITY' or 'DESIRED_ANGLE'
        'objectives': ['box_displacement', 'empowerment'],
        'empowerment_window_size': 15,
        'batching': False,
        'batch_size': 5
    }

def Get_Constants_AFPO_T2():
    return {
        'name': 'window_400',
        'generations': 999,
        'target_population_size': 100,
        'motor_measure': 'DESIRED_ANGLE',
        'objectives': ['box_displacement', 'empowerment'], 
        'empowerment_window_size': 300,
        'batching': False,
        'batch_size': 5
    }

class Experiment:
    def __init__(self, experiment_directory='', N_runs=30):
        print('EXP: experiment directory: ', experiment_directory)
        if experiment_directory: # Continue existing experiment
            self.pickle_file = f'{experiment_directory}/evo_runs.pickle'
            self.experiment_directory = experiment_directory
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

            # 2. Print experiment information to file
            t1_info = Get_Constants_AFPO_T1()
            t2_info = Get_Constants_AFPO_T2()
            info_file = open(f'{self.experiment_directory}/info.txt', 'w')
            info_file.write(str(t1_info) + '\n')
            info_file.write(str(t2_info))
            info_file.close()

            # TODO: Generalize world initialization (make per-experiment)
            # Finish directory setup
            if 'box_displacement' in t1_info['objectives']:
                os.system(f'cp ./task_environments/box_world.sdf {self.experiment_directory}/world.sdf')
            else:
                os.system(f'cp ./task_environments/world.sdf {self.experiment_directory}')
            
            # 3. Initialize N_runs AFPO objects and pickle them
            treatment_1 = { i: AgeFitnessPareto(t1_info, run_id=(i+1), dir=f'{self.experiment_directory}') for i in range(N_runs) }
            treatment_2 = { i: AgeFitnessPareto(t2_info, run_id=(N_runs+i+1), dir=f'{self.experiment_directory}') for i in range(N_runs) }
            self.evo_runs = { t1_info['name']: treatment_1,
                              t2_info['name']: treatment_2 }
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

        os.system(f'cp {self.experiment_directory}/evo_runs.pickle {self.experiment_directory}/evo_runs_saved.pickle')
        
        # 2. Compute a single generation for all runs
        for treatment in self.evo_runs:
            for run in self.evo_runs[treatment]:
                print(f'\n\n========== \n Generation {self.evo_runs[treatment][run].currentGen}, Run {run} \n ==========\n\n')
                self.evo_runs[treatment][run].Evolve_One_Generation()
                self.evo_runs[treatment][run].Clean_Directory() # Clean up experiment directory

        # 3. Pickle runs
        with open(self.pickle_file, 'wb') as pklFileHandle:
            pickle.dump(self.evo_runs, pklFileHandle, protocol=pickle.HIGHEST_PROTOCOL)

        t_end = time.time()
        self.one_gen_time = t_end - t_start
        self.Print_GenTime_To_File()
        # 4. Run t-test and print relevant information

    def Run_T_Test(self):
        return 1

    def Print_GenTime_To_File(self):
        f = open('gen_timing.txt', 'a')
        f.write(f'\ngeneration time: ' + str(self.one_gen_time))
        f.close()
