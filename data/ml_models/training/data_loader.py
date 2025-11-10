"""
Data loader for CyberGuard Spectra Series hybrid neuro-symbolic pipeline.
Supports loading node embeddings, adjacency, sequences, labels, clusters, centrality, outlier scores from CSV and JSON files.
"""
import os
import pandas as pd
import numpy as np
import torch
import json

# --- Logic Rules Integration ---
import sys
sys.path.append(os.path.dirname(__file__))
from model_logic_8_rules_integrated_code_python import LogicModule

# Example: Instantiate logic module for use in training
logic = LogicModule()

# To use in training loop:
# for batch in loader:
#     pred = {...}  # model outputs and batch features
#     meta = {...}  # batch meta info (cluster_label_distribution, forbidden_edge_pairs, etc)
#     logic_out = logic.compute(pred, meta)
#     logic_loss = logic_out['loss']
#     per_rule_diag = logic_out['per_rule']
#     # Use logic_loss in your objective, log per_rule_diag for diagnostics



def load_csv_embeddings(path, emb_prefix='emb_'):
    df = pd.read_csv(path)
    emb_cols = [col for col in df.columns if col.startswith(emb_prefix)]
    embeddings = df[emb_cols].values.astype(np.float32)
    return torch.tensor(embeddings), df

def load_csv_labels(path, label_col='labels'):
    df = pd.read_csv(path)
    labels = df[label_col].values
    label_map = {l: i for i, l in enumerate(sorted(set(labels)))}
    y = np.array([label_map[l] for l in labels], dtype=np.int64)
    return torch.tensor(y), label_map

def load_csv_clusters(df, cluster_col='cluster'):
    if cluster_col in df.columns:
        clusters = df[cluster_col].values.astype(np.int64)
        return torch.tensor(clusters)
    return None

def load_csv_centrality(df, centrality_col='centrality_norm'):
    if centrality_col in df.columns:
        centrality = df[centrality_col].values.astype(np.float32)
        return torch.tensor(centrality)
    return None

def load_csv_outlier(df, outlier_col='outlier'):
    if outlier_col in df.columns:
        outlier = df[outlier_col].values.astype(np.float32)
        return torch.tensor(outlier)
    return None

def load_csv_sequence(df, seq_prefix='seq_'):
    seq_cols = [col for col in df.columns if col.startswith(seq_prefix)]
    if seq_cols:
        seq = df[seq_cols].values.astype(np.float32)
        return torch.tensor(seq)
    return None

def load_csv_adjacency(path, num_nodes):
    df = pd.read_csv(path)
    A = np.zeros((num_nodes, num_nodes), dtype=np.float32)
    for _, row in df.iterrows():
        A[int(row['src']), int(row['dst'])] = 1.0
    np.fill_diagonal(A, 1.0)
    A = A / (A.sum(axis=1, keepdims=True) + 1e-8)
    return torch.tensor(A)

def load_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def batchify_tensor(tensor, batch_size):
    N = tensor.shape[0]
    for i in range(0, N, batch_size):
        yield tensor[i:i+batch_size]



def load_feature_csv(path, dtype=torch.float32):
    if path and os.path.exists(path):
        df = pd.read_csv(path)
        arr = df.values.astype(np.float32)
        return torch.tensor(arr, dtype=dtype)
    return None

