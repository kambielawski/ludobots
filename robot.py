import pyrosim.pyrosim as pyrosim
from pyrosim.neuralNetwork import NEURAL_NETWORK
import pybullet as p
import numpy as np
from pyinform.dist import Dist
from pyinform.shannon import mutual_info
import pyinform
from sensor import Sensor
from motor import Motor
import os
from sys import platform

import constants as c

class Robot:
    def __init__(self, solutionId, urdfFileName=None, nndfFileName=None, empowermentWindowSize=c.DEFAULT_EMPOWERMENT_WINDOW_SIZE):
        self.solutionId = solutionId
        self.nndfFileName = nndfFileName
        self.urdfFileName = urdfFileName
        self.motorVals = []
        self.sensorVals = []
        self.empowermentWindowSize = empowermentWindowSize

        # Empowerment computation setup
        self.motorValBins = np.array([(i / c.NUM_MOTOR_VAL_BUCKETS) - c.MOTOR_JOINT_RANGE for i in range(c.NUM_MOTOR_NEURONS)])
        self.empowerment = 0
        self.empowermentTimesteps = 0

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

    def __del__(self):
        pass

    # create Sensor object for each link & store in dictionary
    def Prepare_To_Sense(self):
        self.sensors = dict()
        for linkName in pyrosim.linkNamesToIndices:
            if linkName != 'Torso': self.sensors[linkName] = Sensor(linkName)

    # create Motor object for each joint 
    def Prepare_To_Act(self):
        self.motors = dict()
        for jointName in pyrosim.jointNamesToIndices:
            self.motors[jointName] = Motor(jointName)

    def Sense(self, timestep):
        sensorVector = []
        for sensor in self.sensors:
            sensorVector.append(self.sensors[sensor].Get_Value(timestep))
        self.sensorVals.append(tuple([1 if s>0 else 0 for s in sensorVector]))
        # calculate empowerment over last k timesteps
        # if timestep >= 2 * self.empowermentWindowSize:
        #     e = self.Empowerment_Window(timestep)
        #     self.empowerment += e
        #     self.empowermentTimesteps += 1

    def Think(self):
        # "think" by updating the neural network
        self.nn.Update()
        # self.nn.Print()

    def Act(self, timestep):
        actionVector = []
        for neuronName in self.nn.Get_Neuron_Names():
            if self.nn.Is_Motor_Neuron(neuronName):
                jointName = self.nn.Get_Motor_Neurons_Joint(neuronName)
                # Neuron value will return a float in [-1,1] (tanh activation)
                desiredAngle = self.nn.Get_Value_Of(neuronName) * c.MOTOR_JOINT_RANGE
                actionVector.append(1 if desiredAngle > 0 else 0)
                self.motors[jointName].Set_Value(self, desiredAngle)
        # actionVector.append(0)
        self.motorVals.append(tuple(actionVector))

    def Bucket_Motor_Val(self, actionVector):
        counts, _ = np.histogram(actionVector, self.motorValBins)
        self.motorVals = [m+c for m,c in zip(self.motorVals, counts)]
        pass
    
    def Empowerment_Window(self, timestep):        # convert motor and sensor states into integers
        actionz = [int(''.join(str(b) for b in A), base=2) for A in self.motorVals[(timestep-(2*self.empowermentWindowSize)):(timestep-self.empowermentWindowSize)]]
        sensorz = [int(''.join(str(b) for b in S), base=2) for S in self.sensorVals[(timestep-self.empowermentWindowSize):timestep]]
        
        # timeseries calculation of mutual information
        mi = pyinform.mutual_info(actionz, sensorz)

        return mi
    
    # returns average empowerment over all windows
    # N timesteps; k window size
    # returns average empowerment over ~N-k windows
    def Empowerment_Fitness(self):
        yPosition = self.Y_Axis_Fitness()
        emp = self.empowerment / self.empowermentTimesteps
        return yPosition, emp

    def Simulation_Empowerment_Fitness(self):
        yPos = self.Y_Axis_Fitness()
        motorDist = Dist(np.array(self.motorVals).flatten())
        sensorDist = Dist(np.array(self.sensorVals).flatten())
        mi = pyinform.mutual_info(sensorDist, motorDist, local=False)
        return yPos, mi

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
        return xPosition

    def Get_Fitness(self):
        displacement, emp = self.Simulation_Empowerment_Fitness()
        fitness = displacement + 10*emp
        fitnessFile = open("tmp_" + str(self.solutionId) + ".txt", "w")
        fitnessFile.write(str(fitness))
        if platform == 'win32':
            os.system("echo " + str(fitness) + " > fitness_" + str(self.solutionId) + ".txt")
        else:
            os.system("mv tmp_" + str(self.solutionId) + ".txt fitness_" + str(self.solutionId) + ".txt")
        

