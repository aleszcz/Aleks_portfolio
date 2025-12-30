"""
Training script for Vesuvius Surface Detection
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from pathlib import Path
import argparse
from tqdm import tqdm
import wandb
import yaml

# Import custom modules
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data.dataset import VesuviusDataset
from src.models.unet3d import UNet3D, ResUNet3D
from src.utils.metrics import dice_coefficient, iou_score
from src.utils.losses import DiceLoss, CombinedLoss


def train_epoch(model, dataloader, criterion, optimizer, device, epoch):
    """Train for one epoch"""
    model.train()
    running_loss = 0.0
    running_dice = 0.0
    
    pbar = tqdm(dataloader, desc=f"Epoch {epoch} [Train]")
    for batch_idx, (volumes, masks) in enumerate(pbar):
        volumes = volumes.to(device)
        masks = masks.to(device)
        
        # Forward pass
        optimizer.zero_grad()
        outputs = model(volumes)
        
        # Calculate loss
        loss = criterion(outputs, masks)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Calculate metrics
        with torch.no_grad():
            preds = torch.sigmoid(outputs) > 0.5
            dice = dice_coefficient(preds, masks)
        
        # Update running metrics
        running_loss += loss.item()
        running_dice += dice.item()
        
        # Update progress bar
        pbar.set_postfix({
            'loss': running_loss / (batch_idx + 1),
            'dice': running_dice / (batch_idx + 1)
        })
    
    avg_loss = running_loss / len(dataloader)
    avg_dice = running_dice / len(dataloader)
    
    return avg_loss, avg_dice


def validate(model, dataloader, criterion, device, epoch):
    """Validate the model"""
    model.eval()
    running_loss = 0.0
    running_dice = 0.0
    running_iou = 0.0
    
    pbar = tqdm(dataloader, desc=f"Epoch {epoch} [Val]")
    with torch.no_grad():
        for batch_idx, (volumes, masks) in enumerate(pbar):
            volumes = volumes.to(device)
            masks = masks.to(device)
            
            # Forward pass
            outputs = model(volumes)
            
            # Calculate loss
            loss = criterion(outputs, masks)
            
            # Calculate metrics
            preds = torch.sigmoid(outputs) > 0.5
            dice = dice_coefficient(preds, masks)
            iou = iou_score(preds, masks)
            
            # Update running metrics
            running_loss += loss.item()
            running_dice += dice.item()
            running_iou += iou.item()
            
            # Update progress bar
            pbar.set_postfix({
                'loss': running_loss / (batch_idx + 1),
                'dice': running_dice / (batch_idx + 1),
                'iou': running_iou / (batch_idx + 1)
            })
    
    avg_loss = running_loss / len(dataloader)
    avg_dice = running_dice / len(dataloader)
    avg_iou = running_iou / len(dataloader)
    
    return avg_loss, avg_dice, avg_iou


def train(config):
    """Main training function"""
    
    # Set device
    device = torch.device(config['device'] if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create datasets
    train_dataset = VesuviusDataset(
        data_dir=config['train_data_dir'],
        patch_size=config['patch_size'],
        stride=config['stride'],
        is_train=True
    )
    
    val_dataset = VesuviusDataset(
        data_dir=config['val_data_dir'],
        patch_size=config['patch_size'],
        stride=config['patch_size'],  # No overlap for validation
        is_train=False
    )
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=config['batch_size'],
        shuffle=True,
        num_workers=config['num_workers'],
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=config['batch_size'],
        shuffle=False,
        num_workers=config['num_workers'],
        pin_memory=True
    )
    
    print(f"Train samples: {len(train_dataset)}")
    print(f"Val samples: {len(val_dataset)}")
    
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
    
    model = model.to(device)
    
    # Create loss function
    if config['loss'] == 'dice':
        criterion = DiceLoss()
    elif config['loss'] == 'combined':
        criterion = CombinedLoss()
    else:
        criterion = nn.BCEWithLogitsLoss()
    
    # Create optimizer
    optimizer = optim.Adam(
        model.parameters(),
        lr=config['learning_rate'],
        weight_decay=config['weight_decay']
    )
    
    # Create scheduler
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=config['epochs'],
        eta_min=config['min_lr']
    )
    
    # Initialize wandb if requested
    if config.get('use_wandb', False):
        wandb.init(
            project="vesuvius-surface-detection",
            config=config,
            name=config.get('experiment_name', 'experiment')
        )
        wandb.watch(model)
    
    # Training loop
    best_dice = 0.0
    save_dir = Path(config['save_dir'])
    save_dir.mkdir(parents=True, exist_ok=True)
    
    for epoch in range(1, config['epochs'] + 1):
        print(f"\nEpoch {epoch}/{config['epochs']}")
        print("-" * 50)
        
        # Train
        train_loss, train_dice = train_epoch(
            model, train_loader, criterion, optimizer, device, epoch
        )
        
        # Validate
        val_loss, val_dice, val_iou = validate(
            model, val_loader, criterion, device, epoch
        )
        
        # Update scheduler
        scheduler.step()
        
        # Print metrics
        print(f"Train Loss: {train_loss:.4f}, Train Dice: {train_dice:.4f}")
        print(f"Val Loss: {val_loss:.4f}, Val Dice: {val_dice:.4f}, Val IoU: {val_iou:.4f}")
        print(f"LR: {scheduler.get_last_lr()[0]:.6f}")
        
        # Log to wandb
        if config.get('use_wandb', False):
            wandb.log({
                'epoch': epoch,
                'train_loss': train_loss,
                'train_dice': train_dice,
                'val_loss': val_loss,
                'val_dice': val_dice,
                'val_iou': val_iou,
                'lr': scheduler.get_last_lr()[0]
            })
        
        # Save best model
        if val_dice > best_dice:
            best_dice = val_dice
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_dice': val_dice,
                'val_iou': val_iou,
                'config': config
            }
            torch.save(checkpoint, save_dir / 'best_model.pth')
            print(f"Saved best model with Dice: {best_dice:.4f}")
        
        # Save checkpoint every N epochs
        if epoch % config.get('save_every', 10) == 0:
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_dice': val_dice,
                'config': config
            }
            torch.save(checkpoint, save_dir / f'checkpoint_epoch_{epoch}.pth')
    
    print("\nTraining completed!")
    print(f"Best validation Dice: {best_dice:.4f}")
    
    if config.get('use_wandb', False):
        wandb.finish()


def main():
    parser = argparse.ArgumentParser(description='Train Vesuvius Surface Detection Model')
    parser.add_argument('--config', type=str, default='configs/default_config.yaml',
                        help='Path to config file')
    args = parser.parse_args()
    
    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Train
    train(config)


if __name__ == "__main__":
    main()
