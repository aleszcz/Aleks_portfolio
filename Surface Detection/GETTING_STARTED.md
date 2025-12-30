# Getting Started with Vesuvius Challenge

This guide will walk you through everything you need to start working on the Vesuvius Challenge Surface Detection competition.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Understanding the Competition](#understanding-the-competition)
4. [Working with the Data](#working-with-the-data)
5. [Your First Model](#your-first-model)
6. [Making a Submission](#making-a-submission)
7. [Tips and Best Practices](#tips-and-best-practices)

## Prerequisites

### Required Skills

- Basic Python programming
- Familiarity with PyTorch or TensorFlow
- Understanding of machine learning concepts
- Basic knowledge of image/volume processing

### Hardware Requirements

**Minimum**:
- 16GB RAM
- 50GB free disk space
- GPU with 8GB VRAM (recommended)

**Recommended**:
- 32GB+ RAM
- 200GB+ free disk space (SSD preferred)
- GPU with 16GB+ VRAM (RTX 3090, A100, etc.)

### Software Requirements

- Python 3.8+
- Docker (optional but recommended)
- Kaggle account
- Git

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/vesuvius-surface-detection.git
cd vesuvius-surface-detection
```

### 2. Set Up Python Environment

**Using venv**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Using conda**:
```bash
conda create -n vesuvius python=3.10
conda activate vesuvius
pip install -r requirements.txt
```

### 3. Set Up Kaggle API

1. Go to https://www.kaggle.com/settings
2. Click "Create New Token" in the API section
3. Download `kaggle.json`
4. Place it in `~/.kaggle/` (Linux/Mac) or `C:\Users\<YourUsername>\.kaggle\` (Windows)
5. Set permissions: `chmod 600 ~/.kaggle/kaggle.json`

### 4. Join the Competition

1. Visit https://www.kaggle.com/competitions/vesuvius-challenge-surface-detection
2. Click "Join Competition"
3. Accept the rules
4. **Remember**: Entry deadline is February 6, 2026!

## Understanding the Competition

### What are we trying to do?

You're helping to virtually unwrap 2,000-year-old scrolls from Herculaneum that were carbonized by Mount Vesuvius. The first step is detecting where the papyrus surface is in 3D CT scans.

### The Data

**Input**: 3D CT scans (volumetric X-ray data)
- Format: OME-Zarr or TIFF stacks
- Values: 8-bit or 16-bit grayscale
- Dimensions: Large volumes (several GB each)

**Output**: Binary masks
- Format: Same as input
- Values: 0 (background) or 1 (papyrus surface)
- Goal: Accurately mark where papyrus sheets are located

### Evaluation Metric

The competition uses a topology-aware metric that rewards:
- High voxel accuracy (correct predictions)
- Good surface connectivity (no gaps or holes)
- Avoiding sheet switches and mergers

## Working with the Data

### Download the Data

```bash
# Using the provided script
chmod +x scripts/download_data.sh
./scripts/download_data.sh

# Or manually
kaggle competitions download -c vesuvius-challenge-surface-detection -p data/raw
cd data/raw
unzip vesuvius-challenge-surface-detection.zip
```

### Explore the Data

Start with the exploration notebook:

```bash
jupyter notebook notebooks/01_data_exploration.ipynb
```

This will show you:
- How to load volumes
- How to visualize 3D data
- Data statistics and distributions
- Surface characteristics

### Volume Cartographer (Optional)

For advanced visualization:

```bash
# Pull Docker image
docker pull ghcr.io/scrollprize/villa/volume-cartographer:edge

# Run (Linux/Mac)
xhost +local:docker
docker run -it --rm \
  -v "$(pwd)/data:/data" \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  ghcr.io/scrollprize/villa/volume-cartographer:edge
```

## Your First Model

### 1. Prepare the Data

Create training patches from the full volumes:

```python
# In Python
from src.data.dataset import VesuviusDataset

dataset = VesuviusDataset(
    data_dir="data/raw/train",
    patch_size=(128, 128, 128),
    stride=(96, 96, 96)  # 32 voxel overlap
)
```

### 2. Train a Baseline Model

Start with a simple 3D U-Net:

```bash
python src/training/train.py --config configs/default_config.yaml
```

This will:
- Load the training data
- Train a 3D U-Net model
- Validate on held-out data
- Save the best model to `models/best_model.pth`

### 3. Monitor Training

**Using TensorBoard**:
```bash
tensorboard --logdir logs/
```

**Using Weights & Biases** (optional):
1. Create account at https://wandb.ai
2. Get API key
3. Edit config: set `use_wandb: true`
4. Run training

### 4. Evaluate Your Model

```python
# Load model and evaluate
from src.models.unet3d import UNet3D
import torch

model = UNet3D()
checkpoint = torch.load('models/best_model.pth')
model.load_state_dict(checkpoint['model_state_dict'])

print(f"Validation Dice: {checkpoint['val_dice']:.4f}")
```

## Making a Submission

### 1. Generate Predictions

```bash
python scripts/prepare_submission.py \
  --test-dir data/raw/test \
  --model-path models/best_model.pth \
  --output data/submissions/submission_001.csv
```

### 2. Submit to Kaggle

```bash
kaggle competitions submit \
  -c vesuvius-challenge-surface-detection \
  -f data/submissions/submission_001.csv \
  -m "Baseline 3D U-Net submission"
```

### 3. Check Leaderboard

1. Go to competition page
2. Click "My Submissions"
3. Wait for scoring (may take a few minutes)
4. View your position on the leaderboard!

## Tips and Best Practices

### Data Handling

1. **Start Small**: Use small patches (64³) initially, increase later
2. **Use SSD**: Store processed data on SSD for faster loading
3. **Zarr Format**: More efficient than TIFF for large volumes
4. **Data Augmentation**: Rotations, flips help a lot

### Model Development

1. **Start Simple**: 3D U-Net is a good baseline
2. **Watch Memory**: 3D models use a lot of GPU memory
3. **Mixed Precision**: Use `torch.cuda.amp` for faster training
4. **Batch Size**: Lower batch size, longer training

### Training

1. **Monitor Overfitting**: Watch validation metrics
2. **Early Stopping**: Stop if validation stops improving
3. **Learning Rate**: Start with 1e-4, adjust as needed
4. **Patience**: 3D training is slow, be patient!

### Debugging

1. **Visualize Predictions**: Always check what your model predicts
2. **Check Data Loading**: Verify inputs look correct
3. **Start on CPU**: Debug on CPU before using GPU
4. **Use Small Subset**: Test on 1-2 volumes first

### Competition Strategy

1. **Make Baseline First**: Get something working quickly
2. **Iterate Fast**: Small improvements add up
3. **Read Discussions**: Learn from other participants
4. **Share Ideas**: Community collaboration is encouraged
5. **Track Experiments**: Document what works and what doesn't

## Common Issues and Solutions

### Out of Memory

- Reduce batch size
- Reduce patch size
- Use gradient accumulation
- Use mixed precision training

### Slow Training

- Use smaller patches initially
- Reduce number of feature channels
- Use fewer workers for data loading
- Check if GPU is being used

### Poor Performance

- Check data loading (visualize inputs)
- Verify labels are correct
- Try different loss functions
- Increase model capacity
- Add data augmentation

## Next Steps

1. **Experiment**: Try different architectures
2. **Ensemble**: Combine multiple models
3. **Post-Processing**: Clean up predictions
4. **Join Discord**: Connect with community
5. **Read Papers**: Learn from related work

## Resources

- **Competition**: https://www.kaggle.com/competitions/vesuvius-challenge-surface-detection
- **Vesuvius Challenge**: https://scrollprize.org
- **Discord**: Join for community help
- **Papers**: Check competition discussion for references

## Getting Help

- **Kaggle Forums**: Ask in competition discussion
- **Discord**: Join Vesuvius Challenge Discord
- **GitHub Issues**: Report bugs or request features
- **Documentation**: Read the full docs in `docs/`

Good luck and happy scrolling! 📜🔍
