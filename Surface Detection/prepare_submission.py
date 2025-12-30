"""
Prepare submission file for Kaggle
"""

import torch
import numpy as np
import zarr
import tifffile
from pathlib import Path
import argparse
from tqdm import tqdm
import pandas as pd

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.models.unet3d import UNet3D, ResUNet3D
from src.data.dataset import VesuviusInferenceDataset
from torch.utils.data import DataLoader


def load_model(checkpoint_path, device):
    """Load trained model from checkpoint"""
    checkpoint = torch.load(checkpoint_path, map_location=device)
    config = checkpoint['config']
    
    # Create model
    if config['model'] == 'unet3d':
        model = UNet3D(
            n_channels=1,
            n_classes=1,
            base_channels=config['base_channels'],
            depth=config['depth']
        )
    elif config['model'] == 'resunet3d':
        model = ResUNet3D(
            n_channels=1,
            n_classes=1,
            base_channels=config['base_channels'],
            depth=config['depth']
        )
    else:
        raise ValueError(f"Unknown model: {config['model']}")
    
    # Load weights
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    print(f"Loaded model from epoch {checkpoint['epoch']}")
    print(f"Validation Dice: {checkpoint.get('val_dice', 'N/A')}")
    
    return model, config


def predict_volume(model, dataloader, volume_shape, device, threshold=0.5):
    """
    Predict masks for entire volume with patch stitching
    """
    # Initialize output volume
    predictions = np.zeros(volume_shape, dtype=np.float32)
    counts = np.zeros(volume_shape, dtype=np.float32)
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Predicting"):
            volumes = batch['volume'].to(device)
            coords = batch['coords']
            
            # Predict
            outputs = model(volumes)
            probs = torch.sigmoid(outputs).cpu().numpy()
            
            # Add predictions to output volume
            for i in range(len(coords)):
                z, y, x = coords[i]
                d, h, w = probs.shape[2:]
                
                predictions[z:z+d, y:y+h, x:x+w] += probs[i, 0]
                counts[z:z+d, y:y+h, x:x+w] += 1
    
    # Average overlapping predictions
    predictions = predictions / np.maximum(counts, 1)
    
    # Apply threshold
    binary_mask = (predictions > threshold).astype(np.uint8)
    
    return binary_mask, predictions


def create_submission(test_dir, model_path, output_path, device, patch_size=(128, 128, 128)):
    """
    Create submission file
    """
    print("Loading model...")
    model, config = load_model(model_path, device)
    
    print("Creating dataset...")
    dataset = VesuviusInferenceDataset(
        data_dir=test_dir,
        patch_size=patch_size,
        overlap=32
    )
    
    dataloader = DataLoader(
        dataset,
        batch_size=config.get('inference', {}).get('batch_size', 2),
        shuffle=False,
        num_workers=4
    )
    
    # Get unique volumes
    volume_paths = {}
    for item in dataset.patches:
        vol_idx = item['volume_idx']
        if vol_idx not in volume_paths:
            volume_paths[vol_idx] = {
                'path': item['volume_path'],
                'shape': item['volume_shape']
            }
    
    # Process each volume
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    submission_data = []
    
    for vol_idx, vol_info in volume_paths.items():
        print(f"\nProcessing volume {vol_idx + 1}/{len(volume_paths)}")
        print(f"Path: {vol_info['path']}")
        print(f"Shape: {vol_info['shape']}")
        
        # Get patches for this volume
        vol_dataloader = DataLoader(
            [item for item in dataset if item['volume_idx'] == vol_idx],
            batch_size=config.get('inference', {}).get('batch_size', 2),
            shuffle=False
        )
        
        # Predict
        binary_mask, probs = predict_volume(
            model,
            dataloader,
            vol_info['shape'],
            device,
            threshold=config.get('inference', {}).get('threshold', 0.5)
        )
        
        # Save prediction
        volume_name = vol_info['path'].parent.name
        pred_path = output_dir / f"{volume_name}_prediction.tif"
        tifffile.imwrite(pred_path, binary_mask)
        print(f"Saved prediction to: {pred_path}")
        
        # Add to submission data
        submission_data.append({
            'volume_id': volume_name,
            'prediction_path': str(pred_path),
            'surface_voxels': binary_mask.sum()
        })
    
    # Create submission CSV
    df = pd.DataFrame(submission_data)
    df.to_csv(output_path, index=False)
    
    print(f"\nSubmission file created: {output_path}")
    print(f"Total volumes: {len(df)}")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Prepare Kaggle submission')
    parser.add_argument('--test-dir', type=str, required=True,
                        help='Path to test data directory')
    parser.add_argument('--model-path', type=str, required=True,
                        help='Path to trained model checkpoint')
    parser.add_argument('--output', type=str, default='data/submissions/submission.csv',
                        help='Output submission file path')
    parser.add_argument('--device', type=str, default='cuda',
                        help='Device to use (cuda/cpu)')
    parser.add_argument('--patch-size', type=int, nargs=3, default=[128, 128, 128],
                        help='Patch size for inference')
    
    args = parser.parse_args()
    
    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    create_submission(
        test_dir=args.test_dir,
        model_path=args.model_path,
        output_path=args.output,
        device=device,
        patch_size=tuple(args.patch_size)
    )
    
    print("\nDone! You can now submit to Kaggle:")
    print(f"kaggle competitions submit -c vesuvius-challenge-surface-detection -f {args.output} -m 'Your message'")


if __name__ == "__main__":
    main()
