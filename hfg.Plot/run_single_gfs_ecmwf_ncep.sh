#!/bin/bash
source ~/.bash_profile
cd /cpvs/bin/5Plot

running=.run_single_$1_$2_$3
if [ ! -f $running ]; then
	  touch $running
	    
  else
	    echo "running process"
	      exit
      fi
      # running process

      python3 dispatch_plot_verify_single.py $1
      python3 dispatch_plot_verify_single.py $2
      python3 dispatch_plot_verify_single.py $3
      rm -rf $running

