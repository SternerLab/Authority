#!/bin/sh
python evaluate_self_citations.py 16000 25000 &
python evaluate_self_citations.py 25000 50000 &
python evaluate_self_citations.py 50000 75000 &
python evaluate_self_citations.py 75000 100000 &
python evaluate_self_citations.py 100000 125000 &
python evaluate_self_citations.py 125000 150000 &
python evaluate_self_citations.py 150000 160000 &
wait


