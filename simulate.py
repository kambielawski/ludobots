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
robot = Robot()
world = World()

simulation.Run(robot)



