import argparse

from robot import Robot
from simulation import Simulation
import constants as c
from plotting.run_plotter import RunPlotter

parser = argparse.ArgumentParser()
parser.add_argument("display", help="Display mode for pybullet. 'GUI' or 'DIRECT'", choices=['GUI', 'DIRECT'])
parser.add_argument("solution_id", help="Solution ID for this simulation", type=int)
parser.add_argument("brain_file", help="Path to .nndf file")
parser.add_argument("body_file", help="Path to .urdf file")
parser.add_argument("--directory", default='.', help="Experiment directory", type=str)
parser.add_argument("--empowerment_window_size", default=c.TIMESTEPS//2, help="Empowerment window size", type=int)
parser.add_argument("--objects_file", default='', help=".sdf file for other world objects (e.g. box)", type=str)
parser.add_argument("--pickle_sim", default=False, help="Pickle the simulation (true/false)", type=bool)
parser.add_argument("--motor_measure", default='DESIRED_ANGLE', help="Motor measurement for empowerment calc. 'VELOCITY' or 'DESIRED_ANGLE'", 
                    type=str,  choices=['VELOCITY', 'DESIRED_ANGLE'])

args = parser.parse_args()

# Setup simulation, world, and robot
simulation = Simulation(args.display, args.solution_id, objectsFile=args.objects_file, dir=args.directory)
robot_options = {
    'motor_measure': args.motor_measure,
    'empowerment_window_size': args.empowerment_window_size,
    'body_file': "robots/body_quadruped.urdf",
    'brain_file': args.brain_file
}
robots = [Robot(args.solution_id, robot_options, dir=args.directory)]

# Run pybullet simulation
simulation.Run(robots)

# Write robot objective values to stdout
simulation.Print_Objectives()

if args.pickle_sim:
    simulation.Pickle_Sim("transient.pkl")

# run_plotter = RunPlotter(simulation)
# run_plotter.Action_Sensor_Pair_LogPlot()