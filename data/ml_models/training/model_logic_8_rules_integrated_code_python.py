"""
Model Logic Integration for Hybrid Neuro-Symbolic Scaffold
---------------------------------------------------------
PyTorch-ready module that implements the 8 logic rules you approved,
returns a differentiable logic loss and per-rule diagnostics.

Usage:
  - Import LogicModule from this file and instantiate: logic = LogicModule(device=device)
  - Call out = logic.compute(pred, meta)
    where `pred` is a dict containing model outputs and intermediate features (see README below)
  - Use out['loss'] in your training objective and log out['per_rule']

This file intentionally expects the following keys in `pred` (most optional):
  - 'probs' : Tensor (B, C)  softmax probs over classes
  - 'logits': Tensor (B, C)  raw logits
  - 'clusters': Tensor (B, K) optional soft cluster membership OR
  - 'cluster_idx': LongTensor (B,) optional hard cluster indices
  - 'confidence': Tensor (B,) optional model confidence (else computed max prob)
  - 'outlier_score': Tensor (B,) optional in [0,1]
  - 'g': Tensor (B, H_g) graph embedding
  - 's': Tensor (B, H_s) sequence embedding (LSTM)
  - 'A': Tensor (B, N, N) adjacency (optional, used for forbidden-edge rule)
  - 'centrality_norm': Tensor (B,) optional precomputed centrality scaled to [0,1]
  - 'rbf': Tensor (B, K) RBF features
  - 'seq_cluster_preds': list of sequences (optional) for transition rule OR
  - 'pred_transitions': Tensor (K,K) predicted transition matrix (optional)

If some fields are missing, the module uses reasonable fallbacks where possible.
"""
from __future__ import annotations
from typing import Dict, Any, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

# Default weights (can be overridden in constructor)
DEFAULT_WEIGHTS = {
    'cluster_purity': 1.0,
    'outlier_consistency': 0.5,
    'transition_consistency': 1.0,
    'graph_sequence_alignment': 0.5,
    'forbidden_edge': 1.0,
    'centrality_confidence': 0.5,
    'similarity_label_smooth': 0.5,
    'rbf_smoothness': 0.5,
}

EPS = 1e-8

