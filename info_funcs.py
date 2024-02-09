from collections import Counter

import numpy as np

def compute_joint(actions, states):
    all_pairs = [(a, s) for a in actions for s in states]
    counts = Counter(all_pairs)
    n = sum(counts.values())
    probs = np.array([count / n for count in counts.values()])
    return probs

def compute_joint_counts(actions, states):
    all_pairs = [(a, s) for a in actions for s in states]
    counts = Counter(all_pairs)
    return counts

def compute_joint_entropy(actions, states):
    probs, _ = compute_joint(actions, states)
    return -np.sum(probs * np.log2(probs))
