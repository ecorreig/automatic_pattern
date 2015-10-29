#!/bin/sh
base=$(dirname $0)
cd $base

date > date
source venv/bin/activate
python main.py > logs/stdout 2> logs/stderr
python send_logs.py logs/stdout logs/stderr