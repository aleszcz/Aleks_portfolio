# RevitAssist: Advanced Multimodal Architecture

## Beyond OCR: Holistic Spatial Understanding

Traditional OCR extracts text from images. RevitAssist requires **spatial reasoning, symbol understanding, and engineering logic** - a fundamentally different problem.

### Key Challenges

| Traditional OCR | HVAC Drawing Understanding |
|----------------|---------------------------|
| Recognize text characters | Understand engineering symbols |
| Sequential reading order | Spatial relationships and topology |
| Text extraction | Component detection + connection inference |
| Character-level accuracy | System-level correctness |
| No domain knowledge | HVAC physics constraints |

---

## Architecture Comparison

We explore 4 architectural approaches, each with different trade-offs:

### 1. Hierarchical Vision-Language Transformer (HVLT)
**Best for:** Component extraction + annotation understanding  
**Strength:** Combines visual and textual understanding  
**Weakness:** May miss implicit spatial relationships

### 2. Spatial Graph Neural Network (SGNN)
**Best for:** Connection inference and topology understanding  
**Strength:** Explicit spatial reasoning via graph structure  
**Weakness:** Requires good initial component detection

### 3. Multi-Scale Vision Transformer (MSVT)
**Best for:** Handling multiple levels of abstraction  
**Strength:** Captures both global layout and local details  
**Weakness:** Computationally expensive

### 4. Neuro-Symbolic Hybrid (NSH)
**Best for:** Validation and constraint satisfaction  
**Strength:** Combines learning with hard engineering rules  
**Weakness:** Requires manual rule encoding

**Recommended Approach:** Combine HVLT for extraction + SGNN for reasoning + NSH for validation

---

## Architecture 1: Hierarchical Vision-Language Transformer (HVLT)

### Conceptual Overview

```
PDF Drawing
    ↓
[Vision Encoder] → Spatial Features
    ↓
[Cross-Attention] ← Text Annotations (from OCR)
    ↓
[Multimodal Fusion]
    ↓
[Component Decoder] → Ducts, Equipment
    ↓
[Relationship Decoder] → Connections
```

### Implementation

