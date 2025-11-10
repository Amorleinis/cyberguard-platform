# hetero_gnn_demo.py
import random
import numpy as np
import torch
import torch.nn.functional as F
from torch_geometric.data import HeteroData
from torch_geometric.nn import HeteroConv, SAGEConv, Linear
from sklearn.metrics import classification_report

# -------------------- Synthetic graph generator --------------------
def make_synthetic_hetero_graph(num_hosts=30, avg_procs_per_host=6, avg_files_per_proc=3, seed=42):
    random.seed(seed); np.random.seed(seed)
    data = HeteroData()

    # Create host nodes
    data['host'].x = torch.randn(num_hosts, 16)
    # binary labels for hosts (1 compromised, 0 benign)
    compromised = (torch.rand(num_hosts) > 0.8).long()
    data['host'].y = compromised

    # Processes
    proc_count = num_hosts * avg_procs_per_host
    data['process'].x = torch.randn(proc_count, 12)
    # host -> process edges
    host_idx = []
    proc_idx = []
    for h in range(num_hosts):
        for i in range(avg_procs_per_host):
            p = h*avg_procs_per_host + i
            host_idx.append(h)
            proc_idx.append(p)
    data['host','runs','process'].edge_index = torch.tensor([host_idx, proc_idx], dtype=torch.long)

    # process -> file edges
    file_count = proc_count * avg_files_per_proc
    data['file'].x = torch.randn(file_count, 10)
    proc_idx2 = []
    file_idx = []
    for p in range(proc_count):
        for j in range(avg_files_per_proc):
            f = p*avg_files_per_proc + j
            proc_idx2.append(p)
            file_idx.append(f)
    data['process','opens','file'].edge_index = torch.tensor([proc_idx2, file_idx], dtype=torch.long)

    # process -> endpoint edges (network connections)
    ep_count = max(16, num_hosts//2)
    data['endpoint'].x = torch.randn(ep_count, 8)
    proc2 = []
    ep_idx = []
    for p in range(proc_count):
        # each proc connects to 0..2 endpoints
        for _ in range(np.random.randint(0,3)):
            ep = np.random.randint(ep_count)
            proc2.append(p)
            ep_idx.append(ep)
    if len(proc2)==0:
        data['process','connects','endpoint'].edge_index = torch.empty((2,0), dtype=torch.long)
    else:
        data['process','connects','endpoint'].edge_index = torch.tensor([proc2, ep_idx], dtype=torch.long)

    # Add reverse edges where helpful (PyG expects explicit edges per relation if used)
    # host <- runs_rev <- process
    data['process','runs_rev','host'].edge_index = data['host','runs','process'].edge_index.flip(0)

    return data

# -------------------- Model --------------------
class SimpleHeteroGNN(torch.nn.Module):
    def __init__(self, hidden_dim=64):
        super().__init__()
        # relation-specific convs
        self.conv1 = HeteroConv({
            ('host','runs','process'): SAGEConv((16,12), hidden_dim),
            ('process','opens','file'): SAGEConv((12,10), hidden_dim),
            ('process','connects','endpoint'): SAGEConv((12,8), hidden_dim),
            ('process','runs_rev','host'): SAGEConv((12,16), hidden_dim)
        }, aggr='mean')
        self.conv2 = HeteroConv({
            ('host','runs','process'): SAGEConv((hidden_dim, hidden_dim), hidden_dim),
            ('process','opens','file'): SAGEConv((hidden_dim, hidden_dim), hidden_dim),
            ('process','connects','endpoint'): SAGEConv((hidden_dim, hidden_dim), hidden_dim),
            ('process','runs_rev','host'): SAGEConv((hidden_dim, hidden_dim), hidden_dim)
        }, aggr='mean')
        self.classifier = Linear(hidden_dim, 2)  # host -> logits

    def forward(self, x_dict, edge_index_dict):
        x_dict = self.conv1(x_dict, edge_index_dict)
        x_dict = {k: F.relu(v) for k,v in x_dict.items()}
        x_dict = self.conv2(x_dict, edge_index_dict)
        host_emb = x_dict['host']
        return self.classifier(host_emb)

# -------------------- Train / Eval --------------------
def train_and_eval():
    data = make_synthetic_hetero_graph()
    model = SimpleHeteroGNN()
    opt = torch.optim.Adam(model.parameters(), lr=0.01)

    # simple train/test split over hosts
    y = data['host'].y
    n = y.size(0)
    idx = torch.randperm(n)
    train_idx = idx[:int(0.7*n)]
    test_idx = idx[int(0.7*n):]

    for epoch in range(80):
        model.train()
        opt.zero_grad()
        logits = model({'host':data['host'].x, 'process':data['process'].x, 'file':data['file'].x, 'endpoint':data['endpoint'].x}, data.edge_index_dict)
        loss = F.cross_entropy(logits[train_idx], data['host'].y[train_idx])
        loss.backward(); opt.step()
        if epoch%20==0:
            print('epoch',epoch,'loss',loss.item())

    model.eval()
    with torch.no_grad():
        logits = model({'host':data['host'].x, 'process':data['process'].x, 'file':data['file'].x, 'endpoint':data['endpoint'].x}, data.edge_index_dict)
        preds = logits.argmax(dim=1).cpu().numpy()
        print(classification_report(data['host'].y.cpu().numpy(), preds))

if __name__=='__main__':
    train_and_eval()
