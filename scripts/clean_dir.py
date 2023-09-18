from sys import platform
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--dir', required=False, default='.', type=str)
args = parser.parse_args()

OS_RM = 'del' if platform == 'win32' else 'rm'
# Remove the rest
os.system(OS_RM + f' {args.dir}/body_*_*.urdf')
os.system(OS_RM + f' {args.dir}/fitness_*.txt')

for i in range(10):
    try:
        os.system(OS_RM + f' {args.dir}/world_{i}*.sdf')
        os.system(OS_RM + f' {args.dir}/brain_{i}*.nndf')
    except:
        print('Something went wrong')