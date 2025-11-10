#!/usr/bin/env python3
import argparse, sys, subprocess
parser = argparse.ArgumentParser()
parser.add_argument('--demo', choices=['hetero','tgn','rl','ingest'], required=True)
args = parser.parse_args()
if args.demo=='hetero':
    subprocess.run([sys.executable,'hetero_gnn_demo.py'])
elif args.demo=='tgn':
    subprocess.run([sys.executable,'tgn_temporal_example.py'])
elif args.demo=='rl':
    subprocess.run([sys.executable,'rl_remediation_env_integrated.py'])
elif args.demo=='ingest':
    subprocess.run([sys.executable,'ingest_pseudocode.py'])
