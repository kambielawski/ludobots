import pybullet as p
import pybullet_data
import numpy as np
import time 

import constants as c

class Simulation:
    def __init__(self, runMode, solutionId, objectsFile='', dir='.'):
        self.runMode = runMode
        self.solutionId = solutionId
        self.dir = dir
        if runMode == "GUI":
            self.physicsClient = p.connect(p.GUI)
        if runMode == "DIRECT":
            self.physicsClient = p.connect(p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0,0,c.GRAVITY_FORCE)
        # Load infinite plane
        self.planeId = p.loadURDF("plane.urdf")
        # Load objects if there are any
        if objectsFile:
            self.objectIds = p.loadSDF(objectsFile)
        else:
            self.objectIds = None

    def __del__(self):
        # self.Save_Values()
        p.disconnect()

    # Run simulation (sense -> act -> update sim) 
    def Run(self, robots):
        self.robots = robots
        for i in range(c.TIMESTEPS):
            p.stepSimulation()
            for robot in self.robots:
                # Just going to let the robots know about all the objects in the world 
                # This "global" information should only be used for computing fitness (robot should not use global info)
                if self.objectIds:
                    robot.Set_Object_Ids(self.objectIds)
                
                # Perception/Action Loop
                robot.Sense(i)
                robot.Think()
                robot.Act(i)
            if self.runMode == "GUI":
                time.sleep(1/10000)

        # PLOT A ROBOT'S JOINTS' VELOCITY VALUES OVER TIME
        # TODO: move this to a better place
        # velocity_vals_over_time = self.robots[0].jointAngularVelocities
        # for i in range(len(velocity_vals_over_time[0])):
        #     joint_val_over_time = [joint_vals[i] for joint_vals in velocity_vals_over_time]
        #     plt.plot(range(len(joint_val_over_time)), joint_val_over_time)
        # plt.show()

    def Get_Fitness(self, objective):
        return self.robots[0].Get_Fitness(objective)

    def Print_Objectives(self):
        self.robots[0].Print_Objectives()

    def Save_Values(self):
        for sensor in self.robot.sensors:
            print(self.robot.sensors[sensor].values)
            np.save(self.dir + "/data/data_" + self.robot.sensors[sensor].name + "_sensor.npy", self.robot.sensors[sensor].values)
            print(f"Sensor data saved to {self.dir}/data/data_" + self.robot.sensors[sensor].name + "_sensor.npy")

