import numpy as np
import pybullet as p
import pyrosim.pyrosim as pyrosim

MAX_FORCE=50 # Newton*meters

class Motor:
    def __init__(self, jointName):
        self.jointName = jointName
        self.values = []

    def Set_Value(self, robot, desiredAngle):
        self.values.append(desiredAngle)
        pyrosim.Set_Motor_For_Joint(
            bodyIndex=robot.robotId,
            jointName=self.jointName,
            controlMode=p.POSITION_CONTROL,
            targetPosition=desiredAngle,
            maxForce=MAX_FORCE
        )
