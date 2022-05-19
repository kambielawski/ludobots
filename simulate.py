import pybullet as p
import time

physicsClient = p.connect(p.GUI)

for i in range(1000):
    # sleep for 1/60 of a second
    time.sleep(1/60)
    # step the simulation
    p.stepSimulation()

p.disconnect()