```python
import torch
import torch.nn as nn
from transformers import CLIPVisionModel, CLIPTextModel

class HVACVisionLanguageTransformer(nn.Module):
    """
    Hierarchical architecture that processes visual and textual information
    in parallel, then fuses them for holistic understanding
    """
    
    def __init__(
        self,
        vision_encoder: str = "openai/clip-vit-large-patch14",
        hidden_dim: int = 768,
        num_component_classes: int = 50,  # Ducts, equipment types
        num_attention_heads: int = 12
    ):
        super().__init__()
        
        # Stage 1: Vision Encoding (Spatial Features)
        self.vision_encoder = CLIPVisionModel.from_pretrained(vision_encoder)
        
        # Stage 2: Text Encoding (Annotations, Schedules)
        self.text_encoder = CLIPTextModel.from_pretrained("openai/clip-vit-large-patch14")
        
        # Stage 3: Cross-Modal Attention
        self.cross_attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=num_attention_heads,
            batch_first=True
        )
        
        # Stage 4: Spatial Reasoning Layer
        self.spatial_reasoning = SpatialReasoningBlock(
            hidden_dim=hidden_dim,
            num_layers=4
        )
        
        # Stage 5: Component Detection Heads
        self.duct_detector = ComponentDetectionHead(
            hidden_dim=hidden_dim,
            num_classes=10,  # Duct types
            output_type="bbox_with_dims"
        )
        
        self.equipment_detector = ComponentDetectionHead(
            hidden_dim=hidden_dim,
            num_classes=20,  # Equipment types
            output_type="point_with_properties"
        )
        
        # Stage 6: Connection Inference
        self.connection_predictor = ConnectionInferenceHead(
            hidden_dim=hidden_dim
        )
    
    def forward(self, image, text_annotations):
        """
        Args:
            image: [B, 3, H, W] - Drawing image
            text_annotations: [B, N, max_len] - Extracted text with positions
            
        Returns:
            ducts: List of detected ducts with properties
            equipment: List of detected equipment
            connections: Predicted connections between components
        """
        # Stage 1: Extract visual features
        vision_features = self.vision_encoder(image).last_hidden_state
        # Shape: [B, num_patches, hidden_dim]
        
        # Stage 2: Extract text features
        text_features = self.text_encoder(text_annotations).last_hidden_state
        # Shape: [B, num_annotations, hidden_dim]
        
        # Stage 3: Cross-modal fusion
        # Query: vision features (what do I see?)
        # Key/Value: text features (what do annotations say?)
        fused_features, attention_weights = self.cross_attention(
            query=vision_features,
            key=text_features,
            value=text_features
        )
        # Shape: [B, num_patches, hidden_dim]
        # attention_weights tells us which text corresponds to which visual region
        
        # Stage 4: Spatial reasoning
        spatial_features = self.spatial_reasoning(fused_features)
        
        # Stage 5: Component detection
        ducts = self.duct_detector(spatial_features)
        equipment = self.equipment_detector(spatial_features)
        
        # Stage 6: Connection inference
        connections = self.connection_predictor(
            spatial_features,
            ducts,
            equipment
        )
        
        return {
            "ducts": ducts,
            "equipment": equipment,
            "connections": connections,
            "attention_weights": attention_weights  # For interpretability
        }


class SpatialReasoningBlock(nn.Module):
    """
    Transformer block specialized for spatial relationships
    """
    
    def __init__(self, hidden_dim, num_layers):
        super().__init__()
        
        self.layers = nn.ModuleList([
            SpatialTransformerLayer(hidden_dim)
            for _ in range(num_layers)
        ])
    
    def forward(self, x):
        """
        Args:
            x: [B, N, D] - Patch features
        """
        for layer in self.layers:
            x = layer(x)
        return x


class SpatialTransformerLayer(nn.Module):
    """
    Single transformer layer with spatial bias
    """
    
    def __init__(self, hidden_dim):
        super().__init__()
        
        # Standard multi-head attention
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=12,
            batch_first=True
        )
        
        # Spatial position encoding
        self.spatial_pe = LearnableSpatialPositionalEncoding(hidden_dim)
        
        # Feed-forward network
        self.ffn = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim * 4),
            nn.GELU(),
            nn.Linear(hidden_dim * 4, hidden_dim)
        )
        
        self.norm1 = nn.LayerNorm(hidden_dim)
        self.norm2 = nn.LayerNorm(hidden_dim)
    
    def forward(self, x):
        """
        Args:
            x: [B, N, D] where N = H * W (flattened spatial positions)
        """
        # Add spatial positional encoding
        x_pe = self.spatial_pe(x)
        
        # Self-attention with spatial bias
        attn_out, _ = self.attention(x_pe, x_pe, x_pe)
        x = self.norm1(x + attn_out)
        
        # Feed-forward
        ffn_out = self.ffn(x)
        x = self.norm2(x + ffn_out)
        
        return x


class LearnableSpatialPositionalEncoding(nn.Module):
    """
    Unlike standard positional encoding, this learns spatial relationships
    specific to HVAC drawings (e.g., "ducts typically run horizontally")
    """
    
    def __init__(self, hidden_dim, max_height=100, max_width=100):
        super().__init__()
        
        # Learnable 2D positional embeddings
        self.height_embed = nn.Parameter(torch.randn(max_height, hidden_dim // 2))
        self.width_embed = nn.Parameter(torch.randn(max_width, hidden_dim // 2))
        
        # Learnable scale for spatial importance
        self.spatial_scale = nn.Parameter(torch.ones(1))
    
    def forward(self, x):
        """
        Args:
            x: [B, H*W, D]
        """
        B, N, D = x.shape
        H = W = int(N ** 0.5)  # Assume square
        
        # Create position grid
        h_pos = self.height_embed[:H].unsqueeze(1).repeat(1, W, 1)  # [H, W, D/2]
        w_pos = self.width_embed[:W].unsqueeze(0).repeat(H, 1, 1)   # [H, W, D/2]
        
        # Concatenate
        pos_embed = torch.cat([h_pos, w_pos], dim=-1)  # [H, W, D]
        pos_embed = pos_embed.reshape(H * W, D).unsqueeze(0)  # [1, N, D]
        
        # Add to features
        return x + self.spatial_scale * pos_embed


class ComponentDetectionHead(nn.Module):
    """
    Detection head that outputs both bounding boxes and properties
    """
    
    def __init__(self, hidden_dim, num_classes, output_type):
        super().__init__()
        
        self.output_type = output_type
        
        # Classification
        self.classifier = nn.Linear(hidden_dim, num_classes)
        
        # Bounding box regression (for ducts)
        if output_type == "bbox_with_dims":
            self.bbox_regressor = nn.Linear(hidden_dim, 4)  # x, y, w, h
            self.dimension_regressor = nn.Linear(hidden_dim, 2)  # width, height (inches)
            self.cfm_regressor = nn.Linear(hidden_dim, 1)  # Airflow
        
        # Point detection (for equipment)
        elif output_type == "point_with_properties":
            self.point_regressor = nn.Linear(hidden_dim, 2)  # x, y
            self.property_regressor = nn.Linear(hidden_dim, 8)  # CFM, HP, voltage, etc.
        
        # Confidence scoring
        self.confidence_head = nn.Linear(hidden_dim, 1)
    
    def forward(self, features):
        """
        Args:
            features: [B, N, D]
            
        Returns:
            detections: List of detected components with properties
        """
        # Classify component type
        class_logits = self.classifier(features)
        
        # Get component locations and properties
        if self.output_type == "bbox_with_dims":
            bboxes = self.bbox_regressor(features)
            dimensions = self.dimension_regressor(features)
            cfm = self.cfm_regressor(features)
            
            detections = {
                "class_logits": class_logits,
                "bboxes": bboxes,
                "dimensions": dimensions,
                "cfm": cfm
            }
        
        else:  # point_with_properties
            points = self.point_regressor(features)
            properties = self.property_regressor(features)
            
            detections = {
                "class_logits": class_logits,
                "points": points,
                "properties": properties
            }
        
        # Confidence for each detection
        detections["confidence"] = torch.sigmoid(self.confidence_head(features))
        
        return detections
```

