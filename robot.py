import pyrosim.pyrosim as pyrosim
import pybullet as p
from sensor import Sensor
from motor import Motor

class Robot:
    def __init__(self):

        self.robotId = p.loadURDF("body.urdf")
        pyrosim.Prepare_To_Simulate(self.robotId)

        self.Prepare_To_Act()
        self.Prepare_To_Sense()
         

    # create Sensor object for each link & store in dictionary
    def Prepare_To_Sense(self):
        self.sensors = dict()
        for linkName in pyrosim.linkNamesToIndices:
            self.sensors[linkName] = Sensor(linkName)

    def Prepare_To_Act(self):
        self.motors = dict()
        for jointName in pyrosim.jointNamesToIndices:
            self.motors[jointName] = Motor(jointName)

    def Sense(self, i):
        for sensor in self.sensors:
            self.sensors[sensor].Get_Value(i)

    def Act(self, i):
        for joint in self.motors:
            self.motors[joint].Set_Value(self, i)



