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
    def __init__(self, solutionId, lineage, constants, dir='.'):
        self.id = solutionId
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
        # self.selection_metrics = None
        self.selection_objectives = np.unique([objective for sim in self.simulations for objective in sim['objectives']])
        self.selection_metrics = {objective: 0 for objective in self.selection_objectives}     # Metrics for selection
        self.aggregate_metrics = {}     # Aggregate metrics 

        # TODO: generalize robot morphology selection
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

    def Run_Simulation(self, runMode="DIRECT", sim_number=0):
        self.runMode=runMode
        self.Create_World(sim_number)

        self.robot.Generate_Robot(self.weights, 0,0,2, orientation=self.simulations[sim_number]['body_orientation']) # TODO: generalize the starting position for robots

        print(self.robot.Get_Body_File())
        subprocess_run_string = ['python3', 'simulate.py', 
                                runMode, 
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
        print(stdout, stderr)
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
            'second_half_box_displacement': float(fitness_metrics[7]) if fitness_metrics[7] != 'None' else 0
        }

        self.sim_metrics[sim_number] = sim_metrics

        for objective in sim_metrics:
            if objective in self.selection_metrics:
                self.selection_metrics[objective] += sim_metrics[objective]

        self.been_simulated[sim_number] = True


    def Mutate(self):
        randRow = random.randint(0,self.robot.NUM_MOTOR_NEURONS-1)
        randCol = random.randint(0,self.robot.NUM_SENSOR_NEURONS-1)

        self.robot.weights[randRow][randCol] = random.random() * 2 - 1
    
    def Create_World(self, sim_number=0):
        self.worldFile = f'{self.dir}/world_{self.id}.sdf'
        task_env_file_name = self.simulations[sim_number]['task_environment'].split('/')[2]
        os.system(f'cp {self.dir}/{task_env_file_name} {self.worldFile}')

    def Dominates_Other(self, other):
        assert self.selection_objectives == other.selection_objectives

        dominates = [self.age <= other.Get_Age()]
        for objective in self.selection_metrics:
            dominates.append(self.selection_metrics[objective] >= other.selection_metrics[objective])

        return all(dominates)

    def Increment_Age(self):
        self.age += 1

    def Get_Age(self):
        return self.age

    def Get_Primary_Objective(self):
        return self.selection_metrics['displacement']

    def Regenerate_Brain_File(self, dir=None):
        self.robot.Generate_NN(dir)

    def Get_Empowerment(self):
        return self.selection_metrics['empowerment']

    def Has_Been_Simulated(self):
        return all(self.been_simulated)

    def Reset_Simulated(self):
        self.selection_metrics = {objective: 0 for objective in self.selection_objectives}
        self.aggregate_metrics = {}
        self.been_simulated = [False for _ in self.simulations]

    def Set_ID(self, newId):
        self.robot.Set_Id(newId)
        self.id = newId

    def Get_ID(self):
        return self.id

    def Get_Lineage(self):
        return self.lineage
