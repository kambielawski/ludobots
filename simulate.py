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
if len(sys.argv) > 2:
    runMode = sys.argv[1]
    solnId = int(sys.argv[2])
else:
    runMode = "DIRECT"
    solnId = 0

simulation = Simulation(runMode, solnId)
robot_1 = Robot("body_1.urdf", solnId)
# robot_2 = Robot("body_1.urdf", solnId)
world = World()

robots = [robot_1]


simulation.Run(robots)
simulation.Get_Fitness()



