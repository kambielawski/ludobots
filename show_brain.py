import sys
import os
from solution import Solution

if len(sys.argv) < 2:
    print("Usage: python3 show_brain.py <brain.nndf file>\n")
    exit(1)


# ensure file exists
brain_file = sys.argv[1]
if not os.path.exists(brain_file):
    print("Could not open " + sys.argv[1])
    exit(1)

os.system("python3 simulate.py GUI 0 best_brain.nndf")

