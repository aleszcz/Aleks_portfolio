"""
HVAC Drawing Processor
Main processing pipeline for HVAC drawings
"""

import cv2
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
import torch

from models.yolo_detector import YOLODetector
from models.spatial_reasoner import SpatialReasoner
from utils.validator import HVACValidator
from utils.scale_detector import ScaleDetector

@dataclass
class Component:
    """Detected HVAC component"""
    id: str
    type: str
    sub_type: str
    bbox: List[float]  # [x, y, width, height]
    confidence: float
    properties: Dict[str, str]
    revit_family: str
    center: tuple  # (x, y)

@dataclass
class ComponentConnection:
    """Connection between components"""
    from_id: str
    to_id: str
    conn_type: str  # "supply", "return", "exhaust"
    confidence: float

@dataclass
class Issue:
    """Validation issue"""
    severity: str
    message: str
    component_id: Optional[str]

@dataclass
class ProcessingOutput:
    """Complete processing result"""
    components: List[Component]
    connections: List[ComponentConnection]
    issues: List[Issue]
    avg_confidence: float
    scale: str

class HVACProcessor:
    """
    Main processor for HVAC drawings
    Coordinates all AI models and processing steps
    """
    
    def __init__(self, model_path: str, device: str = "cuda"):
        """
        Initialize processor with AI models
        
        Args:
            model_path: Path to YOLOv9 model weights
            device: "cuda" or "cpu"
        """
        self.device = torch.device(device)
        
        # Load AI models
        self.detector = YOLODetector(model_path, device)
        self.spatial_reasoner = SpatialReasoner()
        self.validator = HVACValidator()
        self.scale_detector = ScaleDetector()
        
        # HVAC component type mapping
        self.type_mapping = {
            0: ("duct", "supply_rectangular"),
            1: ("duct", "return_rectangular"),
            2: ("duct", "supply_round"),
            3: ("diffuser", "ceiling_square"),
            4: ("diffuser", "ceiling_round"),
            5: ("grille", "supply"),
            6: ("grille", "return"),
            7: ("vav_box", "standard"),
            8: ("fan", "exhaust"),
            9: ("equipment", "air_handler"),
            10: ("fitting", "elbow_90"),
            11: ("fitting", "tee"),
            12: ("damper", "volume"),
            13: ("annotation", "dimension"),
            14: ("annotation", "text"),
            15: ("annotation", "flow_arrow")
        }
        
        # Revit family mapping
        self.revit_families = {
            ("duct", "supply_rectangular"): "Supply Duct - Rectangular",
            ("duct", "return_rectangular"): "Return Duct - Rectangular",
            ("duct", "supply_round"): "Supply Duct - Round",
            ("diffuser", "ceiling_square"): "Ceiling Diffuser - Square",
            ("diffuser", "ceiling_round"): "Ceiling Diffuser - Round",
            ("grille", "supply"): "Supply Grille",
            ("grille", "return"): "Return Grille",
            ("vav_box", "standard"): "VAV Box - Standard",
            ("fan", "exhaust"): "Exhaust Fan",
            ("equipment", "air_handler"): "Air Handling Unit",
            ("fitting", "elbow_90"): "Duct Elbow - 90 Degree",
            ("fitting", "tee"): "Duct Tee",
            ("damper", "volume"): "Volume Damper"
        }
    
    def process_drawing(
        self,
        pdf_path: str,
        drawing_type: str = "hvac_plan",
        level_name: Optional[str] = None,
        scale: Optional[str] = None,
        mode: str = "standard"
    ) -> ProcessingOutput:
        """
        Process HVAC drawing through complete pipeline
        
        Args:
            pdf_path: Path to PDF or image file
            drawing_type: Type of drawing (hvac_plan, etc.)
            level_name: Target Revit level name
            scale: Drawing scale (e.g., "1/4\" = 1'-0\"")
            mode: Processing mode (standard, high_accuracy, fast_preview)
            
        Returns:
            ProcessingOutput with all detected components and connections
        """
        # Step 1: Load and preprocess image
        image = self._load_image(pdf_path)
        
        # Step 2: Detect scale if not provided
        if scale is None:
            scale = self.scale_detector.detect_scale(image)
        
        # Step 3: Detect components
        detections = self.detector.detect(image, conf_threshold=0.5)
        
        # Step 4: Convert to component objects
        components = self._create_components(detections, scale)
        
        # Step 5: Infer spatial connections
        connections = self.spatial_reasoner.infer_connections(
            components,
            image
        )
        
        # Step 6: Validate HVAC logic
        issues = self.validator.validate(components, connections)
        
        # Step 7: Calculate statistics
        avg_confidence = np.mean([c.confidence for c in components])
        
        return ProcessingOutput(
            components=components,
            connections=connections,
            issues=issues,
            avg_confidence=float(avg_confidence),
            scale=scale
        )
    
    def _load_image(self, file_path: str) -> np.ndarray:
        """Load image from PDF or image file"""
        if file_path.lower().endswith('.pdf'):
            # Convert PDF to image (first page)
            from pdf2image import convert_from_path
            images = convert_from_path(file_path, first_page=1, last_page=1)
            image = np.array(images[0])
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        else:
            # Load image directly
            image = cv2.imread(file_path)
        
        return image
    
    def _create_components(
        self,
        detections: List[Dict],
        scale: str
    ) -> List[Component]:
        """Convert YOLO detections to Component objects"""
        components = []
        
        for i, det in enumerate(detections):
            class_id = int(det['class'])
            bbox = det['bbox']  # [x, y, width, height]
            
            # Get component type
            comp_type, sub_type = self.type_mapping.get(
                class_id,
                ("unknown", "unknown")
            )
            
            # Get Revit family
            revit_family = self.revit_families.get(
                (comp_type, sub_type),
                "Generic Model"
            )
            
            # Extract properties from detection
            properties = self._extract_properties(det, comp_type)
            
            # Calculate center point
            center = (
                bbox[0] + bbox[2] / 2,
                bbox[1] + bbox[3] / 2
            )
            
            component = Component(
                id=f"{comp_type}_{i}",
                type=comp_type,
                sub_type=sub_type,
                bbox=bbox,
                confidence=det['confidence'],
                properties=properties,
                revit_family=revit_family,
                center=center
            )
            
            components.append(component)
        
        return components
    
    def _extract_properties(
        self,
        detection: Dict,
        comp_type: str
    ) -> Dict[str, str]:
        """Extract component properties from detection"""
        properties = {}
        
        # Add basic properties
        bbox = detection['bbox']
        properties['width'] = str(bbox[2])
        properties['height'] = str(bbox[3])
        
        # Type-specific properties
        if comp_type == "duct":
            # TODO: Extract CFM from nearby text
            properties['cfm'] = "TBD"
            properties['size'] = f"{bbox[2]:.0f}x{bbox[3]:.0f}"
        
        elif comp_type == "diffuser":
            properties['type'] = "Supply"
            properties['size'] = f"{max(bbox[2], bbox[3]):.0f}"
        
        return properties
