import argparse

from robot import Robot
from simulation import Simulation
from plotting.run_plotter import RunPlotter

TIMESTEPS = 1000

parser = argparse.ArgumentParser()
parser.add_argument("display", help="Display mode for pybullet. 'GUI' or 'DIRECT'", choices=['GUI', 'DIRECT'])
parser.add_argument("solution_id", help="Solution ID for this simulation", type=int)
parser.add_argument("brain_file", help="Path to .nndf file")
parser.add_argument("body_file", help="Path to .urdf file")
parser.add_argument("--directory", default='.', help="Experiment directory", type=str)
parser.add_argument("--empowerment_window_size", default=TIMESTEPS//2, help="Empowerment window size", type=int)
parser.add_argument("--objects_file", default='', help=".sdf file for other world objects (e.g. box)", type=str)
parser.add_argument("--pickle_sim", default=False, help="Pickle the simulation (true/false)", type=bool)
parser.add_argument("--motor_measure", default='DESIRED_ANGLE', help="Motor measurement for empowerment calc. 'VELOCITY' or 'DESIRED_ANGLE'", 
                    type=str,  choices=['VELOCITY', 'DESIRED_ANGLE'])
parser.add_argument("--wind", default=0, type=int, help="Degree of 'windiness', i.e. number of random force vectors to apply during simulation")
parser.add_argument("--save_sa_data", type=str, default="", help="Save sensor and action values over course of simulation")
parser.add_argument("--save_position_data", type=str, default="", help="Save position values over course of simulation")

args = parser.parse_args()

# Setup simulation, world, and robot
simulation = Simulation(args.display, args.solution_id, TIMESTEPS, wind=args.wind, objectsFile=args.objects_file, dir=args.directory)
robot_options = {
    'motor_measure': args.motor_measure,
    'empowerment_window_size': args.empowerment_window_size,
    'body_file': args.body_file,
    'brain_file': args.brain_file
}
robots = [Robot(args.solution_id, robot_options, dir=args.directory)]

# Run pybullet simulation
simulation.Run(robots)

# Write robot objective values to stdout
simulation.Print_Objectives()

if args.pickle_sim:
    simulation.Pickle_Sim("transient.pkl")

if args.save_sa_data != "":
    simulation.save_sa_values(f'{args.save_sa_data}')

if args.save_position_data != "":
    simulation.save_position_values(f'{args.save_position_data}')
