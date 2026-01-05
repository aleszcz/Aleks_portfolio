"""
Generate sample word embeddings for the word relatedness task
"""

import numpy as np
import pandas as pd
import os

# Set random seed for reproducibility
np.random.seed(42)

# Load the development data to get vocabulary
dev_df = pd.read_csv('cs224-wordrelatedness-dev.csv')

# Extract all unique words
vocab = sorted(set(dev_df.word1) | set(dev_df.word2))
print(f"Vocabulary size: {len(vocab)}")

# Generate embeddings with some structure to make evaluation meaningful
# We'll use 50-dimensional vectors
dim = 50

# Create embeddings with some semantic structure
embeddings = {}

# Group semantically related words
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
    'nature': ['tree', 'forest', 'mountain', 'hill', 'ocean', 'water', 
               'grass', 'sky', 'sun', 'moon'],
}

# Generate base vectors for each group
group_vectors = {}
for group_name in semantic_groups:
    group_vectors[group_name] = np.random.randn(dim)

# Generate embeddings for each word
for word in vocab:
    # Check if word belongs to a semantic group
    group_found = None
    for group_name, group_words in semantic_groups.items():
        if word in group_words:
            group_found = group_name
            break
    
    if group_found:
        # Add group vector + noise
        base = group_vectors[group_found]
        noise = np.random.randn(dim) * 0.3
        embeddings[word] = base + noise
    else:
        # Random vector for words not in groups
        embeddings[word] = np.random.randn(dim)

# Create DataFrame
embedding_df = pd.DataFrame(embeddings).T
embedding_df.index.name = 'word'

# Save as CSV
print("Saving embeddings...")
output_dir = 'data/vsmdata'
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, 'giga_window5-scaled.csv.gz')
embedding_df.to_csv(output_path, compression='gzip')

print(f"Embeddings saved to {output_path}")
print(f"Shape: {embedding_df.shape}")
print("\nFirst few rows:")
print(embedding_df.head())
