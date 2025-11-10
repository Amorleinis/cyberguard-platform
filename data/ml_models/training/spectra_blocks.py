# --- LogicRegularizer and example rules ---
import torch
import torch.nn as nn
import torch.nn.functional as F

class LogicRegularizer(nn.Module):
    def __init__(self):
        super().__init__()
        self.rules = []  # list of (name, fn, weight)

    def add_rule(self, name: str, fn, weight: float = 1.0):
        """
        fn: callable(pred_dict) -> Tensor of shape (B,) with values in [0,1]
        weight: multiplicative weight for this rule in final loss
        """
        self.rules.append((name, fn, float(weight)))

    def forward(self, pred: dict) -> dict:
        """
        Returns:
          {
            'loss': scalar tensor,
            'per_rule': {name: {'satisfaction': float, 'penalty': float}}
          }
        """
        device = None
        sats = []
        per_rule = {}
        for name, fn, w in self.rules:
            s = fn(pred)  # expected shape (B,)
            if device is None:
                device = s.device
            # clamp to [0,1]
            s_clamped = torch.clamp(s, 0.0, 1.0)
            mean_sat = float(s_clamped.mean().detach().cpu())
            # rule loss = -log(mean_sat + eps)
            eps = 1e-8
            loss_r = -torch.log(s_clamped.mean() + eps) * w
            sats.append(loss_r)
            per_rule[name] = {'satisfaction': mean_sat, 'penalty': float(loss_r.detach().cpu())}
        if sats:
            total_loss = torch.stack(sats).sum()
        else:
            total_loss = torch.tensor(0.0, device=device or torch.device('cpu'))
        return {'loss': total_loss, 'per_rule': per_rule}

# Example rule functions
def rule_cluster_c_not_asset(pred, c_idx: int, asset_label_idx: int):
    if 'clusters' in pred:
        p_cluster_c = pred['clusters'][:, c_idx]
    else:
        p_cluster_c = (pred['cluster_idx'] == c_idx).float()
    p_asset = pred['probs'][:, asset_label_idx]
    return 1.0 - p_cluster_c * p_asset

def rule_mutual_exclusion(pred, idx_a: int, idx_b: int):
    p_a = pred['probs'][:, idx_a]
    p_b = pred['probs'][:, idx_b]
    return 1.0 - p_a * p_b

def rule_cluster_purity_soft(pred, cluster_idx: int, cluster_label_distribution: torch.Tensor):
    p_cluster = pred['clusters'][:, cluster_idx]
    probs = pred['probs']
    agreement = (probs * cluster_label_distribution.unsqueeze(0)).sum(dim=1)
    return 1.0 - (1.0 - agreement) * p_cluster

def rule_similarity_label_smooth(pred, neighbor_probs, sim_scores):
    p = pred['probs']
    divergence = (p - neighbor_probs).abs().sum(dim=1) / 2.0
    return 1.0 - sim_scores * divergence
"""
Starter implementations for Spectra Series hybrid neuro-symbolic blocks.
Each class matches the interface in spectra_hybrid_interfaces.py.
Replace the pass statements with your own logic or wrap your existing models.
"""
from spectra_hybrid_interfaces import (
    GraphEncoderIF, SeqEncoderIF, TransformerRefinerIF, RBFIF, RBMIF, FusionIF, ClassifierIF, LogicRegIF
)

class MyGraphEncoder(GraphEncoderIF):
    def __init__(self, in_dim=64, hidden=128, layers=2, dropout=0.1, readout='mean'):
        try:
            import torch
            import torch.nn as nn
            import torch.nn.functional as F
        except ImportError:
            raise ImportError('PyTorch is required for this block.')
        self.torch = torch
        self.nn = nn
        self.F = F
        self.linears = nn.ModuleList([nn.Linear(in_dim if i==0 else hidden, hidden) for i in range(layers)])
        self.dropout = nn.Dropout(dropout)
        self.readout = readout

    def encode(self, x_nodes, A, mask=None):
        # x_nodes: torch.Tensor [B, N, D_node], A: torch.Tensor [B, N, N]
        h = x_nodes
        for lin in self.linears:
            h = self.dropout(h)
            h = self.torch.bmm(A, h)
            h = self.F.relu(lin(h))
        if self.readout == 'mean':
            return h.mean(dim=1)
        elif self.readout == 'sum':
            return h.sum(dim=1)
        elif self.readout == 'max':
            return h.max(dim=1)[0]
        else:
            raise ValueError('unknown readout')

