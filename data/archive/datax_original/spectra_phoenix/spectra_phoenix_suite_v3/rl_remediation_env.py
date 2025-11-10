# rl_remediation_env.py
# Full runnable DQN trainer for the MiniNetEnv (educational toy)
# Requirements: torch, numpy
import random
import numpy as np
from collections import deque, namedtuple
import torch
import torch.nn as nn
import torch.optim as optim
import time

# -------------------------
# MiniNetEnv (same as before)
# -------------------------
class MiniNetEnv:
    def __init__(self, n_hosts=5, seed=0):
        random.seed(seed); np.random.seed(seed)
        self.n = n_hosts
        self.reset()

    def reset(self):
        # 0 = clean, 1 = compromised
        self.state = np.zeros(self.n, dtype=np.int32)
        # randomly infect one host
        self.state[np.random.randint(self.n)] = 1
        self.steps = 0
        return self._obs()

    def step(self, action):
        # action = integer: act_type * n_hosts + host_idx
        # act_type: 0=noop,1=isolate,2=reboot
        n_actions = 3
        act_type = action // self.n
        h = action % self.n

        reward = 0.0
        done = False
        # simple infection spread: each compromised host can infect neighbors (linear chain)
        for i in range(self.n):
            if self.state[i] == 1:
                if i + 1 < self.n and np.random.rand() < 0.15:
                    self.state[i + 1] = 1
                if i - 1 >= 0 and np.random.rand() < 0.05:
                    self.state[i - 1] = 1

        # apply action
        if act_type == 0:  # noop
            reward -= 0.01
        elif act_type == 1:  # isolate host -> cures but costs
            if self.state[h] == 1:
                self.state[h] = 0
                reward += 1.0
            reward -= 0.2
        elif act_type == 2:  # reboot (higher cost)
            if self.state[h] == 1:
                self.state[h] = 0
                reward += 1.2
            reward -= 0.5

        # small penalty for remaining compromises
        reward -= 0.5 * self.state.sum()
        self.steps += 1
        if self.steps >= 40:
            done = True
        return self._obs(), float(reward), done, {}

    def _obs(self):
        # continuous float32 obs vector (0/1 per host)
        return self.state.copy().astype(np.float32)


# -------------------------
# Replay buffer
# -------------------------
Transition = namedtuple('Transition', ('state', 'action', 'reward', 'next_state', 'done'))

class ReplayBuffer:
    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)

    def push(self, *args):
        self.buffer.append(Transition(*args))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        return Transition(*zip(*batch))

    def __len__(self):
        return len(self.buffer)


# -------------------------
# DQN Network
# -------------------------
class DQNNet(nn.Module):
    def __init__(self, n_hosts, n_actions):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(n_hosts, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, n_actions)
        )

    def forward(self, x):
        return self.fc(x)


# -------------------------
# Trainer / Utilities
# -------------------------
def select_action(policy_net, state, eps, device):
    # state: numpy array
    if np.random.rand() < eps:
        return np.random.randint(0, policy_net.fc[-1].out_features)
    else:
        s = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        with torch.no_grad():
            q = policy_net(s)
        return int(q.argmax().item())

def compute_loss(policy_net, target_net, batch, device, gamma=0.99):
    states = torch.tensor(np.stack(batch.state), dtype=torch.float32, device=device)
    actions = torch.tensor(batch.action, dtype=torch.int64, device=device).unsqueeze(1)
    rewards = torch.tensor(batch.reward, dtype=torch.float32, device=device).unsqueeze(1)
    next_states = torch.tensor(np.stack(batch.next_state), dtype=torch.float32, device=device)
    dones = torch.tensor(batch.done, dtype=torch.float32, device=device).unsqueeze(1)

    q_values = policy_net(states).gather(1, actions)  # (batch,1)
    with torch.no_grad():
        next_q = target_net(next_states).max(1)[0].unsqueeze(1)
        target_q = rewards + (1.0 - dones) * gamma * next_q
    loss = nn.functional.mse_loss(q_values, target_q)
    return loss

# -------------------------
# Main training loop
# -------------------------
def train_dqn(seed=0,
              n_hosts=6,
              num_episodes=500,
              batch_size=64,
              buffer_capacity=5000,
              device=None):
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    env = MiniNetEnv(n_hosts=n_hosts, seed=seed)
    n_actions = 3 * n_hosts  # act_type * host_idx
    policy_net = DQNNet(n_hosts, n_actions).to(device)
    target_net = DQNNet(n_hosts, n_actions).to(device)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()

    optimizer = optim.Adam(policy_net.parameters(), lr=1e-3)
    buffer = ReplayBuffer(capacity=buffer_capacity)

    eps_start = 1.0
    eps_end = 0.05
    eps_decay = 0.995

    eps = eps_start
    update_target_every = 10  # episodes
    min_buffer_for_training = 200

    stats = {'episode_rewards': []}
    start_time = time.time()

    for ep in range(1, num_episodes + 1):
        state = env.reset()
        ep_reward = 0.0
        done = False
        while not done:
            action = select_action(policy_net, state, eps, device)
            next_state, reward, done, _ = env.step(action)
            buffer.push(state, action, reward, next_state, float(done))
            state = next_state
            ep_reward += reward

            # training step
            if len(buffer) >= min_buffer_for_training:
                batch = buffer.sample(batch_size)
                loss = compute_loss(policy_net, target_net, batch, device)
                optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(policy_net.parameters(), 5.0)
                optimizer.step()

        stats['episode_rewards'].append(ep_reward)
        eps = max(eps_end, eps * eps_decay)

        if ep % update_target_every == 0:
            target_net.load_state_dict(policy_net.state_dict())

        if ep % 20 == 0 or ep == 1:
            avg_reward = np.mean(stats['episode_rewards'][-20:])
            print(f"Ep {ep:4d} | AvgReward(20) {avg_reward:6.3f} | Eps {eps:.3f} | Buffer {len(buffer)}")

    total_time = time.time() - start_time
    print(f"Training done. Episodes: {num_episodes}, Time: {total_time:.1f}s")
    return policy_net, target_net, stats

# -------------------------
# Quick run when executed as script
# -------------------------
if __name__ == "__main__":
    device = torch.device('cpu')
    policy_net, target_net, stats = train_dqn(seed=1, n_hosts=6, num_episodes=300, batch_size=64, device=device)

    # Example: evaluate greedy policy on several episodes
    env = MiniNetEnv(n_hosts=6, seed=42)
    n_eval = 20
    tot = 0.0
    for _ in range(n_eval):
        s = env.reset(); done = False; r_sum = 0.0
        while not done:
            # greedy
            a = select_action(policy_net, s, eps=0.0, device=device)
            s, r, done, _ = env.step(a)
            r_sum += r
        tot += r_sum
    print(f"Avg eval reward over {n_eval} episodes: {tot/n_eval:.3f}")
