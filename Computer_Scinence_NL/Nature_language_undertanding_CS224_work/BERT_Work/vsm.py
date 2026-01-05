# vsm.py

import numpy as np
import pandas as pd
from collections import defaultdict
from utils import cosine_similarity
from scipy.stats import spearmanr
from sklearn.decomposition import TruncatedSVD


class VSM:
    """
    Simple Vector Space Model
    """

    def __init__(self, vectors):
        """
        vectors: dict {word: np.array}
        """
        self.vectors = vectors

    def get_vector(self, word):
        return self.vectors.get(word, None)

    def similarity(self, word1, word2):
        v1 = self.get_vector(word1)
        v2 = self.get_vector(word2)
        return cosine_similarity(v1, v2)


def random_baseline(vocab, dim=100, seed=42):
    """
    Random baseline model
    """
    np.random.seed(seed)
    vectors = {w: np.random.randn(dim) for w in vocab}
    return VSM(vectors)


def count_based_baseline(corpus, window_size=2):
    """
    Simple count-based co-occurrence VSM
    corpus: list of tokenized sentences
    """
    vocab = set(word for sent in corpus for word in sent)
    vocab = sorted(vocab)
    idx = {w: i for i, w in enumerate(vocab)}

    cooc = np.zeros((len(vocab), len(vocab)))

    for sent in corpus:
        for i, word in enumerate(sent):
            for j in range(max(0, i - window_size), min(len(sent), i + window_size + 1)):
                if i != j:
                    cooc[idx[word], idx[sent[j]]] += 1

    vectors = {w: cooc[idx[w]] for w in vocab}
    return VSM(vectors)


def cosine(u, v):
    """Cosine similarity"""
    return cosine_similarity(u, v)


def euclidean(u, v):
    """Euclidean distance"""
    return np.linalg.norm(u - v)


def word_relatedness_evaluation(df, vsm_df, distfunc=cosine):
    """
    Evaluate word relatedness using a VSM dataframe
    """
    scores = []
    predictions = []
    
    for _, row in df.iterrows():
        w1, w2 = row['word1'], row['word2']
        if w1 in vsm_df.index and w2 in vsm_df.index:
            v1 = vsm_df.loc[w1].values
            v2 = vsm_df.loc[w2].values
            sim = distfunc(v1, v2)
            if sim is not None:
                scores.append(row['score'])
                predictions.append(sim)
    
    pred_df = df.copy()
    pred_df['predicted'] = predictions
    
    rho, _ = spearmanr(scores, predictions)
    return pred_df, rho


def ppmi(df, positive=True):
    """
    Compute PPMI transformation
    """
    # Get probabilities
    row_probs = df.sum(axis=1) / df.sum().sum()
    col_probs = df.sum(axis=0) / df.sum().sum()
    
    # Compute PMI
    result = df.copy()
    for i in df.index:
        for j in df.columns:
            p_xy = df.loc[i, j] / df.sum().sum()
            if p_xy > 0:
                pmi = np.log2(p_xy / (row_probs[i] * col_probs[j]))
                result.loc[i, j] = max(pmi, 0) if positive else pmi
            else:
                result.loc[i, j] = 0
    
    return result


def lsa(df, k=100):
    """
    Apply LSA dimensionality reduction
    """
    svd = TruncatedSVD(n_components=k)
    reduced = svd.fit_transform(df)
    return pd.DataFrame(reduced, index=df.index)


def create_subword_pooling_vsm(vocab, bert_model, bert_tokenizer, layers, pool_func):
    """
    Create VSM from BERT subword representations
    """
    vectors = {}
    
    for word in vocab:
        inputs = bert_tokenizer(word, return_tensors='pt')
        outputs = bert_model(**inputs, output_hidden_states=True)
        
        # Get specified layer
        hidden_states = outputs.hidden_states[layers]
        
        # Pool subword representations
        pooled = pool_func(hidden_states[0].detach().numpy())
        vectors[word] = pooled
    
    return pd.DataFrame.from_dict(vectors, orient='index')


def mean_pooling(hidden_states):
    """Mean pooling function"""
    return np.mean(hidden_states, axis=0)


def max_pooling(hidden_states):
    """Max pooling function"""
    return np.max(hidden_states, axis=0)