### Key Innovations in HVLT

1. **Cross-Modal Attention**: Vision features query text features
   - "I see a box here, what does the annotation say?"
   - Attention weights = interpretability

2. **Spatial Reasoning Block**: Specialized for 2D engineering drawings
   - Learns that ducts run in straight lines
   - Equipment typically at intersections
   - Annotations near their referenced components

3. **Multi-Task Heads**: Different detection strategies
   - Ducts: Bounding boxes + dimensions
   - Equipment: Point locations + properties
   - All with confidence scores

---

## Architecture 2: Spatial Graph Neural Network (SGNN)

### Conceptual Overview

```
Drawing → Component Detection
    ↓
Construct Spatial Graph:
  - Nodes = Components
  - Edges = Spatial Proximity + Logical Connections
    ↓
Graph Neural Network
    ↓
Connection Classification
System-Level Reasoning
```

### Why Graphs for HVAC?

HVAC systems are **inherently graphs**:
- **Nodes**: Ducts, equipment, diffusers
- **Edges**: Physical connections, airflow paths
- **Graph properties**: Must form connected network, flow conservation

### Implementation

```python
import torch
import torch.nn as nn
import torch_geometric
from torch_geometric.nn import GCNConv, GATConv, global_mean_pool

class HVACSpatialGraphNetwork(nn.Module):
    """
    Converts drawing to graph, then reasons over spatial relationships
    """
    
    def __init__(
        self,
        node_feature_dim: int = 256,
        edge_feature_dim: int = 64,
        hidden_dim: int = 512,
        num_gnn_layers: int = 6
    ):
        super().__init__()
        
        # Stage 1: Component Detection (from HVLT or standalone)
        self.component_detector = ComponentDetector()
        
        # Stage 2: Graph Construction
        self.graph_builder = SpatialGraphBuilder()
        
        # Stage 3: Graph Neural Network Layers
        self.gnn_layers = nn.ModuleList([
            HVACGraphLayer(
                in_channels=hidden_dim,
                out_channels=hidden_dim,
                edge_dim=edge_feature_dim
            )
            for _ in range(num_gnn_layers)
        ])
        
        # Stage 4: Connection Prediction
        self.edge_classifier = EdgeClassifier(hidden_dim)
        
        # Stage 5: System-Level Reasoning
        self.system_validator = SystemLevelValidator(hidden_dim)
    
    def forward(self, image):
        """
        Args:
            image: [B, 3, H, W]
            
        Returns:
            graph: PyTorch Geometric Data object
            connections: Predicted connections with confidence
            validation_results: System-level checks
        """
        # Stage 1: Detect components
        components = self.component_detector(image)
        # components = {"ducts": [...], "equipment": [...]}
        
        # Stage 2: Build spatial graph
        graph = self.graph_builder(components)
        # graph.x: [num_nodes, node_feature_dim] - Node features
        # graph.edge_index: [2, num_edges] - Edge connectivity
        # graph.edge_attr: [num_edges, edge_feature_dim] - Edge features
        
        # Stage 3: Graph reasoning
        x = graph.x
        edge_index = graph.edge_index
        edge_attr = graph.edge_attr
        
        for gnn_layer in self.gnn_layers:
            x = gnn_layer(x, edge_index, edge_attr)
        
        # Updated node features
        graph.x = x
        
        # Stage 4: Predict which edges are actual connections
        connection_probs = self.edge_classifier(x, edge_index, edge_attr)
        
        # Stage 5: System-level validation
        validation = self.system_validator(graph, connection_probs)
        
        return {
            "graph": graph,
            "connections": connection_probs,
            "validation": validation
        }


class SpatialGraphBuilder(nn.Module):
    """
    Constructs graph from detected components
    """
    
    def __init__(self, connection_radius: float = 50.0):
        super().__init__()
        self.connection_radius = connection_radius
    
    def forward(self, components):
        """
        Args:
            components: Dict with detected ducts, equipment
            
        Returns:
            graph: PyTorch Geometric Data object
        """
        # Combine all components into nodes
        nodes = []
        node_types = []
        positions = []
        
        for duct in components["ducts"]:
            nodes.append(self.encode_duct(duct))
            node_types.append(0)  # Type: duct
            positions.append(duct["center"])
        
        for equip in components["equipment"]:
            nodes.append(self.encode_equipment(equip))
            node_types.append(1)  # Type: equipment
            positions.append(equip["location"])
        
        # Stack into tensor
        x = torch.stack(nodes)  # [num_nodes, feature_dim]
        positions = torch.tensor(positions)  # [num_nodes, 2]
        
        # Build edges based on spatial proximity
        edge_index, edge_attr = self.build_edges(positions, node_types)
        
        # Create PyG Data object
        from torch_geometric.data import Data
        
        graph = Data(
            x=x,
            edge_index=edge_index,
            edge_attr=edge_attr,
            pos=positions
        )
        
        return graph
    
    def build_edges(self, positions, node_types):
        """
        Connect nodes that are spatially close
        
        Edge types:
        - 0: Potential duct-duct connection
        - 1: Potential duct-equipment connection
        - 2: Potential equipment-equipment connection
        """
        num_nodes = len(positions)
        edges = []
        edge_features = []
        
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                # Calculate distance
                dist = torch.norm(positions[i] - positions[j])
                
                if dist < self.connection_radius:
                    # Add bidirectional edge
                    edges.append([i, j])
                    edges.append([j, i])
                    
                    # Edge features: [distance, angle, type_i, type_j]
                    angle = self.calculate_angle(positions[i], positions[j])
                    
                    edge_feat = torch.tensor([
                        dist,
                        angle,
                        node_types[i],
                        node_types[j]
                    ])
                    
                    edge_features.append(edge_feat)
                    edge_features.append(edge_feat)  # Same for both directions
        
        edge_index = torch.tensor(edges).t()  # [2, num_edges]
        edge_attr = torch.stack(edge_features)  # [num_edges, 4]
        
        return edge_index, edge_attr
    
    def encode_duct(self, duct):
        """Encode duct as node feature vector"""
        return torch.tensor([
            duct["width"],
            duct["height"],
            duct["cfm"] if duct["cfm"] else 0,
            duct["length"],
            1 if duct["system"] == "supply" else 0,
            1 if duct["system"] == "return" else 0
        ])
    
    def encode_equipment(self, equip):
        """Encode equipment as node feature vector"""
        return torch.tensor([
            equip["cfm"] if equip["cfm"] else 0,
            equip["static_pressure"] if equip["static_pressure"] else 0,
            equip["motor_hp"] if equip["motor_hp"] else 0,
            1 if equip["type"] == "air_handler" else 0,
            1 if equip["type"] == "exhaust_fan" else 0,
            1 if equip["type"] == "vav" else 0
        ])
    
    @staticmethod
    def calculate_angle(pos1, pos2):
        """Calculate angle between two positions"""
        delta = pos2 - pos1
        return torch.atan2(delta[1], delta[0])


class HVACGraphLayer(nn.Module):
    """
    Graph attention layer specialized for HVAC spatial reasoning
    """
    
    def __init__(self, in_channels, out_channels, edge_dim):
        super().__init__()
        
        # Graph Attention with edge features
        self.gat = GATConv(
            in_channels=in_channels,
            out_channels=out_channels,
            heads=8,
            edge_dim=edge_dim,
            concat=False  # Average multi-head outputs
        )
        
        # Residual connection
        self.residual = nn.Linear(in_channels, out_channels) if in_channels != out_channels else nn.Identity()
        
        self.norm = nn.LayerNorm(out_channels)
    
    def forward(self, x, edge_index, edge_attr):
        """
        Args:
            x: [num_nodes, in_channels]
            edge_index: [2, num_edges]
            edge_attr: [num_edges, edge_dim]
        """
        # Graph attention
        out = self.gat(x, edge_index, edge_attr)
        
        # Residual + norm
        out = self.norm(out + self.residual(x))
        
        return out


class EdgeClassifier(nn.Module):
    """
    Classify which edges are actual HVAC connections
    """
    
    def __init__(self, hidden_dim):
        super().__init__()
        
        self.edge_mlp = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x, edge_index, edge_attr):
        """
        Args:
            x: [num_nodes, hidden_dim] - Updated node features
            edge_index: [2, num_edges]
            edge_attr: [num_edges, edge_dim]
            
        Returns:
            connection_probs: [num_edges] - Probability each edge is a real connection
        """
        # Get node features for each edge
        src_nodes = x[edge_index[0]]  # [num_edges, hidden_dim]
        dst_nodes = x[edge_index[1]]  # [num_edges, hidden_dim]
        
        # Concatenate source + destination features
        edge_features = torch.cat([src_nodes, dst_nodes], dim=-1)
        
        # Classify
        connection_probs = self.edge_mlp(edge_features).squeeze(-1)
        
        return connection_probs


class SystemLevelValidator(nn.Module):
    """
    Check system-level constraints using graph structure
    """
    
    def __init__(self, hidden_dim):
        super().__init__()
        
        # Global graph pooling
        self.graph_pool = global_mean_pool
        
        # System-level checks
        self.system_classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 4),  # 4 validation checks
            nn.Sigmoid()
        )
    
    def forward(self, graph, connection_probs):
        """
        Args:
            graph: PyG Data object
            connection_probs: [num_edges]
            
        Returns:
            validation_scores: {
                "airflow_balance": score,
                "connectivity": score,
                "redundancy": score,
                "code_compliance": score
            }
        """
        # Pool graph to single vector
        batch = torch.zeros(graph.x.size(0), dtype=torch.long)
        graph_embedding = self.graph_pool(graph.x, batch)
        
        # System-level checks
        checks = self.system_classifier(graph_embedding)
        
        return {
            "airflow_balance": checks[0].item(),
            "connectivity": checks[1].item(),
            "redundancy": checks[2].item(),
            "code_compliance": checks[3].item()
        }
```

