import numpy as np
import sys
import os
sys.path.append('../pyrosim')
import pyrosim.pyrosim as pyrosim

class Snake4:
    def __init__(self, solnId, dir='.'):
        self.solnId = solnId
        self.dir = dir
        self.sourceBodyFile = "robots/body_snake4.urdf"
        self.bodyFile = f"{self.dir}/body_snake4_{self.solnId}.urdf"
        self.brainFile = f"{self.dir}/brain_{self.solnId}.nndf"
        os.system('cp ' + self.sourceBodyFile + ' ' + self.bodyFile)

        self.NUM_MOTOR_NEURONS = 3
        self.NUM_SENSOR_NEURONS = 4

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
        start_z = start_z - 0.5 # (The start_z default is 1, so we need to adjust this for the snake because the root link is lower)

        # root link
        pyrosim.Send_Cube(name="Segment1", pos=[start_x, start_y, start_z], size=[1,0.2,0.2])

        # joints extending from root link (still absolute coords)
        pyrosim.Send_Joint(
            name="Segment1_Segment2", 
            parent="Segment1", child="Segment2", 
            type="revolute", 
            position=[start_x+0.5, start_y, start_z], 
            jointAxis="0 1 1"
            )

        # now all links & joints with an upstream joint have positions relative to the upstream joint
        pyrosim.Send_Joint(
            name="Segment2_Segment3", 
            parent="Segment2", 
            child="Segment3", 
            type="revolute", 
            position=[1,0,0], 
            jointAxis="0 1 1"
            )
        pyrosim.Send_Joint(
            name="Segment3_Segment4", 
            parent="Segment3", 
            child="Segment4", 
            type="revolute", 
            position=[1,0,0],
            jointAxis="0 1 1"
            )

        pyrosim.Send_Cube(name="Segment2", pos=[0.5,0,0], size=[1,0.2,0.2])
        pyrosim.Send_Cube(name="Segment3", pos=[0.5,0,0], size=[1,0.2,0.2])
        pyrosim.Send_Cube(name="Segment4", pos=[0.5,0,0], size=[1,0.2,0.2])

        pyrosim.End()
        
    def Generate_NN(self):
    	# .nndf files are just used in Pyrosim
        # "Neural Network Description File"
        pyrosim.Start_NeuralNetwork(f"{self.dir}/brain_{self.solnId}.nndf")

        pyrosim.Send_Sensor_Neuron(name=0, linkName="Segment1")
        pyrosim.Send_Sensor_Neuron(name=1, linkName="Segment2")
        pyrosim.Send_Sensor_Neuron(name=2, linkName="Segment3")
        pyrosim.Send_Sensor_Neuron(name=3, linkName="Segment4")

        pyrosim.Send_Motor_Neuron(name=4, jointName="Segment1_Segment2")
        pyrosim.Send_Motor_Neuron(name=5, jointName="Segment2_Segment3")
        pyrosim.Send_Motor_Neuron(name=6, jointName="Segment3_Segment4")

        self.Generate_Fully_Connected_Synapses()

        pyrosim.End()
        
    def Generate_BrainBody_Files(self):
        self.Generate_Weights()
        self.Generate_Body(0,0,1)
        self.Generate_NN()
        
    def Set_Id(self, newId):
        self.solnId = newId
