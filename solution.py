import os
import numpy as np
import pyrosim.pyrosim as pyrosim
import random
import time

from box import Box
from robots.quadruped import Quadruped
import constants as c

class Solution:
    def __init__(self, solutionId):
        self.id = solutionId
        self.weights = np.random.rand(c.NUM_MOTOR_NEURONS,c.NUM_SENSOR_NEURONS)*2 - 1

    def Start_Simulation(self, runMode="DIRECT"):
        self.runMode=runMode
        self.Create_World()
        self.Generate_Robot()

        # execute simulation with runMode and solution ID and brainfile if it exists
        run_command = "python3 simulate.py " + runMode + " " + str(self.id) + " brain_" + str(self.id) + ".nndf"
        if not c.DEBUG:
            run_command += " >log.txt 2>&1" 
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
        self.fitness = float(fitnessFile.read())

    def Mutate(self):
        randRow = random.randint(0,c.NUM_MOTOR_NEURONS-1)
        randCol = random.randint(0,c.NUM_SENSOR_NEURONS-1)

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

    def Generate_Robot(self):
        self.robot = Quadruped(self.id, self.weights,0,0,1)
        # self.robot.Generate_Fully_Connected_Synapses()

    def Get_Fitness(self):
        return self.fitness

    def Set_ID(self, newId):
        self.id = newId

    def Get_ID(self):
        return self.id