### Key Innovations in SGNN

1. **Explicit Spatial Graph**: Components → nodes, proximity → edges
   - Makes spatial relationships first-class citizens
   - Graph structure matches HVAC system structure

2. **Graph Attention with Edge Features**:
   - Attention weights based on distance, angle, component types
   - Learns which connections are physically/logically possible

3. **System-Level Reasoning**:
   - Graph pooling captures global system properties
   - Checks: Is system connected? Balanced? Code-compliant?

---

## Architecture 3: Multi-Scale Vision Transformer (MSVT)

### Conceptual Overview

Different scales for different abstractions:

```
Coarse Scale (8x downsampled):
- Room layout
- Major equipment zones
- Supply/return system separation

Medium Scale (4x downsampled):
- Duct routes
- Equipment locations
- Major branches

Fine Scale (2x downsampled):
- Duct dimensions
- Text annotations
- Fittings and connections
```

### Implementation

```python
class MultiScaleVisionTransformer(nn.Module):
    """
    Process drawing at multiple scales simultaneously
    """
    
    def __init__(
        self,
        scales=[8, 4, 2],  # Downsampling factors
        hidden_dim=768,
        num_layers_per_scale=4
    ):
        super().__init__()
        
        self.scales = scales
        
        # Separate encoder for each scale
        self.scale_encoders = nn.ModuleList([
            ScaleSpecificEncoder(
                scale=s,
                hidden_dim=hidden_dim,
                num_layers=num_layers_per_scale
            )
            for s in scales
        ])
        
        # Cross-scale fusion
        self.scale_fusion = CrossScaleFusion(
            num_scales=len(scales),
            hidden_dim=hidden_dim
        )
        
        # Task-specific heads
        self.coarse_head = CoarseLayoutHead(hidden_dim)    # System layout
        self.medium_head = MediumComponentHead(hidden_dim)  # Component detection
        self.fine_head = FineDetailHead(hidden_dim)        # Dimensions, text
    
    def forward(self, image):
        """
        Args:
            image: [B, 3, H, W]
        """
        # Process each scale
        scale_features = []
        
        for encoder in self.scale_encoders:
            features = encoder(image)
            scale_features.append(features)
        
        # Fuse across scales
        fused_features = self.scale_fusion(scale_features)
        
        # Extract information at each scale
        coarse_output = self.coarse_head(fused_features[0])    # Layout
        medium_output = self.medium_head(fused_features[1])    # Components
        fine_output = self.fine_head(fused_features[2])        # Details
        
        return {
            "layout": coarse_output,
            "components": medium_output,
            "details": fine_output
        }


class ScaleSpecificEncoder(nn.Module):
    """
    Vision transformer optimized for specific scale
    """
    
    def __init__(self, scale, hidden_dim, num_layers):
        super().__init__()
        
        self.scale = scale
        
        # Convolutional stem (downsampling)
        self.stem = nn.Sequential(
            nn.Conv2d(3, hidden_dim // 4, kernel_size=3, stride=scale, padding=1),
            nn.BatchNorm2d(hidden_dim // 4),
            nn.ReLU(),
            nn.Conv2d(hidden_dim // 4, hidden_dim, kernel_size=3, padding=1),
            nn.BatchNorm2d(hidden_dim),
            nn.ReLU()
        )
        
        # Transformer layers
        self.transformer = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=hidden_dim,
                nhead=12,
                dim_feedforward=hidden_dim * 4,
                batch_first=True
            )
            for _ in range(num_layers)
        ])
    
    def forward(self, x):
        """
        Args:
            x: [B, 3, H, W]
        Returns:
            features: [B, num_patches, hidden_dim]
        """
        # Downsample
        x = self.stem(x)  # [B, hidden_dim, H/scale, W/scale]
        
        # Flatten to patches
        B, C, H, W = x.shape
        x = x.flatten(2).transpose(1, 2)  # [B, H*W, C]
        
        # Transformer
        for layer in self.transformer:
            x = layer(x)
        
        return x


class CrossScaleFusion(nn.Module):
    """
    Fuse information across scales
    Coarse scale provides context for fine scale
    """
    
    def __init__(self, num_scales, hidden_dim):
        super().__init__()
        
        # Upsampling to align scales
        self.upsamplers = nn.ModuleList([
            nn.ConvTranspose2d(hidden_dim, hidden_dim, kernel_size=2**(i+1), stride=2**(i+1))
            for i in range(num_scales - 1)
        ])
        
        # Cross-scale attention
        self.cross_scale_attn = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=12,
            batch_first=True
        )
    
    def forward(self, scale_features):
        """
        Args:
            scale_features: List of [B, N_i, D] for each scale
        """
        # Coarse scale provides context for finer scales
        coarse_context = scale_features[0]
        
        fused = []
        
        for i, fine_features in enumerate(scale_features):
            # Use coarse features as context
            fused_features, _ = self.cross_scale_attn(
                query=fine_features,
                key=coarse_context,
                value=coarse_context
            )
            
            fused.append(fused_features + fine_features)  # Residual
        
        return fused
```

