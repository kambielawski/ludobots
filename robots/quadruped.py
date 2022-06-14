import numpy as np
import sys
sys.path.append('../pyrosim')
import pyrosim.pyrosim as pyrosim

import constants as c

class Quadruped:
    def __init__(self, solnId, weights, start_x, start_y, start_z):
        self.solnId = solnId
        self.start_x = start_x
        self.start_y = start_y
        self.start_z = start_z 
        # self.weights = np.random.rand(c.NUM_MOTOR_NEURONS, c.NUM_SENSOR_NEURONS) * 2 - 1
        self.weights = weights
        self.Generate_Body(start_x, start_y, start_z) 
        self.Generate_NN() 

    def Generate_Fully_Connected_Synapses(self):
        for m in range(c.NUM_MOTOR_NEURONS):
            for s in range(c.NUM_SENSOR_NEURONS):
                pyrosim.Send_Synapse(
                    sourceNeuronName=s,
                    targetNeuronName=m+c.NUM_SENSOR_NEURONS,
                    weight=self.weights[m][s]
                )

    def Generate_Body(self, start_x, start_y, start_z):
        pyrosim.Start_URDF("body_quadruped.urdf")

        # root link
        pyrosim.Send_Cube(name="Torso", pos=[start_x, start_y, start_z], size=[1,1,1])

        # joints extending from root link
        pyrosim.Send_Joint(
            name="Torso_BackLeg", 
            parent="Torso", 
            child="BackLeg", 
            type="revolute", 
            position=[start_x, start_y-0.5,start_z], 
            jointAxis="1 0 1"
        )
        pyrosim.Send_Joint(
            name="Torso_LeftLeg", 
            parent="Torso", child="LeftLeg", 
            type="revolute", 
            position=[start_x-0.5, start_y, start_z], 
            jointAxis="0 1 1"
            )
        pyrosim.Send_Joint(
            name="Torso_RightLeg", 
            parent="Torso", 
            child="RightLeg", 
            type="revolute", 
            position=[start_x+0.5, start_y, start_z], 
            jointAxis="0 1 1"
            )
        pyrosim.Send_Joint(
            name="Torso_FrontLeg", 
            parent="Torso", 
            child="FrontLeg", 
            type="revolute", 
            position=[start_x, 
            start_y+0.5,start_z], 
            jointAxis="1 0 1"
            )

        # now all links & joints with an upstream joint have positions relative to the upstream joint
        pyrosim.Send_Joint(
            name="BackLeg_BackLower", 
            parent="BackLeg", 
            child="BackLower", 
            type="revolute", 
            position=[0,-1,0], 
            jointAxis="1 0 1"
            )
        pyrosim.Send_Joint(
            name="FrontLeg_FrontLower", 
            parent="FrontLeg", 
            child="FrontLower", 
            type="revolute", 
            position=[0,1,0], 
            jointAxis="1 0 1"
            )
        pyrosim.Send_Joint(
            name="RightLeg_RightLower", 
            parent="RightLeg", 
            child="RightLower", 
            type="revolute", 
            position=[1,0,0], 
            jointAxis="0 1 1"
            )
        pyrosim.Send_Joint(
            name="LeftLeg_LeftLower", 
            parent="LeftLeg", 
            child="LeftLower", 
            type="revolute", 
            position=[-1,0,0], 
            jointAxis="0 1 1"
            )

        pyrosim.Send_Cube(name="FrontLeg", pos=[0,0.5,0], size=[0.2,1,0.2])
        pyrosim.Send_Cube(name="LeftLeg", pos=[-0.5,0,0], size=[1,0.2,0.2])
        pyrosim.Send_Cube(name="RightLeg", pos=[0.5,0,0], size=[1,0.2,0.2])
        pyrosim.Send_Cube(name="BackLeg", pos=[0,-0.5,0], size=[0.2,1,0.2])
        pyrosim.Send_Cube(name="BackLower", pos=[0,0,-0.5], size=[0.2,0.2,1])
        pyrosim.Send_Cube(name="FrontLower", pos=[0,0,-0.5], size=[0.2,0.2,1])
        pyrosim.Send_Cube(name="LeftLower", pos=[0,0,-0.5], size=[0.2,0.2,1])
        pyrosim.Send_Cube(name="RightLower", pos=[0,0,-0.5], size=[0.2,0.2,1])

        pyrosim.End()
        
    def Generate_NN(self):
    	# .nndf files are just used in Pyrosim
        # "Neural Network Description File"
        # pyrosim.Start_NeuralNetwork("brain_" + str(self.id) + ".nndf")
        pyrosim.Start_NeuralNetwork("brain_" + str(self.solnId) + ".nndf")

        '''
        pyrosim.Send_Sensor_Neuron(name=0, linkName="Torso")
        pyrosim.Send_Sensor_Neuron(name=1, linkName="BackLeg")
        pyrosim.Send_Sensor_Neuron(name=2, linkName="FrontLeg")
        pyrosim.Send_Sensor_Neuron(name=3, linkName="LeftLeg")
        pyrosim.Send_Sensor_Neuron(name=4, linkName="RightLeg")
        '''
        pyrosim.Send_Sensor_Neuron(name=0, linkName="RightLower")
        pyrosim.Send_Sensor_Neuron(name=1, linkName="LeftLower")
        pyrosim.Send_Sensor_Neuron(name=2, linkName="FrontLower")
        pyrosim.Send_Sensor_Neuron(name=3, linkName="BackLower")

        pyrosim.Send_Motor_Neuron(name=4, jointName="Torso_BackLeg")
        pyrosim.Send_Motor_Neuron(name=5, jointName="Torso_FrontLeg")
        pyrosim.Send_Motor_Neuron(name=6, jointName="Torso_LeftLeg")
        pyrosim.Send_Motor_Neuron(name=7, jointName="Torso_RightLeg")
        pyrosim.Send_Motor_Neuron(name=8, jointName="LeftLeg_LeftLower")
        pyrosim.Send_Motor_Neuron(name=9, jointName="RightLeg_RightLower")
        pyrosim.Send_Motor_Neuron(name=10, jointName="BackLeg_BackLower")
        pyrosim.Send_Motor_Neuron(name=11, jointName="FrontLeg_FrontLower")

        self.Generate_Fully_Connected_Synapses()

        pyrosim.End()
        
