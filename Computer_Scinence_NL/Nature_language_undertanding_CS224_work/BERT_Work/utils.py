# utils.py

import csv
import numpy as np
from scipy.stats import pearsonr

def fix_random_seeds(seed=42):
    """
    Fix random seeds for reproducibility
    """
    import random
    import numpy as np

    random.seed(seed)
    np.random.seed(seed)


def load_word_pairs(csv_path):
    """
    Load word pairs and human scores from CSV.
    Expected columns: word1, word2, score
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
    """Compute cosine similarity between two vectors"""
    if v1 is None or v2 is None:
        return None

    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    if denom == 0:
        return None

    return np.dot(v1, v2) / denom


def evaluate_model(pairs, gold_scores, model):
    """
    Evaluate a VSM model using Pearson correlation
    """
    preds = []

    for w1, w2 in pairs:
        sim = model.similarity(w1, w2)
        if sim is not None:
            preds.append(sim)

    if len(preds) != len(gold_scores):
        raise ValueError("Mismatch between predictions and gold scores")

    return pearsonr(preds, gold_scores)[0]