---

## Architecture 4: Neuro-Symbolic Hybrid (NSH)

### Conceptual Overview

Combine neural networks (learning) with symbolic rules (domain knowledge):

```
Neural Component:
- Vision transformer
- Component detection
- Feature extraction

↓ Interface ↓

Symbolic Component:
- HVAC physics rules
- Building codes
- Engineering constraints

→ Validated Output
```

### Implementation

```python
class NeuroSymbolicHVACSystem(nn.Module):
    """
    Hybrid architecture combining learned and rule-based reasoning
    """
    
    def __init__(self):
        super().__init__()
        
        # Neural component: Learning-based
        self.neural_extractor = HVACVisionLanguageTransformer()
        
        # Symbolic component: Rule-based
        self.symbolic_validator = SymbolicReasoningEngine()
        
        # Bridge: Neural-symbolic interface
        self.neural_to_symbolic = NeuralSymbolicBridge()
    
    def forward(self, image):
        # Stage 1: Neural extraction
        neural_output = self.neural_extractor(image)
        
        # Stage 2: Convert to symbolic representation
        symbolic_graph = self.neural_to_symbolic(neural_output)
        
        # Stage 3: Apply symbolic rules
        validated_output = self.symbolic_validator(symbolic_graph)
        
        return {
            "neural_predictions": neural_output,
            "symbolic_graph": symbolic_graph,
            "validated_output": validated_output,
            "rule_violations": validated_output.violations
        }


class SymbolicReasoningEngine:
    """
    Encodes HVAC domain knowledge as executable rules
    Uses logic programming / constraint satisfaction
    """
    
    def __init__(self):
        # Define rules
        self.rules = [
            AirflowContinuityRule(),
            DuctSizingRule(),
            PressureBalanceRule(),
            CodeComplianceRule(),
            TopologyRule()
        ]
    
    def __call__(self, symbolic_graph):
        """
        Apply all rules to symbolic graph
        
        Args:
            symbolic_graph: Logic representation of HVAC system
            
        Returns:
            Validated graph + violations
        """
        violations = []
        
        for rule in self.rules:
            rule_violations = rule.check(symbolic_graph)
            violations.extend(rule_violations)
        
        # Attempt to repair violations
        repaired_graph = self.repair(symbolic_graph, violations)
        
        return ValidationResult(
            graph=repaired_graph,
            violations=violations,
            confidence=self.calculate_confidence(violations)
        )
    
    def repair(self, graph, violations):
        """
        Attempt automatic repairs for violations
        """
        repaired = graph.copy()
        
        for violation in violations:
            if violation.type == "airflow_mismatch":
                # Try to infer missing ducts
                repaired = self.infer_missing_ducts(repaired, violation)
            
            elif violation.type == "sizing_error":
                # Suggest corrected sizes
                repaired = self.correct_duct_size(repaired, violation)
        
        return repaired


class AirflowContinuityRule:
    """
    Rule: Supply fan CFM must equal sum of branch CFM
    """
    
    def check(self, graph):
        violations = []
        
        for fan in graph.get_nodes_by_type("supply_fan"):
            # Get all downstream ducts
            downstream_ducts = graph.get_downstream_nodes(fan, type="duct")
            
            # Sum CFM
            fan_cfm = fan.properties["cfm"]
            total_branch_cfm = sum(d.properties["cfm"] for d in downstream_ducts if d.properties["cfm"])
            
            # Check tolerance
            if abs(fan_cfm - total_branch_cfm) > 0.1 * fan_cfm:
                violations.append(RuleViolation(
                    rule="airflow_continuity",
                    component=fan.id,
                    severity="high",
                    message=f"Fan {fan_cfm} CFM != branches {total_branch_cfm} CFM",
                    suggestion="Missing ducts or incorrect fan capacity"
                ))
        
        return violations


class DuctSizingRule:
    """
    Rule: Duct size must match CFM per ASHRAE guidelines
    """
    
    VELOCITY_LIMITS = {
        "main_supply": (1500, 2000),
        "branch_supply": (800, 1500)
    }
    
    def check(self, graph):
        violations = []
        
        for duct in graph.get_nodes_by_type("duct"):
            if not (duct.properties["cfm"] and duct.properties["width"] and duct.properties["height"]):
                continue
            
            # Calculate velocity
            area_sqft = (duct.properties["width"] * duct.properties["height"]) / 144
            velocity = duct.properties["cfm"] / area_sqft
            
            # Check limits
            duct_type = "main_supply" if duct.properties["is_main"] else "branch_supply"
            min_vel, max_vel = self.VELOCITY_LIMITS[duct_type]
            
            if velocity > max_vel:
                # Calculate correct size
                correct_area = duct.properties["cfm"] / max_vel
                correct_height = duct.properties["height"]
                correct_width = (correct_area * 144) / correct_height
                
                violations.append(RuleViolation(
                    rule="duct_sizing",
                    component=duct.id,
                    severity="medium",
                    message=f"Velocity {velocity:.0f} FPM > {max_vel} FPM",
                    suggestion=f"Increase width from {duct.properties['width']} to {correct_width:.0f} inches"
                ))
        
        return violations
```

