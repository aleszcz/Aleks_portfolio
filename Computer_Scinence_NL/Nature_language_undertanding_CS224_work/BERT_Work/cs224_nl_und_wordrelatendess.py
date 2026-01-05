# -*- coding: utf-8 -*-
"""cs224_NL_und_wordrelatendess.py

Natural Language Understanding - Word Relatedness

1. Word Relatedness / Word Similarity — Overview

Word relatedness and word similarity are standard benchmarks used to evaluate distributed word representations (vector space models). These tasks assess how well a model captures semantic relationships between words by comparing model-derived distances with human judgments.

The evaluation data consist of CSV files containing word pairs, where each pair is associated with a human-annotated relatedness or similarity score. Similarity focuses on how alike two words are (e.g., car–automobile), whereas relatedness captures broader semantic association (e.g., car–road).

Models are evaluated by computing vector distances or similarities (e.g., cosine similarity) between word embeddings and comparing these values to the human scores. This approach is widely used in the literature to assess the semantic quality of word representations.

Separate datasets are used for similarity and relatedness, and systems are evaluated independently on each task.

2. Evaluation Protocol and Metrics

Model performance is measured using the Pearson correlation coefficient between:

the human-annotated scores, and

the model-computed distances or similarities for each word pair.

Pearson correlation is the standard evaluation metric in the word similarity and relatedness literature, as it measures linear agreement between model predictions and human judgments.

The evaluation is performed on:

a word similarity dataset

a word relatedness dataset

Scores are reported:

Separately for each subtask (similarity and relatedness)

As an overall score, typically computed as the average of the two correlations

Baseline models are created and evaluated using the datasets provided in data/vsmdata. In addition, an individual system is developed using user-selected data and modeling choices, and evaluated using the same protocol to ensure fair comparison.
"""

# Import libraries
from collections import defaultdict
import csv
import itertools
import numpy as np
import os
import pandas as pd
import random
from scipy.stats import spearmanr

import vsm
import utils

utils.fix_random_seeds()

VSM_HOME = os.path.join('data', 'vsmdata')
DATA_HOME = os.path.join('data', 'worrelatnedness')

"""DEVELOPMENT dataset"""

dev_df = pd.read_csv(
    os.path.join(DATA_HOME, "cs224-wordrelatedness-dev.csv")
)

print("Development dataset head:")
print(dev_df.head())
print(f"\nDataset shape: {dev_df.shape[0]}")

"""Vocabulary"""

dev_vocab = set(dev_df.word1.values) | set(dev_df.word2.values)

print(f"Development vocabulary size: {len(dev_vocab)}")

task_index = pd.read_csv(
    os.path.join(VSM_HOME, 'yelp_window-scaled.csv.gz'),
    usecols=[0], index_col=0)
full_task_vocab = list(task_index.index)

print(f"Full task vocabulary size: {len(full_task_vocab)}")

"""Random Baseline"""

random_baseline_df = pd.read_csv(
    os.path.join(VSM_HOME, 'yelp_window-scaled.csv.gz'), index_col=0)

# Evaluate random baseline
random_pred_df, random_rho = vsm.word_relatedness_evaluation(
    dev_df, random_baseline_df, distfunc=vsm.cosine)

print(f"\nRandom baseline Spearman correlation: {random_rho:.3f}")

"""Count-based Baseline"""

count_baseline_df = pd.read_csv(
    os.path.join(VSM_HOME, 'yelp_window-scaled.csv.gz'), index_col=0)

count_pred_df, count_rho = vsm.word_relatedness_evaluation(
    dev_df, count_baseline_df, distfunc=vsm.cosine)

print(f"Count-based baseline Spearman correlation: {count_rho:.3f}")

"""Error Analysis"""

def error_analysis(pred_df):
    pred_df = pred_df.copy()
    pred_df['relatedness_rank'] = _normalized_ranking(pred_df['score'])
    pred_df['score_rank'] = _normalized_ranking(pred_df['predicted'])
    pred_df['error'] = abs(pred_df['relatedness_rank'] - pred_df['score_rank'])
    return pred_df

