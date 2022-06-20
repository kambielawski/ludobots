import pyrosim.pyrosim as pyrosim
from pyrosim.neuralNetwork import NEURAL_NETWORK
import pybullet as p
from sensor import Sensor
from motor import Motor
import os

import constants as c

class Robot:
    def __init__(self, solutionId, urdfFileName=None, nndfFileName=None):
        self.solutionId = solutionId
        self.nndfFileName = nndfFileName
        self.urdfFileName = urdfFileName

        # optionally a body file can be passed in
        if urdfFileName:
            self.robotId = p.loadURDF(urdfFileName)
        # default to a quadruped
        else:
            self.robotId = p.loadURDF("body_quadruped.urdf")

        # optionally a brain file can be passed in
        if nndfFileName:
            self.nn = NEURAL_NETWORK(nndfFileName)
        elif not os.path.exists((nndfFileName := "brain_" + str(self.solutionId) + ".nndf")):
            # print("\nERROR: A brain file must be specified at the commandline or brain_<ID>.nndf must exist\n")
            # exit(1)
            self.nn = NEURAL_NETWORK("best_brain.nndf")
        else:
            self.nndfFileName = "brain_" + str(self.solutionId) + ".nndf"
            self.nn = NEURAL_NETWORK(self.nndfFileName)

        pyrosim.Prepare_To_Simulate(self.robotId)
        self.Prepare_To_Act()
        self.Prepare_To_Sense()

    # create Sensor object for each link & store in dictionary
    def Prepare_To_Sense(self):
        self.sensors = dict()
        for linkName in pyrosim.linkNamesToIndices:
            self.sensors[linkName] = Sensor(linkName)

    # create Motor object for each joint 
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
                desiredAngle = self.nn.Get_Value_Of(neuronName) * c.MOTOR_JOINT_RANGE
                self.motors[jointName].Set_Value(self, desiredAngle)
    
    def Y_Axis_Fitness(self):
        basePositionAndOrientation = p.getBasePositionAndOrientation(self.robotId)
        basePosition = basePositionAndOrientation[0]
        yPosition = basePosition[1]
        return yPosition
        
    def X_Axis_Fitness(self):
        # self.linkZeroState = p.getLinkState(self.robotId, 0)
        # self.positionOfLinkZero = self.linkZeroState[0]
        basePositionAndOrientation = p.getBasePositionAndOrientation(self.robotId)
        basePosition = basePositionAndOrientation[0]
        xPosition = basePosition[0]
        return yPosition

    def Get_Fitness(self):
        fitness = self.Y_Axis_Fitness()
        fitnessFile = open("tmp_" + str(self.solutionId) + ".txt", "w")
        fitnessFile.write(str(fitness))
        os.system("mv tmp_" + str(self.solutionId) + ".txt fitness_" + str(self.solutionId) + ".txt")
            

