#!/bin/bash

#SBATCH --partition=bluemoon
#SBATCH --nodes=1
#SBATCH --ntasks=100
#SBATCH --time=00:20:00
#SBATCH --mem-per-cpu=2G
#SBATCH --job-name=search_exp
#SBATCH --output=%x_%j.out

set -x 

cd /gpfs1/home/k/t/ktbielaw/projects/ludobots

source /gpfs1/home/k/t/ktbielaw/anaconda3/bin/activate pyrosim

# conda env list

# python3 run_exp.py --exp experiment.exp
python3 search.py
