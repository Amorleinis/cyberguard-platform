import pandas as pd
import os

# List of NVD files to process
nvd_files = [
    'data/processed/NVD/further/nvd_enriched.csv',
    'data/processed/NVD/further/nvd_ml_ready.csv',
    # Add more files as needed
]

# Choose label: multiclass severity (cvss_severity) and binary criticality (is_critical)
def add_label_columns(file_path):
    df = pd.read_csv(file_path)
    # Add multiclass label (severity)
    if 'cvss_severity' in df.columns:
        df['label_severity'] = df['cvss_severity']
    # Add binary label (critical or not)
    if 'is_critical' in df.columns:
        df['label_critical'] = df['is_critical']
    # Save new file
    out_path = file_path.replace('.csv', '_with_labels.csv')
    df.to_csv(out_path, index=False)
    print(f"Processed {file_path} -> {out_path}")

for file in nvd_files:
    if os.path.exists(file):
        add_label_columns(file)
    else:
        print(f"File not found: {file}")
