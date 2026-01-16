"""
Training Script for YOLOv9 HVAC Component Detector

Usage:
    python train_yolo.py --data ./data/hvac.yaml --epochs 100

Requirements:
    - Annotated dataset in YOLO format
    - Data YAML configuration file
"""

import argparse
from pathlib import Path
from ultralytics import YOLO
import yaml


def train_yolo(
    data_yaml: str,
    epochs: int = 100,
    batch_size: int = 16,
    img_size: int = 1280,
    pretrained: str = "yolov9e.pt",
    device: str = "0"
):
    """
    Train YOLOv9 model on HVAC dataset
    
    Args:
        data_yaml: Path to data configuration YAML
        epochs: Number of training epochs
        batch_size: Batch size for training
        img_size: Input image size
        pretrained: Pretrained weights to start from
        device: GPU device ID (0, 1, etc.) or "cpu"
    """
    print("=" * 80)
    print("RevitAssist - YOLOv9 HVAC Training")
    print("=" * 80)
    
    # Load model
    print(f"\nLoading YOLOv9 model: {pretrained}")
    model = YOLO(pretrained)
    
    # Verify data configuration
    with open(data_yaml, 'r') as f:
        data_config = yaml.safe_load(f)
    
    print(f"\nDataset: {data_config.get('path', 'Not specified')}")
    print(f"Classes: {len(data_config.get('names', []))}")
    print(f"  - {', '.join(data_config.get('names', []))}")
    
    # Training arguments
    train_args = {
        'data': data_yaml,
        'epochs': epochs,
        'batch': batch_size,
        'imgsz': img_size,
        'device': device,
        'workers': 8,
        'patience': 20,
        'save': True,
        'save_period': 10,
        'cache': True,
        'project': 'runs/train',
        'name': 'hvac_yolov9',
        'exist_ok': True,
        
        # Optimization
        'optimizer': 'AdamW',
        'lr0': 0.001,
        'lrf': 0.01,
        'momentum': 0.9,
        'weight_decay': 0.0005,
        
        # Augmentation
        'hsv_h': 0.015,
        'hsv_s': 0.7,
        'hsv_v': 0.4,
        'degrees': 15.0,
        'translate': 0.1,
        'scale': 0.2,
        'shear': 0.0,
        'perspective': 0.0,
        'flipud': 0.0,
        'fliplr': 0.5,
        'mosaic': 1.0,
        'mixup': 0.1,
        
        # Validation
        'val': True,
        'plots': True,
    }
    
    print("\nTraining Configuration:")
    print(f"  Epochs: {epochs}")
    print(f"  Batch Size: {batch_size}")
    print(f"  Image Size: {img_size}")
    print(f"  Device: {device}")
    
    # Train model
    print("\nStarting training...")
    print("-" * 80)
    
    results = model.train(**train_args)
    
    print("\n" + "=" * 80)
    print("Training Complete!")
    print("=" * 80)
    
    # Validation
    print("\nRunning validation...")
    metrics = model.val()
    
    print(f"\nFinal Metrics:")
    print(f"  mAP@0.5: {metrics.box.map50:.4f}")
    print(f"  mAP@0.5:0.95: {metrics.box.map:.4f}")
    print(f"  Precision: {metrics.box.mp:.4f}")
    print(f"  Recall: {metrics.box.mr:.4f}")
    
    # Export model
    export_path = Path(results.save_dir) / "weights" / "best.pt"
    print(f"\nBest model saved to: {export_path}")
    
    # Optional: Export to ONNX for deployment
    print("\nExporting to ONNX format...")
    onnx_path = model.export(format='onnx')
    print(f"ONNX model: {onnx_path}")
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train YOLOv9 for HVAC component detection"
    )
    
    parser.add_argument(
        '--data',
        type=str,
        required=True,
        help='Path to data YAML configuration'
    )
    
    parser.add_argument(
        '--epochs',
        type=int,
        default=100,
        help='Number of training epochs (default: 100)'
    )
    
    parser.add_argument(
        '--batch',
        type=int,
        default=16,
        help='Batch size (default: 16)'
    )
    
    parser.add_argument(
        '--img-size',
        type=int,
        default=1280,
        help='Input image size (default: 1280)'
    )
    
    parser.add_argument(
        '--pretrained',
        type=str,
        default='yolov9e.pt',
        help='Pretrained weights (default: yolov9e.pt)'
    )
    
    parser.add_argument(
        '--device',
        type=str,
        default='0',
        help='GPU device ID or "cpu" (default: 0)'
    )
    
    args = parser.parse_args()
    
    # Train model
    train_yolo(
        data_yaml=args.data,
        epochs=args.epochs,
        batch_size=args.batch,
        img_size=args.img_size,
        pretrained=args.pretrained,
        device=args.device
    )
