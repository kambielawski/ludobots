import sys
sys.path.append('..')
from plotting.viz import Visualizer

v = Visualizer()
genData = v.Parse_Gen_Data('../data/gen_data_n200g800_trife.txt')

lastGen = sorted(genData[799], key=lambda x:x[2], reverse=True)

print(lastGen[:3])