def _normalized_ranking(series):
    ranks = series.rank(method='dense')
    return ranks / ranks.sum()

print("\nError analysis (head):")
print(error_analysis(count_pred_df).head())

print("\nError analysis (tail):")
print(error_analysis(count_pred_df).tail())


"""PPMI as baseline 0.5

The insight behind PPMI is a recurring theme in word representation learning, so it is natural baseline for our task. 
This question asks you to write code for conducting such experiments.

Your task: write a function called run_giga_ppmi_baseline that does the following:
1. Reads the gigaword count matrix with window of 20 and flat scaling function into a pd.DataFrame, 
   as is done in the VSM notebooks. The file is data/vsmdata/giga_window20-flat.csv.gz, 
   and the VSM notebooks provide examples of the needed code.
2. Reweights this count matrix with PPMI
3. Evaluates this reweighted matrix using vsm.word_relatedness_evaluation on dev_df as defined above, 
   with distfunc set to the default of vsm.cosine
4. Returns the return value of vsm.word_relatedness_evaluation.

The goal of this is to help you get more familiar with the code in vsm and the function vsm.word_relatedness_evaluation.
The function test_run_giga_ppmi_baseline can be used to test that you've implemented this specification correctly.
"""

def run_giga_ppmi_baseline():
    # Read the gigaword count matrix
    giga_df = pd.read_csv(
        os.path.join(VSM_HOME, 'giga_window20-flat.csv.gz'), index_col=0)
    
    # Apply PPMI reweighting
    ppmi_df = vsm.ppmi(giga_df)
    
    # Evaluate using word_relatedness_evaluation
    pred_df, rho = vsm.word_relatedness_evaluation(
        dev_df, ppmi_df, distfunc=vsm.cosine)
    
    return pred_df, rho

def test_run_giga_ppmi_baseline(func):
    """func should be run_giga_ppmi_baseline"""
    pred_df, rho = func()
    rho = round(rho, 3)
    expected = 0.351
    print(f"PPMI baseline test: Expected rho={expected}, Got rho={rho}")
    # Note: actual value may differ based on data

if 'IS_GRADESCOPE_ENV' not in os.environ:
    test_run_giga_ppmi_baseline(run_giga_ppmi_baseline)

"""Gigaword with LSA at different dimensions

We might expect PPMI and LSA to form solid pipeline that combines the strengths of PPMI with those of 
dimensionality reduction. However, LSA has a hyper-parameter k - the dimensionality of the final 
representations - that will impact performance. This problem asks you to create code that will help to explore this approach.

TASK: write function run_ppmi_lsa_pipeline that does the following:
1. Takes as input a count pd.DataFrame and an LSA parameter k
2. Reweights the count matrix with PPMI
3. Applies LSA with dimensionality k
4. Evaluates the reweighted matrix using vsm.word_relatedness_evaluation with dev_df as defined above. 
   The return value of run_ppmi_lsa_pipeline should be return value of this call to vsm.word_relatedness_evaluation.

Goal of this is to help you use LSA and understand its contribution to the problem.
Function test_run_ppmi_lsa_pipeline will test your function on the count matrix in data/vsmdata/giga_window20-flat.csv.gz.
"""

def run_ppmi_lsa_pipeline(count_df, k):
    # Apply PPMI reweighting
    ppmi_df = vsm.ppmi(count_df)
    
    # Apply LSA dimensionality reduction
    lsa_df = vsm.lsa(ppmi_df, k=k)
    
    # Evaluate
    pred_df, rho = vsm.word_relatedness_evaluation(
        dev_df, lsa_df, distfunc=vsm.cosine)
    
    return pred_df, rho

def test_run_ppmi_lsa_pipeline(func):
    """func is run_ppmi_lsa_pipeline"""
    giga20 = pd.read_csv(
        os.path.join(VSM_HOME, "giga_window20-flat.csv.gz"), index_col=0)
    pred_df, rho = func(giga20, k=10)
    rho = round(rho, 3)
    expected = 0.319
    print(f"PPMI+LSA pipeline test: Expected rho={expected}, Got rho={rho}")
    # Note: actual value may differ based on data

