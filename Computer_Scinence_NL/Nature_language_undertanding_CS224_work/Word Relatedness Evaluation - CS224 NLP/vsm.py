# vsm.py
"""
Vector Space Model implementation and evaluation functions
"""

import numpy as np
import pandas as pd
from collections import defaultdict
from scipy.stats import spearmanr
from utils import cosine_similarity, euclidean_distance


class VSM:
    """
    Simple Vector Space Model for word embeddings
    """
    
    def __init__(self, vectors):
        """
        Initialize VSM with word vectors
        
        Parameters:
        -----------
        vectors : dict
            Dictionary mapping words to numpy arrays
        """
        self.vectors = vectors
    
    def get_vector(self, word):
        """
        Get vector for a word
        
        Parameters:
        -----------
        word : str
            Word to look up
        
        Returns:
        --------
        np.array or None
            Word vector, or None if not found
        """
        return self.vectors.get(word, None)
    
    def similarity(self, word1, word2):
        """
        Compute cosine similarity between two words
        
        Parameters:
        -----------
        word1, word2 : str
            Words to compare
        
        Returns:
        --------
        float or None
            Cosine similarity, or None if word not found
        """
        v1 = self.get_vector(word1)
        v2 = self.get_vector(word2)
        return cosine_similarity(v1, v2)
    
    def distance(self, word1, word2):
        """
        Compute Euclidean distance between two words
        
        Parameters:
        -----------
        word1, word2 : str
            Words to compare
        
        Returns:
        --------
        float or None
            Euclidean distance, or None if word not found
        """
        v1 = self.get_vector(word1)
        v2 = self.get_vector(word2)
        return euclidean_distance(v1, v2)


def random_baseline(vocab, dim=100, seed=42):
    """
    Create a random baseline model with Gaussian vectors
    
    Parameters:
    -----------
    vocab : iterable
        Vocabulary words
    dim : int
        Vector dimensionality (default: 100)
    seed : int
        Random seed (default: 42)
    
    Returns:
    --------
    VSM
        Random baseline model
    """
    np.random.seed(seed)
    vectors = {w: np.random.randn(dim) for w in vocab}
    return VSM(vectors)


def count_based_baseline(corpus, window_size=2):
    """
    Create a simple count-based co-occurrence VSM
    
    Parameters:
    -----------
    corpus : list of lists
        List of tokenized sentences
    window_size : int
        Context window size (default: 2)
    
    Returns:
    --------
    VSM
        Count-based model
    """
    # Build vocabulary
    vocab = set(word for sent in corpus for word in sent)
    vocab = sorted(vocab)
    idx = {w: i for i, w in enumerate(vocab)}
    
    # Initialize co-occurrence matrix
    cooc = np.zeros((len(vocab), len(vocab)))
    
    # Count co-occurrences
    for sent in corpus:
        for i, word in enumerate(sent):
            start = max(0, i - window_size)
            end = min(len(sent), i + window_size + 1)
            
            for j in range(start, end):
                if i != j:
                    cooc[idx[word], idx[sent[j]]] += 1
    
    # Create vectors
    vectors = {w: cooc[idx[w]] for w in vocab}
    return VSM(vectors)


def word_relatedness_evaluation(relatedness_data, vsm_df, distfunc=None):
    """
    Evaluate a VSM on word relatedness data
    
    Parameters:
    -----------
    relatedness_data : pd.DataFrame
        DataFrame with columns: word1, word2, score
    vsm_df : pd.DataFrame
        DataFrame with word embeddings (words as index, features as columns)
    distfunc : function, optional
        Distance/similarity function taking two vectors.
        If None, uses negative cosine similarity (default)
    
    Returns:
    --------
    tuple
        (predictions_df, spearman_rho)
        - predictions_df: Copy of relatedness_data with 'prediction' column
        - spearman_rho: Spearman correlation coefficient
    """
    # Check that all words are in the VSM
    all_words = set(relatedness_data.word1) | set(relatedness_data.word2)
    missing_words = all_words - set(vsm_df.index)
    
    if missing_words:
        raise ValueError(
            f"VSM is missing {len(missing_words)} words: {list(missing_words)[:5]}..."
        )
    
    # Default distance function: negative cosine similarity
    # (we use negative because higher cosine = more similar = less distant)
    if distfunc is None:
        def distfunc(v1, v2):
            sim = cosine_similarity(v1, v2)
            return -sim if sim is not None else None
    
    # Compute predictions
    predictions = []
    
    for _, row in relatedness_data.iterrows():
        word1 = row['word1']
        word2 = row['word2']
        
        # Get vectors
        v1 = vsm_df.loc[word1].values
        v2 = vsm_df.loc[word2].values
        
        # Compute distance (note: we negate to convert distance to similarity)
        dist = distfunc(v1, v2)
        
        # For relatedness, we want high scores for related words
        # distfunc should return small values for similar words
        # So we use -dist to get high values for related words
        pred = -dist if dist is not None else 0
        predictions.append(pred)
    
    # Create output dataframe
    pred_df = relatedness_data.copy()
    pred_df['prediction'] = predictions
    
    # Compute Spearman correlation
    rho, _ = spearmanr(pred_df['score'], pred_df['prediction'])
    
    return pred_df, rho


def cosine(v1, v2):
    """
    Cosine distance (1 - cosine_similarity)
    
    Parameters:
    -----------
    v1, v2 : np.array
        Input vectors
    
    Returns:
    --------
    float
        Cosine distance in [0, 2]
    """
    sim = cosine_similarity(v1, v2)
    if sim is None:
        return None
    return 1 - sim


def euclidean(v1, v2):
    """
    Euclidean distance wrapper
    """
    return euclidean_distance(v1, v2)


def load_glove_vectors(filepath, vocab=None, dim=None):
    """
    Load GloVe-format word vectors
    
    Parameters:
    -----------
    filepath : str
        Path to GloVe vectors file (format: word val1 val2 ...)
    vocab : set, optional
        If provided, only load vectors for these words
    dim : int, optional
        Expected dimensionality (for validation)
    
    Returns:
    --------
    dict
        Dictionary mapping words to vectors
    """
    vectors = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            word = parts[0]
            
            # Skip if not in vocab
            if vocab is not None and word not in vocab:
                continue
            
            # Parse vector
            vec = np.array([float(x) for x in parts[1:]])
            
            # Validate dimension
            if dim is not None and len(vec) != dim:
                raise ValueError(f"Expected dim {dim}, got {len(vec)} for '{word}'")
            
            vectors[word] = vec
    
    return vectors


def create_vsm_from_dataframe(df):
    """
    Convert a DataFrame to a VSM object
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with words as index and features as columns
    
    Returns:
    --------
    VSM
        VSM object
    """
    vectors = {word: df.loc[word].values for word in df.index}
    return VSM(vectors)
