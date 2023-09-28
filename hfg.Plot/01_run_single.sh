#!/bin/bash
source ~/.bash_profile
conda activate plotenv
cd /cpvs/bin/5Plot

running=.run_single_$1
if [ ! -f $running ]; then
	touch $running
	    
else
	echo "running process"
	exit
fi
# running process

python3 dispatch_plot_verify_single.py $1
rm -rf $running
