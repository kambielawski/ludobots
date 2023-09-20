import numpy as np
import sys
import os
sys.path.append('../pyrosim')
import pyrosim.pyrosim as pyrosim

class Biped:
    def __init__(self, solnId, dir='.'):
        self.solnId = solnId
        self.dir = dir
        self.sourceBodyFile = "robots/body_biped.urdf"
        self.bodyFile = f"{self.dir}/body_biped_{self.solnId}.urdf"
        self.brainFile = f"{self.dir}/brain_{self.solnId}.nndf"
        os.system('cp ' + self.sourceBodyFile + ' ' + self.bodyFile)

        self.NUM_MOTOR_NEURONS = 4
        self.NUM_SENSOR_NEURONS = 5

        # self.weights = weights

    def Generate_Robot(self, weights, start_x, start_y, start_z):
        self.weights = weights
        self.Generate_Body(start_x, start_y, start_z)
        self.Generate_NN()

    def Generate_Weights(self):
        self.weights = np.random.rand(self.NUM_MOTOR_NEURONS, self.NUM_SENSOR_NEURONS) * 2 - 1
        return self.weights

    def Generate_Fully_Connected_Synapses(self):
        for m in range(self.NUM_MOTOR_NEURONS):
            for s in range(self.NUM_SENSOR_NEURONS):
                pyrosim.Send_Synapse(
                    sourceNeuronName=s,
                    targetNeuronName=m+self.NUM_SENSOR_NEURONS,
                    weight=self.weights[m][s]
                )

    def Get_Body_File(self):
        return self.bodyFile

    def Generate_Body(self, start_x, start_y, start_z):
        pyrosim.Start_URDF(self.bodyFile)
        start_z = start_z + 1.5 # (The start_z default is 1, so we need to adjust this for the biped because the root link is higher)

        # root link
        pyrosim.Send_Cube(name="Torso", pos=[start_x, start_y, start_z], size=[1,1,1])

        # joints extending from root link (still absolute coords)
        pyrosim.Send_Joint(
            name="Torso_LeftLeg", 
            parent="Torso", child="LeftLeg", 
            type="revolute", 
            position=[start_x-0.5, start_y, start_z-0.5], 
            jointAxis="0 1 1"
            )
        pyrosim.Send_Joint(
            name="Torso_RightLeg", 
            parent="Torso", 
            child="RightLeg", 
            type="revolute", 
            position=[start_x+0.5, start_y, start_z-0.5], 
            jointAxis="0 1 1"
            )

        # now all links & joints with an upstream joint have positions relative to the upstream joint
        pyrosim.Send_Joint(
            name="RightLeg_RightLower", 
            parent="RightLeg", 
            child="RightLower", 
            type="revolute", 
            position=[0,0,-1], 
            jointAxis="0 1 1"
            )
        pyrosim.Send_Joint(
            name="LeftLeg_LeftLower", 
            parent="LeftLeg", 
            child="LeftLower", 
            type="revolute", 
            position=[0,0,-1], 
            jointAxis="0 1 1"
            )

        pyrosim.Send_Cube(name="LeftLeg", pos=[0,0,-0.5], size=[0.2,0.2,1])
        pyrosim.Send_Cube(name="RightLeg", pos=[0,0,-0.5], size=[0.2,0.2,1])

        pyrosim.Send_Cube(name="LeftLower", pos=[0,0,-0.5], size=[0.2,0.2,1])
        pyrosim.Send_Cube(name="RightLower", pos=[0,0,-0.5], size=[0.2,0.2,1])

        pyrosim.End()
        
    def Generate_NN(self, dir=None):
    	# .nndf files are just used in Pyrosim
        # "Neural Network Description File"
        brain_dir = dir if dir else self.dir
        pyrosim.Start_NeuralNetwork(f"{brain_dir}/brain_{self.solnId}.nndf")

        pyrosim.Send_Sensor_Neuron(name=0, linkName="RightLower")
        pyrosim.Send_Sensor_Neuron(name=1, linkName="LeftLower")
        pyrosim.Send_Sensor_Neuron(name=2, linkName="LeftLeg")
        pyrosim.Send_Sensor_Neuron(name=3, linkName="RightLeg")
        pyrosim.Send_Sensor_Neuron(name=4, linkName="Torso")

        pyrosim.Send_Motor_Neuron(name=5, jointName="Torso_LeftLeg")
        pyrosim.Send_Motor_Neuron(name=6, jointName="Torso_RightLeg")
        pyrosim.Send_Motor_Neuron(name=7, jointName="LeftLeg_LeftLower")
        pyrosim.Send_Motor_Neuron(name=8, jointName="RightLeg_RightLower")

        self.Generate_Fully_Connected_Synapses()

        pyrosim.End()
        
    def Set_Id(self, newId):
        self.solnId = newId
