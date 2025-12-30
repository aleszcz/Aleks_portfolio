#!/bin/bash
# Script to download competition data from Kaggle

echo "============================================"
echo "Vesuvius Challenge - Data Download Script"
echo "============================================"
echo ""

# Check if kaggle is installed
if ! command -v kaggle &> /dev/null
then
    echo "Error: Kaggle CLI not found. Please install it first:"
    echo "  pip install kaggle"
    exit 1
fi

# Check if kaggle.json exists
if [ ! -f ~/.kaggle/kaggle.json ]; then
    echo "Error: Kaggle API credentials not found!"
    echo ""
    echo "Please follow these steps:"
    echo "1. Go to https://www.kaggle.com/settings"
    echo "2. Scroll to 'API' section"
    echo "3. Click 'Create New Token'"
    echo "4. Place kaggle.json in ~/.kaggle/"
    echo "5. Run: chmod 600 ~/.kaggle/kaggle.json"
    exit 1
fi

# Create data directory
echo "Creating data directories..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/submissions

# Download competition data
echo ""
echo "Downloading competition data..."
echo "This may take a while depending on your internet connection..."
echo ""

kaggle competitions download -c vesuvius-challenge-surface-detection -p data/raw

# Check if download was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "Download completed successfully!"
    echo ""
    echo "Extracting files..."
    
    # Extract zip file
    cd data/raw
    unzip -q vesuvius-challenge-surface-detection.zip
    
    # Remove zip file to save space (optional)
    read -p "Do you want to delete the zip file to save space? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        rm vesuvius-challenge-surface-detection.zip
        echo "Zip file deleted."
    fi
    
    cd ../..
    
    echo ""
    echo "============================================"
    echo "Data download completed!"
    echo "============================================"
    echo ""
    echo "Data location: data/raw/"
    echo ""
    echo "Next steps:"
    echo "1. Explore the data: jupyter notebook notebooks/01_data_exploration.ipynb"
    echo "2. Process the data: python scripts/create_patches.py"
    echo "3. Start training: python src/training/train.py"
    echo ""
else
    echo ""
    echo "Error: Download failed!"
    echo "Please check your internet connection and Kaggle credentials."
    exit 1
fi
