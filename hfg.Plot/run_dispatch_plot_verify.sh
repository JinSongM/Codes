#!/bin/bash
source ~/.bash_profile
cd /cpvs/bin/5Plot

running=.run_$1
if [ ! -f $running ]; then
  touch $running
  
else
  echo "running process"
  exit
fi
# running process

python3 dispatch_plot_verify.py $1

rm -rf $running
