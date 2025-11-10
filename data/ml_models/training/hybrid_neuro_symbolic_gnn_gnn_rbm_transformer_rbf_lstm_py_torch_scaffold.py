"""
Hybrid Neuro-Symbolic GNN
=========================

This PyTorch scaffold fuses:
- Graph encoder (GNN)
- Sequence encoder (LSTM)
- Transformer encoder (contextual refinement)
- RBM (unsupervised latent regularizer)
- RBF (localized basis features)
- Neuro-symbolic logic regularizer (soft constraints via t-norms)

It is designed as a starting point you can adapt to your data/task (classification, link prediction, regression).

Author: ChatGPT (GPT-5 Thinking)
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Optional, Tuple, Dict

import torch
import torch.nn as nn
import torch.nn.functional as F

# If you use torch_geometric, swap this lightweight GNN with GCNConv etc.
class SimpleGCN(nn.Module):
    """A minimal GCN-like layer using dense adjacency for demo purposes.
    For real graphs, prefer PyTorch Geometric or DGL and sparse ops.
    """
    def __init__(self, in_dim: int, out_dim: int, dropout: float = 0.0):
        super().__init__()
        self.lin = nn.Linear(in_dim, out_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, A: torch.Tensor) -> torch.Tensor:
        # Ensure x and A are 3D tensors for torch.bmm
        if x.dim() == 2:
            x = x.unsqueeze(0)
        if A.dim() == 2:
            A = A.unsqueeze(0)
        x = self.dropout(x)
        x = torch.bmm(A, x)  # aggregate neighbors
        x = self.lin(x)
        return F.relu(x)

class GraphEncoder(nn.Module):
    def __init__(self, node_dim: int, hidden: int, layers: int = 2, dropout: float = 0.1, readout: str = "mean"):
        super().__init__()
        self.gnns = nn.ModuleList()
        dims = [node_dim] + [hidden] * layers
        for i in range(layers):
            self.gnns.append(SimpleGCN(dims[i], dims[i+1], dropout))
        self.readout = readout

    def forward(self, x_nodes: torch.Tensor, A: torch.Tensor) -> torch.Tensor:
        # x_nodes: [B, N, D]
        h = x_nodes
        for g in self.gnns:
            h = g(h, A)
        if self.readout == "mean":
            g_repr = h.mean(dim=1)  # [B, H]
        elif self.readout == "sum":
            g_repr = h.sum(dim=1)
        elif self.readout == "max":
            g_repr, _ = h.max(dim=1)
        else:
            raise ValueError("Unknown readout")
        return g_repr

class RBF(nn.Module):
    """Gaussian RBF layer.
    Produces localized features around learnable centers with learnable widths.
    """
    def __init__(self, in_dim: int, num_kernels: int):
        super().__init__()
        self.centers = nn.Parameter(torch.randn(num_kernels, in_dim))
        self.log_sigma = nn.Parameter(torch.zeros(num_kernels))
        self.out_dim = num_kernels

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, D]
        # Expand for pairwise distances
        # [B, 1, D] - [1, K, D] -> [B, K, D]
        diff = x.unsqueeze(1) - self.centers.unsqueeze(0)
        dist2 = (diff ** 2).sum(dim=-1)  # [B, K]
        sigma2 = torch.exp(self.log_sigma) ** 2 + 1e-8
        phi = torch.exp(-0.5 * dist2 / sigma2)  # [B, K]
        return phi

class RBM(nn.Module):
    """Binary-binary RBM for unsupervised regularization.
    In forward(), we expose the hidden probabilities for fusion.
    Use contrastive divergence (CD-k) in rbm_loss() for training signal.
    """
    def __init__(self, v_dim: int, h_dim: int):
        super().__init__()
        self.W = nn.Parameter(torch.randn(v_dim, h_dim) * 0.01)
        self.vb = nn.Parameter(torch.zeros(v_dim))
        self.hb = nn.Parameter(torch.zeros(h_dim))
        self.v_dim = v_dim
        self.h_dim = h_dim

    def hidden_prob(self, v: torch.Tensor) -> torch.Tensor:
        return torch.sigmoid(v @ self.W + self.hb)

    def visible_prob(self, h: torch.Tensor) -> torch.Tensor:
        return torch.sigmoid(h @ self.W.t() + self.vb)

    @torch.no_grad()
    def sample_h(self, v: torch.Tensor) -> torch.Tensor:
        return torch.bernoulli(self.hidden_prob(v))

    @torch.no_grad()
    def sample_v(self, h: torch.Tensor) -> torch.Tensor:
        return torch.bernoulli(self.visible_prob(h))

    def forward(self, v: torch.Tensor) -> torch.Tensor:
        # Return hidden probabilities as a differentiable representation
        return self.hidden_prob(v)

    def rbm_loss(self, v0: torch.Tensor, k: int = 1) -> torch.Tensor:
        """Contrastive divergence loss (negative log-likelihood surrogate)."""
        with torch.no_grad():
            h0 = self.sample_h(v0)
            vk = v0
            hk = h0
            for _ in range(k):
                vk = self.sample_v(hk)
                hk = self.sample_h(vk)
        # Energy terms
        def free_energy(v):
            vbias = (v * self.vb).sum(dim=1)
            wx_b = F.linear(v, self.W.t(), self.hb)
            hidden_term = F.softplus(wx_b).sum(dim=1)
            return -vbias - hidden_term
        return (free_energy(v0) - free_energy(vk)).mean()

class SequenceEncoder(nn.Module):
    def __init__(self, in_dim: int, hidden: int, layers: int = 1, bidirectional: bool = True, dropout: float = 0.1):
        super().__init__()
        self.lstm = nn.LSTM(in_dim, hidden, num_layers=layers, batch_first=True,
                            dropout=(dropout if layers > 1 else 0.0), bidirectional=bidirectional)
        self.out_dim = hidden * (2 if bidirectional else 1)

    def forward(self, x_seq: torch.Tensor) -> torch.Tensor:
        # x_seq: [B, T, D]
        out, (hn, cn) = self.lstm(x_seq)
        # Use last timestep or pooled representation
        return out[:, -1, :]  # [B, H*dir]

class TransformerRefiner(nn.Module):
    def __init__(self, dim: int, heads: int = 4, layers: int = 2, ff_mult: int = 4, dropout: float = 0.1):
        super().__init__()
        encoder_layer = nn.TransformerEncoderLayer(d_model=dim, nhead=heads,
                                                   dim_feedforward=dim*ff_mult, dropout=dropout, batch_first=True)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=layers)

    def forward(self, x: torch.Tensor, src_key_padding_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        # x: [B, T, D]
        y = self.encoder(x, src_key_padding_mask=src_key_padding_mask)
        return y[:, -1, :]  # take last position summary

class GatedFusion(nn.Module):
    def __init__(self, dims: Dict[str, int], out_dim: int):
        super().__init__()
        total = sum(dims.values())
        self.proj = nn.Linear(total, out_dim)
        self.gate = nn.Sequential(
            nn.Linear(total, out_dim),
            nn.Sigmoid()
        )

    def forward(self, parts: Dict[str, torch.Tensor]) -> torch.Tensor:
        # parts: dict of tensors [B, Di]
        xs = [parts[k] for k in sorted(parts.keys())]
        z = torch.cat(xs, dim=-1)
        proj = self.proj(z)
        gate = self.gate(z)
        return proj * gate + proj * (1 - gate)  # gated residual (degenerates to proj)

class LogicRegularizer(nn.Module):
    """Differentiable soft logic constraints using product t-norm.
    Define rules as functions mapping model outputs -> [0,1] satisfactions.
    """
    def __init__(self):
        super().__init__()
        self.rules = []  # list of callables: (pred_dict) -> satisfaction in [0,1]

    def add_rule(self, rule_fn):
        self.rules.append(rule_fn)

    def forward(self, pred: Dict[str, torch.Tensor]) -> torch.Tensor:
        if not self.rules:
            return torch.tensor(0.0, device=next(iter(pred.values())).device)
        sats = []
        for r in self.rules:
            s = torch.clamp(r(pred), 0.0, 1.0)
            sats.append(s.mean())
        # Logic loss = -log satisfaction (maximize satisfaction)
        sat = torch.stack(sats).mean()
        return -torch.log(sat + 1e-6)

@dataclass
class HybridConfig:
    node_dim: int = 64
    seq_dim: int = 32
    gnn_hidden: int = 128
    lstm_hidden: int = 64
    transformer_dim: int = 128
    transformer_heads: int = 4
    transformer_layers: int = 2
    rbf_kernels: int = 64
    rbm_hidden: int = 64
    fusion_dim: int = 128
    num_classes: int = 5
    dropout: float = 0.1

class HybridModel(nn.Module):
    def __init__(self, cfg: HybridConfig):
        super().__init__()
        self.cfg = cfg
        # Encoders
        self.gnn = GraphEncoder(cfg.node_dim, cfg.gnn_hidden, layers=2, dropout=cfg.dropout)
        self.seq = SequenceEncoder(cfg.seq_dim, cfg.lstm_hidden, layers=1, bidirectional=True, dropout=cfg.dropout)
        self.trans_in = nn.Linear(cfg.seq_dim, cfg.transformer_dim)
        self.transformer = TransformerRefiner(cfg.transformer_dim, cfg.transformer_heads, cfg.transformer_layers)
        # RBF & RBM operate on fused or encoder features; here use graph repr as input
        self.rbf = RBF(cfg.gnn_hidden, cfg.rbf_kernels)
        self.rbm = RBM(v_dim=cfg.gnn_hidden, h_dim=cfg.rbm_hidden)
        # Fusion
        dims = {
            "gnn": cfg.gnn_hidden,
            "lstm": self.seq.out_dim,
            "trans": cfg.transformer_dim,
            "rbf": cfg.rbf_kernels,
            "rbm": cfg.rbm_hidden,
        }
        self.fuse = GatedFusion(dims, cfg.fusion_dim)
        self.classifier = nn.Sequential(
            nn.LayerNorm(cfg.fusion_dim),
            nn.Dropout(cfg.dropout),
            nn.Linear(cfg.fusion_dim, cfg.num_classes)
        )
        self.logic = LogicRegularizer()

    def forward(self, x_nodes: torch.Tensor, A: torch.Tensor, x_seq: torch.Tensor,
                attn_mask: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        # Encoders
        g = self.gnn(x_nodes, A)                       # [B, Hg]
        s = self.seq(x_seq)                            # [B, Hs]
        t = self.transformer(self.trans_in(x_seq))     # [B, Ht]
        # RBM & RBF on graph representation (customize as needed)
        rbf = self.rbf(g)                              # [B, Kr]
        rbm_h = self.rbm(g)                            # [B, Hr]
        fused = self.fuse({"gnn": g, "lstm": s, "trans": t, "rbf": rbf, "rbm": rbm_h})
        logits = self.classifier(fused)
        return {
            "logits": logits,
            "gnn": g,
            "lstm": s,
            "trans": t,
            "rbf": rbf,
            "rbm": rbm_h,
            "fused": fused,
        }

    def losses(self, batch: Dict[str, torch.Tensor], outputs: Dict[str, torch.Tensor],
               task: str = "classification", logic_weight: float = 0.1, rbm_k: int = 1) -> Dict[str, torch.Tensor]:
        losses = {}
        if task == "classification":
            y = batch["y"]
            losses["task"] = F.cross_entropy(outputs["logits"], y)
        elif task == "regression":
            y = batch["y"].float()
            losses["task"] = F.mse_loss(outputs["logits"].squeeze(-1), y)
        else:
            raise ValueError("Unsupported task")
        # Logic loss
        logic_loss = self.logic({"logits": outputs["logits"].softmax(dim=-1), "fused": outputs["fused"]})
        losses["logic"] = logic_weight * logic_loss
        # RBM CD loss
        losses["rbm"] = 0.01 * self.rbm.rbm_loss(outputs["gnn"].detach(), k=rbm_k)  # detach to avoid leakage
        losses["total"] = sum(losses.values())
        return losses

# -----------------------
# Demo usage / smoke test
# -----------------------

def _synthetic_batch(B: int = 4, N: int = 12, T: int = 20, cfg: Optional[HybridConfig] = None):
    cfg = cfg or HybridConfig()
    x_nodes = torch.randn(B, N, cfg.node_dim)
    # Row-normalized adjacency with self-loops
    A = torch.rand(B, N, N)
    A = A + torch.eye(N).unsqueeze(0)
    A = A / (A.sum(dim=-1, keepdim=True) + 1e-8)
    x_seq = torch.randn(B, T, cfg.seq_dim)
    y = torch.randint(0, cfg.num_classes, (B,))
    return {"x_nodes": x_nodes, "A": A, "x_seq": x_seq, "y": y}


def smoke_test():
    cfg = HybridConfig()
    model = HybridModel(cfg)
    # Example logic rule: encourage class 0 when fused norm is small (toy)
    def rule_low_norm_implies_class0(pred):
        p = pred["logits"]  # probs expected if softmaxed; here we'll softmax
        probs = F.softmax(p, dim=-1)
        fused = pred["fused"]
        norm = fused.norm(dim=-1, keepdim=True)
        # satisfaction in [0,1]: if norm small, probability of class 0 should be high
        s = torch.exp(-norm) * probs[:, 0:1]
        return s.squeeze(-1)
    model.logic.add_rule(rule_low_norm_implies_class0)

    batch = _synthetic_batch(B=8)
    out = model(batch["x_nodes"], batch["A"], batch["x_seq"])
    losses = model.losses(batch, out)
    print({k: float(v.detach().cpu()) for k, v in losses.items()})

if __name__ == "__main__":
    smoke_test()
