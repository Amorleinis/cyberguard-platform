"""
Sample training script for Hybrid Neuro-Symbolic Model (Spectra Series)
- Loads dummy data
- Instantiates all blocks
- Adds logic rules
- Runs a forward and backward pass
"""
import torch
import torch.nn.functional as F
from hybrid_neuro_symbolic_gnn_gnn_rbm_transformer_rbf_lstm_py_torch_scaffold import (
    GraphEncoder, SequenceEncoder, TransformerRefiner, RBF, RBM, GatedFusion, LogicRegularizer
)

# Dummy data shapes
B, N, D_node, T, D_seq, H_g, H_s, K_rbf, H_rbm, H_f, num_classes = 8, 10, 64, 5, 32, 128, 128, 8, 32, 128, 4
x_nodes = torch.randn(B, N, D_node)
A = torch.eye(N).unsqueeze(0).repeat(B,1,1)  # identity adjacency for demo
x_seq = torch.randn(B, T, D_seq)
y = torch.randint(0, num_classes, (B,))

# Instantiate blocks
graph_encoder = GraphEncoder(D_node, H_g)
seq_encoder = SequenceEncoder(D_seq, H_s)
transformer_refiner = TransformerRefiner(D_seq)
rbf = RBF(H_g, K_rbf)
rbm = RBM(H_g, H_rbm)
fusion = GatedFusion({'gnn':H_g, 'lstm':H_s, 'trans':H_s, 'rbf':K_rbf, 'rbm':H_rbm}, H_f)
classifier = torch.nn.Linear(H_f, num_classes)
logic = LogicRegularizer()

# Add example logic rule: mutual exclusion between class 0 and 3
logic.add_rule('asset_vuln_exclude', lambda p: 1.0 - p['probs'][:,0] * p['probs'][:,3], weight=1.0)

# Forward pass
with torch.no_grad():
    g = graph_encoder(x_nodes, A)
    s = seq_encoder(x_seq)
    t = transformer_refiner(x_seq)
    phi = rbf(g)
    h = rbm(g)
    fused = fusion({'gnn':g, 'lstm':s, 'trans':t, 'rbf':phi, 'rbm':h})
    logits = classifier(fused)
    probs = F.softmax(logits, dim=-1)
    pred = {'probs': probs}
    logic_out = logic(pred)
    L_task = F.cross_entropy(logits, y)
    L_logic = logic_out['loss']
    L_total = L_task + 0.1 * L_logic
    print('L_task:', float(L_task))
    print('L_logic:', float(L_logic))
    print('L_total:', float(L_total))
    print('Per-rule satisfaction:', logic_out['per_rule'])