### Neuro-Symbolic Bridge

```python
class NeuralSymbolicBridge:
    """
    Converts neural network outputs to symbolic representations
    """
    
    def __call__(self, neural_output):
        """
        Args:
            neural_output: {ducts: [...], equipment: [...], connections: [...]}
            
        Returns:
            symbolic_graph: Logic-based representation
        """
        from logic import LogicGraph, Node, Edge, Property
        
        graph = LogicGraph()
        
        # Convert ducts to logic nodes
        for duct in neural_output["ducts"]:
            node = Node(
                id=duct["id"],
                type="duct",
                properties={
                    Property("width", duct["width"]),
                    Property("height", duct["height"]),
                    Property("cfm", duct["cfm"]),
                    Property("system", duct["system"])
                },
                confidence=duct["confidence"]
            )
            graph.add_node(node)
        
        # Convert equipment
        for equip in neural_output["equipment"]:
            node = Node(
                id=equip["id"],
                type=equip["type"],
                properties={
                    Property("cfm", equip["cfm"]),
                    Property("location", equip["location"])
                },
                confidence=equip["confidence"]
            )
            graph.add_node(node)
        
        # Convert connections to edges
        for conn in neural_output["connections"]:
            edge = Edge(
                from_node=conn["from"],
                to_node=conn["to"],
                type=conn["type"],
                confidence=conn["confidence"]
            )
            graph.add_edge(edge)
        
        return graph
```

