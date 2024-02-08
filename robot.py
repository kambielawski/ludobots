"""Robot class for the Pyrosim environment."""
import pyrosim.pyrosim as pyrosim
from pyrosim.neuralNetwork import NEURAL_NETWORK
import pybullet as p
import numpy as np
import random
import math
import pyinform
from sensor import Sensor
from motor import Motor

#TODO: Migrate these to a config file
TIMESTEPS = 1000
MOTOR_JOINT_RANGE = 0.5

class Robot:
    """Robot class for the Pyrosim environment."""
    def __init__(self, solutionId, options, dir='.'):
        self.solutionId = solutionId
        self.empowermentWindowSize = options['empowerment_window_size']
        self.motorScheme = options['motor_measure']
        self.nndfFileName = options['brain_file']
        self.urdfFileName = options['body_file']
        self.morphology = self.urdfFileName.split('.')[0].split('_')[1]
        self.dir = dir
        try:
            self.robotId = p.loadURDF(self.urdfFileName)
        except:
            print(f'Error loading URDF file: {self.urdfFileName}')
        self.objectIds = None
        self.motorVals = []
        self.sensorVals = []
        self.positionVals = []
        self.jointAngularVelocities = []
        self.boxStartPos = None

        # Empowerment computation setup
        self.empowerment = 0
        self.empowermentTimesteps = 0
        self.empowerment_values = []

        # Optionally a brain file can be passed in
        if self.nndfFileName:
            self.nn = NEURAL_NETWORK(self.nndfFileName)
        else:
            self.nndfFileName = "brain_" + str(self.solutionId) + ".nndf"
            self.nn = NEURAL_NETWORK(self.nndfFileName)

        pyrosim.Prepare_To_Simulate(self.robotId)
        self.Prepare_To_Act()
        self.Prepare_To_Sense()

    def __del__(self):
        pass

    def Prepare_To_Sense(self):
        """Create Sensor object for each link & store in dictionary."""
        self.sensors = dict()
        for linkName in pyrosim.linkNamesToIndices:
            if linkName != 'Torso': self.sensors[linkName] = Sensor(linkName, TIMESTEPS)

    def Prepare_To_Act(self):
        """Create Motor object for each joint."""
        self.motors = dict()
        for jointName in pyrosim.jointNamesToIndices:
            self.motors[jointName] = Motor(jointName)

    def Sense(self, timestep):
        """Sense the environment and update sensor values."""
        # If box-moving fitness function, get the original position of the box.
        if timestep == 0 and self.objectIds:
            self.boxStartPos = p.getBasePositionAndOrientation(self.objectIds[0])[0]
        # If tri-fitness, record fitness at simulation half
        if timestep == TIMESTEPS // 2:
            self.firstHalfFitness = self.Y_Axis_Displacement()
            self.firstHalfBoxDisplacement = None if self.objectIds == None else self.Get_Box_Displacement()

        robot_position = p.getBasePositionAndOrientation(self.robotId)[0]
        self.positionVals.append(robot_position)

        # Sense
        sensor_vector = []
        for _, sensor in self.sensors.items():
            sensor_vector.append(sensor.Get_Value(timestep))
        self.sensorVals.append(tuple([1 if s>0 else 0 for s in sensor_vector]))

    def Think(self):
        """Think about the environment and update motor values."""
        self.nn.Update()

    def Act(self, timestep):
        """Act on the environment."""
        # Construct action vector
        self.Compute_Action_Vector()
        
        # calculate empowerment over last k timesteps
        if timestep >= 2 * self.empowermentWindowSize-1:
            e = self.Empowerment_Window(timestep)
            self.empowerment += e
            self.empowermentTimesteps += 1
            self.empowerment_values.append(e)

    def Generate_Random_Force_Vector(self, magnitude):
        """Generate a random force vector of a given magnitude."""
        theta = random.uniform(0, 2 * math.pi)  # azimuthal angle in [0, 2*pi]
        phi = random.uniform(0, math.pi)  # polar angle in [0, pi]

        fx = magnitude * math.sin(phi) * math.cos(theta)
        fy = magnitude * math.sin(phi) * math.sin(theta)
        fz = magnitude * math.cos(phi)

        return [fx, fy, fz]

    def Apply_Random_Force_Vector(self, force_magnitude):
        """Apply a random force vector to the robot."""
        force_vector = self.Generate_Random_Force_Vector(force_magnitude)
        robot_position = p.getBasePositionAndOrientation(self.robotId)[0]
        p.applyExternalForce(objectUniqueId=self.robotId, linkIndex=-1, forceObj=force_vector, posObj=robot_position, flags=p.WORLD_FRAME)

    def Get_Position_Values(self):
        """ Return the position values of the robot over the course of the simulation."""
        return self.positionVals

    def Compute_Action_Vector(self):
        """Compute the action vector based on the motor scheme."""
        # Two action schemes: "desiredAngle" and "velocity"
        if self.motorScheme == 'DESIRED_ANGLE':
            # 1) desiredAngle 
            actionVector = []
            for neuronName in self.nn.Get_Neuron_Names():
                if self.nn.Is_Motor_Neuron(neuronName):
                    jointName = self.nn.Get_Motor_Neurons_Joint(neuronName)
                    # Neuron value will return a float in [-1,1] (tanh activation)
                    desiredAngle = self.nn.Get_Value_Of(neuronName) * MOTOR_JOINT_RANGE
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
                    desiredAngle = self.nn.Get_Value_Of(neuronName) * MOTOR_JOINT_RANGE
                    self.motors[jointName].Set_Value(self, desiredAngle)

            # Get actual motor angular velocities
            jointVelocityVals = [jointState[1] for jointState in p.getJointStates(self.robotId, jointIndices=range(p.getNumJoints(self.robotId)))]
            actionVector = [1 if v > 0 else 0 for v in jointVelocityVals]
            self.jointAngularVelocities.append(jointVelocityVals)
            self.motorVals.append(tuple(actionVector))
            return actionVector
    
    def Empowerment_Window(self, timestep): 
        """Compute empowerment over last k timesteps."""
        # Convert motor and sensor states into integers
        self.actionz = [int(''.join([str(b) for b in A]), base=2) for A in self.motorVals[((timestep+1)-(2*self.empowermentWindowSize)):((timestep+1)-self.empowermentWindowSize)]]
        self.sensorz = [int(''.join([str(b) for b in S]), base=2) for S in self.sensorVals[((timestep+1)-self.empowermentWindowSize):timestep+1]]

        # Compute Mutual Information
        mi = pyinform.mutual_info(self.actionz, self.sensorz, local=False)

        return mi

    def Set_Object_Ids(self, objectIds):
        """Set the object IDs for the robot to sense."""
        self.objectIds = objectIds

    def Get_Box_Displacement(self):
        """Return the displacement of the box from its original position."""
        current_pos = p.getBasePositionAndOrientation(self.objectIds[0])[0]
        return np.linalg.norm([self.boxStartPos[i] - current_pos[i] for i in range(len(current_pos))])

    def Simulation_Empowerment(self):
        """Compute empowerment over the entire simulation."""
        self.actionz = [int(''.join([str(b) for b in A]), base=2) for A in self.motorVals[:(TIMESTEPS //2)]]
        self.sensorz = [int(''.join([str(b) for b in S]), base=2) for S in self.sensorVals[(TIMESTEPS // 2):]]
        mi = pyinform.mutual_info(self.actionz, self.sensorz, local=False)
        return mi

    def Y_Axis_Displacement(self):
        """Return the displacement of the robot in the y-axis."""
        basePositionAndOrientation = p.getBasePositionAndOrientation(self.robotId)
        basePosition = basePositionAndOrientation[0]
        yPosition = basePosition[1]
        return yPosition
        
    def X_Axis_Displacement(self):
        """Return the displacement of the robot in the x-axis."""
        basePositionAndOrientation = p.getBasePositionAndOrientation(self.robotId)
        basePosition = basePositionAndOrientation[0]
        xPosition = basePosition[0]
        return xPosition

    def Get_Empowerment(self):
        """Return the empowerment value."""
        return np.mean(self.empowerment_values)

    def Print_NN(self):
        """Print the neural network synapse weights."""
        print([(s, self.nn.synapses[s].weight) for s in self.nn.synapses])

    def Print_Objectives(self):
        """Print the robot's objectives."""
        displacement = self.Y_Axis_Displacement()
        empowerment = self.Get_Empowerment()
        box_displacement = None if self.objectIds == None else self.Get_Box_Displacement()
        first_half_box_displacement =  None if self.objectIds == None else self.firstHalfBoxDisplacement
        second_half_box_displacement =  None if self.objectIds == None else box_displacement - first_half_box_displacement
        first_half_displacement = self.firstHalfFitness
        second_half_displacement = displacement - first_half_displacement
        random_num = np.random.random()
        print(f'({str(displacement)} {str(empowerment)} {str(first_half_displacement)} {str(second_half_displacement)} {str(random_num)} {str(box_displacement)} {str(first_half_box_displacement)} {str(second_half_box_displacement)})')

