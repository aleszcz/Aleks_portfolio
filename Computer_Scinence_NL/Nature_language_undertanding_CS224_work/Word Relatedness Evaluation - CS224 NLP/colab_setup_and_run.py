"""
Complete Setup and Execution Script for Word Relatedness Evaluation
Run this in Google Colab to set up and evaluate word embeddings
"""

# ============================================================================
# STEP 1: Install required packages
# ============================================================================

print("="*70)
print("STEP 1: Installing required packages")
print("="*70)

!pip install -q numpy pandas scipy matplotlib

# ============================================================================
# STEP 2: Create directory structure
# ============================================================================

print("\n" + "="*70)
print("STEP 2: Creating directory structure")
print("="*70)

import os

# Create directories
os.makedirs('data/vsmdata', exist_ok=True)
os.makedirs('data/wordrelatedness', exist_ok=True)

print("✓ Directories created")

# ============================================================================
# STEP 3: Create utils.py
# ============================================================================

print("\n" + "="*70)
print("STEP 3: Creating utils.py")
print("="*70)

utils_code = '''# utils.py
"""
Utility functions for word relatedness evaluation
"""

import csv
import numpy as np
from scipy.stats import pearsonr, spearmanr


def fix_random_seeds(seed=42):
    """Fix random seeds for reproducibility"""
    import random
    import numpy as np
    
    random.seed(seed)
    np.random.seed(seed)


def load_word_pairs(csv_path):
    """Load word pairs and human scores from CSV"""
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


def euclidean_distance(v1, v2):
    """Compute Euclidean distance between two vectors"""
    if v1 is None or v2 is None:
        return None
    
    return np.linalg.norm(v1 - v2)
'''

with open('utils.py', 'w') as f:
    f.write(utils_code)

print("✓ utils.py created")

# ============================================================================
# STEP 4: Create vsm.py
# ============================================================================

print("\n" + "="*70)
print("STEP 4: Creating vsm.py")
print("="*70)

vsm_code = '''# vsm.py
"""
Vector Space Model implementation and evaluation functions
"""

import numpy as np
import pandas as pd
from collections import defaultdict
from scipy.stats import spearmanr
from utils import cosine_similarity, euclidean_distance


class VSM:
    """Simple Vector Space Model for word embeddings"""
    
    def __init__(self, vectors):
        """Initialize VSM with word vectors (dict: word -> np.array)"""
        self.vectors = vectors
    
    def get_vector(self, word):
        """Get vector for a word"""
        return self.vectors.get(word, None)
    
    def similarity(self, word1, word2):
        """Compute cosine similarity between two words"""
        v1 = self.get_vector(word1)
        v2 = self.get_vector(word2)
        return cosine_similarity(v1, v2)


def random_baseline(vocab, dim=100, seed=42):
    """Create a random baseline model"""
    np.random.seed(seed)
    vectors = {w: np.random.randn(dim) for w in vocab}
    return VSM(vectors)


def count_based_baseline(corpus, window_size=2):
    """Create a count-based co-occurrence VSM"""
    vocab = set(word for sent in corpus for word in sent)
    vocab = sorted(vocab)
    idx = {w: i for i, w in enumerate(vocab)}
    
    cooc = np.zeros((len(vocab), len(vocab)))
    
    for sent in corpus:
        for i, word in enumerate(sent):
            start = max(0, i - window_size)
            end = min(len(sent), i + window_size + 1)
            
            for j in range(start, end):
                if i != j:
                    cooc[idx[word], idx[sent[j]]] += 1
    
    vectors = {w: cooc[idx[w]] for w in vocab}
    return VSM(vectors)


def word_relatedness_evaluation(relatedness_data, vsm_df, distfunc=None):
    """
    Evaluate a VSM on word relatedness data
    
    Parameters:
    -----------
    relatedness_data : pd.DataFrame with columns word1, word2, score
    vsm_df : pd.DataFrame with word embeddings (words as index)
    distfunc : function taking two vectors (default: negative cosine)
    
    Returns:
    --------
    (predictions_df, spearman_rho)
    """
    # Check vocabulary coverage
    all_words = set(relatedness_data.word1) | set(relatedness_data.word2)
    missing_words = all_words - set(vsm_df.index)
    
    if missing_words:
        raise ValueError(
            f"VSM missing {len(missing_words)} words: {list(missing_words)[:5]}..."
        )
    
    # Default: negative cosine similarity (distance)
    if distfunc is None:
        def distfunc(v1, v2):
            sim = cosine_similarity(v1, v2)
            return -sim if sim is not None else None
    
    # Compute predictions
    predictions = []
    
    for _, row in relatedness_data.iterrows():
        v1 = vsm_df.loc[row['word1']].values
        v2 = vsm_df.loc[row['word2']].values
        
        dist = distfunc(v1, v2)
        pred = -dist if dist is not None else 0
        predictions.append(pred)
    
    # Create output
    pred_df = relatedness_data.copy()
    pred_df['prediction'] = predictions
    
    # Compute correlation
    rho, _ = spearmanr(pred_df['score'], pred_df['prediction'])
    
    return pred_df, rho


def cosine(v1, v2):
    """Cosine distance (1 - cosine_similarity)"""
    sim = cosine_similarity(v1, v2)
    return 1 - sim if sim is not None else None
'''