---

## Recommended Hybrid Architecture

**Combine the best of all approaches:**

```
Input: PDF Drawing
    ↓
[HVLT] Vision-Language Transformer
    ↓
Component Detection + Features
    ↓
[SGNN] Spatial Graph Construction
    ↓
Graph-Based Reasoning
    ↓
[NSH] Symbolic Validation
    ↓
Validated Output
```

### Implementation

```python
class RevitAssistHybridArchitecture(nn.Module):
    """
    Production architecture combining all approaches
    """
    
    def __init__(self):
        super().__init__()
        
        # Stage 1: Vision-Language extraction (HVLT)
        self.extractor = HVACVisionLanguageTransformer(
            vision_encoder="openai/clip-vit-large-patch14",
            hidden_dim=768
        )
        
        # Stage 2: Spatial graph reasoning (SGNN)
        self.graph_reasoner = HVACSpatialGraphNetwork(
            node_feature_dim=256,
            hidden_dim=512,
            num_gnn_layers=6
        )
        
        # Stage 3: Symbolic validation (NSH)
        self.validator = SymbolicReasoningEngine()
        
        # Multi-scale processing (MSVT) - optional refinement
        self.multiscale_refiner = MultiScaleVisionTransformer(
            scales=[8, 4, 2],
            hidden_dim=768
        )
    
    def forward(self, image, text_annotations=None):
        # Stage 1: Extract components
        extraction_result = self.extractor(image, text_annotations)
        
        # Stage 2: Graph reasoning
        graph_result = self.graph_reasoner.forward_from_components(
            extraction_result["ducts"],
            extraction_result["equipment"]
        )
        
        # Stage 3: Symbolic validation
        validation_result = self.validator(
            graph_result["graph"],
            graph_result["connections"]
        )
        
        # Optional: Multi-scale refinement for low-confidence components
        low_conf_components = self.find_low_confidence(extraction_result)
        if low_conf_components:
            refinement = self.multiscale_refiner(image)
            extraction_result = self.merge_refinement(
                extraction_result,
                refinement,
                low_conf_components
            )
        
        return {
            "components": extraction_result,
            "graph": graph_result["graph"],
            "connections": graph_result["connections"],
            "validation": validation_result,
            "confidence_map": self.generate_confidence_map(extraction_result)
        }
```

