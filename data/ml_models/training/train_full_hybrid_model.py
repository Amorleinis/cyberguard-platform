# --- Training Monitor ---
def monitor_training(epoch, batch_idx, x_nodes, A, y, logits, L_task, L_logic, logic_out):
    print(f"Epoch {epoch+1} Batch {batch_idx+1}")
    print(f"x_nodes shape: {x_nodes.shape}, A shape: {A.shape}, y shape: {y.shape}, logits shape: {logits.shape}")
    print(f"Task Loss: {L_task.item():.4f}, Logic Loss: {L_logic.item():.4f}, Total Loss: {(L_task+L_logic).item():.4f}")
    print("Logic Rule Diagnostics:")
    for rule, diag in logic_out['per_rule'].items():
        print(f"  {rule}: satisfaction={diag['satisfaction']:.4f}, penalty={diag['penalty']:.4f}")

"""
Full PyTorch training loop for Hybrid Neuro-Symbolic Model (Spectra Series)
- Loads batches from data_loader
- Instantiates all model blocks
- Implements cluster purity, transition, and graph-sequence alignment rules
- Logs per-rule losses and diagnostics
"""
import torch
import torch.nn.functional as F
from data_loader import load_spectra_batch, logic
from hybrid_neuro_symbolic_gnn_gnn_rbm_transformer_rbf_lstm_py_torch_scaffold import (
    GraphEncoder, SequenceEncoder, TransformerRefiner, RBF, RBM, GatedFusion
)

# Hyperparameters
BATCH_SIZE = 32
NUM_EPOCHS = 5
LAMBDA_PARAMS = [1.0, 1.0, 1.0]  # cluster_purity, transition, graph-seq alignment
LEARNING_RATE = 1e-3

# Paths to your data files
EMB_PATH = 'cyberguard_spectra_series/model_training/node2vec_embeddings_with_clusters.csv'
LABEL_PATH = 'cyberguard_spectra_series/model_training/node2vec_embeddings_with_clusters.csv'
ADJ_PATH = None  # or provide edge list CSV if available

# Instantiate model blocks

graph_encoder = GraphEncoder(64, 128)
seq_encoder = SequenceEncoder(32, 128)
transformer_refiner = TransformerRefiner(32)
rbf = RBF(128, 8)
rbm = RBM(128, 32)
fusion = None
classifier = None

## Remove manual rule functions; use LogicModule instead


optimizer = None

# Training loop


for epoch in range(NUM_EPOCHS):
    epoch_loss = 0.0
    for batch_idx, batch in enumerate(load_spectra_batch(EMB_PATH, LABEL_PATH, ADJ_PATH, batch_size=BATCH_SIZE)):
        x_nodes = batch['x_nodes']
        A = batch['A']
        y = batch['y']
        clusters = batch.get('clusters', torch.zeros_like(y))
        centrality = batch.get('centrality_norm', torch.zeros_like(y, dtype=torch.float32))
        outlier = batch.get('outlier_score', torch.zeros_like(y, dtype=torch.float32))
        x_seq = batch.get('x_seq', torch.zeros(x_nodes.shape[0], 5, 32))

        # Forward pass
        g = graph_encoder(x_nodes, A)
        s = seq_encoder(x_seq)
        t = transformer_refiner(x_seq)
        phi = rbf(g)
        h = rbm(g)

        # Print shapes for debugging
        print(f"Shapes: g={g.shape}, s={s.shape}, t={t.shape}, phi={phi.shape}, h={h.shape}")

        # Dynamically set fusion and classifier on first batch
        if fusion is None:
            dims = {'gnn': g.shape[-1], 'lstm': s.shape[-1], 'trans': t.shape[-1], 'rbf': phi.shape[-1], 'rbm': h.shape[-1]}
            fusion = GatedFusion(dims, 128)
            classifier = torch.nn.Linear(128, 4)
            optimizer = torch.optim.Adam(list(graph_encoder.parameters()) + list(seq_encoder.parameters()) + list(transformer_refiner.parameters()) + list(rbf.parameters()) + list(rbm.parameters()) + list(fusion.parameters()) + list(classifier.parameters()), lr=LEARNING_RATE)


        # Ensure all block outputs are [1, N, D] for node-wise prediction
        # If any are [1, D], expand to [1, N, D]
        N = x_nodes.shape[1]
        def expand_to_nodes(tensor):
            if tensor.dim() == 2:
                return tensor.unsqueeze(1).expand(-1, N, -1)
            return tensor
        g = expand_to_nodes(g)
        s = expand_to_nodes(s)
        t = expand_to_nodes(t)
        phi = expand_to_nodes(phi)
        h = expand_to_nodes(h)

        fused = fusion({'gnn':g, 'lstm':s, 'trans':t, 'rbf':phi, 'rbm':h})  # [1, N, fusion_dim]
        logits = classifier(fused)  # [1, N, num_classes]
        logits = logits.squeeze(0)  # [N, num_classes]
        y = y.view(-1)  # [N]
        print(f"DEBUG: logits shape {logits.shape}, y shape {y.shape}")
        assert logits.shape[0] == y.shape[0], f"Logits batch {logits.shape[0]} != y batch {y.shape[0]}"
        probs = F.softmax(logits, dim=-1)

        # Prepare pred and meta dicts for logic module
        clusters = batch.get('clusters')
        if clusters is not None and clusters.dim() == 3:
            clusters = clusters.squeeze(0)
            # Fix clusters shape to match num_nodes
            if 'clusters' in pred:
                clusters = pred['clusters']
                if clusters.shape[0] == 1:
                    pred['clusters'] = clusters.expand(num_nodes, clusters.shape[1])
        
            pred = {
                'logits': logits,
                'probs': probs,
                'clusters': clusters,
                'cluster_idx': clusters,
                'confidence': None,
                'outlier_score': batch.get('outlier_score'),
                'g': g,
                's': s,
                'A': A,
                'centrality_norm': batch.get('centrality_norm'),
                'rbf': phi,
                # Add more batch features as needed
            }
        meta = {
            # Populate with empirical stats if available
            'cluster_label_distribution': {},
            'forbidden_edge_pairs': None,
            'empirical_transitions': None,
            'similarity_pairs': None,
            # Add more meta info as needed
        }

    # Reshape y to 1D for cross_entropy
    y = y.view(-1)
    L_task = F.cross_entropy(logits, y)
    logic_out = logic.compute(pred, meta)
    L_logic = logic_out['loss']
    L_total = L_task + L_logic

    # Monitor training
    monitor_training(epoch, batch_idx, x_nodes, A, y, logits, L_task, L_logic, logic_out)

    # Backward pass
    optimizer.zero_grad()
    L_total.backward()
    optimizer.step()

    epoch_loss += float(L_total)

    print(f"Epoch {epoch+1}/{NUM_EPOCHS}, Loss: {epoch_loss:.4f}")
