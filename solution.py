import os
from sys import platform
import numpy as np
import pyrosim.pyrosim as pyrosim
import random
import time

from box import Box
from robots.quadruped import Quadruped
from robots.hexapod import Hexapod
import constants as c

class Solution:
    def __init__(self, solutionId):
        self.id = solutionId
        self.robot = Quadruped(self.id)
        self.weights = self.robot.Generate_Weights()
        self.age = 1
        self.empowerment = 0
        # self.weights = np.random.rand(c.NUM_MOTOR_NEURONS,c.NUM_SENSOR_NEURONS)*2 - 1

    def Start_Simulation(self, runMode="DIRECT"):
        self.runMode=runMode
        self.Create_World()
        self.robot.Generate_Robot(self.weights, 0,0,1)

        # execute simulation with runMode and solution ID and brainfile if it exists
        run_command = "python simulate.py " + runMode + " " + str(self.id) + " brain_" + str(self.id) + ".nndf " + self.robot.Get_Body_File()
        if c.DEBUG:
            run_command += " >log.txt 2>&1" 
        if platform == 'win32':
            run_command = 'START /B ' + run_command
        else:
            run_command += " &"

        # run simulation
        os.system(run_command)

    def Wait_For_Simulation_To_End(self):
        fitnessFileName = "fitness_" + str(self.id) + ".txt"

        while not os.path.exists(fitnessFileName):
            time.sleep(0.01)

        fitnessFile = open(fitnessFileName, "r")
        while fitnessFile.read() == '':
            fitnessFile.seek(0)
            time.sleep(0.01)

        fitnessFile.seek(0)
        fitnessFileContent = [n.strip('\"\ \n') for n in fitnessFile.readlines()[0].split(' ')]
        self.fitness = float(fitnessFileContent[0])
        self.empowerment = float(fitnessFileContent[1])

    def Mutate(self):
        randRow = random.randint(0,self.robot.NUM_MOTOR_NEURONS-1)
        randCol = random.randint(0,self.robot.NUM_SENSOR_NEURONS-1)

        self.robot.weights[randRow][randCol] = random.random() * 2 - 1

        # self.weights[randRow][randCol] = random.random()*2-1

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
        pyrosim.Start_SDF("world_" + str(self.id) + ".sdf")
        self.Generate_Environment()
        pyrosim.End()

    def Increment_Age(self):
        self.age += 1

    def Get_Robot_Empowerment(self):
        return self.Get_Empowerment()

    def Get_Age(self):
        return self.age

    def Get_Fitness(self):
        return self.fitness

    def Get_Empowerment(self):
        return self.empowerment

    def Set_ID(self, newId):
        self.robot.Set_Id(newId)
        self.id = newId

    def Get_ID(self):
        return self.id
