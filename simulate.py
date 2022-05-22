import pyrosim.pyrosim as pyrosim
import pybullet as p
import pybullet_data
import time
import numpy as np

physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# add a floor
planeId = p.loadURDF("plane.urdf")
# add robot body
robotId = p.loadURDF("body.urdf")

# load box specified by box.sdf into the world
p.loadSDF("world.sdf")

# add gravitational force to world
p.setGravity(0,0,-9.8)

# this gets the simulation ready to read values from sensors
pyrosim.Prepare_To_Simulate(robotId)

# vectors for storing sensor values
backLegSensorValues = np.zeros(1000)
frontLegSensorValues = np.zeros(1000)

for i in range(1000):
    if i%100 == 0:
        print(i)
    # sleep for 1/60 of a second
    time.sleep(1/60)
    # step the simulation
    p.stepSimulation()
    # sensor value from robotId
    backLegSensorValues[i] = pyrosim.Get_Touch_Sensor_Value_For_Link("BackLeg")
    frontLegSensorValues[i] = pyrosim.Get_Touch_Sensor_Value_For_Link("FrontLeg")

np.save("./data/backLegSensor.npy", backLegSensorValues)
np.save("./data/frontLegSensor.npy", frontLegSensorValues)
p.disconnect()
