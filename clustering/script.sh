#!/usr/bin/env bash
# this script performs clustering on the blocks paralelly to speed up the process. Command to use python main_firstinitial.py <starting block number> <ending block number>. By running the command, you perform clustering on blocks starting from <starting block number> to <ending block number>. Adjust the parallelization according to your compute speeds.

python main_firstinitial.py 0 50000 &
python main_firstinitial.py 50000 100000 &
python main_firstinitial.py 100000 150000 &
python main_firstinitial.py 150000 200000 &
python main_firstinitial.py 200000 250000 &
python main_firstinitial.py 250000 300000 &
python main_firstinitial.py 300000 350000 &
python main_firstinitial.py 350000 400000 &
wait