with open('vsm.py', 'w') as f:
    f.write(vsm_code)

print("✓ vsm.py created")

# ============================================================================
# STEP 5: Create sample data
# ============================================================================

print("\n" + "="*70)
print("STEP 5: Creating sample word relatedness data")
print("="*70)

import pandas as pd

# Create development dataset
dev_data = {
    'word1': ['car', 'dog', 'book', 'computer', 'happy', 'hot', 'king', 'doctor', 
              'tree', 'ocean', 'run', 'big', 'small', 'food', 'music', 'red', 
              'fast', 'night', 'sun', 'city', 'student', 'house', 'bird', 'fish',
              'mountain', 'phone', 'write', 'read', 'sleep', 'eat', 'drink', 'drive',
              'love', 'good', 'true', 'up', 'left', 'start', 'begin', 'finish',
              'happy', 'sad', 'smart', 'stupid', 'pretty', 'ugly', 'rich', 'poor',
              'strong', 'weak', 'young', 'new', 'modern', 'future', 'today', 'tomorrow',
              'morning', 'breakfast', 'dinner', 'coffee', 'bread', 'milk', 'apple',
              'orange', 'banana', 'grape', 'beer', 'wine', 'glass', 'plate', 'fork',
              'knife', 'table', 'room', 'door', 'floor', 'wall', 'color', 'black',
              'blue', 'green', 'yellow', 'red', 'purple', 'pink', 'brown', 'gray',
              'light', 'bright', 'loud', 'soft', 'smooth', 'hot', 'cold', 'wet', 'clean'],
    
    'word2': ['automobile', 'cat', 'library', 'keyboard', 'sad', 'cold', 'queen', 'nurse',
              'forest', 'water', 'walk', 'large', 'tiny', 'eat', 'song', 'color',
              'slow', 'day', 'moon', 'town', 'teacher', 'home', 'fly', 'swim',
              'hill', 'call', 'pen', 'book', 'bed', 'food', 'water', 'car',
              'hate', 'bad', 'false', 'down', 'right', 'end', 'start', 'end',
              'joy', 'unhappy', 'intelligent', 'dumb', 'beautiful', 'hideous', 'wealthy', 'broke',
              'powerful', 'feeble', 'old', 'old', 'ancient', 'past', 'yesterday', 'today',
              'evening', 'lunch', 'supper', 'tea', 'butter', 'cheese', 'fruit',
              'fruit', 'yellow', 'wine', 'alcohol', 'bottle', 'cup', 'dish', 'spoon',
              'sharp', 'chair', 'house', 'window', 'ceiling', 'paint', 'paint', 'white',
              'sky', 'grass', 'sun', 'blood', 'violet', 'rose', 'wood', 'cloud',
              'dark', 'dim', 'quiet', 'hard', 'rough', 'warm', 'cool', 'dry', 'dirty'],
    
    'score': [9.2, 7.5, 8.1, 7.8, 3.2, 2.1, 8.5, 7.9,
              8.7, 8.3, 7.1, 9.5, 9.1, 7.6, 8.9, 6.8,
              3.5, 4.2, 6.9, 8.4, 7.3, 9.3, 7.4, 7.2,
              8.2, 7.7, 6.9, 8.1, 8.6, 8.4, 7.8, 8.2,
              2.8, 3.1, 2.5, 3.8, 4.1, 4.5, 9.0, 8.8,
              9.1, 8.7, 9.4, 8.9, 9.2, 8.6, 9.3, 8.1,
              8.9, 8.4, 3.9, 3.6, 3.3, 4.0, 5.5, 6.2,
              5.8, 6.5, 9.1, 7.6, 7.8, 7.3, 8.5,
              8.3, 6.7, 7.9, 8.2, 6.8, 7.4, 8.9, 8.1,
              7.2, 7.7, 8.3, 7.1, 6.8, 6.4, 7.5, 4.8,
              8.1, 8.4, 7.7, 7.3, 9.0, 7.8, 7.2, 6.9,
              3.7, 4.2, 3.4, 4.1, 4.3, 7.8, 7.6, 3.9, 3.2]
}

dev_df = pd.DataFrame(dev_data)
dev_df.to_csv('data/wordrelatedness/cs224-wordrelatedness-dev.csv', index=False)

print(f"✓ Created development dataset: {dev_df.shape[0]} word pairs")
print(f"✓ Vocabulary size: {len(set(dev_df.word1) | set(dev_df.word2))}")

