# tgn_template.py (scaffold)
# NOTE: This is a scaffold; use libraries like `torch_geometric_temporal` or implement TGN memory modules.

import torch
import torch.nn as nn

class SimpleTimeEncoder(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.w = nn.Linear(1, dim)
    def forward(self, t):
        # t is a tensor of timestamps
        return torch.sin(self.w(t.unsqueeze(-1)))

class NodeMemory:
    def __init__(self, num_nodes, dim):
        self.mem = torch.zeros(num_nodes, dim)
    def read(self, idx):
        return self.mem[idx]
    def update(self, idx, message):
        self.mem[idx] = 0.9*self.mem[idx] + 0.1*message

class TemporalGNN(nn.Module):
    def __init__(self, node_dims):
        super().__init__()
        self.time_enc = SimpleTimeEncoder(node_dims)
        self.msg_mlp = nn.Sequential(nn.Linear(node_dims*2 + 1, node_dims), nn.ReLU())
        # a small GNN over a snapshot could be added here

    def compute_message(self, src_emb, dst_emb, t):
        te = self.time_enc(t)
        inp = torch.cat([src_emb, dst_emb, te], dim=-1)
        return self.msg_mlp(inp)

# Usage: maintain NodeMemory; for every incoming event (u,v,t,features) -> read mem[u], mem[v], compute message, update mem[v]
