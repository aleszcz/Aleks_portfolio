# Word Relatedness Evaluation - CS224 NLP

This project evaluates word embeddings using word relatedness benchmarks. It compares model-computed similarities with human judgments using Spearman correlation.

## Overview

Word relatedness evaluation is a standard benchmark for assessing distributed word representations (word embeddings). The task:

1. **Input**: Word pairs with human-annotated relatedness scores
2. **Process**: Compute vector similarities using a word embedding model
3. **Evaluation**: Measure correlation between model scores and human judgments

**Key Metrics:**
- **Spearman's ρ (rho)**: Primary evaluation metric (correlation coefficient)
- Higher ρ indicates better alignment with human judgments

## Project Structure

```
.
├── utils.py                           # Utility functions (similarity, evaluation)
├── vsm.py                            # Vector Space Model implementation
├── colab_setup_and_run.py           # Complete setup script for Colab
├── generate_embeddings.py           # Generate sample embeddings
├── data/
│   ├── wordrelatedness/
│   │   └── cs224-wordrelatedness-dev.csv   # Word pairs + scores
│   └── vsmdata/
│       └── giga_window5-scaled.csv.gz      # Word embeddings
```

## Quick Start (Google Colab)

### Option 1: All-in-One Setup Script

The easiest way to run this in Google Colab:

```python
# Run this single script - it sets up everything and runs evaluation
!wget https://raw.githubusercontent.com/YOUR_REPO/colab_setup_and_run.py
!python colab_setup_and_run.py
```

Or copy-paste the entire contents of `colab_setup_and_run.py` into a Colab cell and run it.

### Option 2: Step-by-Step Setup

**1. Upload files to Colab:**

```python
from google.colab import files

# Upload utils.py
uploaded = files.upload()

# Upload vsm.py
uploaded = files.upload()
```

**2. Create data files:**

```python
# Create directory structure
!mkdir -p data/wordrelatedness data/vsmdata

# Upload your CSV files or use the generation script
!python generate_embeddings.py
```

**3. Run evaluation:**

```python
import pandas as pd
import vsm
import utils

utils.fix_random_seeds()

# Load data
dev_df = pd.read_csv('data/wordrelatedness/cs224-wordrelatedness-dev.csv')
embeddings = pd.read_csv('data/vsmdata/giga_window5-scaled.csv.gz', index_col=0)

# Evaluate
pred_df, rho = vsm.word_relatedness_evaluation(dev_df, embeddings)
print(f"Spearman ρ = {rho:.4f}")
```

## Data Format

### Word Relatedness CSV
Format: `word1,word2,score`

```csv
word1,word2,score
car,automobile,9.2
dog,cat,7.5
book,library,8.1
```

**Columns:**
- `word1`, `word2`: Word pair
- `score`: Human relatedness score (higher = more related)

### Word Embeddings CSV
Format: Words as row index, dimensions as columns

```csv
word,dim0,dim1,dim2,...
car,0.123,-0.456,0.789,...
dog,-0.234,0.567,-0.890,...
```

## Key Functions

### `vsm.word_relatedness_evaluation()`

Main evaluation function.

**Parameters:**
- `relatedness_data` (pd.DataFrame): Word pairs with scores
- `vsm_df` (pd.DataFrame): Word embeddings (words as index)
- `distfunc` (function, optional): Distance function (default: negative cosine)

**Returns:**
- `pred_df` (pd.DataFrame): Predictions with original data
- `rho` (float): Spearman correlation coefficient

**Example:**
```python
pred_df, rho = vsm.word_relatedness_evaluation(dev_df, embeddings_df)
```

### `utils.cosine_similarity()`

Compute cosine similarity between vectors.

**Parameters:**
- `v1`, `v2` (np.array): Input vectors

**Returns:**
- `float`: Cosine similarity in [-1, 1]

### `vsm.random_baseline()`

Create random baseline model.

**Parameters:**
- `vocab` (iterable): Vocabulary words
- `dim` (int): Vector dimensionality
- `seed` (int): Random seed

**Returns:**
- `VSM`: Random baseline model

## Example Usage

### Basic Evaluation

```python
import pandas as pd
import vsm
import utils

# Load data
dev_df = pd.read_csv('data/wordrelatedness/cs224-wordrelatedness-dev.csv')
embeddings = pd.read_csv('data/vsmdata/giga_window5-scaled.csv.gz', index_col=0)

# Evaluate
pred_df, rho = vsm.word_relatedness_evaluation(dev_df, embeddings)

print(f"Spearman ρ: {rho:.4f}")
print("\nSample predictions:")
print(pred_df[['word1', 'word2', 'score', 'prediction']].head())
```

