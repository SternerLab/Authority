#!/bin/sh
python evaluate_self_aini.py 160000 200000 &
python evaluate_self_aini.py 200000 250000 &
python evaluate_self_aini.py 250000 300000 &
python evaluate_self_aini.py 300000 350000 &
python evaluate_self_aini.py 350000 400000 &
python evaluate_self_aini.py 400000 450000 &
python evaluate_self_aini.py 450000 500000 &
wait


