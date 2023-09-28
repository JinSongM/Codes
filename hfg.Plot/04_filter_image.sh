#!/bin/bash
source ~/.bash_profile
conda activate plotenv
cd /cpvs/bin/5Plot
python3 plot_single_Filter.py $1 $2 $3 $4 $5 $6 $7
