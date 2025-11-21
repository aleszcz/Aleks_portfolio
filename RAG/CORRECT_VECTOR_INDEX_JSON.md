# Correct Vector Search Index Configuration for MongoDB Atlas

## The Complete JSON You Need

MongoDB Atlas now requires the `mappings` field. Here's the COMPLETE configuration:

### For HuggingFace Embeddings (768 dimensions):

```json
{
  "mappings": {
    "dynamic": true,
    "fields": {
      "embedding": {
        "type": "knnVector",
        "dimensions": 768,
        "similarity": "cosine"
      }
    }
  }
}
```

### For OpenAI Embeddings (1536 dimensions):

```json
{
  "mappings": {
    "dynamic": true,
    "fields": {
      "embedding": {
        "type": "knnVector",
        "dimensions": 1536,
        "similarity": "cosine"
      }
    }
  }
}
```

### With Metadata Filtering (if you have hasCode, keywords, etc.):

```json
{
  "mappings": {
    "dynamic": true,
    "fields": {
      "embedding": {
        "type": "knnVector",
        "dimensions": 768,
        "similarity": "cosine"
      },
      "hasCode": {
        "type": "token"
      },
      "keywords": {
        "type": "token"
      }
    }
  }
}
```

## Step-by-Step Instructions

### Step 1: Go to MongoDB Atlas
1. Open: https://cloud.mongodb.com/
2. Navigate to: **Database** → **Browse Collections**
3. Find your database: `book_mongodb_chunks`
4. Find your collection: `chunked_data`

### Step 2: Create Search Index
1. Click the **"Search Indexes"** tab (at the top, next to "Indexes")
2. Click **"Create Search Index"** button

### Step 3: Choose Index Type
1. Select **"Atlas Vector Search"** (not "Atlas Search")
   - Or if you see "JSON Editor", choose that
2. Click **"Next"**

### Step 4: Configure Index
1. **Index Name**: `vector_index` (must be exactly this!)
2. **Database**: `book_mongodb_chunks` (should be pre-selected)
3. **Collection**: `chunked_data` (should be pre-selected)

### Step 5: Paste the JSON
Delete any default JSON and paste this (since you're using HuggingFace):

```json
{
  "mappings": {
    "dynamic": true,
    "fields": {
      "embedding": {
        "type": "knnVector",
        "dimensions": 768,
        "similarity": "cosine"
      }
    }
  }
}
```

### Step 6: Create and Wait
1. Click **"Next"** or **"Create Search Index"**
2. Review the configuration
3. Click **"Create Search Index"**
4. Wait 1-3 minutes for the status to change to **"Active"**

## Alternative: Using Atlas UI Wizard (Easier!)

If you see a visual editor instead of JSON:

1. Click **"Create Search Index"**
2. Choose **"Atlas Vector Search"**
3. Select **"JSON Editor"** at the top right (or follow visual editor)
4. If using visual editor:
   - **Field to Index**: `embedding`
   - **Data Type**: `knnVector`
   - **Dimensions**: `768` (for HuggingFace) or `1536` (for OpenAI)
   - **Similarity Function**: `cosine`
5. Click **"Create Search Index"**

## Verify the Index

After creating, run this in Colab to verify:

```python
from pymongo import MongoClient

MONGODB_URI = "mongodb+srv://aleszczucsd_db_user:kRKTnGA06CQcqbKD@clusterfree512mb.rmopras.mongodb.net/"

client = MongoClient(MONGODB_URI)
db = client["book_mongodb_chunks"]
collection = db["chunked_data"]

# List search indexes
indexes = list(collection.list_search_indexes())

print("Search Indexes:")
for idx in indexes:
    print(f"  Name: {idx['name']}")
    print(f"  Status: {idx.get('status', 'unknown')}")
    print(f"  Type: {idx.get('type', 'unknown')}")
    
    # Check if it's vector_index
    if idx['name'] == 'vector_index':
        status = idx.get('status', 'unknown')
        if status in ['READY', 'ACTIVE']:
            print("  ✅ Index is ready to use!")
        else:
            print(f"  ⏳ Index is still building... Status: {status}")
    print()

# Check if vector_index exists
if any(idx['name'] == 'vector_index' for idx in indexes):
    print("✅ vector_index found! You can now run queries.")
else:
    print("❌ vector_index not found. Please create it.")
```

## Common Issues

### Issue 1: "Dimensions must be specified"
**Solution**: Make sure you include the `dimensions` field in the JSON:
```json
"dimensions": 768
```

### Issue 2: "Invalid field type"
**Solution**: Use `knnVector` (not `vector`):
```json
"type": "knnVector"
```

### Issue 3: Can't find "Atlas Vector Search" option
**Solution**: 
- Your MongoDB Atlas version might be older
- Use the JSON Editor option instead
- Paste the complete JSON with mappings

### Issue 4: Index stays in "Building" status
**Solution**: 
- This is normal, wait 1-3 minutes
- Refresh the page to see updated status
- If it takes longer than 5 minutes, delete and recreate

## What Each Field Means

```json
{
  "mappings": {                    // Required wrapper
    "dynamic": true,               // Allow dynamic fields
    "fields": {                    // Define indexed fields
      "embedding": {               // Your vector field name
        "type": "knnVector",       // Vector search type
        "dimensions": 768,         // Number of dimensions
        "similarity": "cosine"     // Similarity function
      }
    }
  }
}
```

## After Creating the Index

Once the index status shows **"Active"**, run your queries again:

```python
# This should now work!
ask_question("What is MongoDB?")
```

You should now see results like:
```
Found 3 relevant chunks:

--- Result 1 ---
Content: MongoDB is a document database...
```

## Quick Reference

| Embedding Model | Dimensions | JSON to Use |
|----------------|-----------|-------------|
| HuggingFace (all-mpnet-base-v2) | 768 | Use `"dimensions": 768` |
| OpenAI (text-embedding-ada-002) | 1536 | Use `"dimensions": 1536` |
| OpenAI (text-embedding-3-small) | 1536 | Use `"dimensions": 1536` |
| OpenAI (text-embedding-3-large) | 3072 | Use `"dimensions": 3072` |

## Full Working Example for Your Setup

Since you're using HuggingFace embeddings (from the code), use this exact JSON:

```json
{
  "mappings": {
    "dynamic": true,
    "fields": {
      "embedding": {
        "type": "knnVector",
        "dimensions": 768,
        "similarity": "cosine"
      }
    }
  }
}
```

Index name: **`vector_index`** (exactly!)

That's it! Create the index with this JSON and your queries will work! 🚀
