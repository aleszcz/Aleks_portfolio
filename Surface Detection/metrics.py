"""
Metrics for evaluating segmentation performance
"""

import torch
import numpy as np


def dice_coefficient(preds, targets, smooth=1e-6):
    """
    Calculate Dice coefficient
    
    Args:
        preds: Predicted masks (binary)
        targets: Ground truth masks (binary)
        smooth: Smoothing factor to avoid division by zero
    
    Returns:
        Dice coefficient
    """
    preds = preds.contiguous().view(-1)
    targets = targets.contiguous().view(-1)
    
    intersection = (preds * targets).sum()
    dice = (2. * intersection + smooth) / (preds.sum() + targets.sum() + smooth)
    
    return dice


def iou_score(preds, targets, smooth=1e-6):
    """
    Calculate Intersection over Union (IoU) / Jaccard Index
    
    Args:
        preds: Predicted masks (binary)
        targets: Ground truth masks (binary)
        smooth: Smoothing factor
    
    Returns:
        IoU score
    """
    preds = preds.contiguous().view(-1)
    targets = targets.contiguous().view(-1)
    
    intersection = (preds * targets).sum()
    union = preds.sum() + targets.sum() - intersection
    
    iou = (intersection + smooth) / (union + smooth)
    
    return iou


def precision(preds, targets, smooth=1e-6):
    """Calculate precision"""
    preds = preds.contiguous().view(-1)
    targets = targets.contiguous().view(-1)
    
    true_positives = (preds * targets).sum()
    predicted_positives = preds.sum()
    
    return (true_positives + smooth) / (predicted_positives + smooth)


def recall(preds, targets, smooth=1e-6):
    """Calculate recall / sensitivity"""
    preds = preds.contiguous().view(-1)
    targets = targets.contiguous().view(-1)
    
    true_positives = (preds * targets).sum()
    actual_positives = targets.sum()
    
    return (true_positives + smooth) / (actual_positives + smooth)


def f1_score(preds, targets, smooth=1e-6):
    """Calculate F1 score"""
    prec = precision(preds, targets, smooth)
    rec = recall(preds, targets, smooth)
    
    return 2 * (prec * rec) / (prec + rec + smooth)


def specificity(preds, targets, smooth=1e-6):
    """Calculate specificity"""
    preds = preds.contiguous().view(-1)
    targets = targets.contiguous().view(-1)
    
    true_negatives = ((1 - preds) * (1 - targets)).sum()
    actual_negatives = (1 - targets).sum()
    
    return (true_negatives + smooth) / (actual_negatives + smooth)


def hausdorff_distance(preds, targets):
    """
    Calculate Hausdorff distance (simplified 3D version)
    Note: This is a basic implementation. For production, use scipy or specialized libraries.
    """
    from scipy.ndimage import distance_transform_edt
    
    preds_np = preds.cpu().numpy()
    targets_np = targets.cpu().numpy()
    
    # Get surface voxels (boundary)
    preds_surface = preds_np - distance_transform_edt(preds_np) <= 1
    targets_surface = targets_np - distance_transform_edt(targets_np) <= 1
    
    # Calculate distances
    dist_preds_to_targets = distance_transform_edt(~targets_surface)
    dist_targets_to_preds = distance_transform_edt(~preds_surface)
    
    hausdorff_dist = max(
        dist_preds_to_targets[preds_surface].max(),
        dist_targets_to_preds[targets_surface].max()
    )
    
    return hausdorff_dist


def surface_dice(preds, targets, tolerance=2.0):
    """
    Surface Dice: Dice coefficient computed on surface voxels only
    
    Args:
        preds: Predicted masks
        targets: Ground truth masks
        tolerance: Distance tolerance for surface matching
    """
    from scipy.ndimage import distance_transform_edt
    
    preds_np = preds.cpu().numpy().astype(bool)
    targets_np = targets.cpu().numpy().astype(bool)
    
    # Get surface voxels
    preds_surface = preds_np ^ distance_transform_edt(preds_np) <= 1
    targets_surface = targets_np ^ distance_transform_edt(targets_np) <= 1
    
    # Calculate distances from pred surface to target surface
    dist_preds_to_targets = distance_transform_edt(~targets_surface)
    dist_targets_to_preds = distance_transform_edt(~preds_surface)
    
    # Count surface voxels within tolerance
    preds_within_tolerance = (dist_preds_to_targets[preds_surface] <= tolerance).sum()
    targets_within_tolerance = (dist_targets_to_preds[targets_surface] <= tolerance).sum()
    
    # Calculate surface Dice
    numerator = preds_within_tolerance + targets_within_tolerance
    denominator = preds_surface.sum() + targets_surface.sum()
    
    surface_dice_score = numerator / denominator if denominator > 0 else 0
    
    return surface_dice_score


class MetricsCalculator:
    """Calculate and track multiple metrics"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all metrics"""
        self.dice_scores = []
        self.iou_scores = []
        self.precision_scores = []
        self.recall_scores = []
        self.f1_scores = []
    
    def update(self, preds, targets):
        """Update metrics with new batch"""
        preds = (preds > 0.5).float()
        targets = targets.float()
        
        self.dice_scores.append(dice_coefficient(preds, targets).item())
        self.iou_scores.append(iou_score(preds, targets).item())
        self.precision_scores.append(precision(preds, targets).item())
        self.recall_scores.append(recall(preds, targets).item())
        self.f1_scores.append(f1_score(preds, targets).item())
    
    def get_metrics(self):
        """Get average metrics"""
        return {
            'dice': np.mean(self.dice_scores),
            'iou': np.mean(self.iou_scores),
            'precision': np.mean(self.precision_scores),
            'recall': np.mean(self.recall_scores),
            'f1': np.mean(self.f1_scores)
        }


if __name__ == "__main__":
    # Test metrics
    preds = torch.rand(2, 1, 32, 32, 32) > 0.5
    targets = torch.rand(2, 1, 32, 32, 32) > 0.5
    
    print(f"Dice: {dice_coefficient(preds, targets):.4f}")
    print(f"IoU: {iou_score(preds, targets):.4f}")
    print(f"Precision: {precision(preds, targets):.4f}")
    print(f"Recall: {recall(preds, targets):.4f}")
    print(f"F1: {f1_score(preds, targets):.4f}")
