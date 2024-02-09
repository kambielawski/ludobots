"""This file contains the Motor class, which is used to control the joints of the robot. """
import pybullet as p
import pyrosim.pyrosim as pyrosim

#TODO: Migrate this to a config file
MAX_FORCE=50 # Newton*meters

class Motor:
    """The Motor class is used to control the joints of the robot."""
    def __init__(self, jointName):
        self.jointName = jointName
        self.values = []

    def Set_Value(self, robot, desiredAngle):
        """Sets the value of the motor to the desired angle."""
        self.values.append(desiredAngle)
        pyrosim.Set_Motor_For_Joint(
            bodyIndex=robot.robotId,
            jointName=self.jointName,
            controlMode=p.POSITION_CONTROL,
            targetPosition=desiredAngle,
            maxForce=MAX_FORCE
        )
