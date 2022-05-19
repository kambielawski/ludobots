import pybullet as p
import pybullet_data
import time

physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# add a floor
planeId = p.loadURDF("plane.urdf")

# load box specified by box.sdf into the world
p.loadSDF("boxes.sdf")

# add gravitational force to world
p.setGravity(0,0,-9.8)

while True:
    # sleep for 1/60 of a second
    time.sleep(1/60)
    # step the simulation
    p.stepSimulation()

p.disconnect()
