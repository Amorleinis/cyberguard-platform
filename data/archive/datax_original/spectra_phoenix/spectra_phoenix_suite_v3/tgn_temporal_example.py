# tgn_temporal_example.py
# Working temporal example that consumes a toy event stream and updates node memories.

import numpy as np
import torch
from tgn_template import NodeMemory, SimpleTimeEncoder, TemporalGNN

def simulate_events(n_nodes=6, n_events=50, seed=0):
    rng = np.random.RandomState(seed)
    events = []
    for i in range(n_events):
        src = rng.randint(0, n_nodes)
        dst = rng.randint(0, n_nodes)
        t = i * 1.0  # timestamp
        events.append((src, dst, t))
    return events

def run_temporal_example():
    n_nodes = 6
    dim = 16
    mem = NodeMemory(n_nodes, dim)
    time_enc = SimpleTimeEncoder(dim)
    msg_mlp = torch.nn.Sequential(torch.nn.Linear(dim*2 + dim, dim), torch.nn.ReLU())

    events = simulate_events(n_nodes=n_nodes, n_events=30)
    for (u,v,t) in events:
        src = torch.tensor(mem.read(u)).float()
        dst = torch.tensor(mem.read(v)).float()
        te = time_enc(torch.tensor([t]).float())
        inp = torch.cat([src, dst, te.squeeze(0)], dim=-1)
        msg = msg_mlp(inp)
        mem.update(v, msg.detach().numpy())
    # print final memory vectors for nodes
    for i in range(n_nodes):
        print(f\"Node {i} memory (first 6 dims):\", mem.read(i)[:6])

if __name__=='__main__':
    run_temporal_example()
