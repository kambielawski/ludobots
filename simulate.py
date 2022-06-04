import pyrosim.pyrosim as pyrosim
import pybullet as p
import pybullet_data
import time
import numpy as np
import random
import sys

from robot import Robot
from world import World
from simulation import Simulation
import constants as c

# runMode can be GUI or DIRECT
if len(sys.argv) > 1:
    runMode = sys.argv[1]
else:
    runMode = "DIRECT"

simulation = Simulation(runMode)
robot_1 = Robot("body_0.urdf")
# robot_2 = Robot("body_1.urdf")
world = World()

robots = [robot_1]


simulation.Run(robots)
simulation.Get_Fitness()



