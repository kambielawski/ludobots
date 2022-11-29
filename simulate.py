import argparse

from robot import Robot
from world import World
from simulation import Simulation
import constants as c

parser = argparse.ArgumentParser()
parser.add_argument("display", help="Display mode for pybullet. 'GUI' or 'DIRECT'", choices=['GUI', 'DIRECT'])
parser.add_argument("solution_id", help="Solution ID for this simulation", type=int)
parser.add_argument("brain_file", help="Path to .nndf file")
parser.add_argument("body_file", help="Path to .urdf file")
# parser.add_argument("objective", help="Objective scheme for AFPO", choices=['emp_fitness', 'tri_fitness'])
parser.add_argument("--directory", default='.', help="Experiment directory", type=str)
parser.add_argument("--window", help="Empowerment window size", type=int)

args = parser.parse_args()

windowSize = c.TIMESTEPS if args.window else 0

# Setup simulation, world, and robot
simulation = Simulation(args.display, args.solution_id, dir=args.directory)
world = World(args.solution_id, dir=args.directory)
# robots = [Robot(args.solution_id, args.body_file, args.brain_file, windowSize)]
robots = [Robot(args.solution_id, "robots/body_quadruped.urdf", args.brain_file, windowSize, dir=args.directory)]

# Run pybullet simulation
simulation.Run(robots)
# Write robot objective values to stdout
simulation.Print_Objectives()