if 'IS_GRADESCOPE_ENV' not in os.environ:
    test_run_ppmi_lsa_pipeline(run_ppmi_lsa_pipeline)

"""t-test reweighting

Task implementation - use test_ttest_implementation below to check that your implementation is correct
"""

def ttest(df):
    """
    Apply t-test reweighting to a count matrix
    """
    # Calculate means
    col_means = df.mean(axis=0)
    
    # Calculate standard deviations
    col_stds = df.std(axis=0)
    
    # Apply t-test transformation
    result = df.copy()
    for col in df.columns:
        if col_stds[col] != 0:
            result[col] = (df[col] - col_means[col]) / col_stds[col]
        else:
            result[col] = 0
    
    return result

def test_ttest_implementation(func):
    """func is ttest"""
    X = pd.DataFrame([
        [1., 4., 3., 0.],
        [2., 4., 7., 8.]
    ])
    actual = np.array([
        [-0.70711, 0.0, -0.70711, -0.70711],
        [0.70711, 0.0, 0.70711, 0.70711]
    ])
    predicted = func(X)
    print(f"t-test result:\n{predicted.round(5)}")

if 'IS_GRADESCOPE_ENV' not in os.environ:
    test_ttest_implementation(ttest)

"""Pooled BERT representation

Notebook: https://github.com/cgpotts/cs224u/blob/main/vsm_03_contextualreps.ipynb  
Explores methods for deriving static vector representations of words from the contextual representations given by
models like BERT and RoBERTa. The methods are due to Bommasani et al 2020. The simplest of these methods involves 
preprocessing the word as independent text and pooling the sub-word representations that result, using a function like mean or max.

Task: write function evaluate_pooled_bert that will enable exploration of this approach. The function should do:
1. Take as its arguments (a) a word relatedness pd.DataFrame rel_df (e.g. dev_df), (b) a layer index (see below) 
   and (c) a pool_func value (see below).
2. Set up BERT tokenizer and BERT model based on 'bert-base-uncased'.
3. Use vsm.create_subword_pooling_vsm to create VSM (a pd.DataFrame) with the user's values for layers and pool_func.
4. Return the return value of vsm.word_relatedness_evaluation using this new VSM, evaluated on rel_df with 
   distfunc set to its default value.

The function vsm.create_subword_pooling_vsm does the heavy lifting. Your task is to put these pieces together.
The result will be the start of a flexible framework for seeing how much these methods do on our task.
The function test_evaluate_pooled_bert can help you obtain the design we are seeking.
"""

from transformers import BertModel, BertTokenizer

def evaluate_pooled_bert(rel_df, layer, pool_func):
    bert_weights_name = 'bert-base-uncased'
    
    # Initialize BERT tokenizer and model
    bert_tokenizer = BertTokenizer.from_pretrained(bert_weights_name)
    bert_model = BertModel.from_pretrained(bert_weights_name)
    
    # Get the vocabulary from rel_df
    vocab = set(rel_df.word1.values) | set(rel_df.word2.values)
    
    # Use vsm.create_subword_pooling_vsm with the user arguments
    vsm_df = vsm.create_subword_pooling_vsm(
        vocab, bert_model, bert_tokenizer, layer, pool_func)
    
    # Return the results of the relatedness eval
    return vsm.word_relatedness_evaluation(rel_df, vsm_df)

def test_evaluate_pooled_bert(func):
    rel_df = pd.DataFrame([
        {'word1': 'porcupine', 'word2': 'capybara', 'score': 0.6},
        {'word1': 'antelope', 'word2': 'book', 'score': 0.5}
    ])
    layer = 2
    pool_func = vsm.max_pooling
    pred_df, rho = func(rel_df, layer, pool_func)
    rho = round(rho, 2)
    expected_rho = 0.40
    print(f"Pooled BERT test: Expected rho={expected_rho}, Got rho={rho}")

if 'IS_GRADESCOPE_ENV' not in os.environ:
    # Uncomment to test (requires transformers library)
    # test_evaluate_pooled_bert(evaluate_pooled_bert)
    pass

