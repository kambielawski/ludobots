import numpy as np
import pybullet as p
import pyrosim.pyrosim as pyrosim

import constants as c

class Motor:
    def __init__(self, jointName):
        self.jointName = jointName
        self.Prepare_To_Act()

    def Prepare_To_Act(self):
        self.amplitude = c.AMPLITUDE_FRONT
        self.frequency = c.FREQUENCY_FRONT
        self.offset = c.PHASE_OFFSET_FRONT
        self.motorValues = np.sin(np.linspace(0,2*np.pi, c.TIMESTEPS) * self.frequency + self.offset)*self.amplitude

    def Set_Value(self, robot, i):
        pyrosim.Set_Motor_For_Joint(
            bodyIndex=robot.robotId,
            jointName=self.jointName,
            controlMode=p.POSITION_CONTROL,
            targetPosition=self.motorValues[i],
            maxForce=c.MAX_FORCE
        )