class MySeqEncoder(SeqEncoderIF):
    def __init__(self, in_dim=32, hidden=128, layers=1, bidir=True, dropout=0.1):
        import torch
        import torch.nn as nn
        self.lstm = nn.LSTM(in_dim, hidden, num_layers=layers, batch_first=True, bidirectional=bidir, dropout=(dropout if layers>1 else 0.0))
        self.out_dim = hidden * (2 if bidir else 1)
    def encode(self, x_seq, mask=None):
        out, (hn, cn) = self.lstm(x_seq)
        return out[:, -1, :]

class MyTransformerRefiner(TransformerRefinerIF):
    def __init__(self, dim=32, heads=4, layers=2, ff_mult=4, dropout=0.1):
        import torch.nn as nn
        layer = nn.TransformerEncoderLayer(d_model=dim, nhead=heads, dim_feedforward=dim*ff_mult, batch_first=True)
        self.enc = nn.TransformerEncoder(layer, num_layers=layers)
    def refine(self, x_seq, mask=None):
        y = self.enc(x_seq)
        return y[:, -1, :]

class MyRBF(RBFIF):
    def __init__(self, in_dim=128, num_kernels=8):
        import torch
        import torch.nn as nn
        self.centers = nn.Parameter(torch.randn(num_kernels, in_dim))
        self.log_sigma = nn.Parameter(torch.zeros(num_kernels))
    def apply(self, x):
        import torch
        diff = x.unsqueeze(1) - self.centers.unsqueeze(0)
        dist2 = (diff**2).sum(dim=-1)
        sigma2 = torch.exp(self.log_sigma)**2 + 1e-8
        return torch.exp(-0.5 * dist2 / sigma2)

class MyRBM(RBMIF):
    def __init__(self, v_dim=128, h_dim=32):
        import torch
        import torch.nn as nn
        import torch.nn.functional as F
        self.W = nn.Parameter(torch.randn(v_dim, h_dim) * 0.01)
        self.vb = nn.Parameter(torch.zeros(v_dim))
        self.hb = nn.Parameter(torch.zeros(h_dim))
        self.F = F
    def forward(self, v):
        import torch
        return torch.sigmoid(v @ self.W + self.hb)
    def loss_cd(self, v0, k=1):
        import torch
        F = self.F
        with torch.no_grad():
            h0 = torch.bernoulli(self.forward(v0))
            vk = v0
            hk = h0
            for _ in range(k):
                vk = torch.bernoulli(torch.sigmoid(hk @ self.W.t() + self.vb))
                hk = torch.bernoulli(torch.sigmoid(vk @ self.W + self.hb))
        def free_energy(v):
            vbias = (v * self.vb).sum(dim=1)
            wx_b = F.linear(v, self.W.t(), self.hb)
            hidden_term = F.softplus(wx_b).sum(dim=1)
            return -vbias - hidden_term
        return (free_energy(v0) - free_energy(vk)).mean()

class MyFusion(FusionIF):
    def __init__(self, dims=None, out_dim=128):
        import torch
        import torch.nn as nn
        if dims is None:
            dims = {'gnn':128, 'lstm':128, 'trans':128, 'rbf':8, 'rbm':32}
        total = sum(dims.values())
        self.proj = nn.Linear(total, out_dim)
        self.gate = nn.Sequential(nn.Linear(total, out_dim), nn.Sigmoid())
    def fuse(self, parts):
        import torch
        xs = [parts[k] for k in sorted(parts.keys())]
        z = torch.cat(xs, dim=-1)
        proj = self.proj(z)
        gate = self.gate(z)
        return proj * gate + proj * (1 - gate)

class MyClassifier(ClassifierIF):
    def __init__(self, in_dim=128, num_classes=4, dropout=0.1):
        import torch.nn as nn
        self.head = nn.Sequential(nn.LayerNorm(in_dim), nn.Dropout(dropout), nn.Linear(in_dim, num_classes))
    def predict(self, z):
        return self.head(z)

class MyLogicReg(LogicRegIF):
    def __init__(self):
        self.rules = []
    def add_rule(self, rule_fn):
        self.rules.append(rule_fn)
    def loss(self, pred):
        import torch
        if not self.rules:
            return torch.tensor(0.0, device=next(iter(pred.values())).device)
        sats = []
        for r in self.rules:
            s = torch.clamp(r(pred), 0.0, 1.0)
            sats.append(s.mean())
        sat = torch.stack(sats).mean()
        return -torch.log(sat + 1e-6)
