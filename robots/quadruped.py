import math
import numpy as np
import sys
import os
sys.path.append('../pyrosim')
import pyrosim.pyrosim as pyrosim

class Quadruped:
    def __init__(self, solnId, dir='.'):
        self.solnId = solnId
        self.dir = dir
        self.sourceBodyFile = "robots/body_quadruped.urdf"
        self.bodyFile = f"{self.dir}/body_quadruped_{self.solnId}.urdf"
        self.brainFile = f"{self.dir}/brain_{self.solnId}.nndf"
        os.system('cp ' + self.sourceBodyFile + ' ' + self.bodyFile)

        self.NUM_MOTOR_NEURONS = 9
        self.NUM_SENSOR_NEURONS = 5

        # self.weights = weights

    def Generate_Robot(self, weights, start_x, start_y, start_z, orientation=0):
        self.weights = weights
        self.bodyFile = f"{self.dir}/body_quadruped_{orientation}_{self.solnId}.urdf"
        self.Generate_Body(start_x, start_y, start_z, orientation)
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

    def Generate_Body(self, start_x, start_y, start_z, orientation=0):
        pyrosim.Start_URDF(self.bodyFile)

        orientations = [
            {"x": 0, "y": 0, "z": 0},
            {"x": 0, "y": 90, "z": 0},
            {"x": 0, "y": 180, "z": 0},
            {"x": 0, "y": -90, "z": 0},
            {"x": 90, "y": 0, "z": 0},
            {"x": -90, "y": 0, "z": 0}
        ]

        o = orientations[orientation]

        # root link
        pyrosim.Send_Cube(name="Torso", pos=[start_x, start_y, start_z], size=[1,1,1])

        torso_backleg_pos = [start_x, start_y-0.5,start_z]
        torso_leftleg_pos = [start_x-0.5, start_y, start_z]
        torso_rightleg_pos = [start_x+0.5, start_y, start_z]
        torso_frontleg_pos = [start_x, start_y+0.5,start_z]

        torso_backleg_transform = self.transform_position(torso_backleg_pos, orientation=o, start_pos=(start_x, start_y, start_z))
        torso_leftleg_transform = self.transform_position(torso_leftleg_pos, orientation=o, start_pos=(start_x, start_y, start_z))
        torso_rightleg_transform = self.transform_position(torso_rightleg_pos, orientation=o, start_pos=(start_x, start_y, start_z))
        torso_frontleg_transform = self.transform_position(torso_frontleg_pos, orientation=o, start_pos=(start_x, start_y, start_z))

        backleg_relative = np.array(torso_backleg_transform) - np.array([start_x, start_y, start_z])
        frontleg_relative = np.array(torso_frontleg_transform) - np.array([start_x, start_y, start_z])
        rightleg_relative = np.array(torso_rightleg_transform) - np.array([start_x, start_y, start_z])
        leftleg_relative = np.array(torso_leftleg_transform) - np.array([start_x, start_y, start_z])

        # print('joint transforms absolute')
        # print(torso_frontleg_pos, '-->', torso_frontleg_transform)
        # print(torso_backleg_pos, '-->', torso_backleg_transform)
        # print(torso_leftleg_pos, '-->', torso_leftleg_transform)
        # print(torso_rightleg_pos, '-->', torso_rightleg_transform)

        joint_axis_front = ' '.join(['1' if b==0 else '0' for b in [1 if a != 0 else a for a in frontleg_relative]])
        joint_axis_back = ' '.join(['1' if b==0 else '0' for b in [1 if a != 0 else a for a in backleg_relative]])
        joint_axis_left = ' '.join(['1' if b==0 else '0' for b in [1 if a != 0 else a for a in leftleg_relative]])
        joint_axis_right = ' '.join(['1' if b==0 else '0' for b in [1 if a != 0 else a for a in rightleg_relative]])

        # print(joint_axis_front)
        # print(joint_axis_back)
        # print(joint_axis_left)
        # print(joint_axis_right)

        # print('top link relative positions')
        # print(frontleg_relative)
        # print(backleg_relative)
        # print(leftleg_relative)
        # print(rightleg_relative)

        # joints extending from root link
        pyrosim.Send_Joint(
            name="Torso_BackLeg", 
            parent="Torso", 
            child="BackLeg", 
            type="revolute", 
            position=torso_backleg_transform, 
            jointAxis=joint_axis_back
        )
        pyrosim.Send_Joint(
            name="Torso_LeftLeg", 
            parent="Torso", child="LeftLeg", 
            type="revolute", 
            position=torso_leftleg_transform, 
            jointAxis=joint_axis_left
            )
        pyrosim.Send_Joint(
            name="Torso_RightLeg", 
            parent="Torso", 
            child="RightLeg", 
            type="revolute", 
            position=torso_rightleg_transform, 
            jointAxis=joint_axis_right
            )
        pyrosim.Send_Joint(
            name="Torso_FrontLeg", 
            parent="Torso", 
            child="FrontLeg", 
            type="revolute", 
            position=torso_frontleg_transform, 
            jointAxis=joint_axis_front
            )

        backleg_backlower_joint_pos = 2*(backleg_relative)
        frontleg_frontlower_joint_pos = 2*(frontleg_relative)
        rightleg_rightlower_joint_pos = 2*(rightleg_relative)
        lefttleg_leftlower_joint_pos = 2*(leftleg_relative)

        # print('lower joint relative positions')
        # print(frontleg_frontlower_joint_pos)
        # print(backleg_backlower_joint_pos)
        # print(lefttleg_leftlower_joint_pos)
        # print(rightleg_rightlower_joint_pos)

        # now all links & joints with an upstream joint have positions relative to the upstream joint
        pyrosim.Send_Joint(
            name="BackLeg_BackLower", 
            parent="BackLeg", 
            child="BackLower", 
            type="revolute", 
            position=backleg_backlower_joint_pos, # [0,-1,0], 
            jointAxis=joint_axis_back
            )
        pyrosim.Send_Joint(
            name="FrontLeg_FrontLower", 
            parent="FrontLeg", 
            child="FrontLower", 
            type="revolute", 
            position=frontleg_frontlower_joint_pos, # [0,1,0], 
            jointAxis=joint_axis_front
            )
        pyrosim.Send_Joint(
            name="RightLeg_RightLower", 
            parent="RightLeg", 
            child="RightLower", 
            type="revolute", 
            position=rightleg_rightlower_joint_pos, # [1,0,0], 
            jointAxis=joint_axis_right
            )
        pyrosim.Send_Joint(
            name="LeftLeg_LeftLower", 
            parent="LeftLeg", 
            child="LeftLower", 
            type="revolute", 
            position=lefttleg_leftlower_joint_pos, # [-1,0,0], 
            jointAxis=joint_axis_left
            )

        rightleg_size = [0.2 if a == 0 else a for a in np.abs(rightleg_relative * 2)]
        leftleg_size = [0.2 if a == 0 else a for a in np.abs(leftleg_relative * 2)]
        frontleg_size = [0.2 if a == 0 else a for a in np.abs(frontleg_relative * 2)]
        backleg_size = [0.2 if a == 0 else a for a in np.abs(backleg_relative * 2)]

        # print('top leg size')
        # print(frontleg_size)
        # print(backleg_size)
        # print(leftleg_size)
        # print(rightleg_size)

        # Relative to upstream joint...
        pyrosim.Send_Cube(name="FrontLeg", pos=frontleg_relative, size=frontleg_size) # [0.2,1,0.2])
        pyrosim.Send_Cube(name="LeftLeg", pos=leftleg_relative, size=leftleg_size) # [1,0.2,0.2])
        pyrosim.Send_Cube(name="RightLeg", pos=rightleg_relative, size=rightleg_size) # [1,0.2,0.2])
        pyrosim.Send_Cube(name="BackLeg", pos=backleg_relative, size=backleg_size) # [0.2,1,0.2])

        bottomlegs_relative_pos = self.transform_position([0,0,-0.5], orientation=o, start_pos=(0,0,0))
        bottomlegs_size = [0.2 if a == 0 else a for a in np.abs(np.array(bottomlegs_relative_pos) * 2)]

        # print('bottom leg')
        # print(bottomlegs_relative_pos)
        # print(bottomlegs_size)

        pyrosim.Send_Cube(name="BackLower", pos=bottomlegs_relative_pos, size=bottomlegs_size)
        pyrosim.Send_Cube(name="FrontLower", pos=bottomlegs_relative_pos, size=bottomlegs_size)
        pyrosim.Send_Cube(name="LeftLower", pos=bottomlegs_relative_pos, size=bottomlegs_size)
        pyrosim.Send_Cube(name="RightLower", pos=bottomlegs_relative_pos, size=bottomlegs_size)

        print('filetype: ', pyrosim.filetype)
        print('file: ', pyrosim.f)
        
        pyrosim.filetype = pyrosim.URDF_FILETYPE
        pyrosim.End()

    def round_if_close(self, num, tolerance=1e-9):
        """Round number if it's very close to a whole number."""
        if abs(num - round(num)) < tolerance:
            return round(num)
        return num

    def transform_position(self, original_pos, orientation, start_pos):
        x, y, z = original_pos

        # Center of rotation
        cx, cy, cz = start_pos

        # Translate point to origin
        x -= cx
        y -= cy
        z -= cz

        # Rotation about x-axis
        theta_x = math.radians(orientation["x"])
        y_new = y * math.cos(theta_x) - z * math.sin(theta_x)
        z_new = y * math.sin(theta_x) + z * math.cos(theta_x)
        y, z = y_new, z_new

        # Rotation about y-axis
        theta_y = math.radians(orientation["y"])
        x_new = x * math.cos(theta_y) + z * math.sin(theta_y)
        z_new = -x * math.sin(theta_y) + z * math.cos(theta_y)
        x, z = x_new, z_new

        # Rotation about z-axis
        theta_z = math.radians(orientation["z"])
        x_new = x * math.cos(theta_z) - y * math.sin(theta_z)
        y_new = x * math.sin(theta_z) + y * math.cos(theta_z)
        x, y = x_new, y_new

        # Translate point back
        x += cx
        y += cy
        z += cz

        x = self.round_if_close(x)
        y = self.round_if_close(y)
        z = self.round_if_close(z)

        return [x, y, z]

        
    def Generate_NN(self, dir=None):
    	# .nndf files are just used in Pyrosim
        # "Neural Network Description File"
        brain_dir = dir if dir else self.dir
        pyrosim.Start_NeuralNetwork(f"{brain_dir}/brain_{self.solnId}.nndf")

        pyrosim.Send_Sensor_Neuron(name=0, linkName="RightLower")
        pyrosim.Send_Sensor_Neuron(name=1, linkName="LeftLower")
        pyrosim.Send_Sensor_Neuron(name=2, linkName="FrontLower")
        pyrosim.Send_Sensor_Neuron(name=3, linkName="BackLower")
        pyrosim.Send_Sensor_Neuron(name=4, linkName="Torso")

        pyrosim.Send_Motor_Neuron(name=5, jointName="Torso_BackLeg")
        pyrosim.Send_Motor_Neuron(name=6, jointName="Torso_FrontLeg")
        pyrosim.Send_Motor_Neuron(name=7, jointName="Torso_LeftLeg")
        pyrosim.Send_Motor_Neuron(name=8, jointName="Torso_RightLeg")
        pyrosim.Send_Motor_Neuron(name=9, jointName="LeftLeg_LeftLower")
        pyrosim.Send_Motor_Neuron(name=10, jointName="RightLeg_RightLower")
        pyrosim.Send_Motor_Neuron(name=11, jointName="BackLeg_BackLower")
        pyrosim.Send_Motor_Neuron(name=12, jointName="FrontLeg_FrontLower")

        self.Generate_Fully_Connected_Synapses()

        pyrosim.filetype = pyrosim.NNDF_FILETYPE
        pyrosim.End()
        
    def Set_Id(self, newId):
        self.solnId = newId
