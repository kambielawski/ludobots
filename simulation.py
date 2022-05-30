import pyrosim.pyrosim as pyrosim
import pybullet as p
import pybullet_data
import numpy as np
import time 

import constants as c

class Simulation:
    def __init__(self):
        self.physicsClient = p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0,0,c.GRAVITY_FORCE)

    def __del__(self):
        p.disconnect()

    def Run(self, robot):
        self.robot = robot
        self.backLegSensorValues = np.zeros(c.TIMESTEPS)
        self.frontLegSensorValues = np.zeros(c.TIMESTEPS)
        self.targetAngles_front = np.sin(np.linspace(0,2*np.pi, c.TIMESTEPS) * c.FREQUENCY_FRONT + c.PHASE_OFFSET_FRONT)*c.AMPLITUDE_FRONT
        self.targetAngles_back = np.sin(np.linspace(0,2*np.pi, c.TIMESTEPS) * c.FREQUENCY_BACK + c.PHASE_OFFSET_BACK)*c.AMPLITUDE_BACK
        for i in range(c.TIMESTEPS):
            if i%100 == 0:
                print(i)

            self.robot.Sense(i)
            p.stepSimulation()
            time.sleep(1/60)

'''
            # sensor value from robotId
            self.backLegSensorValues[i] = pyrosim.Get_Touch_Sensor_Value_For_Link("BackLeg")
            self.frontLegSensorValues[i] = pyrosim.Get_Touch_Sensor_Value_For_Link("FrontLeg")

            # simulate a motor for a particular joint
            pyrosim.Set_Motor_For_Joint(
                bodyIndex=robotId,
                jointName="Torso_BackLeg",
                controlMode=p.POSITION_CONTROL,
                targetPosition=self.targetAngles_back[i],
                maxForce=c.MAX_FORCE
            )
            pyrosim.Set_Motor_For_Joint(
                bodyIndex=robotId,
                jointName="Torso_FrontLeg",
                controlMode=p.POSITION_CONTROL,
                targetPosition=self.targetAngles_front[i],
                maxForce=c.MAX_FORCE
            )
'''
