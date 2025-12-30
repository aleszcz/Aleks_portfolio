"""
Loss functions for segmentation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class DiceLoss(nn.Module):
    """
    Dice Loss for binary segmentation
    """
    
    def __init__(self, smooth=1e-6):
        super(DiceLoss, self).__init__()
        self.smooth = smooth
    
    def forward(self, logits, targets):
        """
        Args:
            logits: Model output (before sigmoid)
            targets: Ground truth masks
        """
        probs = torch.sigmoid(logits)
        probs = probs.view(-1)
        targets = targets.view(-1)
        
        intersection = (probs * targets).sum()
        dice = (2. * intersection + self.smooth) / (probs.sum() + targets.sum() + self.smooth)
        
        return 1 - dice


class FocalLoss(nn.Module):
    """
    Focal Loss for handling class imbalance
    """
    
    def __init__(self, alpha=0.25, gamma=2.0):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
    
    def forward(self, logits, targets):
        """
        Args:
            logits: Model output (before sigmoid)
            targets: Ground truth masks
        """
        bce_loss = F.binary_cross_entropy_with_logits(logits, targets, reduction='none')
        probs = torch.sigmoid(logits)
        pt = torch.where(targets == 1, probs, 1 - probs)
        
        focal_weight = (1 - pt) ** self.gamma
        alpha_weight = torch.where(targets == 1, self.alpha, 1 - self.alpha)
        
        loss = alpha_weight * focal_weight * bce_loss
        
        return loss.mean()


class TverskyLoss(nn.Module):
    """
    Tversky Loss - generalization of Dice loss
    Controls trade-off between false positives and false negatives
    """
    
    def __init__(self, alpha=0.5, beta=0.5, smooth=1e-6):
        super(TverskyLoss, self).__init__()
        self.alpha = alpha  # Weight for false positives
        self.beta = beta    # Weight for false negatives
        self.smooth = smooth
    
    def forward(self, logits, targets):
        probs = torch.sigmoid(logits)
        probs = probs.view(-1)
        targets = targets.view(-1)
        
        # True Positives, False Positives & False Negatives
        TP = (probs * targets).sum()
        FP = ((1 - targets) * probs).sum()
        FN = (targets * (1 - probs)).sum()
        
        tversky = (TP + self.smooth) / (TP + self.alpha * FP + self.beta * FN + self.smooth)
        
        return 1 - tversky


class CombinedLoss(nn.Module):
    """
    Combination of Dice Loss and BCE Loss
    """
    
    def __init__(self, dice_weight=0.5, bce_weight=0.5):
        super(CombinedLoss, self).__init__()
        self.dice_weight = dice_weight
        self.bce_weight = bce_weight
        self.dice_loss = DiceLoss()
        self.bce_loss = nn.BCEWithLogitsLoss()
    
    def forward(self, logits, targets):
        dice = self.dice_loss(logits, targets)
        bce = self.bce_loss(logits, targets)
        
        return self.dice_weight * dice + self.bce_weight * bce


class DiceBCELoss(nn.Module):
    """
    Dice Loss + Binary Cross Entropy Loss
    """
    
    def __init__(self, smooth=1e-6, dice_weight=0.5):
        super(DiceBCELoss, self).__init__()
        self.smooth = smooth
        self.dice_weight = dice_weight
        self.bce_weight = 1 - dice_weight
    
    def forward(self, logits, targets):
        # Dice loss
        probs = torch.sigmoid(logits)
        probs_flat = probs.view(-1)
        targets_flat = targets.view(-1)
        
        intersection = (probs_flat * targets_flat).sum()
        dice_loss = 1 - (2. * intersection + self.smooth) / (
            probs_flat.sum() + targets_flat.sum() + self.smooth
        )
        
        # BCE loss
        bce_loss = F.binary_cross_entropy_with_logits(logits, targets)
        
        # Combined loss
        return self.dice_weight * dice_loss + self.bce_weight * bce_loss


class IoULoss(nn.Module):
    """
    IoU Loss (Jaccard Loss)
    """
    
    def __init__(self, smooth=1e-6):
        super(IoULoss, self).__init__()
        self.smooth = smooth
    
    def forward(self, logits, targets):
        probs = torch.sigmoid(logits)
        probs = probs.view(-1)
        targets = targets.view(-1)
        
        intersection = (probs * targets).sum()
        total = (probs + targets).sum()
        union = total - intersection
        
        iou = (intersection + self.smooth) / (union + self.smooth)
        
        return 1 - iou


class WeightedCombinedLoss(nn.Module):
    """
    Weighted combination of multiple losses
    """
    
    def __init__(self, dice_weight=1.0, bce_weight=1.0, focal_weight=0.0):
        super(WeightedCombinedLoss, self).__init__()
        self.dice_weight = dice_weight
        self.bce_weight = bce_weight
        self.focal_weight = focal_weight
        
        self.dice_loss = DiceLoss()
        self.bce_loss = nn.BCEWithLogitsLoss()
        self.focal_loss = FocalLoss()
    
    def forward(self, logits, targets):
        loss = 0
        
        if self.dice_weight > 0:
            loss += self.dice_weight * self.dice_loss(logits, targets)
        
        if self.bce_weight > 0:
            loss += self.bce_weight * self.bce_loss(logits, targets)
        
        if self.focal_weight > 0:
            loss += self.focal_weight * self.focal_loss(logits, targets)
        
        return loss


def test_losses():
    """Test loss functions"""
    # Create dummy data
    logits = torch.randn(2, 1, 32, 32, 32)
    targets = torch.randint(0, 2, (2, 1, 32, 32, 32)).float()
    
    # Test losses
    dice_loss = DiceLoss()
    focal_loss = FocalLoss()
    tversky_loss = TverskyLoss()
    combined_loss = CombinedLoss()
    iou_loss = IoULoss()
    
    print(f"Dice Loss: {dice_loss(logits, targets):.4f}")
    print(f"Focal Loss: {focal_loss(logits, targets):.4f}")
    print(f"Tversky Loss: {tversky_loss(logits, targets):.4f}")
    print(f"Combined Loss: {combined_loss(logits, targets):.4f}")
    print(f"IoU Loss: {iou_loss(logits, targets):.4f}")


if __name__ == "__main__":
    test_losses()
