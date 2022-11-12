from sys import platform
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--dir', required=False, default='.', type=str)
args = parser.parse_args()

OS_RM = 'del' if platform == 'win32' else 'rm'
# Remove the rest
os.system(OS_RM + f' {args.dir}/world_*.sdf && ' 
        + OS_RM + f' {args.dir}/brain_*.nndf && ' 
        + OS_RM + f' {args.dir}/body_quadruped_*.urdf && ' 
        + OS_RM + f' {args.dir}/fitness_*.txt')