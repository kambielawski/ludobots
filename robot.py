import pyrosim.pyrosim as pyrosim
from pyrosim.neuralNetwork import NEURAL_NETWORK
import pybullet as p
from sensor import Sensor
from motor import Motor
import os

class Robot:
    def __init__(self, urdfFileName, solutionId):
        self.robotId = p.loadURDF(urdfFileName)
        self.solutionId = solutionId
        self.nn = NEURAL_NETWORK("brain_" + str(self.solutionId) + ".nndf")
        pyrosim.Prepare_To_Simulate(self.robotId)

        self.Prepare_To_Act()
        self.Prepare_To_Sense()

        # clean up NN file (it has already been read into a data structure)
        os.system("rm brain_" + str(self.solutionId) + ".nndf")
         

    # create Sensor object for each link & store in dictionary
    def Prepare_To_Sense(self):
        self.sensors = dict()
        for linkName in pyrosim.linkNamesToIndices:
            self.sensors[linkName] = Sensor(linkName)

    def Prepare_To_Act(self):
        self.motors = dict()
        for jointName in pyrosim.jointNamesToIndices:
            self.motors[jointName] = Motor(jointName)

    def Sense(self, i):
        for sensor in self.sensors:
            self.sensors[sensor].Get_Value(i)

    def Think(self):
        # "think" by updating the neural network
        self.nn.Update()
        # self.nn.Print()

    def Act(self, i):
        for neuronName in self.nn.Get_Neuron_Names():
            if self.nn.Is_Motor_Neuron(neuronName):
                jointName = self.nn.Get_Motor_Neurons_Joint(neuronName)
                desiredAngle = self.nn.Get_Value_Of(neuronName)
                self.motors[jointName].Set_Value(self, desiredAngle)

    def Get_Fitness(self):
        self.linkZeroState = p.getLinkState(self.robotId, 0)
        self.positionOfLinkZero = self.linkZeroState[0]
        fitnessFile = open("tmp_" + str(self.solutionId) + ".txt", "w")
        fitnessFile.write(str(self.positionOfLinkZero[0]))
        os.system("mv tmp_" + str(self.solutionId) + ".txt fitness_" + str(self.solutionId) + ".txt")
            

