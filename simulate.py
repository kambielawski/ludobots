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

simulation = Simulation()
robot_1 = Robot("body_0.urdf")
robot_2 = Robot("body_1.urdf")
world = World()

robots = [robot_1, robot_2]

simulation.Run(robots)



