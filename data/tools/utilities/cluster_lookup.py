"""
cluster_lookup.py

Utility to load and query cluster assignments and outlier flags for use in Sentry/Guardian/Phoenix modules.
"""
import pandas as pd
import os

CLUSTER_CSV = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../node2vec_embeddings_with_clusters_and_outliers.csv'))

class ClusterLookup:
    def __init__(self, csv_path=CLUSTER_CSV):
        self.df = pd.read_csv(csv_path)
        self.df.set_index('node_id', inplace=True)

    def get_cluster_info(self, node_id):
        """Return cluster, outlier flag, and (optionally) label for a node_id."""
        if node_id not in self.df.index:
            return None
        row = self.df.loc[node_id]
        return {
            'cluster': int(row['cluster']),
            'outlier': bool(row['outlier']),
            'label': row['labels'] if 'labels' in row else None
        }

# Example usage:
if __name__ == '__main__':
    lookup = ClusterLookup()
    test_id = lookup.df.index[0]
    print(f"Info for node_id {test_id}: {lookup.get_cluster_info(test_id)}")
