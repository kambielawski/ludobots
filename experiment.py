import time
import pickle
import os
import numpy as np

from ageFitnessPareto import AgeFitnessPareto

class Experiment:
    """Experiment class"""
    def __init__(self, experiment_directory='.', exp_file=None):
        if experiment_directory: # Continue existing experiment
            self.pickle_file = f'{experiment_directory}/evo_runs.pickle'
            self.experiment_directory = experiment_directory
        else: # Initialize a new experiment
            # 1. Create a new experiment directory
            experiment_parameters = self.Get_Experiment_Parameters(exp_file)
            self.n_runs = experiment_parameters['n_trials']
            self.max_generations = experiment_parameters['generations']
            self.current_generation = 0

            timestr = time.strftime('%b%d_%I_%M')
            motor_str = 'mA' if experiment_parameters['motor_measure'] == 'VELOCITY' else 'mD'
            morphology = experiment_parameters['morphology']
            windy = 'windy_' if experiment_parameters['wind'] else ''
            self.experiment_directory = f'experiments/{timestr}_' + experiment_parameters['morphology'] + '_' \
                                        + '_' \
                                        + windy \
                                        + motor_str + '_' + f'n{self.n_runs}' + 'p' \
                                        + str(experiment_parameters['target_population_size']) + 'w' \
                                        + str(experiment_parameters['empowerment_window_size'])
            os.system(f'mkdir {self.experiment_directory}')
            os.system(f'mkdir {self.experiment_directory}/data')
            os.system(f'mkdir {self.experiment_directory}/plots')
            os.system(f'mkdir {self.experiment_directory}/best_robots')
            os.system(f'mkdir {self.experiment_directory}/pareto_front')
            os.system(f'cp robots/body_{morphology}.urdf {self.experiment_directory}')

            # 2. Print experiment parameters to file
            info_file = open(f'{self.experiment_directory}/exp_params.txt', 'w')
            info_file.write(str(experiment_parameters) + '\n')
            info_file.close()

            # Finish directory setup with task environment
            if 'boxdisplacement' in np.array([sim['objectives'] for sim in experiment_parameters['simulations']]).flatten() and experiment_parameters['task_environment'] != './task_environments/box_world.sdf':
                raise ValueError('Check your experiment setup. Cannot select for box displacement if box_world.sdf is not the task environment.')
            
            for sim in experiment_parameters['simulations']:
                # self.task_env = experiment_parameters['task_environment']
                task_env_file_name = sim['task_environment'].split('/')[2]
                template_env_file = sim['task_environment']
                os.system(f'cp {template_env_file} {self.experiment_directory}/{task_env_file_name}')
            
            # 3. Initialize n_runs AFPO objects and pickle them
            treatment_1 = { i: AgeFitnessPareto(experiment_parameters, run_id=(i+1), dir=f'{self.experiment_directory}') for i in range(self.n_runs) }
            self.evo_runs = { experiment_parameters['name']: treatment_1 }
            self.pickle_file = f'{self.experiment_directory}/evo_runs.pickle'
            with open(self.pickle_file, 'wb') as pklFileHandle:
                pickle.dump(self.evo_runs, pklFileHandle)


    def Run(self):
        """Run the different runs until we max out"""
        while self.current_generation < self.max_generations:
            self.Run_One_Generation()


    def Run_One_Generation(self):
        t_start = time.time()
        # 1. Unpickle previous generation
        with open(self.pickle_file, 'rb') as pickle_file:
            self.pkl_obj = pickle.load(pickle_file)
            if isinstance(self.pkl_obj, dict):
                self.evo_runs = self.pkl_obj
            elif isinstance(self.pkl_obj, Experiment):
                self.evo_runs = self.pkl_obj.evo_runs
            else:
                raise TypeError("Pickled object needs to be of type Experiment or type dictionary")

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

    def Get_Experiment_Parameters(self, experiment_file):
        expfile = open(experiment_file)
        exp_string = expfile.read()
        exp_params = eval(exp_string)
        expfile.close()
        return exp_params

    def Print_GenTime_To_File(self):
        f = open('gen_timing.txt', 'a')
        f.write(f'\ngeneration time: ' + str(self.one_gen_time))
        f.close()
