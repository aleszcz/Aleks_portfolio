# QUICK REFERENCE: Vector Search Index for MongoDB Atlas

## 🎯 COPY THIS EXACT JSON

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

## 📝 CHECKLIST

- [ ] Go to MongoDB Atlas: https://cloud.mongodb.com/
- [ ] Click: Database → Browse Collections
- [ ] Find: `book_mongodb_chunks` → `chunked_data`
- [ ] Click: "Search Indexes" tab
- [ ] Click: "Create Search Index"
- [ ] Choose: "Atlas Vector Search" or "JSON Editor"
- [ ] Name: `vector_index` ⚠️ MUST BE EXACTLY THIS
- [ ] Paste: The JSON above
- [ ] Click: Create
- [ ] Wait: 1-3 minutes for "Active" status ⏳
- [ ] Test: Run your queries! 🎉

## ⚡ KEY POINTS

✅ Index name MUST be: `vector_index`
✅ Dimensions: `768` for HuggingFace, `1536` for OpenAI
✅ Type: `knnVector` (not just "vector")
✅ Include: `mappings` wrapper (required!)
✅ Wait: For "Active" status before querying

## 🔍 VERIFY IT WORKED

Run this in Colab after creating:

```python
from pymongo import MongoClient

MONGODB_URI = "your_connection_string"
client = MongoClient(MONGODB_URI)
db = client["book_mongodb_chunks"]
collection = db["chunked_data"]

indexes = list(collection.list_search_indexes())
for idx in indexes:
    if idx['name'] == 'vector_index':
        print(f"✅ vector_index: {idx.get('status')}")
```

Expected output:
```
✅ vector_index: READY
```

## 🎊 THEN RUN YOUR QUERIES

```python
ask_question("What is MongoDB?")
```

Should now show:
```
Found 3 relevant chunks: ✅
```

## 🆘 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Can't save without mappings | Use the JSON above with mappings |
| Dimensions error | Check: 768 for HuggingFace, 1536 for OpenAI |
| Index not found | Check name is exactly `vector_index` |
| Still 0 results | Wait for "Active" status (refresh page) |

---

**Created by Claude for your MongoDB RAG project** 🚀