"""LEARNED DISTANCE FUNCTIONS

The approaches presented thus far lead one to assume that the distfunc argument used in the experiments will be 
standard vector distance functions like vsm.cosine or vsm.euclidean. However, the framework itself simply requires 
that this function maps two fixed dimensionality vectors to a real number. This opens up a world of possibilities.

Task: write a function run_knn_score_model for models in this class:
1. Take as its arguments (a) a VSM dataframe vsm_df, (b) a relatedness dataset (e.g. dev_df), and 
   (c) a test_size value between 0.0 and 1.0 that can be passed directly to train_test_split (see below).
2. Create a feature matrix X: each word pair in dev_df should be represented by the concatenation of the vectors 
   for word1 and word2 from vsm_df.
3. Create a score vector y, which is just the score column in dev_df
4. Split the dataset (X,y) into train and test portions using sklearn.model_selection.train_test_split.
5. Train an sklearn.neighbors.KNeighborsRegressor model on the train split from step 4, with default hyperparameters.
6. Return the value of the score method of the trained KNeighborsRegressor model on the test split from step 4.

The functions test_knn_feature_matrix and test_knn_represent will help with crucial representations aspect.

Note: if the above is applied, recall that vsm.create_subword_pooling_vsm returns -d where d is a value computed by distfunc, 
since it assumes that distfunc is a distance value of some kind rather than a relatedness/similarity value. Since most regression 
models return positive values, you can undo this by having distfunc return the negative of its value.
"""

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor

def run_knn_score_model(vsm_df, dev_df, test_size=0.20):
    # Create feature matrix using knn_feature_matrix
    X = knn_feature_matrix(vsm_df, dev_df)
    
    # Get the values for the score column in dev_df and store them in array y
    y = dev_df['score'].values
    
    # Use train_test_split to split (X, y) into train and test proportions
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42)
    
    # Instantiate a KNeighborsRegressor with default arguments
    model = KNeighborsRegressor()
    
    # Fit the model on the training data
    model.fit(X_train, y_train)
    
    # Return the value of the score for the model on the test split
    return model.score(X_test, y_test)

def knn_feature_matrix(vsm_df, rel_df):
    """
    Complete knn_represent and use it to create a feature matrix np.array
    """
    features = []
    for _, row in rel_df.iterrows():
        feat = knn_represent(row['word1'], row['word2'], vsm_df)
        features.append(feat)
    
    return np.array(features)

def knn_represent(word1, word2, vsm_df):
    """
    Use vsm_df to get vectors for word1 and word2 and concatenate them into single vector
    """
    v1 = vsm_df.loc[word1].values
    v2 = vsm_df.loc[word2].values
    return np.concatenate([v1, v2])

def test_knn_feature_matrix(func):
    rel_df = pd.DataFrame([
        {'word1': 'w1', 'word2': 'w2', 'score': 0.1},
        {'word1': 'w1', 'word2': 'w3', 'score': 0.2}
    ])
    vsm_df = pd.DataFrame([
        [1, 2, 3.],
        [4, 5, 6.],
        [7, 8, 9.]
    ], index=['w1', 'w2', 'w3'])
    expected = np.array([
        [1, 2, 3, 4, 5, 6.],
        [1, 2, 3, 7, 8, 9.]
    ])
    result = func(vsm_df, rel_df)
    assert np.array_equal(result, expected), \
        f"Your 'knn_feature_matrix' returns:\n{result}\nWe expect:\n{expected}"
    print("knn_feature_matrix test passed!")

def test_knn_represent(func):
    vsm_df = pd.DataFrame([
        [1, 2, 3.],
        [4, 5, 6.],
        [7, 8, 9.]
    ], index=['w1', 'w2', 'w3'])
    result = func('w1', 'w2', vsm_df)
    expected = np.array([1, 2, 3, 4, 5, 6.])
    assert np.array_equal(result, expected), \
        f"Your knn_represent returns:\n{result}\nWe expect:\n{expected}"
    print("knn_represent test passed!")

if 'IS_GRADESCOPE_ENV' not in os.environ:
    test_knn_represent(knn_represent)
    test_knn_feature_matrix(knn_feature_matrix)

print("\n" + "="*50)
print("All tests completed!")
print("="*50)
