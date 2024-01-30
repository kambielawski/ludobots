#!/bin/bash

#SBATCH --partition=bluemoon
#SBATCH --nodes=1
# #SBATCH --ncpu=100
#SBATCH --ntasks=100
#SBATCH --time=30:00:00
#SBATCH --mem-per-cpu=2G
#SBATCH --job-name=experiment_test_1
#SBATCH --output=%x_%j.out

set -x 

cd /gpfs1/home/k/t/ktbielaw/projects/ludobots

source /gpfs1/home/k/t/ktbielaw/anaconda3/bin/activate pyrosim

conda env list

python3 run_exp.py --exp experiment.exp
