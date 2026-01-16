# Quick Start Guide

Get RevitAssist up and running in 15 minutes!

## Prerequisites

- **Revit**: 2020-2024
- **Python**: 3.8 or higher
- **GPU**: NVIDIA GPU with CUDA (recommended)
- **Git**: For cloning the repository

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/RevitAssist.git
cd RevitAssist
```

### Step 2: Set Up Python Backend

```bash
# Create virtual environment
cd AIBackend
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download pretrained models (placeholder - you'll need to train or obtain these)
python download_models.py
```

### Step 3: Build Revit Plugin

```bash
# Open in Visual Studio
cd ../RevitPlugin
start RevitAssist.sln

# Build solution (or use command line)
dotnet build --configuration Release
```

### Step 4: Install Plugin in Revit

```bash
# Copy built files to Revit addins folder
# Windows:
copy bin\Release\*.dll "%APPDATA%\Autodesk\Revit\Addins\2024\"
copy RevitAssist.addin "%APPDATA%\Autodesk\Revit\Addins\2024\"
```

## First Use

### 1. Start the AI Backend

```bash
cd AIBackend
python app.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Models loaded successfully!
```

### 2. Open Revit

1. Launch Autodesk Revit
2. Create or open a project
3. Look for "RevitAssist" tab in the ribbon

### 3. Import Your First Drawing

1. Click **"Import Drawing"**
2. Select an HVAC PDF or image
3. Choose drawing type: "HVAC Plan"
4. Select target level (e.g., "Level 1")
5. Click **"Next"**

### 4. Process with AI

1. Click **"Process with AI"**
2. Wait 2-5 minutes while AI analyzes the drawing
3. Review the results when complete

### 5. Review & Insert

1. Click **"Review & Edit"** to inspect detected components
2. Fix any misclassifications if needed
3. Click **"Insert to Model"** to create Revit elements

## Testing Without Training Data

If you don't have trained models yet, you can test with a simple demo:

```bash
# Use demo mode (returns mock data)
cd AIBackend
python app.py --demo
```

This will return simulated detections for testing the plugin UI.

## Training Your Own Model

If you have annotated HVAC drawings:

```bash
# Prepare your dataset in YOLO format
cd Training
python prepare_dataset.py --input ./raw_data --output ./data/hvac

# Train YOLOv9
python train_yolo.py --data ./data/hvac.yaml --epochs 100 --batch 16

# Copy trained weights
copy runs/train/hvac_yolov9/weights/best.pt ../AIBackend/models/weights/yolov9_hvac.pt
```

## Troubleshooting

### Plugin Not Showing in Revit

1. Check Revit version matches (2020-2024)
2. Verify files are in correct folder:
   ```
   %APPDATA%\Autodesk\Revit\Addins\2024\
   ```
3. Check Revit Addins Manager for errors

### AI Backend Won't Start

1. Verify Python version: `python --version` (should be 3.8+)
2. Check CUDA installation if using GPU: `nvidia-smi`
3. Try CPU mode: Edit `config.yaml`, set `DEVICE: "cpu"`

### "Models Not Found" Error

Download pretrained models or train your own:
```bash
cd AIBackend
# Option 1: Download (when available)
python download_models.py

# Option 2: Train your own
cd ../Training
python train_yolo.py --data ./data/hvac.yaml
```

### Low Detection Accuracy

1. Ensure drawing quality is good (300+ DPI)
2. Try "High Accuracy" processing mode
3. Fine-tune model on your specific drawing style

## Next Steps

- Read the [full documentation](docs/)
- Check out [example workflows](examples/)
- Join the [community discussions](https://github.com/yourusername/RevitAssist/discussions)
- Report [issues](https://github.com/yourusername/RevitAssist/issues)

## Getting Help

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/RevitAssist/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/RevitAssist/discussions)
- **Email**: your.email@example.com

---

Happy automating! 🚀
