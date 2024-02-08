"""Simulation class"""
import pickle
import pybullet as p
import pybullet_data
import numpy as np
import time 
import random

#TODO: Migrate this to a config file
GRAVITY_FORCE = -9.8 # m/s^2

class Simulation:
    """Simulation class
    - Manages Pybullet setup and interfacing
    """
    def __init__(self, runMode, solutionId, timesteps, wind=0, objectsFile='', dir='.'):
        self.runMode = runMode
        self.solutionId = solutionId
        self.timesteps = timesteps
        self.dir = dir
        self.been_run = False
        self.wind = wind
        self.wind_timesteps = random.sample(range(self.timesteps), self.wind)
        self.body_positions = []
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

    def Run(self, robots):
        """Run simulation for robots (sense -> act -> update sim)"""
        self.robots = robots
        p.setRealTimeSimulation(0)
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

                # Apply wind
                if self.wind > 0 and i in self.wind_timesteps:
                    robot.Apply_Random_Force_Vector(5000)

            if self.runMode == "GUI":
                time.sleep(1/10000)

        self.been_run = True

    def Pickle_Sim(self, pickle_file_name="sim.pkl"):
        """Pickle the simulation object for later use"""
        with open(pickle_file_name, 'wb') as pf:
            pickle.dump(self, pf, protocol=pickle.HIGHEST_PROTOCOL)

    def Print_Objectives(self):
        """Print the objectives of the robot in the simulation."""
        self.robots[0].Print_Objectives()

    def Get_Robots(self):
        """Return the robots in the simulation."""
        return self.robots

    def Save_SA_Values(self, dir):
        """Save sensor and action values over the course of the simulation."""
        all_robot_sa_values = []
        for robot in self.robots:
            sa_values = {'sensor_states': robot.sensorVals, 'motor_states': robot.motorVals}
            all_robot_sa_values.append(sa_values)

        with open(f'{dir}/{robot.solutionId}_sa.pkl', 'wb') as pf:
            pickle.dump(all_robot_sa_values, pf)

    def Save_Position_Values(self, dir):
        """Save position values over the course of the simulation."""
        all_position_values = []
        for robot in self.robots: 
            all_position_values.append(robot.Get_Position_Values())

        with open(f'{dir}/{robot.solutionId}_positions.pkl', 'wb') as pf:
            pickle.dump(all_position_values, pf)
    