### Custom Distance Function

```python
def custom_distance(v1, v2):
    """Custom distance function"""
    # Return negative Euclidean distance
    return -np.linalg.norm(v1 - v2)

pred_df, rho = vsm.word_relatedness_evaluation(
    dev_df, embeddings, distfunc=custom_distance
)
```

### Error Analysis

```python
def error_analysis(pred_df):
    """Find worst predictions"""
    pred_df = pred_df.copy()
    
    # Normalize rankings
    pred_df['pred_rank'] = pred_df.prediction.rank() / len(pred_df)
    pred_df['gold_rank'] = pred_df.score.rank() / len(pred_df)
    pred_df['error'] = abs(pred_df['pred_rank'] - pred_df['gold_rank'])
    
    return pred_df.sort_values('error', ascending=False)

errors = error_analysis(pred_df)
print("Worst predictions:")
print(errors[['word1', 'word2', 'score', 'prediction', 'error']].head())
```

### Compare Multiple Models

```python
models = {
    'random': vsm.random_baseline(vocab, dim=50),
    'glove': load_glove_embeddings('glove.txt'),
    'custom': your_custom_embeddings
}

for name, model_df in models.items():
    _, rho = vsm.word_relatedness_evaluation(dev_df, model_df)
    print(f"{name:15s} ρ = {rho:.4f}")
```

## Interpreting Results

**Spearman ρ ranges from -1 to 1:**

- **ρ > 0.5**: Good correlation with human judgments
- **ρ = 0.3-0.5**: Moderate correlation
- **ρ < 0.3**: Weak correlation
- **ρ ≈ 0**: Random baseline performance
- **ρ < 0**: Negative correlation (unusual, suggests errors)

**Typical benchmark scores:**
- Random baseline: ρ ≈ 0.0 to 0.1
- Count-based models: ρ ≈ 0.3 to 0.5
- GloVe/Word2Vec: ρ ≈ 0.5 to 0.7
- Contextualized models: ρ ≈ 0.6 to 0.8

## Troubleshooting

### Issue: "VSM missing X words"

**Cause:** Embedding vocabulary doesn't cover all words in evaluation data.

**Solution:**
```python
# Check vocabulary coverage
eval_vocab = set(dev_df.word1) | set(dev_df.word2)
embed_vocab = set(embeddings.index)
missing = eval_vocab - embed_vocab

print(f"Missing words: {missing}")

# Option 1: Add random vectors for missing words
for word in missing:
    embeddings.loc[word] = np.random.randn(embeddings.shape[1])

# Option 2: Filter evaluation data
dev_df_filtered = dev_df[
    dev_df.word1.isin(embed_vocab) & dev_df.word2.isin(embed_vocab)
]
```

### Issue: Very low correlation (ρ < 0.1)

**Possible causes:**
1. Random embeddings (expected for random baseline)
2. Distance function reversed (should return small values for similar words)
3. Embeddings not loaded correctly

**Debug:**
```python
# Check a few similarity scores manually
w1, w2 = 'car', 'automobile'  # Should be similar
v1, v2 = embeddings.loc[w1], embeddings.loc[w2]

print(f"Cosine similarity: {utils.cosine_similarity(v1, v2):.3f}")
# Should be positive and relatively high for similar words
```

### Issue: Import errors in Colab

**Solution:**
```python
# Make sure files are in the current directory
!ls -la

# If files are missing, re-upload them
from google.colab import files
uploaded = files.upload()
```

## References

- **Spearman's Rank Correlation**: Non-parametric measure of rank correlation
- **Cosine Similarity**: Measures angle between vectors (not magnitude)
- **Word Relatedness vs Similarity**: 
  - Similarity: How alike (car ↔ automobile)
  - Relatedness: Broader association (car ↔ road)

## Tips for Best Results

1. **Normalize embeddings**: Improves cosine similarity computation
   ```python
   from sklearn.preprocessing import normalize
   embeddings_norm = normalize(embeddings, axis=1)
   ```

2. **Use appropriate distance metric**: 
   - Cosine for direction-based similarity
   - Euclidean for magnitude-based distance

3. **Check vocabulary coverage**: Ensure all evaluation words have embeddings

4. **Set random seeds**: For reproducible results

5. **Visualize score distributions**: Understand data before evaluation

## License

This is educational code for CS224 NLP course.