def load_feature_json(path):
    if path and os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def load_spectra_batch(
    emb_path,
    label_path,
    adj_path=None,
    cluster_path=None,
    centrality_path=None,
    outlier_path=None,
    seq_path=None,
    threats_path=None,
    techniques_path=None,
    assets_path=None,
    silhouette_path=None,
    ml_dataset_path=None,
    ml_dataset_context_path=None,
    ml_dataset_graph_features_path=None,
    node2vec_path=None,
    node2vec_outliers_path=None,
    cluster_centroids_path=None,
    cluster_label_summary_path=None,
    cluster_transition_matrix_path=None,
    label_cluster_confusion_matrix_path=None,
    cve_data_ml_ready_path=None,
    cybersecurity_threat_taxonomy_path=None,
    has_vulnerability_path=None,
    experiment_config_path=None,
    nvdcve_json_paths=None,
    batch_size=32
):
    embeddings, emb_df = load_csv_embeddings(emb_path)
    y, label_map = load_csv_labels(label_path)
    clusters = load_csv_clusters(emb_df)
    centrality = load_csv_centrality(emb_df)
    outlier = load_csv_outlier(emb_df)
    seq = load_csv_sequence(emb_df)

    num_nodes = embeddings.shape[0]
    # Sanity check: cap num_nodes to prevent huge memory allocation
    MAX_NODES = 10000
    if num_nodes > MAX_NODES:
        print(f"Warning: num_nodes ({num_nodes}) exceeds MAX_NODES ({MAX_NODES}). Capping to {MAX_NODES}.")
        num_nodes = MAX_NODES
        embeddings = embeddings[:MAX_NODES]
        y = y[:MAX_NODES]
        # Also cap other batch features if needed
        if clusters is not None:
            clusters = clusters[:MAX_NODES]
        if centrality is not None:
            centrality = centrality[:MAX_NODES]
        if outlier is not None:
            outlier = outlier[:MAX_NODES]
        if seq is not None:
            seq = seq[:MAX_NODES]
    if adj_path:
        A = load_csv_adjacency(adj_path, num_nodes)
    else:
        A = torch.eye(num_nodes)

    # Load additional features
    threats = load_feature_csv(threats_path)
    techniques = load_feature_csv(techniques_path)
    assets = load_feature_csv(assets_path)
    silhouette = load_feature_csv(silhouette_path)
    ml_dataset = load_feature_csv(ml_dataset_path)
    ml_dataset_context = load_feature_csv(ml_dataset_context_path)
    ml_dataset_graph_features = load_feature_csv(ml_dataset_graph_features_path)
    node2vec = load_feature_csv(node2vec_path)
    node2vec_outliers = load_feature_csv(node2vec_outliers_path)
    cluster_centroids = load_feature_csv(cluster_centroids_path)
    cluster_label_summary = load_feature_csv(cluster_label_summary_path)
    cluster_transition_matrix = load_feature_csv(cluster_transition_matrix_path)
    label_cluster_confusion_matrix = load_feature_csv(label_cluster_confusion_matrix_path)
    cve_data_ml_ready = load_feature_csv(cve_data_ml_ready_path)
    cybersecurity_threat_taxonomy = load_feature_csv(cybersecurity_threat_taxonomy_path)
    has_vulnerability = load_feature_csv(has_vulnerability_path)
    experiment_config = load_feature_json(experiment_config_path)
    nvdcve_jsons = [load_feature_json(p) for p in nvdcve_json_paths or []]

    # For GNN blocks, yield the full capped graph as a single batch
    batch = {
        'x_nodes': embeddings.unsqueeze(0),  # [1, N, D]
        'A': A.unsqueeze(0) if A.dim() == 2 else A,  # [1, N, N]
        'y': y.unsqueeze(0),  # [1, N]
        'label_map': label_map
    }
    if clusters is not None:
        batch['clusters'] = clusters.unsqueeze(0)
    if centrality is not None:
        batch['centrality_norm'] = centrality.unsqueeze(0)
    if outlier is not None:
        batch['outlier_score'] = outlier.unsqueeze(0)
    if seq is not None:
        batch['x_seq'] = seq.unsqueeze(0)
    if threats is not None:
        batch['threats'] = threats.unsqueeze(0)
    if techniques is not None:
        batch['techniques'] = techniques.unsqueeze(0)
    if assets is not None:
        batch['assets'] = assets.unsqueeze(0)
    if silhouette is not None:
        batch['silhouette'] = silhouette.unsqueeze(0)
    if ml_dataset is not None:
        batch['ml_dataset'] = ml_dataset.unsqueeze(0)
    if ml_dataset_context is not None:
        batch['ml_dataset_context'] = ml_dataset_context.unsqueeze(0)
    if ml_dataset_graph_features is not None:
        batch['ml_dataset_graph_features'] = ml_dataset_graph_features.unsqueeze(0)
    if node2vec is not None:
        batch['node2vec'] = node2vec.unsqueeze(0)
    if node2vec_outliers is not None:
        batch['node2vec_outliers'] = node2vec_outliers.unsqueeze(0)
    if cluster_centroids is not None:
        batch['cluster_centroids'] = cluster_centroids.unsqueeze(0)
    if cluster_label_summary is not None:
        batch['cluster_label_summary'] = cluster_label_summary.unsqueeze(0)
    if cluster_transition_matrix is not None:
        batch['cluster_transition_matrix'] = cluster_transition_matrix.unsqueeze(0)
    if label_cluster_confusion_matrix is not None:
        batch['label_cluster_confusion_matrix'] = label_cluster_confusion_matrix.unsqueeze(0)
    if cve_data_ml_ready is not None:
        batch['cve_data_ml_ready'] = cve_data_ml_ready.unsqueeze(0)
    if cybersecurity_threat_taxonomy is not None:
        batch['cybersecurity_threat_taxonomy'] = cybersecurity_threat_taxonomy.unsqueeze(0)
    if has_vulnerability is not None:
        batch['has_vulnerability'] = has_vulnerability.unsqueeze(0)
    if experiment_config is not None:
        batch['experiment_config'] = experiment_config
    if nvdcve_jsons:
        batch['nvdcve_jsons'] = nvdcve_jsons
    yield batch
