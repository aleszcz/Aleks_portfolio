# 🧬 GenoScope: AI-Powered Genomics Data Discovery

> Transform how you search for genomics data - use natural language instead of complex database queries

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NCBI E-utilities](https://img.shields.io/badge/NCBI-E--utilities-green.svg)](https://www.ncbi.nlm.nih.gov/books/NBK25501/)

## 🌟 What is GenoScope?

GenoScope is an AI-powered platform that makes finding genomics data as simple as asking a question. Instead of learning complex database syntax, just describe what you're looking for in plain English.

**Instead of this:**
```
Database: gds
Query: "breast cancer"[MeSH Terms] AND "Homo sapiens"[Organism] AND "Expression profiling by array"[DataSet Type]
```

**Just say this:**
```
"Find human breast cancer RNA-seq data"
```

## ✨ Key Features

- 🤖 **Natural Language Processing** - Ask questions in plain English
- 🔍 **Multi-Database Search** - Searches NCBI, GEO, SRA automatically
- 📊 **Smart Ranking** - Results sorted by relevance
- 🎯 **Intent Recognition** - Understands organisms, data types, and conditions
- 🔗 **Direct Downloads** - One-click access to datasets
- ⚡ **Fast & Efficient** - Optimized API usage with intelligent caching

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- NCBI API key (free - [get one here](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/genoscope.git
cd genoscope
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up your API key**
```bash
# Windows
set NCBI_API_KEY=your_api_key_here

# Linux/Mac
export NCBI_API_KEY=your_api_key_here
```

4. **Test the installation**
```bash
python test_ncbi.py
```

### Usage Examples

**Example 1: Search for datasets**
```bash
python src/genomics_query_agent.py
```

**Example 2: Use in your own code**
```python
from src.genomics_query_agent import GenomicsQueryAgent
import asyncio

async def search():
    agent = GenomicsQueryAgent()
    results = await agent.process_query("Find mouse Alzheimer studies")
    
    for result in results['results']:
        print(f"{result['accession']}: {result['title']}")
        print(f"Download: {result['download_url']}\n")

asyncio.run(search())
```

## 📚 Example Queries

GenoScope understands various types of queries:

```python
# Disease research
"Find breast cancer RNA-seq data in humans"
"Show me Alzheimer's disease gene expression studies"

# Organism-specific
"Mouse diabetes genomic data"
"Zebrafish heart development sequences"

# Data type specific
"COVID-19 protein sequences"
"Single cell RNA-seq for cancer research"
```

## 🏗️ Project Structure

```
genoscope/
├── src/
│   ├── ncbi_mcp_server.py        # MCP server for NCBI databases
│   └── genomics_query_agent.py   # AI agent for query processing
├── examples/
│   └── basic_search.py           # Example usage scripts
├── tests/
│   └── test_ncbi.py              # Test suite
├── requirements.txt              # Python dependencies
├── .env.template                 # Environment variables template
└── README.md                     # This file
```

## 🔧 How It Works

```
User Query → Intent Parser → Search Strategies → MCP Servers → NCBI/GEO APIs
                                                       ↓
User Results ← Result Formatter ← Relevance Ranking ← Raw Data
```

1. **Intent Parser**: Extracts organism, data type, and condition from natural language
2. **Search Strategies**: Generates optimized queries for different databases
3. **MCP Servers**: Standardized interface to NCBI E-utilities
4. **Relevance Ranking**: Scores results based on biological relevance
5. **Result Formatter**: Presents data in user-friendly format

## 🎯 Supported Databases

- **NCBI Nucleotide** - DNA/RNA sequences
- **NCBI Protein** - Protein sequences
- **GEO (Gene Expression Omnibus)** - Expression datasets
- **SRA (Sequence Read Archive)** - Raw sequencing data

## 📊 Use Cases

- **Researchers**: Find relevant datasets for literature reviews
- **Bioinformaticians**: Quick dataset discovery for analysis pipelines
- **Students**: Learn about available genomics data
- **Data Scientists**: Build training datasets for ML models

## 🛠️ Development Roadmap

- [x] Core MCP server for NCBI
- [x] Natural language query processing
- [x] Multi-database search
- [x] Relevance ranking
- [ ] Web interface (Streamlit)
- [ ] Local caching system
- [ ] Batch download functionality
- [ ] Advanced filtering options
- [ ] NVIDIA Jetson deployment (offline mode)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the My License - (ask#) file for details.

## 🙏 Acknowledgments

- **NCBI E-utilities** for providing comprehensive API access
- **Anthropic** for Claude and the Model Context Protocol (MCP)

## 📧 Contact

Your Name - [@www.linkedin.com/in/to-aleks-les](https://twitter.com/yourtwitter)

Project Link: [(https://github.com/aleszcz/Aleks_portfolio/edit/main/GenoScope_1)]

---

⭐ **Star this repository if you find it helpful!**

🧬 Built with passion for open science and AI-powered discovery