class LogicModule(nn.Module):
    """Implements 8 differentiable rules and returns loss + diagnostics.

    Call compute(pred, meta) -> {'loss': Tensor, 'per_rule': {...}}

    `meta` can include extra precomputed stats: example: {
        'cluster_label_distribution': {cluster_idx: Tensor(C,) soft dist},
        'forbidden_edge_pairs': [(u_label_idx, v_label_idx), ...],
        'empirical_transitions': Tensor(K,K),
        'similarity_pairs': (indices_tensor, sim_scores_tensor),
    }
    """
    def __init__(self, weights: Optional[Dict[str, float]] = None, device: Optional[torch.device] = None):
        super().__init__()
        self.weights = DEFAULT_WEIGHTS.copy()
        if weights:
            self.weights.update(weights)
        self.device = device or (torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'))

    # -------------------- Helpers --------------------
    def _get_probs(self, pred: Dict[str, Any]) -> torch.Tensor:
        if 'probs' in pred:
            return pred['probs']
        elif 'logits' in pred:
            return F.softmax(pred['logits'], dim=-1)
        else:
            raise KeyError("pred must contain 'probs' or 'logits'")

    def _get_confidence(self, pred: Dict[str, Any]) -> torch.Tensor:
        if 'confidence' in pred:
            return pred['confidence']
        probs = self._get_probs(pred)
        return probs.max(dim=-1).values

    def _soft_cluster_membership(self, pred: Dict[str, Any], c_idx: int) -> torch.Tensor:
        # returns (B,) in [0,1]
        if 'clusters' in pred:
            clusters = pred['clusters']  # (B, K)
            return clusters[:, c_idx]
        elif 'cluster_idx' in pred:
            return (pred['cluster_idx'] == c_idx).float()
        else:
            # fallback: uniform low membership
            B = self._get_probs(pred).shape[0]
            return torch.full((B,), 1e-6, device=self.device)

    # -------------------- Rule implementations --------------------
    def rule_cluster_purity(self, pred: Dict[str, Any], meta: Dict[str, Any]) -> torch.Tensor:
        """Rule 1: Nodes in same cluster should share dominant label.
        We compute per-node satisfaction S_i in [0,1] where high = good.
        If meta provides 'cluster_label_distribution' (dict mapping idx->Tensor(C,)) we use it.
        Otherwise we approximate by using hard cluster idx and the model prob at that dominant label.
        """
        probs = self._get_probs(pred)  # (B, C)
        B, C = probs.shape
        if meta and 'cluster_label_distribution' in meta:
            # meta: dict cluster_idx -> Tensor(C,)
            # pred must provide cluster_idx or clusters
            sats = []
            for i in range(B):
                # find cluster membership distribution row
                if 'clusters' in pred:
                    mem = pred['clusters'][i]  # (K,)
                    # apply soft: expected agreement = sum_k mem_k * dot(probs_i, q_k)
                    expected = 0.0
                    for k, qk in meta['cluster_label_distribution'].items():
                        expected = expected + mem[int(k)] * (probs[i] * qk.to(probs.device)).sum()
                    sats.append(expected)
                elif 'cluster_idx' in pred:
                    k = int(pred['cluster_idx'][i].item())
                    qk = meta['cluster_label_distribution'].get(k, None)
                    if qk is None:
                        sats.append(probs[i].max())
                    else:
                        sats.append((probs[i] * qk.to(probs.device)).sum())
                else:
                    sats.append(probs[i].max())
            sats = torch.stack([s if torch.is_tensor(s) else torch.tensor(s, device=probs.device) for s in sats])
            return sats.clamp(0.0, 1.0)
        else:
            # fallback: for each sample, satisfaction = model prob at dominant label of cluster (if provided)
            if 'cluster_idx' in pred:
                sats = []
                # require meta.cluster_major_label map? try to use meta['cluster_major_label'] if present
                cl_major = meta.get('cluster_major_label', {}) if meta else {}
                for i in range(B):
                    k = int(pred['cluster_idx'][i].item())
                    maj = cl_major.get(k, None)
                    if maj is None:
                        sats.append(probs[i].max())
                    else:
                        sats.append(probs[i, maj])
                return torch.stack(sats).clamp(0.0, 1.0)
            else:
                # no cluster info: return per-sample max-prob
                return probs.max(dim=-1).values

    def rule_outlier_consistency(self, pred: Dict[str, Any], meta: Dict[str, Any]) -> torch.Tensor:
        """Rule 2: Outlier nodes should have low confidence.
        Satisfaction: 1 - (conf - tau)_+ normalized
        We'll use tau_outlier from meta or default 0.6.
        """
        conf = self._get_confidence(pred)
        outlier = pred.get('outlier_score', None)
        if outlier is None:
            # no outlier signal -> vacuously satisfied (1.0)
            return torch.ones_like(conf)
        tau = meta.get('tau_outlier', 0.6) if meta else 0.6
        # penalty term p = relu(conf - tau); satisfaction = 1 - p/(1-tau)
        p = F.relu(conf - tau)
        sat = 1.0 - p / (1.0 - tau + EPS)
        return sat.clamp(0.0, 1.0)

    def rule_transition_consistency(self, pred: Dict[str, Any], meta: Dict[str, Any]) -> torch.Tensor:
        """Rule 3: predicted transition distributions should align with empirical transitions.
        meta should provide 'empirical_transitions' Tensor (K,K).
        pred may provide 'pred_transitions' (K,K) or 'seq_cluster_preds' list of sequences to compute pred transitions.
        We compute a single scalar satisfaction per batch sample (broadcasted) as 1 - normalized KL.
        """
        if meta is None or 'empirical_transitions' not in meta:
            # can't compute -> vacuously satisfied
            B = self._get_probs(pred).shape[0]
            return torch.ones(B, device=self.device)
        P_emp = meta['empirical_transitions'].to(self.device) + EPS  # (K,K)
        P_emp = P_emp / P_emp.sum(dim=1, keepdim=True).clamp_min(EPS)

        if 'pred_transitions' in pred:
            P_hat = pred['pred_transitions'].to(self.device) + EPS
            P_hat = P_hat / P_hat.sum(dim=1, keepdim=True).clamp_min(EPS)
        elif 'seq_cluster_preds' in pred:
            # estimate transitions from predicted cluster sequences in batch (simple aggregate)
            sequences = pred['seq_cluster_preds']  # list of lists (seq of ints)
            K = P_emp.shape[0]
            C = torch.zeros_like(P_emp)
            for seq in sequences:
                for i in range(len(seq)-1):
                    a, b = seq[i], seq[i+1]
                    if 0 <= a < K and 0 <= b < K:
                        C[a, b] += 1.0
            P_hat = (C + EPS) / (C.sum(dim=1, keepdim=True).clamp_min(EPS))
        else:
            B = self._get_probs(pred).shape[0]
            return torch.ones(B, device=self.device)

        # compute symmetric KL-like measure row-wise and convert to satisfaction
        kl = (P_emp * (P_emp.log() - P_hat.log())).sum(dim=1).clamp_min(0.0)  # (K,)
        # normalize by log(K)
        K = P_emp.shape[0]
        kl_norm = kl / (math.log(max(2, K)) + EPS)
        # map to [0,1] satisfaction: s = exp(-kl_norm)
        s_rows = torch.exp(-kl_norm)
        # broadcast per-sample as mean over rows
        s = s_rows.mean().repeat(self._get_probs(pred).shape[0])
        return s.clamp(0.0, 1.0)

    def rule_graph_sequence_alignment(self, pred: Dict[str, Any], meta: Dict[str, Any]) -> torch.Tensor:
        """Rule 4: LSTM (s) and GNN (g) embeddings should be consistent: high cosine similarity.
        Satisfaction = (cos_sim + 1)/2 to map into [0,1].
        """
        g = pred.get('g', None)
        s = pred.get('s', None)
        if g is None or s is None:
            B = self._get_probs(pred).shape[0]
            return torch.ones(B, device=self.device)
        # ensure same dim: project if needed by simple linear mapping (here: mean-reduce larger dim)
        if g.shape[-1] != s.shape[-1]:
            # project both to min dim by linear layer would be ideal; here use mean along features fallback
            if g.shape[-1] > s.shape[-1]:
                g_p = g[:, :s.shape[-1]]
                s_p = s
            else:
                s_p = s[:, :g.shape[-1]]
                g_p = g
        else:
            g_p = g
            s_p = s
        cos = F.cosine_similarity(g_p, s_p, dim=-1)
        sat = (cos + 1.0) / 2.0
        return sat.clamp(0.0, 1.0)

    def rule_forbidden_edge(self, pred: Dict[str, Any], meta: Dict[str, Any]) -> torch.Tensor:
        """Rule 5: Forbidden label pairs should not be adjacent. meta['forbidden_edge_pairs'] expected as list of (a_idx,b_idx).
        For each sample, we compute fraction of violated forbidden edges; satisfaction = 1 - violation_fraction.
        pred should include 'A' adjacency and 'label_idx' (B,) hard labels or 'probs' to conjecture label per node.
        NOTE: this is expensive if you have per-graph many nodes; we make simple batch-global check if needed.
        """
        if meta is None or 'forbidden_edge_pairs' not in meta:
            B = self._get_probs(pred).shape[0]
            return torch.ones(B, device=self.device)
        pairs = meta['forbidden_edge_pairs']
        # We expect pred to have per-graph adjacency A and per-node labels: for simplicity assume single-node-per-sample setup
        # If graph-level, this rule should be applied upstream per-graph with node-level labels.
        # Fallback: if pred contains 'label_idx' per sample and 'A' is (B,1,1) trivial, evaluate trivially.
        B = self._get_probs(pred).shape[0]
        if 'A' not in pred or ('label_idx' not in pred and 'node_label_idx' not in pred):
            return torch.ones(B, device=self.device)
        A = pred['A']  # (B,N,N)
        # label indices per node required: pred['node_label_idx'] expected (B,N)
        node_labels = pred.get('node_label_idx', None)
        if node_labels is None:
            return torch.ones(B, device=self.device)
        device = A.device
        sats = []
        for b in range(A.shape[0]):
            adj = A[b]
            labels = node_labels[b]
            N = labels.shape[0]
            violations = 0
            total_checked = 0
            for u in range(N):
                for v in range(N):
                    if adj[u, v] > 0:
                        total_checked += 1
                        a_lbl = int(labels[u].item())
                        b_lbl = int(labels[v].item())
                        if (a_lbl, b_lbl) in pairs or (b_lbl, a_lbl) in pairs:
                            violations += 1
            frac = (violations / total_checked) if total_checked > 0 else 0.0
            sats.append(1.0 - frac)
        return torch.tensor(sats, device=device).clamp(0.0, 1.0)

    def rule_centrality_confidence(self, pred: Dict[str, Any], meta: Dict[str, Any]) -> torch.Tensor:
        """Rule 6: High centrality -> higher confidence. We'll compute Spearman-like soft satisfaction by mapping centrality to [0,1]
        and penalizing cases where centrality high but confidence low.
        satisfaction = 1 - relu(conf_threshold - conf) * centrality_norm
        """
        conf = self._get_confidence(pred)
        central = pred.get('centrality_norm', None)
        if central is None:
            # try to compute from adjacency sum
            if 'A' in pred:
                A = pred['A']
                # degree per sample: sum over nodes then average (use normalization)
                deg = A.sum(dim=(1,2)) / (A.shape[1] + EPS)
                central = (deg - deg.min()) / (deg.max() - deg.min() + EPS)
            else:
                return torch.ones_like(conf)
        # normalize central to [0,1]
        central = central.clamp(0.0, 1.0)
        # desired conf threshold increases with centrality: thr = 0.5 + 0.4*central
        thr = 0.5 + 0.4 * central
        p = F.relu(thr - conf)
        sat = 1.0 - p  # high when conf >= thr
        return sat.clamp(0.0, 1.0)

    def rule_similarity_label_smooth(self, pred: Dict[str, Any], meta: Dict[str, Any]) -> torch.Tensor:
        """Rule 7: Highly similar nodes (by embeddings) should have similar predicted distributions.
        meta should provide pairs and sim_scores: meta['similarity_pairs'] = (idx_pairs, sim_scores)
        where idx_pairs is (M,2) mapping into batch indices and sim_scores (M,) in [0,1].
        Returns per-sample satisfaction averaged across pairs that include the sample.
        """
        probs = self._get_probs(pred)
        B = probs.shape[0]
        if not meta or 'similarity_pairs' not in meta:
            return torch.ones(B, device=self.device)
        idx_pairs, sim_scores = meta['similarity_pairs']  # idx_pairs: (M,2) tensor long, sim_scores: (M,)
        idx_pairs = idx_pairs.to(self.device)
        sim_scores = sim_scores.to(self.device)
        M = idx_pairs.shape[0]
        if M == 0:
            return torch.ones(B, device=self.device)
        divergences = (probs[idx_pairs[:,0]] - probs[idx_pairs[:,1]]).abs().sum(dim=1) / 2.0  # (M,) in [0,1]
        sats_pairs = 1.0 - sim_scores * divergences  # (M,)
        # aggregate per sample
        sats = torch.ones(B, device=self.device)
        counts = torch.zeros(B, device=self.device)
        for m in range(M):
            i, j = int(idx_pairs[m,0].item()), int(idx_pairs[m,1].item())
            s = sats_pairs[m]
            sats[i] += s
            sats[j] += s
            counts[i] += 1
            counts[j] += 1
        # avoid divide-by-zero
        mask = counts > 0
        sats[mask] = sats[mask] / (counts[mask] + 1.0)  # note we added initial 1.0 so normalize appropriately
        return sats.clamp(0.0, 1.0)

    def rule_rbf_smoothness(self, pred: Dict[str, Any], meta: Dict[str, Any]) -> torch.Tensor:
        """Rule 8: Nodes close in RBF-space should have similar predictions. We build a Laplacian regularizer.
        meta may provide an rbf_similarity_matrix (B,B) or we compute from pred['rbf'].'"""
        probs = self._get_probs(pred)
        B = probs.shape[0]
        if 'rbf' in pred:
            rbf = pred['rbf']  # (B, K)
            # cosine similarity in rbf space
            rbfn = rbf / (rbf.norm(dim=1, keepdim=True) + EPS)
            S = rbfn @ rbfn.t()  # (B,B) in [-1,1]
            S = (S + 1.0) / 2.0
        elif meta and 'rbf_similarity' in meta:
            S = meta['rbf_similarity'].to(self.device)
        else:
            return torch.ones(B, device=self.device)
        # threshold to sparsify
        thresh = meta.get('rbf_sim_threshold', 0.7) if meta else 0.7
        W = (S > thresh).float() * S
        # compute Laplacian loss: sum_ij W_ij * ||p_i - p_j||^2 normalized
        diffs = probs.unsqueeze(1) - probs.unsqueeze(0)  # (B,B,C)
        sq = (diffs ** 2).sum(dim=-1)  # (B,B)
        numer = (W * sq).sum()
        denom = (W.sum() + EPS)
        # satisfaction per sample simplified as 1 - normalized local discrepancy
        loss_val = numer / denom
        # convert to per-sample satisfaction by measuring row-wise
        row_sum = (W * sq).sum(dim=1) / (W.sum(dim=1) + EPS)
        sats = 1.0 - (row_sum / (row_sum.max() + EPS))
        return sats.clamp(0.0, 1.0)

    # -------------------- Compute overall loss --------------------
    def compute(self, pred: Dict[str, Any], meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Compute weighted logic loss and per-rule diagnostics.
        Returns {'loss': Tensor, 'per_rule': {name: {satisfaction:float, penalty:float}}}
        """
        device = self.device
        per_rule = {}
        total_loss_terms = []

        # Rule 1: Cluster Purity
        sat1 = self.rule_cluster_purity(pred, meta or {})
        mean1 = float(sat1.mean().detach().cpu())
        loss1 = -torch.log(sat1.mean() + EPS) * self.weights['cluster_purity']
        per_rule['cluster_purity'] = {'satisfaction': mean1, 'penalty': float(loss1.detach().cpu())}
        total_loss_terms.append(loss1)

        # Rule 2: Outlier consistency
        sat2 = self.rule_outlier_consistency(pred, meta or {})
        mean2 = float(sat2.mean().detach().cpu())
        loss2 = -torch.log(sat2.mean() + EPS) * self.weights['outlier_consistency']
        per_rule['outlier_consistency'] = {'satisfaction': mean2, 'penalty': float(loss2.detach().cpu())}
        total_loss_terms.append(loss2)

        # Rule 3: Transition consistency
        sat3 = self.rule_transition_consistency(pred, meta or {})
        mean3 = float(sat3.mean().detach().cpu())
        loss3 = -torch.log(sat3.mean() + EPS) * self.weights['transition_consistency']
        per_rule['transition_consistency'] = {'satisfaction': mean3, 'penalty': float(loss3.detach().cpu())}
        total_loss_terms.append(loss3)

        # Rule 4: Graph-Sequence alignment
        sat4 = self.rule_graph_sequence_alignment(pred, meta or {})
        mean4 = float(sat4.mean().detach().cpu())
        loss4 = -torch.log(sat4.mean() + EPS) * self.weights['graph_sequence_alignment']
        per_rule['graph_sequence_alignment'] = {'satisfaction': mean4, 'penalty': float(loss4.detach().cpu())}
        total_loss_terms.append(loss4)

        # Rule 5: Forbidden edge pairs
        sat5 = self.rule_forbidden_edge(pred, meta or {})
        mean5 = float(sat5.mean().detach().cpu())
        loss5 = -torch.log(sat5.mean() + EPS) * self.weights['forbidden_edge']
        per_rule['forbidden_edge'] = {'satisfaction': mean5, 'penalty': float(loss5.detach().cpu())}
        total_loss_terms.append(loss5)

        # Rule 6: Centrality - Confidence
        sat6 = self.rule_centrality_confidence(pred, meta or {})
        mean6 = float(sat6.mean().detach().cpu())
        loss6 = -torch.log(sat6.mean() + EPS) * self.weights['centrality_confidence']
        per_rule['centrality_confidence'] = {'satisfaction': mean6, 'penalty': float(loss6.detach().cpu())}
        total_loss_terms.append(loss6)

        # Rule 7: Similarity label smooth
        sat7 = self.rule_similarity_label_smooth(pred, meta or {})
        mean7 = float(sat7.mean().detach().cpu())
        loss7 = -torch.log(sat7.mean() + EPS) * self.weights['similarity_label_smooth']
        per_rule['similarity_label_smooth'] = {'satisfaction': mean7, 'penalty': float(loss7.detach().cpu())}
        total_loss_terms.append(loss7)

        # Rule 8: RBF smoothness
        sat8 = self.rule_rbf_smoothness(pred, meta or {})
        mean8 = float(sat8.mean().detach().cpu())
        loss8 = -torch.log(sat8.mean() + EPS) * self.weights['rbf_smoothness']
        per_rule['rbf_smoothness'] = {'satisfaction': mean8, 'penalty': float(loss8.detach().cpu())}
        total_loss_terms.append(loss8)

        total_loss = torch.stack(total_loss_terms).sum()
        return {'loss': total_loss, 'per_rule': per_rule}


# ---------------- Example usage snippet ----------------
# logic = LogicModule()
# pred = {'logits': logits, 'g': g, 's': s, 'rbf': rbf, 'clusters': clusters_soft}
# meta = {'cluster_label_distribution': {...}, 'empirical_transitions': P_emp, 'forbidden_edge_pairs': [(0,3), ...], 'similarity_pairs': (idx_pairs, sim_scores)}
# out = logic.compute(pred, meta)
# L_logic = out['loss']
# logger.log(out['per_rule'])

