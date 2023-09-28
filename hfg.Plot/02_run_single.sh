#!/bin/bash
source ~/.bash_profile
conda activate plotenv
cd /cpvs/bin/5Plot

para1=$(ps -ef | grep "dispatch_plot_verify_single.py $1" | grep -v grep | cut -c 9-15)
if [ -z "$para1" ]
then  
  echo "IS NULL"  
else  
  echo "NOT NULL"
  echo "kill $para1" 
  ps -ef | grep "dispatch_plot_verify_single.py $1" | grep -v grep | cut -c 9-15 | xargs kill -9
  ps -ef | grep "defunct" | grep -v grep | cut -c 9-15 | xargs kill -9
fi    


python3 dispatch_plot_verify_single.py $1
