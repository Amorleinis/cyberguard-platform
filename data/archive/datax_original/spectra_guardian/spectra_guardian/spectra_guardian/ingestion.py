import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../model_training')))
from cluster_lookup import ClusterLookup
import os
# ...existing code...

def enrich_with_cluster_info(df, node_id_col='node_id'):
    """
    Enrich a DataFrame with cluster and outlier info for each node/event.
    Adds columns: 'cluster', 'outlier', 'label' (if available).
    """
    lookup = ClusterLookup()
    clusters = []
    outliers = []
    labels = []
    for node_id in df[node_id_col]:
        info = lookup.get_cluster_info(node_id)
        if info:
            clusters.append(info['cluster'])
            outliers.append(info['outlier'])
            labels.append(info['label'])
        else:
            clusters.append(None)
            outliers.append(None)
            labels.append(None)
    df['cluster'] = clusters
    df['outlier'] = outliers
    df['label'] = labels
    return df

# Example usage:
if __name__ == '__main__':
    # Example: Enrich a dummy DataFrame
    import pandas as pd
    test_df = pd.DataFrame({'node_id': [1, 2, 3]})
    enriched = enrich_with_cluster_info(test_df)
    print(enriched)
import pandas as pd
import json
from pathlib import Path

def load_logs(paths):
    """
    Load logs from CSV or JSON files, parse timestamps.
    """
    # TODO: implement
    pass

def preprocess_network_logs(df):
    """
    Clean and normalize network logs.
    """
    # TODO: implement
    pass
