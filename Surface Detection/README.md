# Vesuvius Challenge - Surface Detection Competition

![Vesuvius Challenge](https://img.shields.io/badge/Prize-$100k-gold)
![Competition](https://img.shields.io/badge/Kaggle-Competition-blue)
![Deadline](https://img.shields.io/badge/Deadline-Feb%206%202026-red)

A comprehensive guide and toolkit for participating in the [Vesuvius Challenge Surface Detection Kaggle Competition](https://www.kaggle.com/competitions/vesuvius-challenge-surface-detection).

## 🎯 Competition Overview

**Goal**: Build a model to segment papyrus surfaces from 3D CT scans of ancient Herculaneum scrolls.

- **Prize Pool**: $100,000
- **Entry Deadline**: February 6, 2026
- **Task**: Detect papyrus surfaces inside 3D CT scans with topology-clean results (no gaps, holes, or sheet mergers)
- **Why it matters**: Better surface detection enables virtual unwrapping to read 2,000-year-old carbonized scrolls!

### What You'll Build

- **Input**: CT scan chunks (3D volumetric data)
- **Output**: Binary masks showing papyrus sheet positions
- **Scoring**: Topology-aware linear blend rewarding both voxel accuracy and surface connectivity

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Detailed Setup Guide](#detailed-setup-guide)
- [Project Structure](#project-structure)
- [Data](#data)
- [Development Workflow](#development-workflow)
- [Resources](#resources)
- [Contributing](#contributing)

## 🚀 Quick Start

```bash
# 1. Clone this repository
git clone https://github.com/YOUR_USERNAME/vesuvius-surface-detection.git
cd vesuvius-surface-detection

# 2. Create Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download competition data (requires Kaggle API setup)
kaggle competitions download -c vesuvius-challenge-surface-detection -p data/raw

# 5. Extract data
unzip data/raw/vesuvius-challenge-surface-detection.zip -d data/raw/

# 6. Run example notebook
jupyter notebook notebooks/01_data_exploration.ipynb
```

## 📚 Detailed Setup Guide

### Phase 1: Set Up Kaggle Account

1. **Create a Kaggle Account**
   - Go to [kaggle.com](https://www.kaggle.com)
   - Click "Register" and create an account
   - Verify your email address

2. **Join the Competition**
   - Visit the [competition page](https://www.kaggle.com/competitions/vesuvius-challenge-surface-detection)
   - Click "Join Competition"
   - Accept the competition rules
   - ⚠️ **Must join before February 6, 2026**

3. **Set Up Kaggle API**
   ```bash
   pip install kaggle
   ```
   
   - Go to [kaggle.com/settings](https://www.kaggle.com/settings)
   - Scroll to "API" section → "Create New Token"
   - Download `kaggle.json`
   - Place it in:
     - **Linux/Mac**: `~/.kaggle/kaggle.json`
     - **Windows**: `C:\Users\<YourUsername>\.kaggle\kaggle.json`
   - Set permissions (Linux/Mac): `chmod 600 ~/.kaggle/kaggle.json`

### Phase 2: Install Docker & Volume Cartographer

Volume Cartographer is essential for viewing and working with 3D CT scans.

#### Docker Installation

1. Download [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Install and start Docker Desktop

#### Pull Volume Cartographer Image

```bash
docker pull ghcr.io/scrollprize/villa/volume-cartographer:edge
```

#### Set Up X Server (for GUI)

**Linux**:
```bash
xhost +local:docker
```

**macOS**:
- Install [XQuartz](https://www.xquartz.org)
- Open XQuartz preferences → Security → Enable "Allow connections from network clients"
- Restart XQuartz

**Windows**:
- Install [VcXsrv](https://sourceforge.net/projects/vcxsrv/)
- Run XLaunch with default settings

#### Run Volume Cartographer

**Linux/macOS**:
```bash
xhost +local:docker
docker run -it --rm \
  -v "$(pwd)/data:/data" \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  -e QT_QPA_PLATFORM=xcb \
  -e QT_X11_NO_MITSHM=1 \
  ghcr.io/scrollprize/villa/volume-cartographer:edge
```

**Windows**:
```powershell
docker run -it --rm `
  -v "${PWD}/data:/data" `
  -e DISPLAY=host.docker.internal:0.0 `
  ghcr.io/scrollprize/villa/volume-cartographer:edge
```

### Phase 3: Development Environment

#### Python Dependencies

All required packages are in `requirements.txt`:

```bash
pip install -r requirements.txt
```

#### GPU Setup (Optional but Recommended)

For training deep learning models:

**PyTorch with CUDA**:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**TensorFlow with GPU**:
```bash
pip install tensorflow[and-cuda]
```

## 📁 Project Structure

```
vesuvius-surface-detection/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
├── LICENSE                  # MIT License
├── docker/                  # Docker configurations
│   ├── Dockerfile          # Custom Dockerfile
│   └── docker-compose.yml  # Docker Compose config
├── data/                    # Data directory (gitignored)
│   ├── raw/                # Raw competition data
│   ├── processed/          # Processed data
│   ├── submissions/        # Submission files
│   └── README.md           # Data documentation
├── notebooks/               # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_baseline_model.ipynb
│   └── 03_advanced_model.ipynb
├── src/                     # Source code
│   ├── __init__.py
│   ├── data/               # Data loading and processing
│   │   ├── __init__.py
│   │   ├── dataset.py
│   │   └── transforms.py
│   ├── models/             # Model architectures
│   │   ├── __init__.py
│   │   ├── unet3d.py
│   │   └── resnet3d.py
│   ├── training/           # Training scripts
│   │   ├── __init__.py
│   │   ├── train.py
│   │   └── validate.py
│   └── utils/              # Utility functions
│       ├── __init__.py
│       ├── metrics.py
│       └── visualization.py
├── scripts/                 # Utility scripts
│   ├── download_data.sh
│   ├── prepare_submission.py
│   └── convert_to_zarr.py
├── configs/                 # Configuration files
│   ├── default_config.yaml
│   └── training_config.yaml
├── tests/                   # Unit tests
│   └── test_dataset.py
└── docs/                    # Additional documentation
    ├── GETTING_STARTED.md
    ├── DATA_FORMAT.md
    └── SUBMISSION_GUIDE.md
```

## 📊 Data

### Understanding the Data Structure

The competition provides:
- **3D CT Scans**: Volumetric X-ray data of carbonized scrolls
- **Binary Masks**: Ground truth surface annotations
- **Format**: OME-Zarr or TIFF stacks

### Data Organization

```
data/raw/
├── train/
│   ├── scroll_1/
│   │   ├── volume.zarr/      # 3D CT scan
│   │   └── mask.zarr/         # Ground truth mask
│   ├── scroll_2/
│   └── ...
├── test/
│   └── ...
└── sample_submission.csv
```

### Loading Data

See `notebooks/01_data_exploration.ipynb` for examples of:
- Loading Zarr volumes
- Visualizing 3D data
- Understanding mask annotations
- Basic data statistics

## 🔬 Development Workflow

### 1. Data Exploration

```bash
jupyter notebook notebooks/01_data_exploration.ipynb
```

Explore the 3D CT scans and understand the data structure.

### 2. Baseline Model

Start with a simple 3D U-Net:

```bash
python src/training/train.py --config configs/baseline_config.yaml
```

### 3. Experiment Tracking

Use Weights & Biases or MLflow to track experiments:

```bash
wandb login
python src/training/train.py --use-wandb
```

### 4. Create Submission

```bash
python scripts/prepare_submission.py \
  --model-path models/best_model.pth \
  --output data/submissions/submission_001.csv
```

### 5. Submit to Kaggle

```bash
kaggle competitions submit \
  -c vesuvius-challenge-surface-detection \
  -f data/submissions/submission_001.csv \
  -m "First submission with baseline U-Net"
```

## 🎓 Model Development Tips

### Recommended Approaches

1. **3D U-Net Architecture**
   - Start with a standard 3D U-Net
   - Use residual connections
   - Try different depths (3-5 levels)

2. **Data Augmentation**
   - Random rotations
   - Random flips
   - Gaussian noise
   - Elastic deformations

3. **Loss Functions**
   - Dice Loss (for segmentation)
   - Binary Cross-Entropy
   - Focal Loss (for class imbalance)
   - Combination losses

4. **Training Strategies**
   - Start with smaller patches (64³ or 128³)
   - Use mixed precision training
   - Implement gradient accumulation for larger batches
   - Learning rate scheduling (CosineAnnealingLR)

### Example Training Command

```bash
python src/training/train.py \
  --batch-size 4 \
  --patch-size 128 \
  --epochs 100 \
  --lr 1e-4 \
  --model unet3d \
  --loss dice \
  --device cuda
```

## 📚 Resources

### Official Resources

- **Competition Page**: [Kaggle Competition](https://www.kaggle.com/competitions/vesuvius-challenge-surface-detection)
- **Vesuvius Challenge**: [scrollprize.org](https://scrollprize.org)
- **Villa Repository**: [GitHub - ScrollPrize/villa](https://github.com/ScrollPrize/villa)
- **Volume Cartographer**: [GitHub - volume-cartographer](https://github.com/ScrollPrize/villa/tree/main/volume-cartographer)
- **Segmentation Tutorial**: [scrollprize.org/segmentation](https://scrollprize.org/segmentation)

### Community

- **Discord**: Join the Vesuvius Challenge Discord for discussions
- **Kaggle Forums**: Check the competition's Discussion tab
- **Paper**: [Reading the Herculaneum Scrolls](https://arxiv.org/abs/2304.02084)

### Related Competitions

- [Vesuvius Challenge - Ink Detection](https://www.kaggle.com/competitions/vesuvius-challenge-ink-detection) (Previous competition)

### Useful Papers

- "U-Net: Convolutional Networks for Biomedical Image Segmentation"
- "3D U-Net: Learning Dense Volumetric Segmentation from Sparse Annotation"
- "nnU-Net: Self-adapting Framework for U-Net-Based Medical Image Segmentation"

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Vesuvius Challenge team for organizing this amazing competition
- EduceLab for developing Volume Cartographer
- The entire community of scroll enthusiasts and researchers

## 📞 Contact

- **Your Name**: [Your Email]
- **GitHub**: [@YourUsername](https://github.com/YourUsername)
- **Kaggle**: [Your Kaggle Profile](https://www.kaggle.com/yourusername)

---

**Happy scrolling! 📜🔍 Let's make history by reading ancient texts!**
