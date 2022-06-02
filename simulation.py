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
        # self.Save_Values()
        p.disconnect()

    # Run simulation (sense -> act -> update sim) 
    def Run(self, robots):
        self.robots = robots
        for i in range(c.TIMESTEPS):
            if i%100 == 0:
                print(i)

            p.stepSimulation()
            for robot in self.robots:
                robot.Sense(i)
                robot.Think()
                robot.Act(i)
            # time.sleep(1/60)

    def Save_Values(self):
        for sensor in self.robot.sensors:
            print(self.robot.sensors[sensor].values)
            np.save("./data/data_" + self.robot.sensors[sensor].name + "_sensor.npy", self.robot.sensors[sensor].values)
            print("Sensor data saved to ./data/data_" + self.robot.sensors[sensor].name + "_sensor.npy")
