"""
Master pipeline script: export data, engineer features, train GNN, and evaluate results.
Edit paths and parameters as needed for your use case.
"""


import subprocess
import os
import shutil
import logging
import yaml
from utils import setup_logging, get_versioned_output_dir

# Step 1: Export data from Neo4j
def export_data(out_dir):
    logging.info("[1/4] Exporting graph data from Neo4j...")
    subprocess.run(["python", "data_export/export_graph_data.py"], check=True)
    # Move exported CSVs to versioned output dir
    for fname in ["assets.csv", "threats.csv", "techniques.csv", "vulnerabilities.csv", "has_vulnerability.csv", "uses.csv", "exploits.csv"]:
        if os.path.exists(fname):
            shutil.move(fname, os.path.join(out_dir, fname))
            logging.info(f"Moved {fname} to {out_dir}")

# Step 2: Feature engineering
def engineer_features(out_dir):
    logging.info("[2/4] Engineering features...")
    # Copy needed CSVs to cwd
    for fname in ["assets.csv", "threats.csv", "techniques.csv", "vulnerabilities.csv"]:
        src = os.path.join(out_dir, fname)
        if os.path.exists(src):
            shutil.copy(src, fname)
    subprocess.run(["python", "feature_engineering/feature_engineering.py"], check=True)
    # Move feature files to versioned output dir
    for fname in ["assets_features.csv"]:
        if os.path.exists(fname):
            shutil.move(fname, os.path.join(out_dir, fname))
            logging.info(f"Moved {fname} to {out_dir}")

# Step 3: Train GNN model
def train_gnn(out_dir):
    logging.info("[3/4] Training GNN model with Neo4j GDS...")
    subprocess.run(["python", "training/train_gnn_gds.py"], check=True)
    # (Optional) Move model artifacts to out_dir if generated

# Step 4: Evaluate model
def evaluate(out_dir):
    logging.info("[4/4] Evaluating model predictions...")
    # Copy needed files to cwd
    for fname in ["predictions.csv"]:
        src = os.path.join(out_dir, fname)
        if os.path.exists(src):
            shutil.copy(src, fname)
    subprocess.run(["python", "evaluation/evaluate_gnn.py"], check=True)


def load_config(config_path="experiment_config.yaml"):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def cleanup_old_runs(base_dir="../models", keep_last_n=5):
    runs = [d for d in os.listdir(base_dir) if d.startswith("run_")]
    runs = sorted(runs, reverse=True)
    for old_run in runs[keep_last_n:]:
        path = os.path.join(base_dir, old_run)
        shutil.rmtree(path)
        logging.info(f"Deleted old run directory: {path}")

if __name__ == "__main__":
    config = load_config()
    log_file = setup_logging()
    out_dir = get_versioned_output_dir()
    logging.info(f"Pipeline started. Output dir: {out_dir}")
    export_data(out_dir)
    engineer_features(out_dir)
    train_gnn(out_dir)
    evaluate(out_dir)
    cleanup_old_runs(base_dir="../models", keep_last_n=config.get('output', {}).get('keep_last_n_runs', 5))
    logging.info("Pipeline complete. Check outputs in the versioned models/ directory.")
    print(f"Pipeline complete. Log: {log_file}\nOutputs: {out_dir}")
