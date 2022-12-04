import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# from ageFitnessPareto import AgeFitnessPareto
from plotting.experiment_plotter import ExperimentPlotter

experiments = {
    'emp_v_random': './experiments/exp_Dec03_12_23',
    'emp_v_fitness': './experiments/exp_Nov17_03_35'
}

plotter = ExperimentPlotter()
for exp in experiments:
    plotter.Load_Experiment(experiments[exp], exp)

plotter.Plot_Combined_Top_Fitness([e for e in experiments])
# plotter.Plot_Combined_Top_Empowerment([e for e in experiments])