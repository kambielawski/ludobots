import os
import pyrosim.pyrosim as pyrosim
import random
import subprocess
import re

from robots.quadruped import Quadruped
from robots.hexapod import Hexapod
from robots.biped import Biped
from robots.snake4 import Snake4

class Solution:
    def __init__(self, solutionId, lineage, constants, dir='.'):
        self.id = solutionId
        self.age = 1
        self.empowerment = 0
        self.been_simulated = False
        self.lineage = lineage
        self.objectives = constants['objectives']
        self.empowerment_window_size = constants['empowerment_window_size']
        self.motor_measure = constants['motor_measure']
        self.morphology = constants['morphology']

        # TODO: generalize robot morphology selection
        if self.morphology == 'quadruped':
            self.robot = Quadruped(self.id, dir=dir)
        elif self.morphology == 'hexapod':
            self.robot = Hexapod(self.id, dir=dir)
        elif self.morphology == 'biped':
            self.robot = Biped(self.id, dir=dir)
        elif self.morphology == 'snake4':
            self.robot = Snake4(self.id, dir=dir)
            
        self.weights = self.robot.Generate_Weights()

        self.dir = dir

    def Run_Simulation(self, runMode="DIRECT"):
        self.runMode=runMode
        self.Create_World()
        self.robot.Generate_Robot(self.weights, 0,0,1) # TODO: generalize the starting position for robots

        sp = subprocess.Popen(['python3', 'simulate.py', 
                                runMode, 
                                str(self.id), 
                                f'{self.dir}/brain_{self.id}.nndf', 
                                self.robot.Get_Body_File(), 
                                '--directory', self.dir,
                                '--objects_file', self.worldFile,
                                '--motor_measure', self.motor_measure,
                                '--empowerment_window_size', str(self.empowerment_window_size)],
                                stdout=subprocess.PIPE)

        # Parse standard output from subprocess
        stdout, stderr = sp.communicate()
        sp.wait()
        out_str = stdout.decode()
        fitness_metrics = re.search('\(.+\)', out_str)[0].strip('()').split(' ')
        self.selection_metrics = {
            'displacement': float(fitness_metrics[0]),
            'empowerment': float(fitness_metrics[1]),
            'first_half_displacement': float(fitness_metrics[2]),
            'second_half_displacement': float(fitness_metrics[3]),
            'random': float(fitness_metrics[4]),
            'boxdisplacement': float(fitness_metrics[5]) if fitness_metrics[5] != 'None' else 0,
            'first_half_box_displacement': float(fitness_metrics[6]) if fitness_metrics[6] != 'None' else 0,
            'second_half_box_displacement': float(fitness_metrics[7]) if fitness_metrics[7] != 'None' else 0
        }

        self.been_simulated = True # Set simulated flag

        return self.selection_metrics

    def Mutate(self):
        randRow = random.randint(0,self.robot.NUM_MOTOR_NEURONS-1)
        randCol = random.randint(0,self.robot.NUM_SENSOR_NEURONS-1)

        self.robot.weights[randRow][randCol] = random.random() * 2 - 1
    
    def Create_World(self):
        self.worldFile = f'{self.dir}/world_{self.id}.sdf'
        os.system(f'cp {self.dir}/world.sdf {self.worldFile}')

    def Dominates_Other(self, other):
        assert self.objectives == other.objectives

        dominates = [self.age <= other.Get_Age()]
        # We have 1) Fitness, 2) First-half Fitness, 3) Second-half Fitness, 4) Empowerment
        for objective in self.objectives:
            # Always maximize these selection metrics
            dominates.append(self.selection_metrics[objective] >= other.selection_metrics[objective])

        return all(dominates)

    def Increment_Age(self):
        self.age += 1

    def Get_Age(self):
        return self.age

    def Get_Primary_Objective(self):
        # First objective listed in self.objectives will be the "primary objective"
        return self.selection_metrics[self.objectives[0]]

    def Regenerate_Brain_File(self):
        self.robot.Generate_NN()

    def Get_Fitness(self):
        return self.selection_metrics['displacement']

    def Get_Empowerment(self):
        return self.selection_metrics['empowerment']

    def Has_Been_Simulated(self):
        return self.been_simulated

    def Reset_Simulated(self):
        self.been_simulated = False

    def Set_ID(self, newId):
        self.robot.Set_Id(newId)
        self.id = newId

    def Get_ID(self):
        return self.id

    def Get_Lineage(self):
        return self.lineage
