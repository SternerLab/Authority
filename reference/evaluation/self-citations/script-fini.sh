#!/bin/sh
python evaluate_self_fini.py 0 500 &
python evaluate_self_fini.py 500 1500 &
python evaluate_self_fini.py 1500 5000 &
python evaluate_self_fini.py 5000 16000 &
python evaluate_self_fini.py 16000 25000 &
python evaluate_self_fini.py 25000 50000 &
python evaluate_self_fini.py 50000 75000 &
python evaluate_self_fini.py 75000 100000 &
python evaluate_self_fini.py 100000 125000 &
python evaluate_self_fini.py 125000 150000 &
python evaluate_self_fini.py 150000 160000 &
wait


