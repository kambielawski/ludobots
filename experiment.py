import time
import pickle
import os
import numpy as np

from ageFitnessPareto import AgeFitnessPareto

class Trial:
    """Trial class
    - Initialized when an experiment is submitted
    - Creates and manages experiment directory
    - Has access to the AFPO-level pickle file
    """
    def __init__(self, run_idx, experiment_directory, experiment_parameters):
        self.experiment_directory = experiment_directory
        self.trial_directory = self.experiment_directory + f'/trial_{run_idx}'
        self.pickle_file = f'{self.trial_directory}/trial_{run_idx}.pkl'

        self.afpo = AgeFitnessPareto(experiment_parameters, run_id=run_idx, dir=f'{self.experiment_directory}/trial_{run_idx}')
        self.max_generations = experiment_parameters['generations']
        self.current_generation = 0
        # Create trial-level pickle file for AFPO object
        with open(self.pickle_file, 'wb') as pickle_file:
            pickle.dump(self.afpo, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)

    def Run(self):
        """Run the different runs until we max out"""
        while self.current_generation < self.max_generations:
            self.Run_One_Generation()

    def Run_One_Generation(self):
        """Run a single generation of the trial"""
        t_start = time.time()
        # 1. Unpickle previous generation
        with open(self.pickle_file, 'rb') as pickle_file:
            self.afpo = pickle.load(pickle_file)
            if not isinstance(self.afpo, AgeFitnessPareto):
                raise TypeError("Pickled object needs to be of type AgeFitnessPareto")

        # Save population pickle file (for insurance)
        os.system(f'cp {self.trial_directory}/{self.pickle_file} {self.trial_directory}/saved_{self.pickle_file}')
        
        # 2. Compute a single generation for this trial
        print(f'\n\n========== \n Generation {self.afpo.currentGen} - Run {self.afpo.run_id} \n ==========\n\n')
        self.afpo.Evolve_One_Generation()
        self.afpo.Clean_Directory()

        # 3. Pickle runs
        with open(self.pickle_file, 'wb') as pkl:
            pickle.dump(self.afpo, pkl, protocol=pickle.HIGHEST_PROTOCOL)

        t_end = time.time()
        self.one_gen_time = t_end - t_start


class Experiment:
    """Experiment class
    - Initialized when an experiment is submitted
    - Creates and manages experiment directory
    """
    def __init__(self, experiment_directory='.', exp_file=None):
        if experiment_directory: # Continue existing experiment
            #TODO: error checking on directory status
            self.pickle_file = f'{experiment_directory}/experiment.pkl'
            self.experiment_directory = experiment_directory

            with open(self.pickle_file, 'rb') as pkl:
                self.experiment_object = pickle.load(pkl, 'rb')
                self.experiment_directory = self.experiment_object['experiment_directory']
                self.trials = self.experiment_object['trials']
                self.experiment_params = self.experiment_object['experiment_parameters']
        else: # Initialize a new experiment
            self.initialize_directory(exp_file)

    def Run(self):
        """Run the different runs until we max out"""
        for run_idx, trial in self.trials.items():
            trial.Run()

    def Run_Vacc(self):
        # Submit a job for each trial... 
        # all the trials use the exact same exp params
        # Each job will be a run_exp.py (NOT run_exp_vacc.py) with the
        # TRIAL directory as the argument for exp_directory
        for trial in self.trials:
            # submit VACC job
            pass

    def initialize_directory(self, exp_file):
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
          param_file = open(f'{self.experiment_directory}/exp_params.txt', 'w')
          param_file.write(str(experiment_parameters) + '\n')
          param_file.close()

          # 3. Copy experiment parameters for 1 trial into trial directories
          exp_params_1trial = experiment_parameters
          exp_params_1trial['n_trials'] = 1
          
          for run_idx in range(self.n_runs):
              os.system(f'mkdir {self.experiment_directory}/trial_{run_idx}')
              param_file_1trial = open(f'{self.experiment_directory}/trial_{run_idx}/params_trial_{run_idx}.txt', 'w')
              param_file_1trial.write(str(exp_params_1trial) + '\n')
              param_file.close()

          # Error checking for proper task environment
          if 'boxdisplacement' in np.array([sim['objectives'] for sim in experiment_parameters['simulations']]).flatten() and experiment_parameters['task_environment'] != './task_environments/box_world.sdf':
              raise ValueError('Check your experiment setup. Cannot select for box displacement if box_world.sdf is not the task environment.')
          
          # Bring all necessary task environments into the experiment directory
          for sim in experiment_parameters['simulations']:
              # self.task_env = experiment_parameters['task_environment']
              task_env_file_name = sim['task_environment'].split('/')[2]
              template_env_file = sim['task_environment']
              os.system(f'cp {template_env_file} {self.experiment_directory}/{task_env_file_name}')
              for run_idx in range(self.n_runs):
                  os.system(f'cp {template_env_file} {self.experiment_directory}/trial_{run_idx}/{task_env_file_name}')
          
          # 5. Initialize n_runs Trial objects and pickle them into an aggregate trial directories
          self.trials = { run_idx: Trial(run_idx, self.experiment_directory, exp_params_1trial) for run_idx in range(self.n_runs) }
          self.experiment_params = experiment_parameters
          experiment_object = {
              'trials': self.trials,
              'experiment_parameters': experiment_parameters,
              'experiment_directory': self.experiment_directory
          }
          with open(f'{self.experiment_directory}/experiment.pkl', 'wb') as pkl:
              pickle.dump(experiment_object, pkl)
      
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
