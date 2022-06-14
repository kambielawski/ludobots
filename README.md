# ludobots

To run: 

`python3 simulate.py <run_mode> <id> <brain_file>`

`run_mode` can take on values `GUI` or `DIRECT` (default: `DIRECT`)
`id` specifies the solution ID (default: `0`)
specifying `brain_file` allows you to run a specific brain in simulation (default: None)

to run the pybullet physics simulation (pulling from the files generated from previous command)

### To run an evolutionary algorithm

`python3 search.py`

Specify number of generations and population size in constants.py

### To run an experiment:

1. Build an experiment (altering Experiment class in experiment.py) by changing the Experiment's parameters  

2. `python3 experiment.py`
