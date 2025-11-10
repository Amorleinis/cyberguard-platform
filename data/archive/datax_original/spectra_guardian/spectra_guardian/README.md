# Spectra Guardian

## Overview
Spectra Guardian is a GNN-based intrusion response and mitigation system that builds dynamic graphs from network, login, and IDS logs, trains temporal GNN models, and integrates with SOAR/firewall for automated mitigation.

## Setup
- Create and activate Python virtual environment
- Install dependencies: `pip install -r requirements.txt`

## Usage
- Place your logs in the `data/` folder
- Implement modules in `spectra_guardian/`
- Run training and inference: `python run_training.py`
- Launch dashboard: `streamlit run spectra_guardian/dashboard.py`
