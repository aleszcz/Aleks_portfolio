"""
3D U-Net model for volumetric segmentation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class DoubleConv3D(nn.Module):
    """Double convolution block for U-Net"""
    
    def __init__(self, in_channels, out_channels, mid_channels=None):
        super().__init__()
        if not mid_channels:
            mid_channels = out_channels
        
        self.double_conv = nn.Sequential(
            nn.Conv3d(in_channels, mid_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm3d(mid_channels),
            nn.ReLU(inplace=True),
            nn.Conv3d(mid_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        return self.double_conv(x)


class Down3D(nn.Module):
    """Downscaling with maxpool then double conv"""
    
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool3d(2),
            DoubleConv3D(in_channels, out_channels)
        )
    
    def forward(self, x):
        return self.maxpool_conv(x)


class Up3D(nn.Module):
    """Upscaling then double conv"""
    
    def __init__(self, in_channels, out_channels, trilinear=True):
        super().__init__()
        
        if trilinear:
            self.up = nn.Upsample(scale_factor=2, mode='trilinear', align_corners=True)
            self.conv = DoubleConv3D(in_channels, out_channels, in_channels // 2)
        else:
            self.up = nn.ConvTranspose3d(in_channels, in_channels // 2, kernel_size=2, stride=2)
            self.conv = DoubleConv3D(in_channels, out_channels)
    
    def forward(self, x1, x2):
        x1 = self.up(x1)
        
        # Handle odd dimensions
        diffZ = x2.size()[2] - x1.size()[2]
        diffY = x2.size()[3] - x1.size()[3]
        diffX = x2.size()[4] - x1.size()[4]
        
        x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2,
                        diffY // 2, diffY - diffY // 2,
                        diffZ // 2, diffZ - diffZ // 2])
        
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class UNet3D(nn.Module):
    """
    3D U-Net for volumetric segmentation
    
    Args:
        n_channels: Number of input channels
        n_classes: Number of output classes
        base_channels: Number of channels in first layer
        depth: Depth of the network
        trilinear: Use trilinear upsampling (True) or transposed convolution (False)
    """
    
    def __init__(self, n_channels=1, n_classes=1, base_channels=32, depth=4, trilinear=True):
        super(UNet3D, self).__init__()
        self.n_channels = n_channels
        self.n_classes = n_classes
        self.trilinear = trilinear
        self.depth = depth
        
        # Input convolution
        self.inc = DoubleConv3D(n_channels, base_channels)
        
        # Encoder (downsampling)
        self.down_blocks = nn.ModuleList()
        in_ch = base_channels
        for i in range(depth):
            out_ch = in_ch * 2
            self.down_blocks.append(Down3D(in_ch, out_ch))
            in_ch = out_ch
        
        # Decoder (upsampling)
        self.up_blocks = nn.ModuleList()
        for i in range(depth):
            out_ch = in_ch // 2
            self.up_blocks.append(Up3D(in_ch, out_ch, trilinear))
            in_ch = out_ch
        
        # Output convolution
        self.outc = nn.Conv3d(base_channels, n_classes, kernel_size=1)
    
    def forward(self, x):
        # Encoder
        x = self.inc(x)
        skip_connections = [x]
        
        for down in self.down_blocks:
            x = down(x)
            skip_connections.append(x)
        
        # Remove last skip connection (it's the bottleneck)
        skip_connections = skip_connections[:-1]
        
        # Decoder
        for up, skip in zip(self.up_blocks, reversed(skip_connections)):
            x = up(x, skip)
        
        # Output
        logits = self.outc(x)
        return logits


class ResidualBlock3D(nn.Module):
    """3D Residual block"""
    
    def __init__(self, channels):
        super().__init__()
        self.conv1 = nn.Conv3d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm3d(channels)
        self.conv2 = nn.Conv3d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm3d(channels)
        self.relu = nn.ReLU(inplace=True)
    
    def forward(self, x):
        residual = x
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual
        out = self.relu(out)
        return out


class ResUNet3D(nn.Module):
    """3D Residual U-Net with residual blocks"""
    
    def __init__(self, n_channels=1, n_classes=1, base_channels=32, depth=4):
        super().__init__()
        self.n_channels = n_channels
        self.n_classes = n_classes
        
        # Input
        self.inc = DoubleConv3D(n_channels, base_channels)
        
        # Encoder
        self.down_blocks = nn.ModuleList()
        self.residual_blocks = nn.ModuleList()
        in_ch = base_channels
        
        for i in range(depth):
            out_ch = in_ch * 2
            self.down_blocks.append(Down3D(in_ch, out_ch))
            self.residual_blocks.append(ResidualBlock3D(out_ch))
            in_ch = out_ch
        
        # Decoder
        self.up_blocks = nn.ModuleList()
        for i in range(depth):
            out_ch = in_ch // 2
            self.up_blocks.append(Up3D(in_ch, out_ch))
            in_ch = out_ch
        
        # Output
        self.outc = nn.Conv3d(base_channels, n_classes, kernel_size=1)
    
    def forward(self, x):
        # Encoder
        x = self.inc(x)
        skip_connections = [x]
        
        for down, res_block in zip(self.down_blocks, self.residual_blocks):
            x = down(x)
            x = res_block(x)
            skip_connections.append(x)
        
        skip_connections = skip_connections[:-1]
        
        # Decoder
        for up, skip in zip(self.up_blocks, reversed(skip_connections)):
            x = up(x, skip)
        
        # Output
        logits = self.outc(x)
        return logits


def test_model():
    """Test the model with a dummy input"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Create model
    model = UNet3D(n_channels=1, n_classes=1, base_channels=16, depth=3)
    model = model.to(device)
    
    # Create dummy input
    batch_size = 2
    x = torch.randn(batch_size, 1, 64, 64, 64).to(device)
    
    # Forward pass
    with torch.no_grad():
        output = model(x)
    
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    return model


if __name__ == "__main__":
    test_model()
