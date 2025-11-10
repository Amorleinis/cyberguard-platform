# rl_remediation_env_integrated.py
# Integration: hetero-GNN embeddings -> RL trainer
# Requirements: torch, torch_geometric, numpy
import torch
import numpy as np
from hetero_gnn_demo import make_synthetic_hetero_graph, SimpleHeteroGNN
from rl_remediation_env import MiniNetEnv, ReplayBuffer, DQNNet, select_action, compute_loss
import torch.nn as nn
import torch.optim as optim
import time
import random

class IntegratedEnvWrapper:
    def __init__(self, n_hosts=6, embed_dim=64, device=None):
        self.device = device or torch.device('cpu')
        self.n_hosts = n_hosts
        self.embed_dim = embed_dim
        # prepare a pretrained (or randomly initialized) hetero GNN
        self.gnn = SimpleHeteroGNN(hidden_dim=self.embed_dim).to(self.device)
        # generate a synthetic graph once; in real system, you'd update graph each step
        self.graph = make_synthetic_hetero_graph(num_hosts=self.n_hosts)
        self.model_ready = True

    def compute_host_embeddings(self):
        # run the GNN forward to get host logits/embeddings (we'll reuse hidden layer outputs)
        self.gnn.eval()
        with torch.no_grad():
            x_dict = {'host': self.graph['host'].x, 'process': self.graph['process'].x, 'file': self.graph['file'].x, 'endpoint': self.graph['endpoint'].x}
            out = self.gnn(x_dict, self.graph.edge_index_dict)  # logits shape (n_hosts, 2)
            # as a proxy for embeddings, take the pre-classifier hidden representation by re-running convs
            # simpler: use the classifier output's first layer weights projection; here just use logits as small embedding
            emb = out.cpu().numpy()  # shape (n_hosts, 2)
            # if embed_dim > 2, pad with zeros
            if emb.shape[1] < self.embed_dim:
                pad = np.zeros((emb.shape[0], self.embed_dim - emb.shape[1]))
                emb = np.concatenate([emb, pad], axis=1)
            return emb.astype(np.float32)

# Modified trainer that consumes embeddings
def train_integrated(seed=0, n_hosts=6, embed_dim=16, num_episodes=200, batch_size=64, device=None):
    if device is None:
        device = torch.device('cpu')
    random.seed(seed); np.random.seed(seed)
    env = MiniNetEnv(n_hosts=n_hosts, seed=seed)
    integ = IntegratedEnvWrapper(n_hosts=n_hosts, embed_dim=embed_dim, device=device)
    n_actions = 3 * n_hosts
    # DQN input size = n_hosts (binary state) + n_hosts * embed_dim (flattened embeddings)
    obs_size = n_hosts + n_hosts * embed_dim
    policy_net = DQNNet(obs_size, n_actions).to(device)
    target_net = DQNNet(obs_size, n_actions).to(device)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()
    optimizer = optim.Adam(policy_net.parameters(), lr=1e-3)
    buffer = ReplayBuffer(capacity=5000)
    eps = 1.0; eps_end = 0.05; eps_decay = 0.995
    min_buffer = 200; update_target_every = 10
    stats = {'episode_rewards': []}
    start_time = time.time()

    for ep in range(1, num_episodes+1):
        state = env.reset()  # binary state
        ep_reward = 0.0; done=False
        while not done:
            # compute embeddings from GNN (in prod, this would be incremental)
            emb = integ.compute_host_embeddings()  # shape (n_hosts, embed_dim)
            obs = np.concatenate([state, emb.flatten()])
            # select action using policy_net with observation size matching
            if np.random.rand() < eps:
                action = np.random.randint(0, n_actions)
            else:
                s = torch.tensor(obs, dtype=torch.float32, device=device).unsqueeze(0)
                with torch.no_grad():
                    q = policy_net(s)
                action = int(q.argmax().item())
            next_state, reward, done, _ = env.step(action)
            next_emb = integ.compute_host_embeddings()
            next_obs = np.concatenate([next_state, next_emb.flatten()])
            buffer.push(obs, action, reward, next_obs, float(done))
            state = next_state
            ep_reward += reward

            if len(buffer) >= min_buffer:
                batch = buffer.sample(batch_size)
                loss = compute_loss(policy_net, target_net, batch, device)
                optimizer.zero_grad(); loss.backward(); optimizer.step()

        stats['episode_rewards'].append(ep_reward)
        eps = max(eps_end, eps*eps_decay)
        if ep % update_target_every == 0:
            target_net.load_state_dict(policy_net.state_dict())
        if ep % 20 == 0 or ep == 1:
            avg_reward = np.mean(stats['episode_rewards'][-20:])
            print(f"Ep {ep:4d} | AvgReward(20) {avg_reward:6.3f} | Eps {eps:.3f} | Buffer {len(buffer)}")

    print("Training complete")
    return policy_net, target_net, stats

if __name__=='__main__':
    train_integrated(seed=1, n_hosts=6, embed_dim=4, num_episodes=120, batch_size=64, device=torch.device('cpu'))
