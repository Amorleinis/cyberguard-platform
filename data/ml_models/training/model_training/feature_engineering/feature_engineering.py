"""
Feature engineering for GNN training: load exported CSVs, create node/edge features, and save processed data.
"""
import pandas as pd
import numpy as np

# Load nodes
assets = pd.read_csv('assets.csv')
threats = pd.read_csv('threats.csv')
techniques = pd.read_csv('techniques.csv')
vulnerabilities = pd.read_csv('vulnerabilities.csv')

# Load relationships
has_vuln = pd.read_csv('has_vulnerability.csv')

# Compute vuln_count per asset using has_vulnerability.csv
if not has_vuln.empty and 'source' in has_vuln.columns:
	vuln_counts = has_vuln['source'].value_counts().to_dict()
	assets['vuln_count'] = assets['asset_id'].map(vuln_counts).fillna(0).astype(int)
else:
	assets['vuln_count'] = 0

# Example: is_critical feature
assets['is_critical'] = assets['criticality'].apply(lambda x: 1 if str(x).lower() == 'high' else 0)

# Save processed features
assets.to_csv('assets_features.csv', index=False)
print('Saved asset features to assets_features.csv')
