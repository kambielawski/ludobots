import numpy as np
import sys
import os
sys.path.append('../pyrosim')
import pyrosim.pyrosim as pyrosim

class Octoped:
    def __init__(self, solnId, dir='.'):
        self.solnId = solnId
        self.dir = dir
        self.sourceBodyFile = "robots/body_octoped.urdf"
        self.bodyFile = f"{self.dir}/body_octoped_{self.solnId}.urdf"
        self.brainFile = f"{self.dir}/brain_{self.solnId}.nndf"
        os.system('cp ' + self.sourceBodyFile + ' ' + self.bodyFile)

        self.NUM_MOTOR_NEURONS = 16
        self.NUM_SENSOR_NEURONS = 8

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
            parent="Torso", 
            child="LeftLeg", 
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
            position=[start_x, start_y+0.5,start_z], 
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
        # X Y Z (z is up-down axis) Top leg joints (absolute)
        pyrosim.Send_Joint( name="Torso_TopFrontLeftLower", parent="Torso", child="TopFrontLeftLower", type="revolute", position=[start_x-0.5, start_y+0.5,start_z+0.5], jointAxis="0 1 1")
        pyrosim.Send_Joint( name="Torso_TopFrontRightLower", parent="Torso", child="TopFrontRightLower", type="revolute", position=[start_x+0.5, start_y+0.5,start_z+0.5], jointAxis="0 1 1")
        pyrosim.Send_Joint( name="Torso_TopBackLeftLower", parent="Torso", child="TopBackLeftLower", type="revolute", position=[start_x-0.5, start_y-0.5,start_z+0.5], jointAxis="0 1 1")
        pyrosim.Send_Joint( name="Torso_TopBackRightLower", parent="Torso", child="TopBackRightLower", type="revolute", position=[start_x+0.5, start_y-0.5,start_z+0.5], jointAxis="0 1 1")
        # Top leg joints (relative)
        pyrosim.Send_Joint( name="TopFrontLeftLower_TopFrontLeftUpper", parent="TopFrontLeftLower", child="TopFrontLeftUpper", type="revolute", position=[0,0,1], jointAxis="0 1 1")
        pyrosim.Send_Joint( name="TopFrontRightLower_TopFrontRightUpper", parent="TopFrontRightLower", child="TopFrontRightUpper", type="revolute", position=[0,0,1], jointAxis="0 1 1")
        pyrosim.Send_Joint( name="TopBackLeftLower_TopBackLeftUpper", parent="TopBackLeftLower", child="TopBackLeftUpper", type="revolute", position=[0,0,1], jointAxis="0 1 1")
        pyrosim.Send_Joint( name="TopBackRightLower_TopBackRightUpper", parent="TopBackRightLower", child="TopBackRightUpper", type="revolute", position=[0,0,1], jointAxis="0 1 1")



        pyrosim.Send_Cube(name="FrontLeg", pos=[0,0.5,0], size=[0.2,1,0.2])
        pyrosim.Send_Cube(name="LeftLeg", pos=[-0.5,0,0], size=[1,0.2,0.2])
        pyrosim.Send_Cube(name="RightLeg", pos=[0.5,0,0], size=[1,0.2,0.2])
        pyrosim.Send_Cube(name="BackLeg", pos=[0,-0.5,0], size=[0.2,1,0.2])
        pyrosim.Send_Cube(name="BackLower", pos=[0,0,-0.5], size=[0.2,0.2,1])
        pyrosim.Send_Cube(name="FrontLower", pos=[0,0,-0.5], size=[0.2,0.2,1])
        pyrosim.Send_Cube(name="LeftLower", pos=[0,0,-0.5], size=[0.2,0.2,1])
        pyrosim.Send_Cube(name="RightLower", pos=[0,0,-0.5], size=[0.2,0.2,1])
        # Absolute top legs
        pyrosim.Send_Cube(name="TopFrontLeftLower", pos=[0,0,0.5], size=[0.2,0.2,1])
        pyrosim.Send_Cube(name="TopFrontRightLower", pos=[0,0,0.5], size=[0.2,0.2,1])
        pyrosim.Send_Cube(name="TopBackRightLower", pos=[0,0,0.5], size=[0.2,0.2,1])
        pyrosim.Send_Cube(name="TopBackLeftLower", pos=[0,0,0.5], size=[0.2,0.2,1])
        # Relative top legs
        pyrosim.Send_Cube(name="TopFrontLeftUpper", pos=[0,0,0.5], size=[0.2,0.2,1])
        pyrosim.Send_Cube(name="TopFrontRightUpper", pos=[0,0,0.5], size=[0.2,0.2,1])
        pyrosim.Send_Cube(name="TopBackRightUpper", pos=[0,0,0.5], size=[0.2,0.2,1])
        pyrosim.Send_Cube(name="TopBackLeftUpper", pos=[0,0,0.5], size=[0.2,0.2,1])

        pyrosim.End()
        
    def Generate_NN(self, dir=None):
    	# .nndf files are just used in Pyrosim
        # "Neural Network Description File"
        brain_dir = dir if dir else self.dir
        pyrosim.Start_NeuralNetwork(f"{brain_dir}/brain_{self.solnId}.nndf")

        pyrosim.Send_Sensor_Neuron(name=0, linkName="RightLower")
        pyrosim.Send_Sensor_Neuron(name=1, linkName="LeftLower")
        pyrosim.Send_Sensor_Neuron(name=2, linkName="FrontLower")
        pyrosim.Send_Sensor_Neuron(name=3, linkName="BackLower")

        pyrosim.Send_Sensor_Neuron(name=4, linkName="TopFrontLeftLower")
        pyrosim.Send_Sensor_Neuron(name=5, linkName="TopFrontRightLower")
        pyrosim.Send_Sensor_Neuron(name=6, linkName="TopBackLeftLower")
        pyrosim.Send_Sensor_Neuron(name=7, linkName="TopBackRightLower")

        pyrosim.Send_Motor_Neuron(name=8, jointName="Torso_BackLeg")
        pyrosim.Send_Motor_Neuron(name=9, jointName="Torso_FrontLeg")
        pyrosim.Send_Motor_Neuron(name=10, jointName="Torso_LeftLeg")
        pyrosim.Send_Motor_Neuron(name=11, jointName="Torso_RightLeg")
        pyrosim.Send_Motor_Neuron(name=12, jointName="LeftLeg_LeftLower")
        pyrosim.Send_Motor_Neuron(name=13, jointName="RightLeg_RightLower")
        pyrosim.Send_Motor_Neuron(name=14, jointName="BackLeg_BackLower")
        pyrosim.Send_Motor_Neuron(name=15, jointName="FrontLeg_FrontLower")

        pyrosim.Send_Motor_Neuron(name=16, jointName="Torso_TopFrontLeftLower")
        pyrosim.Send_Motor_Neuron(name=17, jointName="Torso_TopFrontRightLower")
        pyrosim.Send_Motor_Neuron(name=18, jointName="Torso_TopBackLeftLower")
        pyrosim.Send_Motor_Neuron(name=19, jointName="Torso_TopBackRightLower")
        pyrosim.Send_Motor_Neuron(name=20, jointName="TopFrontRightLower_TopFrontRightUpper")
        pyrosim.Send_Motor_Neuron(name=21, jointName="TopFrontLeftLower_TopFrontLeftUpper")
        pyrosim.Send_Motor_Neuron(name=22, jointName="TopBackRightLower_TopBackRightUpper")
        pyrosim.Send_Motor_Neuron(name=23, jointName="TopBackLeftLower_TopBackLeftUpper")

        self.Generate_Fully_Connected_Synapses()

        pyrosim.End()
        
    def Set_Id(self, newId):
        self.solnId = newId
