# CS224 Natural Language Understanding - Word Relatedness

## Overview

This project implements word relatedness and word similarity evaluation using Vector Space Models (VSMs). These are standard benchmarks used to evaluate distributed word representations by comparing model-derived distances with human judgments.

## Key Concepts

### Word Relatedness vs Word Similarity
- **Similarity**: How alike two words are (e.g., car–automobile)
- **Relatedness**: Broader semantic association (e.g., car–road)

### Evaluation Protocol
Performance is measured using the **Pearson correlation coefficient** between:
1. Human-annotated scores
2. Model-computed distances or similarities for each word pair

## Project Structure

```
.
├── cs224_nl_und_wordrelatendess.py    # Main implementation
├── utils.py                            # Utility functions
├── vsm.py                              # Vector Space Model classes
├── data/
│   ├── worrelatnedness/
│   │   └── cs224-wordrelatedness-dev.csv
│   └── vsmdata/
│       ├── yelp_window-scaled.csv.gz
│       └── giga_window20-flat.csv.gz
└── README.md
```

## Installation

```bash
pip install numpy pandas scipy scikit-learn transformers
```

## Usage

### Basic Usage

```python
import pandas as pd
import vsm
import utils

# Load data
dev_df = pd.read_csv('data/worrelatnedness/cs224-wordrelatedness-dev.csv')

# Run evaluation
vsm_df = pd.read_csv('data/vsmdata/yelp_window-scaled.csv.gz', index_col=0)
pred_df, rho = vsm.word_relatedness_evaluation(dev_df, vsm_df)

print(f"Spearman correlation: {rho:.3f}")
```

## Implemented Baselines

### 1. Random Baseline
Creates random vectors for vocabulary words and evaluates similarity.

```python
random_baseline_df = pd.read_csv('data/vsmdata/yelp_window-scaled.csv.gz', index_col=0)
pred_df, rho = vsm.word_relatedness_evaluation(dev_df, random_baseline_df)
```

### 2. Count-based Baseline
Uses co-occurrence counts within a window to create word vectors.

```python
count_baseline_df = pd.read_csv('data/vsmdata/yelp_window-scaled.csv.gz', index_col=0)
pred_df, rho = vsm.word_relatedness_evaluation(dev_df, count_baseline_df)
```

### 3. PPMI Baseline
Applies Positive Pointwise Mutual Information reweighting.

```python
def run_giga_ppmi_baseline():
    giga_df = pd.read_csv('data/vsmdata/giga_window20-flat.csv.gz', index_col=0)
    ppmi_df = vsm.ppmi(giga_df)
    return vsm.word_relatedness_evaluation(dev_df, ppmi_df)
```

### 4. PPMI + LSA Pipeline
Combines PPMI with Latent Semantic Analysis for dimensionality reduction.

```python
def run_ppmi_lsa_pipeline(count_df, k):
    ppmi_df = vsm.ppmi(count_df)
    lsa_df = vsm.lsa(ppmi_df, k=k)
    return vsm.word_relatedness_evaluation(dev_df, lsa_df)
```

### 5. T-test Reweighting
Applies statistical t-test transformation to count matrices.

```python
def ttest(df):
    col_means = df.mean(axis=0)
    col_stds = df.std(axis=0)
    result = df.copy()
    for col in df.columns:
        if col_stds[col] != 0:
            result[col] = (df[col] - col_means[col]) / col_stds[col]
    return result
```

## Advanced Methods

### Pooled BERT Representations
Derives static vector representations from BERT's contextual representations.

```python
from transformers import BertModel, BertTokenizer

def evaluate_pooled_bert(rel_df, layer, pool_func):
    bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    bert_model = BertModel.from_pretrained('bert-base-uncased')
    vocab = set(rel_df.word1.values) | set(rel_df.word2.values)
    vsm_df = vsm.create_subword_pooling_vsm(vocab, bert_model, bert_tokenizer, layer, pool_func)
    return vsm.word_relatedness_evaluation(rel_df, vsm_df)
```

### Learned Distance Functions (KNN)
Uses K-Nearest Neighbors regression to learn distance functions.

```python
from sklearn.neighbors import KNeighborsRegressor

def run_knn_score_model(vsm_df, dev_df, test_size=0.20):
    X = knn_feature_matrix(vsm_df, dev_df)
    y = dev_df['score'].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
    model = KNeighborsRegressor()
    model.fit(X_train, y_train)
    return model.score(X_test, y_test)
```

## Evaluation Metrics

### Spearman Correlation
Primary metric for evaluation - measures monotonic relationship between model predictions and human scores.

### Error Analysis
```python
def error_analysis(pred_df):
    pred_df['relatedness_rank'] = _normalized_ranking(pred_df['score'])
    pred_df['score_rank'] = _normalized_ranking(pred_df['predicted'])
    pred_df['error'] = abs(pred_df['relatedness_rank'] - pred_df['score_rank'])
    return pred_df
```

## Data Format

### Input CSV Format
```csv
word1,word2,score
computer,keyboard,8.5
car,automobile,9.0
book,paper,6.5
```

- **word1**: First word in the pair
- **word2**: Second word in the pair
- **score**: Human-annotated relatedness score (typically 0-10)

### Count Matrix Format
Compressed CSV files (`.csv.gz`) with:
- Rows: Words in vocabulary
- Columns: Words in vocabulary
- Values: Co-occurrence counts

## Testing

All functions include test cases to verify correct implementation:

```python
if 'IS_GRADESCOPE_ENV' not in os.environ:
    test_run_giga_ppmi_baseline(run_giga_ppmi_baseline)
    test_run_ppmi_lsa_pipeline(run_ppmi_lsa_pipeline)
    test_ttest_implementation(ttest)
    test_knn_represent(knn_represent)
    test_knn_feature_matrix(knn_feature_matrix)
```

## References

- Bommasani et al. 2020 - Contextual word representations
- CS224U Stanford NLP course materials
- Vector Space Models notebook: https://github.com/cgpotts/cs224u/

## License

This code is for educational purposes as part of CS224U coursework.
