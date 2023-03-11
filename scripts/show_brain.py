import sys
import os

if len(sys.argv) < 3:
    print("Usage: python show_brain.py <brain.nndf file> <body.urdf file>\n")
    exit(1)


# ensure file exists
brain_file = sys.argv[1]
if not os.path.exists(brain_file):
    print("Could not open " + sys.argv[1])
    exit(1)

# ensure file exists
body_file = sys.argv[2]
if not os.path.exists(body_file):
    print("Could not open " + sys.argv[2])
    exit(1)

# ensure file exists
world_file = sys.argv[3] if len(sys.argv) > 3 else 'world.sdf'
if not os.path.exists(world_file):
    print("Could not open " + sys.argv[3])
    exit(1)

# for windowSize in range(10,500,10):
os.system("python3 simulate.py GUI 0 " + brain_file + " " + body_file + " --objects_file " + world_file)

