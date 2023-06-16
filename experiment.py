import time
import pickle
import os

from ageFitnessPareto import AgeFitnessPareto

def Get_Experiment_Parameters():
    return {
        'name': 'boxdisplacement-emp',
        'morphology': 'hexapod',
        'task_environment': './task_environments/box_world.sdf',
        'generations': 999,
        'target_population_size': 100,
        'motor_measure': 'VELOCITY', # 'VELOCITY' or 'DESIRED_ANGLE'
        'objectives': ['empowerment'], 
        'empowerment_window_size': 500,
    }

class Experiment:
    def __init__(self, experiment_directory='.', N_runs=30):
        print('EXP: experiment directory: ', experiment_directory)
        if experiment_directory: # Continue existing experiment
            self.pickle_file = f'{experiment_directory}/evo_runs.pickle'
            self.experiment_directory = experiment_directory
        else: # Initialize a new experiment
            # 1. Create a new experiment directory
            experiment_parameters = Get_Experiment_Parameters()

            timestr = time.strftime('%b%d_%I_%M')
            motor_str = 'mA' if experiment_parameters['motor_measure'] == 'VELOCITY' else 'mD'
            morphology = experiment_parameters['morphology']
            self.experiment_directory = f'experiments/{timestr}_' + experiment_parameters['morphology'] + '_' + '-'.join(experiment_parameters['objectives']) + '_' + motor_str + '_' + f'n{N_runs}' + 'p' + str(experiment_parameters['target_population_size']) + 'w' + str(experiment_parameters['empowerment_window_size'])
            os.system(f'mkdir {self.experiment_directory}')
            os.system(f'mkdir {self.experiment_directory}/data')
            os.system(f'mkdir {self.experiment_directory}/plots')
            os.system(f'mkdir {self.experiment_directory}/best_robots')
            os.system(f'mkdir {self.experiment_directory}/pareto_front')
            os.system(f'cp robots/body_{morphology}.urdf {self.experiment_directory}')

            # 2. Print experiment parameters to file
            info_file = open(f'{self.experiment_directory}/info.txt', 'w')
            info_file.write(str(experiment_parameters) + '\n')
            info_file.close()

            # Finish directory setup with task environment
            if 'boxdisplacement' in experiment_parameters['objectives'] and experiment_parameters['task_environment'] != './task_environments/box_world.sdf':
                raise ValueError('Check your experiment setup. Cannot select for box displacement if box_world.sdf is not the task environment.')
            self.task_env = experiment_parameters['task_environment']
            os.system(f'cp {self.task_env} {self.experiment_directory}/world.sdf')
            
            # 3. Initialize N_runs AFPO objects and pickle them
            treatment_1 = { i: AgeFitnessPareto(experiment_parameters, run_id=(i+1), dir=f'{self.experiment_directory}') for i in range(N_runs) }
            self.evo_runs = { experiment_parameters['name']: treatment_1 }
            self.pickle_file = f'{self.experiment_directory}/evo_runs.pickle'
            with open(self.pickle_file, 'wb') as pklFileHandle:
                pickle.dump(self.evo_runs, pklFileHandle)

    def Run_One_Generation(self):
        t_start = time.time()
        # 1. Unpickle previous generation
        with open(self.pickle_file, 'rb') as pickle_file:
            self.evo_runs = pickle.load(pickle_file)

        # Save population pickle file (for insurance)
        os.system(f'cp {self.experiment_directory}/evo_runs.pickle {self.experiment_directory}/evo_runs_saved.pickle')
        
        # 2. Compute a single generation for all runs
        for treatment in self.evo_runs:
            for run in self.evo_runs[treatment]:
                # Create a directory for the *active* pareto front if it doesn't exist yet 
                if not os.path.exists(f'{self.experiment_directory}/pareto_front/run_{self.evo_runs[treatment][run].run_id}'):
                    os.system(f'mkdir {self.experiment_directory}/pareto_front/run_{self.evo_runs[treatment][run].run_id}')
                print(f'\n\n========== \n Generation {self.evo_runs[treatment][run].currentGen} - Run {run} \n ==========\n\n')
                self.evo_runs[treatment][run].Evolve_One_Generation()
                self.evo_runs[treatment][run].Clean_Directory() # Clean up experiment directory

        # 3. Pickle runs
        with open(self.pickle_file, 'wb') as pklFileHandle:
            pickle.dump(self.evo_runs, pklFileHandle, protocol=pickle.HIGHEST_PROTOCOL)

        t_end = time.time()
        self.one_gen_time = t_end - t_start
        self.Print_GenTime_To_File()

    def Print_GenTime_To_File(self):
        f = open('gen_timing.txt', 'a')
        f.write(f'\ngeneration time: ' + str(self.one_gen_time))
        f.close()
