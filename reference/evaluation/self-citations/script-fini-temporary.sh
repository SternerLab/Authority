#!/bin/sh
python evaluate_self_fini.py 160000 200000 &
python evaluate_self_fini.py 200000 250000 &
python evaluate_self_fini.py 250000 300000 &
python evaluate_self_fini.py 300000 350000 &
python evaluate_self_fini.py 350000 400000 &
python evaluate_self_fini.py 400000 450000 &
python evaluate_self_fini.py 450000 500000 &
wait


