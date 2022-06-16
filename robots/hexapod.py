import numpy as np
import sys
sys.path.append('../pyrosim')
import pyrosim.pyrosim as pyrosim

class Hexapod:
    def __init__(self, solnId):
        self.solnId = solnId
        self.bodyFile = "body_hexapod.urdf"

        self.NUM_MOTOR_NEURONS = 6
        self.NUM_SENSOR_NEURONS = 6

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

        # root link
        pyrosim.Send_Cube(name="Torso", pos=[start_x, start_y, start_z], size=[1,2,1])

        pyrosim.Send_Joint(
            name="Torso_RightMid",
            parent="Torso",
            child="RightMid",
            type="revolute",
            position=[start_x+0.5,start_y,start_z-0.5],
            jointAxis="1 1 1"
        )
        pyrosim.Send_Joint(
            name="Torso_RightFront",
            parent="Torso",
            child="RightFront",
            type="revolute",
            position=[start_x+0.5,start_y+1,start_z-0.5],
            jointAxis="1 1 1"
        )
        pyrosim.Send_Joint(
            name="Torso_RightBack",
            parent="Torso",
            child="RightBack",
            type="revolute",
            position=[start_x+0.5,start_y-1,start_z-0.5],
            jointAxis="1 1 1"
        )
        pyrosim.Send_Joint(
            name="Torso_LeftMid",
            parent="Torso",
            child="LeftMid",
            type="revolute",
            position=[start_x-0.5,start_y,start_z-0.5],
            jointAxis="1 1 1"
        )
        pyrosim.Send_Joint(
            name="Torso_LeftFront",
            parent="Torso",
            child="LeftFront",
            type="revolute",
            position=[start_x-0.5,start_y+1,start_z-0.5],
            jointAxis="1 1 1"
        )
        pyrosim.Send_Joint(
            name="Torso_LeftBack",
            parent="Torso",
            child="LeftBack",
            type="revolute",
            position=[start_x-0.5,start_y-1,start_z-0.5],
            jointAxis="1 1 1"
        )

        pyrosim.Send_Cube(name="RightMid", pos=[0.5,0,0], size=[1,0.2,0.2])
        pyrosim.Send_Cube(name="RightFront", pos=[0.5,0,0], size=[1,0.2,0.2])
        pyrosim.Send_Cube(name="RightBack", pos=[0.5,0,0], size=[1,0.2,0.2])
        pyrosim.Send_Cube(name="LeftMid", pos=[-0.5,0,0], size=[1,0.2,0.2])
        pyrosim.Send_Cube(name="LeftFront", pos=[-0.5,0,0], size=[1,0.2,0.2])
        pyrosim.Send_Cube(name="LeftBack", pos=[-0.5,0,0], size=[1,0.2,0.2])

        pyrosim.End()
        
    def Generate_NN(self):
    	# .nndf files are just used in Pyrosim
        # "Neural Network Description File"
        # pyrosim.Start_NeuralNetwork("brain_" + str(self.id) + ".nndf")
        pyrosim.Start_NeuralNetwork("brain_" + str(self.solnId) + ".nndf")

        pyrosim.Send_Sensor_Neuron(name=0, linkName="LeftMid")
        pyrosim.Send_Sensor_Neuron(name=1, linkName="RightMid")
        pyrosim.Send_Sensor_Neuron(name=2, linkName="LeftFront")
        pyrosim.Send_Sensor_Neuron(name=3, linkName="LeftBack")
        pyrosim.Send_Sensor_Neuron(name=4, linkName="RightFront")
        pyrosim.Send_Sensor_Neuron(name=5, linkName="RightBack")

        pyrosim.Send_Motor_Neuron(name=6, jointName="Torso_LeftMid")
        pyrosim.Send_Motor_Neuron(name=7, jointName="Torso_RightMid")
        pyrosim.Send_Motor_Neuron(name=8, jointName="Torso_LeftFront")
        pyrosim.Send_Motor_Neuron(name=9, jointName="Torso_RightFront")
        pyrosim.Send_Motor_Neuron(name=10, jointName="Torso_LeftBack")
        pyrosim.Send_Motor_Neuron(name=11, jointName="Torso_RightBack")

        self.Generate_Fully_Connected_Synapses()

        pyrosim.End()
        
    def Set_Id(self, newId):
        self.solnId = newId
