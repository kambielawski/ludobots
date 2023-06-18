import pickle
import pybullet as p
import pybullet_data
import numpy as np
import time 

GRAVITY_FORCE = -9.8 # m/s^2

'''
Simulation:
- Manages Pybullet setup and interfacing 
- 
'''
class Simulation:
    def __init__(self, runMode, solutionId, timesteps, objectsFile='', dir='.'):
        self.runMode = runMode
        self.solutionId = solutionId
        self.timesteps = timesteps
        self.dir = dir
        self.been_run = False
        if runMode == "GUI":
            self.physicsClient = p.connect(p.GUI)
        if runMode == "DIRECT":
            self.physicsClient = p.connect(p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0,0,GRAVITY_FORCE)
        # Load infinite plane
        self.planeId = p.loadURDF("plane.urdf")
        # Load objects if there are any
        if objectsFile:
            self.objectIds = p.loadSDF(objectsFile)
        else:
            self.objectIds = None

    def __del__(self):
        p.disconnect()

    # Run simulation (sense -> act -> update sim) 
    def Run(self, robots):
        self.robots = robots
        for i in range(self.timesteps):
            p.stepSimulation()
            for robot in self.robots:
                # Just going to let the robots know about all the objects in the world 
                # This "global" information should only be used for computing fitness (robot should not use global info for action)
                if self.objectIds:
                    robot.Set_Object_Ids(self.objectIds)
                
                # Perception/Action Loop
                robot.Sense(i)
                robot.Think()
                robot.Act(i)
            if self.runMode == "GUI":
                time.sleep(1/10000)

        self.been_run = True

    def Pickle_Sim(self, pickle_file_name="sim.pkl"):
        with open(pickle_file_name, 'wb') as pf:
            pickle.dump(self, pf, protocol=pickle.HIGHEST_PROTOCOL)

    def Print_Objectives(self):
        self.robots[0].Print_Objectives()

    def Get_Robots(self):
        return self.robots

    def Save_Values(self):
        for sensor in self.robot.sensors:
            print(self.robot.sensors[sensor].values)
            np.save(self.dir + "/data/data_" + self.robot.sensors[sensor].name + "_sensor.npy", self.robot.sensors[sensor].values)
            print(f"Sensor data saved to {self.dir}/data/data_" + self.robot.sensors[sensor].name + "_sensor.npy")

