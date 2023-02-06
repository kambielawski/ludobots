import os
from sys import platform
import numpy as np
import pyrosim.pyrosim as pyrosim
import random
import subprocess
import re

from box import Box
from robots.quadruped import Quadruped
from robots.hexapod import Hexapod
import constants as c

class Solution:
    def __init__(self, solutionId, lineage, constants, dir='.'):
        self.id = solutionId
        self.robot = Quadruped(self.id, dir=dir)
        self.weights = self.robot.Generate_Weights()
        self.age = 1
        self.empowerment = 0
        self.been_simulated = False
        self.lineage = lineage
        self.objectives = constants['objectives']
        self.empowerment_window_size = constants['empowerment_window_size'] or c.TIMESTEPS // 2
        self.motor_measure = constants['motor_measure']

        self.dir = dir

    def Run_Simulation(self, runMode="DIRECT"):
        self.runMode=runMode
        self.Create_World()
        self.robot.Generate_Robot(self.weights, 0,0,1)

        sp = subprocess.Popen(['python3', 'simulate.py', 
                                runMode, 
                                str(self.id), 
                                f'{self.dir}/brain_{self.id}.nndf', 
                                self.robot.Get_Body_File(), 
                                '--directory', self.dir,
                                '--objects_file', self.worldFile,
                                '--motor_measure', self.motor_measure],
                                # '--empowerment_window_size', str(self.empowerment_window_size)],
                                stdout=subprocess.PIPE)

        # Parse standard output from subprocess
        stdout, stderr = sp.communicate()
        sp.wait()
        out_str = stdout.decode('utf-8')
        fitness_metrics = re.search('\(.+\)', out_str)[0].strip('()').split(' ')
        self.selection_metrics = {
            'displacement': float(fitness_metrics[0]),
            'empowerment': float(fitness_metrics[1]),
            'first_half_displacement': float(fitness_metrics[2]),
            'second_half_displacement': float(fitness_metrics[3]),
            'random': float(fitness_metrics[4]),
            'box_displacement': float(fitness_metrics[5])
        }

        self.been_simulated = True # Set simulated flag

        return self.selection_metrics

    def Mutate(self):
        randRow = random.randint(0,self.robot.NUM_MOTOR_NEURONS-1)
        randCol = random.randint(0,self.robot.NUM_SENSOR_NEURONS-1)

        self.robot.weights[randRow][randCol] = random.random() * 2 - 1

    def Generate_Environment(self):
        cubes = []
        l = 1
        w = 1
        h = 1
        x = -4
        y = 4
        z = 0.5
        cubes.append(Box(dims=[l,w,h], pos=[x,y,z]))
        for cube in cubes:
            pyrosim.Send_Cube(name="Box", pos=cube.pos, size=cube.dims)
    
    def Create_World(self):
        self.worldFile = f'{self.dir}/world_{self.id}.sdf'
        os.system(f'cp {self.dir}/world.sdf {self.worldFile}')
        pyrosim.Start_SDF(f"{self.dir}/world_{self.id}.sdf")
        self.Generate_Environment()
        pyrosim.End()

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
