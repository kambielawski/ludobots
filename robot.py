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
    def __init__(self, solutionId, options, dir='.'):
        self.solutionId = solutionId
        self.empowermentWindowSize = options['empowerment_window_size']
        self.motorScheme = options['motor_measure']
        self.nndfFileName = options['brain_file']
        self.urdfFileName = options['body_file']
        self.dir = dir

        self.robotId = None
        self.objectIds = None
        self.motorVals = []
        self.sensorVals = []
        self.empowerment_values = []
        self.jointAngularVelocities = []
        self.boxStartPos = None

        # Empowerment computation setup
        self.motorValBins = np.array([(i / c.NUM_MOTOR_VAL_BUCKETS) - c.MOTOR_JOINT_RANGE for i in range(c.NUM_MOTOR_NEURONS)])
        self.empowerment = 0
        self.empowermentTimesteps = 0

        while not self.robotId:
            try:
                # optionally a body file can be passed in
                if self.urdfFileName:
                    self.robotId = p.loadURDF(self.urdfFileName)
                # default to a quadruped
                else:
                    self.robotId = p.loadURDF("robots/body_quadruped.urdf")
            except:
                continue

        # optionally a brain file can be passed in
        if self.nndfFileName:
            self.nn = NEURAL_NETWORK(self.nndfFileName)
        elif not os.path.exists("brain_" + str(self.solutionId) + ".nndf"):
            # print("\nERROR: A brain file must be specified at the commandline or brain_<ID>.nndf must exist\n")
            # exit(1)
            self.nn = NEURAL_NETWORK("best_brain.nndf")
            self.nndfFileName = "best_brain.nndf"
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
        # If box-moving fitness function, get the original position of the box.
        if timestep == 0 and self.objectIds:
            self.boxStartPos = p.getBasePositionAndOrientation(self.objectIds[0])[0]
        # If tri-fitness, record fitness at simulation half
        if timestep == c.TIMESTEPS // 2:
            self.firstHalfFitness = self.Y_Axis_Fitness()
        
        # Sense
        # sensorVector = [sensor.Get_Value(timestep) for sensor in self.sensors]
        sensorVector = []
        for sensor in self.sensors:
            sensorVector.append(self.sensors[sensor].Get_Value(timestep))
        self.sensorVals.append(tuple([1 if s>0 else 0 for s in sensorVector]))

    def Think(self):
        # "think" by updating the neural network
        self.nn.Update()
        # self.nn.Print()

    def Act(self, timestep):
        # Construct action vector
        self.Compute_Action_Vector()
        
        # calculate empowerment over last k timesteps
        if timestep >= 2 * self.empowermentWindowSize-1:
            e = self.Empowerment_Window(timestep)
            self.empowerment += e
            self.empowermentTimesteps += 1
            self.empowerment_values.append(e)

    def Compute_Action_Vector(self):
        # Two action schemes: "desiredAngle" and "velocity"
        if self.motorScheme == 'DESIRED_ANGLE':
            # 1) desiredAngle 
            actionVector = []
            for neuronName in self.nn.Get_Neuron_Names():
                if self.nn.Is_Motor_Neuron(neuronName):
                    jointName = self.nn.Get_Motor_Neurons_Joint(neuronName)
                    # Neuron value will return a float in [-1,1] (tanh activation)
                    desiredAngle = self.nn.Get_Value_Of(neuronName) * c.MOTOR_JOINT_RANGE
                    actionVector.append(1 if desiredAngle > 0 else 0)
                    self.motors[jointName].Set_Value(self, desiredAngle)
            self.motorVals.append(tuple(actionVector))
            return actionVector

        elif self.motorScheme == 'VELOCITY':
            # 2) Velocity 
            actionVector = []
            for neuronName in self.nn.Get_Neuron_Names(): # Update motors in simulation
                if self.nn.Is_Motor_Neuron(neuronName):
                    jointName = self.nn.Get_Motor_Neurons_Joint(neuronName)
                    # Neuron value will return a float in [-1,1] (tanh activation)
                    desiredAngle = self.nn.Get_Value_Of(neuronName) * c.MOTOR_JOINT_RANGE
                    self.motors[jointName].Set_Value(self, desiredAngle)

            # Get actual motor angular velocities
            jointVelocityVals = [jointState[1] for jointState in p.getJointStates(self.robotId, jointIndices=range(p.getNumJoints(self.robotId)))]
            actionVector = [1 if v > 0 else 0 for v in jointVelocityVals]
            self.jointAngularVelocities.append(jointVelocityVals)
            self.motorVals.append(tuple(actionVector))
            return actionVector


    def Bucket_Motor_Val(self, actionVector):
        counts, _ = np.histogram(actionVector, self.motorValBins)
        self.motorVals = [m+c for m,c in zip(self.motorVals, counts)]
        pass
    
    def Empowerment_Window(self, timestep): 
        # convert motor and sensor states into integers
        actionz = [int(''.join([str(b) for b in A]), base=2) for A in self.motorVals[((timestep+1)-(2*self.empowermentWindowSize)):((timestep+1)-self.empowermentWindowSize)]]
        sensorz = [int(''.join([str(b) for b in S]), base=2) for S in self.sensorVals[((timestep+1)-self.empowermentWindowSize):timestep+1]]
        # Coarse grained actions, raw sensor states (both 2D arrays, flattened)
        # actionz = np.array(self.motorVals[(timestep - (2*self.empowermentWindowSize)):(timestep - self.empowermentWindowSize)]).flatten()
        # sensorz = np.array(self.sensorVals[(timestep-self.empowermentWindowSize):timestep]).flatten()
        # timeseries calculation of mutual information
        # mi = ee.mi(actionz, sensorz)
        mi = pyinform.mutual_info(actionz, sensorz, local=False)

        return mi

    def Set_Object_Ids(self, objectIds):
        self.objectIds = objectIds

    def Get_Box_Displacement(self):
        currentPos = p.getBasePositionAndOrientation(self.objectIds[0])[0]
        return np.linalg.norm([self.boxStartPos[i] - currentPos[i] for i in range(len(currentPos))])
    
    # returns average empowerment over all windows
    # N timesteps; k window size
    # returns average empowerment over ~N-k windows
    def Empowerment_Window_Average(self):
        emp = self.empowerment / self.empowermentTimesteps
        return emp

    def Empowerment_Window_Max(self):
        return max(self.empowerment_values)

    def Simulation_Empowerment(self):
        actionz = [int(''.join([str(b) for b in A]), base=2) for A in self.motorVals[:(c.TIMESTEPS //2)]]
        sensorz = [int(''.join([str(b) for b in S]), base=2) for S in self.sensorVals[(c.TIMESTEPS // 2):]]
        mi = pyinform.mutual_info(actionz, sensorz, local=False)
        return mi

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

    def Get_Empowerment(self):
        # return self.Empowerment_Window_Average()
        # return self.Simulation_Empowerment()
        # return self.Empowerment_Window()
        # return self.Empowerment_Window_Average()
        return self.Empowerment_Window_Max()

    def Print_Objectives(self):
        displacement = self.Y_Axis_Fitness()
        empowerment = self.Get_Empowerment()
        box_displacement = None if self.objectIds == None else self.Get_Box_Displacement()
        first_half_displacement = self.firstHalfFitness
        second_half_displacement = displacement - first_half_displacement
        random = np.random.random()
        print(f'({str(displacement)} {str(empowerment)} {str(first_half_displacement)} {str(second_half_displacement)} {str(random)} {str(box_displacement)})')

    def Get_Fitness(self, objective='tri_fitness'):
        '''
        Writes both the fitness and the empowerment to stdout
        '''
        if objective == 'emp_fitness':
            fitness = self.Y_Axis_Fitness()
            empowerment = self.Get_Empowerment()
            print(f'({str(fitness)} {str(empowerment)})')
        elif objective == 'tri_fitness':
            fitness1 = self.firstHalfFitness
            fitness2 = self.Y_Axis_Fitness()
            print(f'({str(fitness1)} {str(fitness2)})')

