# Quick Start Guide - Visual Workflow

## Option 1: Google Colab (EASIEST - START HERE!)

```
Step 1: Open Colab
├─→ Go to https://colab.research.google.com/
└─→ Create new notebook

Step 2: Copy Code
├─→ Open: RAG_with_MongoDB_Colab.py
└─→ Copy each "CELL" into a new cell in Colab

Step 3: Run Setup
├─→ Run CELL 1 (install packages) - takes 1-2 min
└─→ Wait for "✓ All packages installed!"

Step 4: Upload PDF
├─→ Run CELL 2
└─→ Click "Choose Files" and upload your PDF

Step 5: Configure MongoDB
├─→ Run CELL 3
├─→ Replace YOUR_USERNAME, YOUR_PASSWORD, YOUR_CLUSTER
└─→ Should see "✓ Successfully connected to MongoDB!"

Step 6: Process PDF
├─→ Run CELL 4
└─→ Wait 2-5 minutes (creates embeddings)
    │   Loading PDF...
    │   ✓ Loaded X pages
    │   ✓ Created X chunks
    │   Creating embeddings...
    │   ✓ SUCCESS!

Step 7: Create Vector Index
├─→ Read CELL 5 instructions
├─→ Go to MongoDB Atlas dashboard
├─→ Create vector search index (copy JSON from cell)
└─→ Wait ~1 minute for it to build

Step 8: Start Querying!
├─→ Run CELL 6 (setup)
├─→ Run CELL 7 (example queries)
└─→ See results! 🎉

Step 9 (Optional): Chat Interface
└─→ Run CELL 8 for interactive chat
```

## Option 2: Local Computer

```
Step 1: Setup Environment
├─→ Install Python 3.8+
├─→ Download all files
└─→ Open terminal in project folder

Step 2: Install Dependencies
├─→ Run: pip install -r requirements.txt
└─→ Wait for installation to complete

Step 3: Configure Credentials
├─→ Open key_param.py
├─→ Add MongoDB connection string
└─→ (Optional) Add OpenAI API key

Step 4: Prepare Data
├─→ Create folder: sample_files/
└─→ Put your PDF in: sample_files/mongodb.pdf

Step 5: Create Vector Index
├─→ Go to MongoDB Atlas
├─→ Create vector search index
└─→ Use JSON from README.md

Step 6: Load Data (ONE TIME ONLY)
├─→ Edit rag_with_mongodb_fixed.py
├─→ Uncomment: load_data_huggingface()
├─→ Run: python rag_with_mongodb_fixed.py
└─→ Wait for completion

Step 7: Query Data
├─→ Edit example_usage.py
├─→ Uncomment the query lines
├─→ Run: python example_usage.py
└─→ See results! 🎉
```

## Decision Tree: Which Option Should You Choose?

```
START HERE
    ↓
Do you want the EASIEST setup?
    ├─ YES → Use Colab
    └─ NO  → Continue
          ↓
    Is your data sensitive/private?
          ├─ YES → Use Local Computer
          └─ NO  → Continue
                ↓
          Do you have a powerful GPU?
                ├─ YES → Use Local Computer
                ├─ NO  → Use Colab (free GPU!)
                └─ MAYBE → Use Colab to test first

RECOMMENDATION: Start with Colab, move to local later if needed
```

## HuggingFace vs OpenAI - Which Embeddings?

```
START HERE
    ↓
Do you want it FREE?
    ├─ YES → Use HuggingFace
    └─ NO  → Continue
          ↓
    Do you need metadata filtering?
    (e.g., filter by hasCode, keywords)
          ├─ YES → Use OpenAI
          └─ NO  → Continue
                ↓
          Is speed critical?
                ├─ YES → Use OpenAI
                └─ NO  → Use HuggingFace

RECOMMENDATION: 
- Testing/Learning → HuggingFace (free)
- Production/Advanced → OpenAI (better features)
```

## Typical First-Time Experience

### Timeline for Colab:
```
00:00 - Open Colab and create notebook
00:05 - Copy code cells
00:10 - Install packages (CELL 1)
00:12 - Upload PDF (CELL 2)
00:15 - Configure MongoDB (CELL 3)
00:20 - Process PDF & create embeddings (CELL 4)
00:25 - Create vector index in Atlas (CELL 5)
00:30 - First successful query! 🎉

Total: ~30 minutes for first time
```

### Timeline for Local:
```
00:00 - Download files
00:05 - Install Python packages
00:10 - Configure credentials
00:15 - Prepare PDF file
00:20 - Create vector index
00:25 - Load data (first time)
00:30 - First successful query! 🎉

Total: ~30 minutes for first time
```

## What Success Looks Like

### When Loading Data:
```
✓ Loaded 156 pages
✓ 143 pages after cleaning
✓ Created 412 chunks
✓ Embedding model loaded
✓ SUCCESS! Loaded 412 chunks into MongoDB!
```

### When Querying:
```
Question: What is MongoDB?
============================================================
Found 3 relevant chunks:

--- Result 1 ---
Content: MongoDB is a document database designed for ease 
of application development and scaling...
Source: Page 5

--- Result 2 ---
Content: MongoDB stores data in flexible, JSON-like 
documents...
Source: Page 12
```

## Common First-Time Mistakes

❌ Forgot to create vector search index
   → Solution: Check CELL 5 / README.md

❌ Wrong dimensions in vector index
   → Solution: Use 768 for HuggingFace, 1536 for OpenAI

❌ MongoDB connection fails
   → Solution: Check connection string, whitelist your IP

❌ Ran query before loading data
   → Solution: Must run load_data_*() function first

❌ PDF file not found
   → Solution: Check file path, create sample_files/ folder

## Getting Help

If stuck, check in this order:
1. ✅ README.md - Comprehensive guide
2. ✅ SUMMARY.md - Overview and fixes
3. ✅ This file - Quick visual guide
4. ✅ Error message - Usually explains the issue
5. ✅ MongoDB Atlas logs - Check for index/connection issues

## Ready to Start?

Recommended path:
1. Read SUMMARY.md (5 minutes)
2. Follow this Quick Start Guide with Colab (30 minutes)
3. Experiment and learn (1-2 hours)
4. Read full README.md when ready to move to local

Good luck! 🚀