---

## Training Strategy

### Multi-Task Learning

```python
class HVACMultiTaskLoss(nn.Module):
    """
    Combined loss for all tasks
    """
    
    def __init__(self):
        super().__init__()
        
        # Component detection loss
        self.detection_loss = nn.CrossEntropyLoss()
        
        # Bounding box regression loss
        self.bbox_loss = nn.SmoothL1Loss()
        
        # Connection prediction loss
        self.connection_loss = nn.BCEWithLogitsLoss()
        
        # Property regression loss
        self.property_loss = nn.MSELoss()
        
        # Validation loss (symbolic rules)
        self.validation_loss = SymbolicRuleLoss()
        
        # Loss weights
        self.weights = {
            "detection": 1.0,
            "bbox": 0.5,
            "connection": 1.5,  # Higher weight - critical
            "property": 0.8,
            "validation": 2.0   # Highest - enforce constraints
        }
    
    def forward(self, predictions, targets):
        loss = 0
        
        # Component detection
        loss += self.weights["detection"] * self.detection_loss(
            predictions["class_logits"],
            targets["class_labels"]
        )
        
        # Bounding boxes
        loss += self.weights["bbox"] * self.bbox_loss(
            predictions["bboxes"],
            targets["bboxes"]
        )
        
        # Connections
        loss += self.weights["connection"] * self.connection_loss(
            predictions["connections"],
            targets["connections"]
        )
        
        # Properties (CFM, dimensions)
        loss += self.weights["property"] * self.property_loss(
            predictions["properties"],
            targets["properties"]
        )
        
        # Symbolic rule violations
        loss += self.weights["validation"] * self.validation_loss(
            predictions["validation"],
            targets["ground_truth_rules"]
        )
        
        return loss
```

---

## Comparison Summary

| Architecture | Strength | Weakness | Best For |
|--------------|----------|----------|----------|
| **HVLT** | Vision + text fusion | May miss spatial patterns | Component extraction |
| **SGNN** | Explicit spatial reasoning | Needs good initial detection | Connection inference |
| **MSVT** | Multi-scale understanding | Computationally expensive | Complex layouts |
| **NSH** | Hard constraints | Requires rule engineering | Validation |
| **Hybrid** | Best of all | More complex | Production system |

**Recommended for RevitAssist:** Hybrid architecture (HVLT → SGNN → NSH)

---

**Document Version:** 1.0  
**Last Updated:** January 2025
