import os

from hillclimber import HillClimber

hc = HillClimber()
hc.Evolve()
hc.Show_Best()

'''
for i in range(2):
    os.system("python3 generate.py")
    os.system("python3 simulate.py")
'''

