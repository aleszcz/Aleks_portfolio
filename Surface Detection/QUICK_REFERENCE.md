# Quick Reference Guide

Fast reference for common commands and workflows.

## Initial Setup

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/vesuvius-surface-detection.git
cd vesuvius-surface-detection
./setup.sh

# Activate environment
source venv/bin/activate
```

## Data

```bash
# Download competition data
./scripts/download_data.sh

# Or manually
kaggle competitions download -c vesuvius-challenge-surface-detection -p data/raw
cd data/raw && unzip vesuvius-challenge-surface-detection.zip
```

## Volume Cartographer

```bash
# Pull Docker image
docker pull ghcr.io/scrollprize/villa/volume-cartographer:edge

# Run (Linux/Mac)
xhost +local:docker
docker run -it --rm \
  -v "$(pwd)/data:/data" \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  -e QT_QPA_PLATFORM=xcb \
  -e QT_X11_NO_MITSHM=1 \
  ghcr.io/scrollprize/villa/volume-cartographer:edge
```

## Training

```bash
# Basic training
python src/training/train.py --config configs/default_config.yaml

# With W&B logging
python src/training/train.py --config configs/default_config.yaml

# Custom parameters
python src/training/train.py \
  --config configs/default_config.yaml \
  --batch-size 2 \
  --epochs 50
```

## Jupyter

```bash
# Start Jupyter
jupyter notebook

# Or JupyterLab
jupyter lab

# Specific notebook
jupyter notebook notebooks/01_data_exploration.ipynb
```

## Monitoring

```bash
# TensorBoard
tensorboard --logdir logs/

# Check GPU usage
nvidia-smi
watch -n 1 nvidia-smi
```

## Inference & Submission

```bash
# Generate predictions
python scripts/prepare_submission.py \
  --test-dir data/raw/test \
  --model-path models/best_model.pth \
  --output data/submissions/submission_001.csv

# Submit to Kaggle
kaggle competitions submit \
  -c vesuvius-challenge-surface-detection \
  -f data/submissions/submission_001.csv \
  -m "Your message here"

# Check submissions
kaggle competitions submissions vesuvius-challenge-surface-detection
```

## Docker

```bash
# Build image
cd docker
docker-compose build

# Run development container
docker-compose up vesuvius-dev

# Run Jupyter in Docker
docker-compose up jupyter

# Run TensorBoard
docker-compose up tensorboard

# Stop all
docker-compose down
```

## Python Quick Scripts

### Check model

```python
import torch
checkpoint = torch.load('models/best_model.pth')
print(f"Epoch: {checkpoint['epoch']}")
print(f"Val Dice: {checkpoint['val_dice']:.4f}")
```

### Load and visualize data

```python
import zarr
import matplotlib.pyplot as plt

volume = zarr.open('data/raw/train/scroll_1/volume.zarr', 'r')
plt.imshow(volume[100, :, :], cmap='gray')
plt.show()
```

### Quick prediction

```python
from src.models.unet3d import UNet3D
import torch

model = UNet3D()
checkpoint = torch.load('models/best_model.pth')
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

# Predict
with torch.no_grad():
    output = model(input_volume)
    prediction = torch.sigmoid(output) > 0.5
```

## Git Commands

```bash
# Initial commit
git add .
git commit -m "Initial commit"
git push origin main

# Create branch
git checkout -b experiment/new-architecture

# Update
git add .
git commit -m "Improved model architecture"
git push
```

## Kaggle CLI

```bash
# List competitions
kaggle competitions list

# Competition info
kaggle competitions files vesuvius-challenge-surface-detection

# Download specific file
kaggle competitions download -c vesuvius-challenge-surface-detection -f train.zip

# Leaderboard
kaggle competitions leaderboard vesuvius-challenge-surface-detection

# Submissions
kaggle competitions submissions vesuvius-challenge-surface-detection
```

## Debugging

```bash
# Test model
python src/models/unet3d.py

# Test dataset
python src/data/dataset.py

# Test metrics
python src/utils/metrics.py

# Python debugger
python -m pdb src/training/train.py

# IPython debugger (in code)
import IPython; IPython.embed()
```

## Environment

```bash
# Export environment
pip freeze > requirements_current.txt

# Check installed packages
pip list

# Update package
pip install --upgrade torch

# Uninstall package
pip uninstall package_name
```

## Useful Aliases (add to ~/.bashrc)

```bash
alias va='source venv/bin/activate'
alias train='python src/training/train.py --config configs/default_config.yaml'
alias submit='python scripts/prepare_submission.py'
alias nb='jupyter notebook'
```

## File Locations

- **Data**: `data/raw/`, `data/processed/`
- **Models**: `models/`
- **Logs**: `logs/`
- **Submissions**: `data/submissions/`
- **Configs**: `configs/`
- **Notebooks**: `notebooks/`
- **Source**: `src/`

## Important Links

- Competition: https://www.kaggle.com/competitions/vesuvius-challenge-surface-detection
- Vesuvius Challenge: https://scrollprize.org
- Villa Repo: https://github.com/ScrollPrize/villa
- Documentation: See `docs/` folder

## Common Issues

**Out of memory**: Reduce batch size or patch size
**Slow training**: Check GPU is being used, reduce num_workers
**ImportError**: Check PYTHONPATH, activate venv
**Kaggle auth**: Check ~/.kaggle/kaggle.json permissions

## Tips

- Start with small experiments
- Always validate before submitting
- Keep track of experiments
- Save models regularly
- Read competition discussions
- Join Discord for help

---

For detailed guides, see:
- `docs/GETTING_STARTED.md`
- `docs/SUBMISSION_GUIDE.md`
- `README.md`
