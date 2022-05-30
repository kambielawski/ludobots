import pyrosim.pyrosim as pyrosim
import pybullet as p
import pybullet_data
import time
import numpy as np
import random

from robot import Robot
from world import World
from simulation import Simulation
import constants as c

'''
physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# add a floor
planeId = p.loadURDF("plane.urdf")
# add robot body
robotId = p.loadURDF("body.urdf")

# load box specified by box.sdf into the world
p.loadSDF("world.sdf")

# add gravitational force to world (x,y,z)
p.setGravity(0,0,c.GRAVITY_FORCE)

# this gets the simulation ready to read values from sensors
pyrosim.Prepare_To_Simulate(robotId)

# vectors for storing sensor values
backLegSensorValues = np.zeros(c.TIMESTEPS)
frontLegSensorValues = np.zeros(c.TIMESTEPS)

targetAngles_front = np.sin(np.linspace(0, 2*np.pi, c.TIMESTEPS) * c.FREQUENCY_FRONT + c.PHASE_OFFSET_FRONT)*c.AMPLITUDE_FRONT
targetAngles_back = np.sin(np.linspace(0, 2*np.pi, c.TIMESTEPS) * c.FREQUENCY_BACK + c.PHASE_OFFSET_BACK)*c.AMPLITUDE_BACK
# np.save("./data/targetAngles_front.npy", targetAngles_front)
# np.save("./data/targetAngles_back.npy", targetAngles_back)
# exit()

for i in range(c.TIMESTEPS):
    if i%100 == 0:
        print(i)
    # sleep for 1/60 of a second
    time.sleep(1/60)
    # step the simulation
    p.stepSimulation()
    # sensor value from robotId
    backLegSensorValues[i] = pyrosim.Get_Touch_Sensor_Value_For_Link("BackLeg")
    frontLegSensorValues[i] = pyrosim.Get_Touch_Sensor_Value_For_Link("FrontLeg")

    # simulate a motor for a particular joint
    pyrosim.Set_Motor_For_Joint(
        bodyIndex=robotId,
        jointName="Torso_BackLeg",
        controlMode=p.POSITION_CONTROL,
        targetPosition=targetAngles_back[i],
        # max force calculated in Newton*meters
        maxForce=c.MAX_FORCE
    )
    pyrosim.Set_Motor_For_Joint(
        bodyIndex=robotId,
        jointName="Torso_FrontLeg",
        controlMode=p.POSITION_CONTROL,
        targetPosition=targetAngles_front[i],
        # max force calculated in Newton*meters
        maxForce=c.MAX_FORCE
    )

np.save("./data/backLegSensor.npy", backLegSensorValues)
np.save("./data/frontLegSensor.npy", frontLegSensorValues)
p.disconnect()
'''

simulation = Simulation()
robot = Robot()
world = World()

simulation.Run(robot)



