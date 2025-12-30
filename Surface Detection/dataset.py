"""
Dataset classes for Vesuvius Challenge Surface Detection
"""

import numpy as np
import torch
from torch.utils.data import Dataset
import zarr
import tifffile
from pathlib import Path
from typing import Optional, Tuple, List
import random


class VesuviusDataset(Dataset):
    """
    Dataset for loading 3D CT scan volumes and surface masks
    """
    
    def __init__(
        self,
        data_dir: str,
        patch_size: Tuple[int, int, int] = (128, 128, 128),
        stride: Optional[Tuple[int, int, int]] = None,
        transform=None,
        is_train: bool = True
    ):
        """
        Args:
            data_dir: Path to data directory containing volumes and masks
            patch_size: Size of 3D patches to extract (D, H, W)
            stride: Stride for patch extraction. If None, uses patch_size (no overlap)
            transform: Optional transforms to apply
            is_train: Whether this is training data
        """
        self.data_dir = Path(data_dir)
        self.patch_size = patch_size
        self.stride = stride if stride is not None else patch_size
        self.transform = transform
        self.is_train = is_train
        
        # Find all volume files
        self.volume_paths = sorted(self.data_dir.glob("*/volume.zarr"))
        if not self.volume_paths:
            self.volume_paths = sorted(self.data_dir.glob("*/volume.tif"))
        
        # Create list of all patches
        self.patches = self._create_patch_list()
        
    def _create_patch_list(self) -> List[dict]:
        """Create list of all possible patches"""
        patches = []
        
        for vol_idx, vol_path in enumerate(self.volume_paths):
            # Load volume to get shape
            volume = self._load_volume(vol_path)
            d, h, w = volume.shape
            
            # Generate patch coordinates
            for z in range(0, d - self.patch_size[0] + 1, self.stride[0]):
                for y in range(0, h - self.patch_size[1] + 1, self.stride[1]):
                    for x in range(0, w - self.patch_size[2] + 1, self.stride[2]):
                        patches.append({
                            'volume_idx': vol_idx,
                            'coords': (z, y, x)
                        })
        
        return patches
    
    def _load_volume(self, path: Path) -> np.ndarray:
        """Load volume from zarr or tiff file"""
        if path.suffix == '.zarr':
            return zarr.open(str(path), mode='r')
        else:
            return tifffile.imread(str(path))
    
    def _load_mask(self, volume_path: Path) -> np.ndarray:
        """Load corresponding mask"""
        mask_path = volume_path.parent / "mask.zarr"
        if not mask_path.exists():
            mask_path = volume_path.parent / "mask.tif"
        
        return self._load_volume(mask_path)
    
    def __len__(self) -> int:
        return len(self.patches)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get a training sample"""
        patch_info = self.patches[idx]
        volume_path = self.volume_paths[patch_info['volume_idx']]
        z, y, x = patch_info['coords']
        
        # Load volume and mask
        volume = self._load_volume(volume_path)
        mask = self._load_mask(volume_path)
        
        # Extract patch
        d, h, w = self.patch_size
        volume_patch = volume[z:z+d, y:y+h, x:x+w]
        mask_patch = mask[z:z+d, y:y+h, x:x+w]
        
        # Convert to numpy arrays if needed
        if isinstance(volume_patch, zarr.Array):
            volume_patch = np.array(volume_patch)
        if isinstance(mask_patch, zarr.Array):
            mask_patch = np.array(mask_patch)
        
        # Normalize volume to [0, 1]
        volume_patch = volume_patch.astype(np.float32) / 255.0
        mask_patch = mask_patch.astype(np.float32)
        
        # Apply transforms
        if self.transform:
            volume_patch, mask_patch = self.transform(volume_patch, mask_patch)
        
        # Add channel dimension and convert to torch tensors
        volume_patch = torch.from_numpy(volume_patch[np.newaxis, ...])
        mask_patch = torch.from_numpy(mask_patch[np.newaxis, ...])
        
        return volume_patch, mask_patch


class VesuviusInferenceDataset(Dataset):
    """
    Dataset for inference on test data
    """
    
    def __init__(
        self,
        data_dir: str,
        patch_size: Tuple[int, int, int] = (128, 128, 128),
        overlap: int = 32
    ):
        """
        Args:
            data_dir: Path to test data directory
            patch_size: Size of 3D patches
            overlap: Overlap between patches for smoother stitching
        """
        self.data_dir = Path(data_dir)
        self.patch_size = patch_size
        self.overlap = overlap
        
        # Find all test volumes
        self.volume_paths = sorted(self.data_dir.glob("*/volume.zarr"))
        if not self.volume_paths:
            self.volume_paths = sorted(self.data_dir.glob("*/volume.tif"))
        
        # Create patch list
        self.patches = self._create_patch_list()
    
    def _load_volume(self, path: Path) -> np.ndarray:
        """Load volume from zarr or tiff file"""
        if path.suffix == '.zarr':
            return zarr.open(str(path), mode='r')
        else:
            return tifffile.imread(str(path))
    
    def _create_patch_list(self) -> List[dict]:
        """Create list of all patches for inference"""
        patches = []
        stride = tuple(s - self.overlap for s in self.patch_size)
        
        for vol_idx, vol_path in enumerate(self.volume_paths):
            volume = self._load_volume(vol_path)
            d, h, w = volume.shape
            
            for z in range(0, d - self.patch_size[0] + 1, stride[0]):
                for y in range(0, h - self.patch_size[1] + 1, stride[1]):
                    for x in range(0, w - self.patch_size[2] + 1, stride[2]):
                        patches.append({
                            'volume_idx': vol_idx,
                            'volume_path': vol_path,
                            'coords': (z, y, x),
                            'volume_shape': (d, h, w)
                        })
        
        return patches
    
    def __len__(self) -> int:
        return len(self.patches)
    
    def __getitem__(self, idx: int) -> dict:
        """Get inference sample with metadata"""
        patch_info = self.patches[idx]
        volume_path = patch_info['volume_path']
        z, y, x = patch_info['coords']
        
        # Load volume
        volume = self._load_volume(volume_path)
        
        # Extract patch
        d, h, w = self.patch_size
        volume_patch = volume[z:z+d, y:y+h, x:x+w]
        
        if isinstance(volume_patch, zarr.Array):
            volume_patch = np.array(volume_patch)
        
        # Normalize
        volume_patch = volume_patch.astype(np.float32) / 255.0
        
        # Convert to tensor
        volume_patch = torch.from_numpy(volume_patch[np.newaxis, ...])
        
        return {
            'volume': volume_patch,
            'coords': patch_info['coords'],
            'volume_idx': patch_info['volume_idx'],
            'volume_shape': patch_info['volume_shape']
        }


if __name__ == "__main__":
    # Example usage
    dataset = VesuviusDataset(
        data_dir="data/processed/train",
        patch_size=(64, 64, 64),
        is_train=True
    )
    
    print(f"Dataset size: {len(dataset)}")
    
    # Load first sample
    volume, mask = dataset[0]
    print(f"Volume shape: {volume.shape}")
    print(f"Mask shape: {mask.shape}")
    print(f"Volume range: [{volume.min():.3f}, {volume.max():.3f}]")
    print(f"Mask values: {mask.unique()}")
