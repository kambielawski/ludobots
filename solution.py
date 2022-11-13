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
    def __init__(self, solutionId, lineage, objective, dir='.'):
        self.id = solutionId
        self.robot = Quadruped(self.id, dir=dir)
        self.weights = self.robot.Generate_Weights()
        self.age = 1
        self.empowerment = 0
        self.been_simulated = False
        self.lineage = lineage
        self.objective = objective
        self.dir = dir

    def Run_Simulation(self, runMode="DIRECT"):
        self.runMode=runMode
        self.Create_World()
        self.robot.Generate_Robot(self.weights, 0,0,1)

        self.sp = subprocess.Popen(['python3', 'simulate.py', 
                                runMode, 
                                str(self.id), 
                                f'{self.dir}/brain_{self.id}.nndf', 
                                self.robot.Get_Body_File(), 
                                self.objective,
                                '--directory', self.dir],
                                stdout=subprocess.PIPE)

        # Parse standard output from subprocess
        stdout, stderr = self.sp.communicate()
        self.sp.wait()
        out_str = stdout.decode('utf-8')
        fitness_metrics = re.search('\(.+\)', out_str)[0].strip('()').split(' ')

        if self.objective == 'tri_fitness':
            self.firstHalfFitness = float(fitness_metrics[0])
            self.secondHalfFitness = float(fitness_metrics[1])
        elif self.objective == 'emp_fitness':
            self.fitness = float(fitness_metrics[0])
            self.empowerment = float(fitness_metrics[1])
        
        # Need to reset self.sp because Popen object is not picklable
        self.sp = None
        self.been_simulated = True # Set simulated flag

        return re.search('\(.+\)', out_str)[0]


    def Start_Simulation(self, runMode="DIRECT"):
        self.runMode=runMode
        self.Create_World()
        self.robot.Generate_Robot(self.weights, 0,0,1)

        # execute simulation with runMode and solution ID and brainfile if it exists
        run_command = f"python3 simulate.py {runMode} {str(self.id)} {self.dir}/brain_{self.id}.nndf {self.robot.Get_Body_File()} {self.objective} --directory {self.dir}"
        
        self.sp = subprocess.Popen(['python3', 'simulate.py', 
                                runMode, 
                                str(self.id), 
                                f'{self.dir}/brain_{self.id}.nndf', 
                                self.robot.Get_Body_File(), 
                                self.objective,
                                '--directory', self.dir],
                                stdout=subprocess.PIPE)

        # if c.DEBUG:
        #     run_command += " >log.txt 2>&1" 
        # if platform == 'win32':
        #     run_command = 'START /B ' + run_command
        # else:
        #     run_command += " &"

        # run simulation
        # os.system(run_command)

    def Wait_For_Simulation_To_End(self):
        # fitnessFileName = f"{self.dir}/fitness_{self.id}.txt"

        # # Wait for fitness file to be readable
        # while not os.path.exists(fitnessFileName):
        #     time.sleep(0.01)
        # fitnessFile = open(fitnessFileName, "r")
        # while fitnessFile.read() == '':
        #     fitnessFile.seek(0)
        #     time.sleep(0.01)

        # # Read file contents
        # fitnessFile.seek(0)
        # fitnessFileContent = [n.strip('\"\ \n') for n in fitnessFile.readlines()[0].split(' ')]
        # fitnessFile.close()
        out_str = self.sp.stdout.read().decode('utf-8')
        print(re.search('\(.+\)', out_str)[0])
        exit()
        print(q)
        stdout, stderr = self.sp.communicate()
        self.sp.wait()
        out_str = stdout.decode('utf-8')
        

        # Read values into objective variables
        # if self.objective == 'tri_fitness':
        #     self.firstHalfFitness = float(fitnessFileContent[0])
        #     self.secondHalfFitness = float(fitnessFileContent[1])
        # elif self.objective == 'emp_fitness':
        #     self.fitness = float(fitnessFileContent[0])
        #     self.empowerment = float(fitnessFileContent[1])
        
        self.been_simulated = True # Set simulated flag

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
        os.system(f'cp {self.dir}/world.sdf {self.dir}/world_{self.id}.sdf')
        pyrosim.Start_SDF(f"{self.dir}/world_{self.id}.sdf")
        self.Generate_Environment()
        pyrosim.End()

    def Increment_Age(self):
        self.age += 1

    def Get_Age(self):
        return self.age

    def Get_Primary_Objective(self):
        if self.objective == 'tri_fitness':
            return self.secondHalfFitness
        elif self.objective == 'emp_fitness':
            return self.fitness

    def Get_Fitness(self):
        if self.objective == 'tri_fitness':
            return (self.firstHalfFitness, self.secondHalfFitness)
        elif self.objective == 'emp_fitness':
            return self.fitness

    def Get_Empowerment(self):
        return self.empowerment

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