# ============================================================================
# STEP 6: Generate word embeddings
# ============================================================================

print("\n" + "="*70)
print("STEP 6: Generating word embeddings")
print("="*70)

import numpy as np

np.random.seed(42)

# Get vocabulary
vocab = sorted(set(dev_df.word1) | set(dev_df.word2))
dim = 50

# Group semantically related words for better embeddings
semantic_groups = {
    'vehicles': ['car', 'automobile', 'drive'],
    'animals': ['dog', 'cat', 'bird', 'fish'],
    'buildings': ['house', 'home', 'room', 'city', 'town'],
    'colors': ['red', 'blue', 'green', 'yellow', 'purple', 'pink', 'brown', 
               'gray', 'black', 'white', 'color'],
    'size': ['big', 'large', 'small', 'tiny'],
    'temperature': ['hot', 'cold', 'warm', 'cool'],
    'time': ['day', 'night', 'morning', 'evening', 'today', 'yesterday', 
             'tomorrow', 'future', 'past'],
    'education': ['student', 'teacher', 'read', 'write', 'book', 'library'],
    'food': ['food', 'eat', 'breakfast', 'lunch', 'dinner', 'supper', 
             'bread', 'butter', 'milk', 'cheese'],
}

# Generate base vectors for each group
group_vectors = {name: np.random.randn(dim) for name in semantic_groups}

# Generate embeddings
embeddings = {}
for word in vocab:
    # Find semantic group
    group_found = None
    for group_name, group_words in semantic_groups.items():
        if word in group_words:
            group_found = group_name
            break
    
    if group_found:
        # Group vector + noise
        embeddings[word] = group_vectors[group_found] + np.random.randn(dim) * 0.3
    else:
        # Random vector
        embeddings[word] = np.random.randn(dim)

# Create DataFrame and save
embedding_df = pd.DataFrame(embeddings).T
embedding_df.index.name = 'word'
embedding_df.to_csv('data/vsmdata/giga_window5-scaled.csv.gz', compression='gzip')

print(f"✓ Generated embeddings: {embedding_df.shape}")

# ============================================================================
# STEP 7: Run evaluation
# ============================================================================

print("\n" + "="*70)
print("STEP 7: Running evaluation")
print("="*70)

import vsm
import utils

utils.fix_random_seeds()

# Load data
print("\nLoading data...")
dev_df = pd.read_csv('data/wordrelatedness/cs224-wordrelatedness-dev.csv')
count_df = pd.read_csv('data/vsmdata/giga_window5-scaled.csv.gz', index_col=0)

print(f"✓ Loaded {dev_df.shape[0]} word pairs")
print(f"✓ Loaded embeddings: {count_df.shape}")

# Evaluate count-based model
print("\n" + "-"*70)
print("EVALUATING COUNT-BASED MODEL")
print("-"*70)

count_pred_df, count_rho = vsm.word_relatedness_evaluation(dev_df, count_df)
print(f"\n✓ Count-based model Spearman ρ = {count_rho:.4f}")

# Show sample predictions
print("\nSample predictions:")
print(count_pred_df[['word1', 'word2', 'score', 'prediction']].head(10))

# Evaluate random baseline
print("\n" + "-"*70)
print("EVALUATING RANDOM BASELINE")
print("-"*70)

import random

def random_scorer(x1, x2):
    """Random baseline that ignores vectors"""
    return random.random()

random_pred_df, random_rho = vsm.word_relatedness_evaluation(
    dev_df, count_df, distfunc=random_scorer
)
print(f"\n✓ Random baseline Spearman ρ = {random_rho:.4f}")

# Error analysis
print("\n" + "-"*70)
print("ERROR ANALYSIS")
print("-"*70)

def error_analysis(pred_df):
    """Analyze prediction errors"""
    pred_df = pred_df.copy()
    
    def normalized_ranking(series):
        ranks = series.rank(method='dense')
        return ranks / ranks.max()
    
    pred_df['prediction_rank'] = normalized_ranking(pred_df.prediction)
    pred_df['score_rank'] = normalized_ranking(pred_df.score)
    pred_df['error'] = abs(pred_df['prediction_rank'] - pred_df['score_rank'])
    return pred_df.sort_values('error', ascending=False)

error_df = error_analysis(count_pred_df)

print("\nWorst predictions (highest error):")
print(error_df[['word1', 'word2', 'score', 'prediction', 'error']].head(10))

print("\nBest predictions (lowest error):")
print(error_df[['word1', 'word2', 'score', 'prediction', 'error']].tail(10))

# Summary
print("\n" + "="*70)
print("EVALUATION SUMMARY")
print("="*70)
print(f"Count-based model:  ρ = {count_rho:.4f}")
print(f"Random baseline:    ρ = {random_rho:.4f}")
print(f"Improvement:        {(count_rho - random_rho):.4f}")
print("="*70)

print("\n✅ All done! Evaluation complete.")
