"""Solution class"""
import os
import pyrosim.pyrosim as pyrosim
import random
import subprocess
import re
import numpy as np

from robots.quadruped import Quadruped
from robots.hexapod import Hexapod
from robots.biped import Biped
from robots.snake4 import Snake4
from robots.octoped import Octoped
from robots.quadruped2x import Quadruped2X

class Solution:
    """Solution class"""
    def __init__(self, solution_id, lineage, constants, dir='.'):
        self.id = solution_id
        self.age = 1
        self.empowerment = 0
        self.lineage = lineage
        self.simulations = constants['simulations']
        self.empowerment_window_size = constants['empowerment_window_size']
        self.motor_measure = constants['motor_measure']
        self.morphology = constants['morphology']
        self.wind = constants['wind']
        self.been_simulated = [False for _ in self.simulations]
        self.sim_metrics = {}           # Metrics for individual simulations
        self.selection_objectives = np.unique([objective for sim in self.simulations for objective in sim['objectives']])
        self.selection_metrics = {objective: 0 for objective in self.selection_objectives}     # Metrics for selection
        self.aggregate_metrics = {}     # Aggregate metrics 

        #TODO: generalize robot morphology selection
        if self.morphology == 'quadruped':
            self.robot = Quadruped(self.id, dir=dir)
        elif self.morphology == 'hexapod':
            self.robot = Hexapod(self.id, dir=dir)
        elif self.morphology == 'biped':
            self.robot = Biped(self.id, dir=dir)
        elif self.morphology == 'snake4':
            self.robot = Snake4(self.id, dir=dir)
        elif self.morphology == 'octoped':
            self.robot = Octoped(self.id, dir=dir)
        elif self.morphology == 'quadruped2x':
            self.robot = Quadruped2X(self.id, dir=dir)
            
        self.weights = self.robot.Generate_Weights()

        self.dir = dir

    def Run_Simulation(self, run_mode="DIRECT", sim_number=0):
        """Run simulation for this solution."""
        self.run_mode=run_mode
        self.Create_World(sim_number)

        self.robot.Generate_Robot(self.weights, 0,0,2, orientation=self.simulations[sim_number]['body_orientation']) # TODO: generalize the starting position for robots

        subprocess_run_string = ['python3', 'simulate.py',
                                run_mode,
                                str(self.id),
                                f'{self.dir}/brain_{self.id}.nndf', 
                                self.robot.Get_Body_File(),
                                '--directory', self.dir,
                                '--objects_file', self.worldFile,
                                '--motor_measure', self.motor_measure,
                                '--empowerment_window_size', str(self.empowerment_window_size),
                                '--wind', str(self.wind)]

        sp = subprocess.Popen(subprocess_run_string, stdout=subprocess.PIPE)

        # Parse standard output from subprocess
        stdout, stderr = sp.communicate()
        sp.wait()
        out_str = stdout.decode()
        fitness_metrics = re.search('\(.+\)', out_str)[0].strip('()').split(' ')
        sim_metrics = {
            'displacement': float(fitness_metrics[0]),
            'empowerment': float(fitness_metrics[1]),
            'first_half_displacement': float(fitness_metrics[2]),
            'second_half_displacement': float(fitness_metrics[3]),
            'random': float(fitness_metrics[4]),
            'boxdisplacement': float(fitness_metrics[5]) if fitness_metrics[5] != 'None' else 0,
            'first_half_box_displacement': float(fitness_metrics[6]) if fitness_metrics[6] != 'None' else 0,
            'second_half_box_displacement': float(fitness_metrics[7]) if fitness_metrics[7] != 'None' else 0,
            'H_actions': float(fitness_metrics[8]),
            'H_sensors': float(fitness_metrics[9]),
            'H_joint_AS': float(fitness_metrics[10]),
            'H_A_cond_S': float(fitness_metrics[11]),
            'H_S_cond_A': float(fitness_metrics[12]),
            'empowerment_joint_normalized': float(fitness_metrics[13]),
            '-empowerment': -float(fitness_metrics[1]),
            '-H_actions': -float(fitness_metrics[8]),
            '-H_sensors': -float(fitness_metrics[9]),
            '-H_joint_AS': -float(fitness_metrics[10]),
            '-H_A_cond_S': -float(fitness_metrics[11]),
            '-H_S_cond_A': -float(fitness_metrics[12]),
            '-empowerment_joint_normalized': -float(fitness_metrics[13]),
        }

        self.sim_metrics[sim_number] = sim_metrics

        for objective in sim_metrics:
            if objective in self.selection_metrics:
                self.selection_metrics[objective] += sim_metrics[objective]

        self.been_simulated[sim_number] = True


    def Mutate(self):
        """Mutate the solution's weights."""
        rand_row = random.randint(0,self.robot.NUM_MOTOR_NEURONS-1)
        rand_col = random.randint(0,self.robot.NUM_SENSOR_NEURONS-1)

        self.robot.weights[rand_row][rand_col] = random.random() * 2 - 1
    
    def Create_World(self, sim_number=0):
        """Create the world file for the simulation."""
        self.worldFile = f'{self.dir}/world_{self.id}.sdf'
        task_env_file_name = self.simulations[sim_number]['task_environment'].split('/')[2]
        os.system(f'cp {self.dir}/{task_env_file_name} {self.worldFile}')

    def Dominates_Other(self, other):
        """Check if this solution dominates another."""
        assert self.selection_objectives == other.selection_objectives

        dominates = [self.age <= other.Get_Age()]
        for objective in self.selection_metrics:
            dominates.append(self.selection_metrics[objective] >= other.selection_metrics[objective])

        return all(dominates)

    def Increment_Age(self):
        """Increment the age of the solution."""
        self.age += 1

    def Get_Age(self):
        """Return the age of the solution."""
        return self.age

    def Get_Primary_Objective(self):
        """Return the primary objective of the solution (first objective listed)."""
        primary_objective = self.selection_objectives[0]
        return self.selection_metrics[primary_objective]

    def Regenerate_Brain_File(self, dir=None):
        """Regenerate the brain file for the solution."""
        self.robot.Generate_NN(dir)

    def Has_Been_Simulated(self):
        """Return whether the solution has been simulated."""
        return all(self.been_simulated)

    def Reset_Simulated(self):
        """Reset the simulated attribute of the solution."""
        self.selection_metrics = {objective: 0 for objective in self.selection_objectives}
        self.aggregate_metrics = {}
        self.been_simulated = [False for _ in self.simulations]

    def Set_ID(self, newId):
        """Set the ID of the solution."""
        self.robot.Set_Id(newId)
        self.id = newId

    def Get_ID(self):
        """Return the ID of the solution."""
        return self.id

    def Get_Lineage(self):
        """Return the lineage of the solution."""
        return self.lineage
