import os

files = list(filter(lambda file: 'brain_' in file, os.listdir('./best_robots/empowered')))
for brain in files:
    os.system(f'python3 simulate.py GUI 0 ./best_robots/empowered/{brain} robots/body_quadruped.urdf')