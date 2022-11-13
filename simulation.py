import pybullet as p
import pybullet_data
import numpy as np
import time 

import constants as c

class Simulation:
    def __init__(self, runMode, solutionId, dir='.'):
        self.runMode = runMode
        self.solutionId = solutionId
        self.dir = dir
        if runMode == "GUI":
            self.physicsClient = p.connect(p.GUI)
        if runMode == "DIRECT":
            self.physicsClient = p.connect(p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0,0,c.GRAVITY_FORCE)

    def __del__(self):
        # self.Save_Values()
        p.disconnect()

    # Run simulation (sense -> act -> update sim) 
    def Run(self, robots):
        self.robots = robots
        for i in range(c.TIMESTEPS):
            p.stepSimulation()
            for robot in self.robots:
                robot.Sense(i)
                robot.Think()
                robot.Act(i)
            if self.runMode == "GUI":
                time.sleep(1/360)

    def Get_Fitness(self, objective):
        return self.robots[0].Get_Fitness(objective)

    def Save_Values(self):
        for sensor in self.robot.sensors:
            print(self.robot.sensors[sensor].values)
            np.save(self.dir + "/data/data_" + self.robot.sensors[sensor].name + "_sensor.npy", self.robot.sensors[sensor].values)
            print(f"Sensor data saved to {self.dir}/data/data_" + self.robot.sensors[sensor].name + "_sensor.npy")

