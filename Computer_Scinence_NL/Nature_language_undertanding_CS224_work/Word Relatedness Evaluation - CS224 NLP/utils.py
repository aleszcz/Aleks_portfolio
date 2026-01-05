# utils.py
"""
Utility functions for word relatedness evaluation
"""

import csv
import numpy as np
from scipy.stats import pearsonr, spearmanr


def fix_random_seeds(seed=42):
    """
    Fix random seeds for reproducibility across random, numpy
    
    Parameters:
    -----------
    seed : int
        Random seed value (default: 42)
    """
    import random
    import numpy as np
    
    random.seed(seed)
    np.random.seed(seed)


def load_word_pairs(csv_path):
    """
    Load word pairs and human scores from CSV.
    
    Parameters:
    -----------
    csv_path : str
        Path to CSV file with columns: word1, word2, score
    
    Returns:
    --------
    pairs : list of tuples
        List of (word1, word2) tuples
    scores : np.array
        Array of human relatedness scores
    """
    pairs = []
    scores = []
    
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pairs.append((row['word1'], row['word2']))
            scores.append(float(row['score']))
    
    return pairs, np.array(scores)


def cosine_similarity(v1, v2):
    """
    Compute cosine similarity between two vectors
    
    Parameters:
    -----------
    v1, v2 : np.array or None
        Input vectors
    
    Returns:
    --------
    float or None
        Cosine similarity in [-1, 1], or None if input is invalid
    """
    if v1 is None or v2 is None:
        return None
    
    # Handle zero vectors
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    if denom == 0:
        return None
    
    return np.dot(v1, v2) / denom


def euclidean_distance(v1, v2):
    """
    Compute Euclidean distance between two vectors
    
    Parameters:
    -----------
    v1, v2 : np.array or None
        Input vectors
    
    Returns:
    --------
    float or None
        Euclidean distance, or None if input is invalid
    """
    if v1 is None or v2 is None:
        return None
    
    return np.linalg.norm(v1 - v2)


def evaluate_model(pairs, gold_scores, model, metric='pearson'):
    """
    Evaluate a VSM model using correlation with human judgments
    
    Parameters:
    -----------
    pairs : list of tuples
        Word pairs to evaluate
    gold_scores : np.array
        Human relatedness scores
    model : VSM object
        Model with similarity() method
    metric : str
        'pearson' or 'spearman' correlation (default: 'pearson')
    
    Returns:
    --------
    float
        Correlation coefficient
    """
    preds = []
    
    for w1, w2 in pairs:
        sim = model.similarity(w1, w2)
        if sim is not None:
            preds.append(sim)
    
    if len(preds) != len(gold_scores):
        raise ValueError(
            f"Mismatch: {len(preds)} predictions vs {len(gold_scores)} gold scores"
        )
    
    if metric == 'pearson':
        return pearsonr(preds, gold_scores)[0]
    elif metric == 'spearman':
        return spearmanr(preds, gold_scores)[0]
    else:
        raise ValueError(f"Unknown metric: {metric}")


def normalize_vectors(vectors_dict):
    """
    L2-normalize all vectors in a dictionary
    
    Parameters:
    -----------
    vectors_dict : dict
        Dictionary mapping words to vectors
    
    Returns:
    --------
    dict
        Dictionary with normalized vectors
    """
    normalized = {}
    for word, vec in vectors_dict.items():
        norm = np.linalg.norm(vec)
        if norm > 0:
            normalized[word] = vec / norm
        else:
            normalized[word] = vec
    return normalized


def print_summary_stats(scores):
    """
    Print summary statistics for a score array
    
    Parameters:
    -----------
    scores : np.array or list
        Numeric scores
    """
    scores = np.array(scores)
    print(f"  Count: {len(scores)}")
    print(f"  Mean:  {np.mean(scores):.3f}")
    print(f"  Std:   {np.std(scores):.3f}")
    print(f"  Min:   {np.min(scores):.3f}")
    print(f"  Max:   {np.max(scores):.3f}")
    print(f"  Median: {np.median(scores):.3f}")
