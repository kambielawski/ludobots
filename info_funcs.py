from collections import Counter

import numpy as np

def compute_entropy(states):
    counts = Counter(states)
    n = sum(counts.values())
    probs = np.array([count / n for count in counts.values()])
    return -np.sum(probs * np.log2(probs))

def compute_joint_prob(actions, states):
    list(zip(actions, states))
    all_pairs = [(a, s) for a in actions for s in states]
    counts = Counter(all_pairs)
    n = sum(counts.values())
    probs = np.array([count / n for count in counts.values()])
    return probs

def compute_joint_counts(actions, states):
    all_pairs = [(a, s) for a in actions for s in states]
    counts = Counter(all_pairs)
    return list(counts.values())

def compute_joint_entropy(arr1, arr2):
    """
    Compute the joint entropy of two discrete variables represented by integer arrays.
    
    Parameters:
    - arr1: array-like, observations of the first variable
    - arr2: array-like, observations of the second variable
    
    Returns:
    - joint_entropy: float, the joint entropy of the two variables
    """
    # Ensure inputs are NumPy arrays for consistent indexing
    arr1 = np.array(arr1)
    arr2 = np.array(arr2)
    
    # Check if arrays are of the same length
    if len(arr1) != len(arr2):
        raise ValueError("Arrays must have the same length")
    
    # Pair up elements to form joint observations
    joint_states = list(zip(arr1, arr2))
    
    # Count occurrences of each unique joint state
    counts = Counter(joint_states)
    
    # Total number of observations
    n = len(joint_states)
    
    # Calculate probabilities of each joint state
    probs = np.array([count / n for count in counts.values()])
    
    # Calculate joint entropy
    joint_entropy = -np.sum(probs * np.log2(probs))
    
    return joint_entropy