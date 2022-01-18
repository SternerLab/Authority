#!/bin/sh
python evaluate_self_aini.py 0 500 &
python evaluate_self_aini.py 500 1500 &
python evaluate_self_aini.py 1500 5000 &
python evaluate_self_aini.py 5000 16000 &
python evaluate_self_aini.py 16000 25000 &
python evaluate_self_aini.py 25000 50000 &
python evaluate_self_aini.py 50000 75000 &
python evaluate_self_aini.py 75000 100000 &
python evaluate_self_aini.py 100000 125000 &
python evaluate_self_aini.py 125000 150000 &
python evaluate_self_aini.py 150000 160000 &
wait


