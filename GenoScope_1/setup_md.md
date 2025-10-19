# GenoScope Setup Guide

Complete guide to setting up GenoScope on your system.

## 📋 Prerequisites

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **NCBI API Key** - [Get free API key](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)

## 🚀 Installation Steps

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/genoscope.git
cd genoscope
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

If you encounter any errors, try:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Get Your NCBI API Key

1. Go to: https://www.ncbi.nlm.nih.gov/account/
2. Sign in or create an account (free)
3. Go to Settings → API Key Management
4. Click "Create an API Key"
5. Copy your API key

### Step 5: Configure Environment Variables

**Option A: Set environment variable directly**

Windows:
```bash
set NCBI_API_KEY=your_api_key_here
```

Linux/Mac:
```bash
export NCBI_API_KEY=your_api_key_here
```

**Option B: Use .env file**

1. Copy the template:
```bash
cp .env.template .env
```

2. Edit `.env` and add your API key:
```
NCBI_API_KEY=your_api_key_here
```

### Step 6: Test Your Installation

```bash
python test_ncbi.py
```

You should see:
```
✅ API Key found: bf86122e...
✅ Connection successful!
```

## 🧪 Running Examples

### Basic Search
```bash
python examples/basic_search.py
```

### Query Agent
```bash
python src/genomics_query_agent.py
```

### MCP Server Test
```bash
python src/ncbi_mcp_server.py
```

## 🔧 Troubleshooting

### Issue: ModuleNotFoundError

**Solution:** Make sure you're in the project directory and have activated the virtual environment:
```bash
cd genoscope
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Issue: API Key Not Found

**Solution:** Set the environment variable:
```bash
# Check if it's set
echo $NCBI_API_KEY  # Linux/Mac
echo %NCBI_API_KEY%  # Windows

# Set it
export NCBI_API_KEY=your_key  # Linux/Mac
set NCBI_API_KEY=your_key     # Windows
```

### Issue: Connection Timeout

**Solution:** 
- Check your internet connection
- Verify NCBI services are online: https://www.ncbi.nlm.nih.gov/
- Try again in a few minutes

### Issue: Rate Limit Exceeded

**Solution:**
- Make sure your API key is set correctly
- Without an API key, you're limited to 3 requests/second
- With an API key, you get 10 requests/second

## 📊 Verify Everything Works

Run this quick test:

```python
python -c "import aiohttp, pandas, Bio; print('✅ All packages installed!')"
```

Then run:
```bash
python test_ncbi.py
```

If both succeed, you're ready to use GenoScope! 🎉

## 🆘 Still Having Issues?

1. Check [GitHub Issues](https://github.com/yourusername/genoscope/issues)
2. Create a new issue with:
   - Your Python version (`python --version`)
   - Your OS (Windows/Mac/Linux)
   - Error message
   - What you've tried

## 📚 Next Steps

Once setup is complete:
1. Read the [README.md](README.md) for usage examples
2. Try the examples in `examples/`
3. Check out [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
4. Build something amazing! 🚀
