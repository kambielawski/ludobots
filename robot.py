import pyrosim.pyrosim as pyrosim
from pyrosim.neuralNetwork import NEURAL_NETWORK
import pybullet as p
from sensor import Sensor
from motor import Motor
import os

import constants as c

class Robot:
    def __init__(self, solutionId, urdfFileName, brainFileName=None):
        self.robotId = p.loadURDF(urdfFileName)
        self.solutionId = solutionId
        self.brainFileName = brainFileName

        # optionally a brain file can be passed in
        if brainFileName:
            self.nn = NEURAL_NETWORK(brainFileName)
        elif not os.path.exists((brainFileName := "brain_" + str(self.solutionId) + ".nndf")):
            print("\nERROR: A brain file must be specified at the commandline or brain_<ID>.nndf must exist\n")
            exit(1)
        else:
            self.brainFileName = "brain_" + str(self.solutionId) + ".nndf"
            self.nn = NEURAL_NETWORK(self.BrainFileName)

        pyrosim.Prepare_To_Simulate(self.robotId)
        self.Prepare_To_Act()
        self.Prepare_To_Sense()

        # clean up NN file (it has already been read into a data structure)
        # os.system("rm brain_" + str(self.solutionId) + ".nndf")
         

    # create Sensor object for each link & store in dictionary
    def Prepare_To_Sense(self):
        self.sensors = dict()
        for linkName in pyrosim.linkNamesToIndices:
            self.sensors[linkName] = Sensor(linkName)

    # create Motor object for each joint 
    def Prepare_To_Act(self):
        self.motors = dict()
        print(pyrosim.jointNamesToIndices)
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
                desiredAngle = self.nn.Get_Value_Of(neuronName) * c.MOTOR_JOINT_RANGE
                self.motors[jointName].Set_Value(self, desiredAngle)

    def Get_Fitness(self):
        # self.linkZeroState = p.getLinkState(self.robotId, 0)
        # self.positionOfLinkZero = self.linkZeroState[0]
        basePositionAndOrientation = p.getBasePositionAndOrientation(self.robotId)
        basePosition = basePositionAndOrientation[0]
        xPosition = basePosition[0]
        fitnessFile = open("tmp_" + str(self.solutionId) + ".txt", "w")
        fitnessFile.write(str(xPosition))
        os.system("mv tmp_" + str(self.solutionId) + ".txt fitness_" + str(self.solutionId) + ".txt")
            

