from sys import platform
import os

OS_RM = 'del' if platform == 'win32' else 'rm'
# Remove the rest
os.system(OS_RM + ' ./world_*.sdf && ' 
        + OS_RM + ' ./brain_*.nndf && ' 
        + OS_RM + ' ./body_quadruped_*.urdf && ' 
        + OS_RM + ' ./fitness_*.txt')