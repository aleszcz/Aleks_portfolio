#!/bin/bash
# Setup script for Vesuvius Surface Detection project

set -e  # Exit on error

echo "============================================"
echo "Vesuvius Challenge - Setup Script"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check Python version
print_status "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then 
    print_status "Python $PYTHON_VERSION found"
else
    print_error "Python $REQUIRED_VERSION or higher is required"
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        print_status "Removed existing virtual environment"
    fi
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null

# Install requirements
print_status "Installing Python dependencies..."
echo "This may take several minutes..."
pip install -r requirements.txt

# Check if PyTorch is installed with GPU support
print_status "Checking PyTorch installation..."
python3 -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"

if python3 -c "import torch; exit(0 if torch.cuda.is_available() else 1)"; then
    print_status "PyTorch with CUDA support detected"
else
    print_warning "PyTorch without CUDA detected (CPU only)"
    read -p "Do you want to install PyTorch with CUDA 11.8? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installing PyTorch with CUDA 11.8..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
        print_status "PyTorch with CUDA installed"
    fi
fi

# Create necessary directories
print_status "Creating project directories..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/submissions
mkdir -p models
mkdir -p logs
mkdir -p notebooks
print_status "Directories created"

# Check for Kaggle API
print_status "Checking Kaggle API setup..."
if command -v kaggle &> /dev/null; then
    print_status "Kaggle CLI found"
    
    if [ -f ~/.kaggle/kaggle.json ]; then
        print_status "Kaggle credentials found"
    else
        print_warning "Kaggle credentials not found"
        echo ""
        echo "To set up Kaggle API:"
        echo "1. Go to https://www.kaggle.com/settings"
        echo "2. Click 'Create New Token' in the API section"
        echo "3. Place kaggle.json in ~/.kaggle/"
        echo "4. Run: chmod 600 ~/.kaggle/kaggle.json"
        echo ""
    fi
else
    print_warning "Kaggle CLI not found (already included in requirements)"
fi

# Check for Docker
print_status "Checking Docker..."
if command -v docker &> /dev/null; then
    print_status "Docker found: $(docker --version)"
else
    print_warning "Docker not found (optional, but recommended)"
    echo "Install from: https://www.docker.com/products/docker-desktop"
fi

# Make scripts executable
print_status "Making scripts executable..."
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x scripts/*.py 2>/dev/null || true

echo ""
echo "============================================"
echo -e "${GREEN}Setup completed successfully!${NC}"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Activate the environment: source venv/bin/activate"
echo "2. Set up Kaggle credentials (if not done)"
echo "3. Download data: ./scripts/download_data.sh"
echo "4. Explore data: jupyter notebook notebooks/01_data_exploration.ipynb"
echo "5. Train model: python src/training/train.py --config configs/default_config.yaml"
echo ""
echo "For more information, see: docs/GETTING_STARTED.md"
echo ""
