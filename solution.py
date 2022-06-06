import os
import numpy as np
import pyrosim.pyrosim as pyrosim
import random
import time

from box import Box

class Solution:
    def __init__(self, solutionId):
        self.id = solutionId
        self.weights = np.random.rand(3,2)*2 - 1

    def Evaluate(self, runMode="DIRECT"):
        self.runMode=runMode
        self.Create_World()
        self.Generate_Body(
            robotId=0,
            start_x=0,
            start_y=0,
            start_z=1.5
        )
        self.Generate_Brain()

        # run simulation
        os.system("python3 simulate.py " + runMode + " " + str(self.id) + " " + " &")

        fitnessFileName = "fitness_" + str(self.id) + ".txt"

        while not os.path.exists(fitnessFileName):
            time.sleep(0.01)

        fitnessFile = open(fitnessFileName, "r")
        self.fitness = float(fitnessFile.read())
        print(self.fitness)

    def Start_Simulation(self, runMode="DIRECT"):
        self.runMode=runMode
        self.Create_World()
        self.Generate_Body(
            robotId=0,
            start_x=0,
            start_y=0,
            start_z=1.5
        )
        self.Generate_Brain()

        # run simulation
        os.system("python3 simulate.py " + runMode + " " + str(self.id) + " " + " &")

    def Wait_For_Simulation_To_End(self):
        fitnessFileName = "fitness_" + str(self.id) + ".txt"

        while not os.path.exists(fitnessFileName):
            time.sleep(0.01)

        fitnessFile = open(fitnessFileName, "r")
        print(fitnessFile)
        self.fitness = float(fitnessFile.read())
        os.system("rm fitness_" + str(self.id) + ".txt")

    def Mutate(self):
        randRow = random.randint(0,2)
        randCol = random.randint(0,1)

        self.weights[randRow][randCol] = random.random()*2-1

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
        pyrosim.Start_SDF("world.sdf")
        self.Generate_Environment()
        pyrosim.End()

    def Generate_Body(self, robotId, start_x, start_y, start_z):
        # .urdf files are broadly used in the robotics community
        # "Universal Robot Description File"
        pyrosim.Start_URDF("body_" + str(robotId) + ".urdf")

        # the first link and the first joint have absolute positions
        pyrosim.Send_Cube(name="Torso", pos=[start_x, start_y, start_z], size=[1,1,1])
        pyrosim.Send_Joint(name="Torso_BackLeg", parent="Torso", child="BackLeg", type="revolute", position=[start_x-0.5, start_y,start_z-0.5])
        # now all links & joints with an upstream joint have positions relative to the upstream joint
        pyrosim.Send_Joint(name="Torso_FrontLeg", parent="Torso", child="FrontLeg", type="revolute", position=[start_x+0.5, start_y,start_z-0.5])
        pyrosim.Send_Cube(name="FrontLeg", pos=[0.5,0,-0.5], size=[1,1,1])
        pyrosim.Send_Cube(name="BackLeg", pos=[-0.5,0,-0.5], size=[1,1,1])

        pyrosim.End()

    # generates random starting weight values
    def Generate_Fully_Connected_Synapses(self):
        for s in range(3):
            for m in range(2):
                pyrosim.Send_Synapse(
                    sourceNeuronName=s,
                    targetNeuronName=m+3,
                    weight=self.weights[s][m]
                )
        
    def Generate_Brain(self):
        # .nndf files are just used in Pyrosim
        # "Neural Network Description File"
        pyrosim.Start_NeuralNetwork("brain_" + str(self.id) + ".nndf")

        pyrosim.Send_Sensor_Neuron(name=0, linkName="Torso")
        pyrosim.Send_Sensor_Neuron(name=1, linkName="BackLeg")
        pyrosim.Send_Sensor_Neuron(name=2, linkName="FrontLeg")

        pyrosim.Send_Motor_Neuron(name=3, jointName="Torso_BackLeg")
        pyrosim.Send_Motor_Neuron(name=4, jointName="Torso_FrontLeg")

        self.Generate_Fully_Connected_Synapses()

        pyrosim.End()

    def Get_Fitness(self):
        return self.fitness

    def Set_ID(self, newId):
        self.id = newId
