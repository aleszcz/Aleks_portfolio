# -*- coding: utf-8 -*-
"""cs224_NL_word_relatedness.ipynb

Word Relatedness / Word Similarity Evaluation

This notebook evaluates distributed word representations using word relatedness
and similarity benchmarks.
"""

# Install required packages
# !pip install anthropic

"""
1. Word Relatedness / Word Similarity – Overview

Word relatedness and word similarity are standard benchmarks used to evaluate 
distributed word representations (vector space models). These tasks assess how 
well a model captures semantic relationships between words by comparing 
model-derived distances with human judgments.

The evaluation data consist of CSV files containing word pairs, where each pair 
is associated with a human-annotated relatedness or similarity score. 
Similarity focuses on how alike two words are (e.g., car–automobile), whereas 
relatedness captures broader semantic association (e.g., car–road).

Models are evaluated by computing vector distances or similarities (e.g., 
cosine similarity) between word embeddings and comparing these values to the 
human scores.

2. Evaluation Protocol and Metrics

Model performance is measured using the Pearson/Spearman correlation coefficient 
between the human-annotated scores and the model-computed distances or 
similarities for each word pair.
"""

# ============================================================================
# IMPORTS
# ============================================================================

from collections import defaultdict
import csv
import itertools
import numpy as np
import os
import pandas as pd
import random
from scipy.stats import spearmanr, pearsonr

import vsm
import utils

# Fix random seeds for reproducibility
utils.fix_random_seeds()

# ============================================================================
# SETUP PATHS
# ============================================================================

VSM_HOME = os.path.join('data', 'vsmdata')
DATA_HOME = os.path.join('data', 'wordrelatedness')

# Create directories if they don't exist
os.makedirs(VSM_HOME, exist_ok=True)
os.makedirs(DATA_HOME, exist_ok=True)

# ============================================================================
# LOAD DEVELOPMENT DATASET
# ============================================================================

print("Loading development dataset...")
dev_df = pd.read_csv(
    os.path.join(DATA_HOME, "cs224-wordrelatedness-dev.csv")
)

print("\nFirst few rows:")
print(dev_df.head())

print(f"\nDataset size: {dev_df.shape[0]} word pairs")

# ============================================================================
# VOCABULARY ANALYSIS
# ============================================================================

# Extract vocabulary from development set
dev_vocab = set(dev_df.word1.values) | set(dev_df.word2.values)
print(f"\nDevelopment vocabulary size: {len(dev_vocab)}")

# Load task vocabulary index
print("\nLoading task vocabulary...")
task_index = pd.read_csv(
    os.path.join(VSM_HOME, 'giga_window5-scaled.csv.gz'),
    usecols=[0], 
    index_col=0
)
full_task_vocab = list(task_index.index)
print(f"Full task vocabulary size: {len(full_task_vocab)}")

# ============================================================================
# SCORE DISTRIBUTION ANALYSIS
# ============================================================================

print("\nPlotting score distribution...")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
dev_df['score'].hist(bins=30, ax=ax, edgecolor='black')
ax.set_xlabel("Relatedness score", fontsize=12)
ax.set_ylabel("Frequency", fontsize=12)
ax.set_title("Distribution of Relatedness Scores", fontsize=14)
plt.tight_layout()
plt.savefig('score_distribution.png', dpi=100, bbox_inches='tight')
print("Score distribution plot saved as 'score_distribution.png'")

# ============================================================================
# CHECK FOR REPEATED PAIRS
# ============================================================================

print("\nChecking for repeated word pairs...")
repeats = dev_df.groupby(['word1', 'word2']).apply(
    lambda x: x.score.var()
)
repeats = repeats[repeats > 0].sort_values(ascending=False)
repeats.name = 'score variance'

print(f"Number of repeated pairs with variance: {repeats.shape[0]}")
if repeats.shape[0] > 0:
    print("\nTop repeated pairs:")
    print(repeats.head())

# ============================================================================
# EVALUATION
# ============================================================================

"""
Our evaluation function is vsm.word_relatedness_evaluation. Its arguments:
1. relatedness_data: pd.DataFrame - e.g. dev_df as given above
2. vsm_df: pd.DataFrame - e.g., giga5 or some transformation thereof, 
   or a GloVe embedding space, or something you have created on your own. 
   The function checks that you have a representation for every word in 
   dev_df and raises an exception if you can't.
3. Optional distfunc argument which defaults to vsm.cosine

The function returns a tuple:
- A copy of dev_df with a new column giving your predictions
- Spearman rho value (our primary score)

Important note: vsm.word_relatedness_evaluation uses -distfunc(x1, x2) as 
its score where x1 and x2 are vector representations of words. This is 
because the scores in our data are positive relatedness scores, whereas 
we are assuming the distfunc is a distance function.
"""

# ============================================================================
# COUNT-BASED BASELINE
# ============================================================================

print("\n" + "="*70)
print("EVALUATING COUNT-BASED BASELINE")
print("="*70)

count_df = pd.read_csv(
    os.path.join(VSM_HOME, "giga_window5-scaled.csv.gz"), 
    index_col=0
)

count_pred_df, count_rho = vsm.word_relatedness_evaluation(dev_df, count_df)

print(f"\nCount-based model Spearman rho: {count_rho:.4f}")
print("\nSample predictions:")
print(count_pred_df.head())

# ============================================================================
# RANDOM BASELINE
# ============================================================================

print("\n" + "="*70)
print("EVALUATING RANDOM BASELINE")
print("="*70)

def random_scorer(x1, x2):
    """
    x1 and x2 are vectors to conform to the requirements of 
    vsm.word_relatedness_evaluation, but this function just returns 
    a random number in [0, 1].
    """
    return random.random()

random_pred_df, random_rho = vsm.word_relatedness_evaluation(
    dev_df, count_df, distfunc=random_scorer
)

print(f"\nRandom baseline Spearman rho: {random_rho:.4f}")

# ============================================================================
# ERROR ANALYSIS
# ============================================================================

print("\n" + "="*70)
print("ERROR ANALYSIS")
print("="*70)

def _normalized_ranking(series):
    """Compute normalized ranks for a series"""
    ranks = series.rank(method='dense')
    return ranks / ranks.max()

def error_analysis(pred_df):
    """
    Analyze errors by comparing predicted rankings to gold rankings
    """
    pred_df = pred_df.copy()
    pred_df['prediction_rank'] = _normalized_ranking(pred_df.prediction)
    pred_df['score_rank'] = _normalized_ranking(pred_df.score)
    pred_df['error'] = abs(pred_df['prediction_rank'] - pred_df['score_rank'])
    return pred_df.sort_values('error', ascending=False)

# Perform error analysis on count-based model
error_df = error_analysis(count_pred_df)

print("\nWorst predictions (highest error):")
print(error_df.head(10))

print("\nBest predictions (lowest error):")
print(error_df.tail(10))

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("EVALUATION SUMMARY")
print("="*70)
print(f"Count-based model: ρ = {count_rho:.4f}")
print(f"Random baseline:   ρ = {random_rho:.4f}")
print("="*70)
