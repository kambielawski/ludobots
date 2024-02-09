"""Robot class for the Pyrosim environment."""
import pyrosim.pyrosim as pyrosim
from pyrosim.neuralNetwork import NEURAL_NETWORK
import pybullet as p
import numpy as np
import random
import math
import pyinform
from pyinform.dist import Dist
from sensor import Sensor
from motor import Motor

from info_funcs import compute_joint_entropy, compute_joint_counts

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

        # Information computation setup
        self.empowerment = 0
        self.empowermentTimesteps = 0
        self.entropy_action_values = []
        self.entropy_sensor_values = []
        self.entropy_joint_values = []
        self.entropy_s_cond_a_values = []
        self.entropy_a_cond_s_values = []
        self.empowerment_values = []
        self.empowerment_joint_normalized_values = []

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
            self.Compute_Information_Components(timestep)

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
        
    def Compute_Information_Components(self, timestep):
        # Convert motor and sensor states into integers
        action_states = [int(''.join([str(b) for b in A]), base=2) for A in self.motorVals[((timestep+1)-(2*self.empowermentWindowSize)):((timestep+1)-self.empowermentWindowSize)]]
        sensor_states = [int(''.join([str(b) for b in S]), base=2) for S in self.sensorVals[((timestep+1)-self.empowermentWindowSize):timestep+1]]
        
        # Create distribution objects
        action_dist = Dist(action_states)
        sensor_dist = Dist(sensor_states)
        joint_dist = Dist(compute_joint_counts(action_states, sensor_states))

        # Compute entropy components
        entropy_actions = pyinform.shannon.entropy(action_dist)
        entropy_sensors = pyinform.shannon.entropy(sensor_dist)
        entropy_joint_AS = pyinform.shannon.entropy(joint_dist)
        entropy_A_cond_S = entropy_joint_AS - entropy_sensors
        entropy_S_cond_A = entropy_joint_AS - entropy_actions
        empowerment = entropy_joint_AS - entropy_A_cond_S - entropy_S_cond_A

        self.entropy_action_values.append(entropy_actions)
        self.entropy_sensor_values.append(entropy_sensors)
        self.entropy_joint_values.append(entropy_joint_AS)
        self.entropy_s_cond_a_values.append(entropy_S_cond_A)
        self.entropy_a_cond_s_values.append(entropy_A_cond_S)
        self.empowerment_values.append(empowerment)
        self.empowerment_joint_normalized_values.append(empowerment / entropy_joint_AS)

        self.empowermentTimesteps += 1

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

    def Print_NN(self):
        """Print the neural network synapse weights."""
        print([(s, self.nn.synapses[s].weight) for s in self.nn.synapses])

    def Print_Objectives(self):
        """Print the robot's objectives.
        This communicates the robot's objectives to the parent process (in solution)."""
        displacement = self.Y_Axis_Displacement()
        box_displacement = None if self.objectIds == None else self.Get_Box_Displacement()
        first_half_box_displacement =  None if self.objectIds == None else self.firstHalfBoxDisplacement
        second_half_box_displacement =  None if self.objectIds == None else box_displacement - first_half_box_displacement
        first_half_displacement = self.firstHalfFitness
        second_half_displacement = displacement - first_half_displacement
        random_num = np.random.random()

        # Compute entropy components
        entropy_actions = np.mean(self.entropy_action_values)
        entropy_sensors = np.mean(self.entropy_sensor_values)
        entropy_joint_AS = np.mean(self.entropy_joint_values)
        entropy_AcondS = np.mean(self.entropy_a_cond_s_values)
        entropy_ScondA = np.mean(self.entropy_s_cond_a_values)
        empowerment = np.mean(self.empowerment_values)
        empowerment_joint_normalized = np.mean(self.empowerment_joint_normalized_values)

        print(f'({str(displacement)} {str(empowerment)} {str(first_half_displacement)} \
                {str(second_half_displacement)} {str(random_num)} {str(box_displacement)} \
                {str(first_half_box_displacement)} {str(second_half_box_displacement)} \
                {str(entropy_actions)} {str(entropy_sensors)} {str(entropy_joint_AS)} \
                {str(entropy_AcondS)} {str(entropy_ScondA)} {str(empowerment_joint_normalized)}')

