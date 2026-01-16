"""
YOLOv9 HVAC Component Detector
Wrapper for YOLOv9 model trained on HVAC components
"""

import torch
import cv2
import numpy as np
from typing import List, Dict
from ultralytics import YOLO

class YOLODetector:
    """
    YOLOv9 detector for HVAC components
    """
    
    # HVAC component classes
    CLASSES = [
        "duct_supply_rect",      # 0
        "duct_return_rect",      # 1
        "duct_supply_round",     # 2
        "diffuser_ceiling_sq",   # 3
        "diffuser_ceiling_rd",   # 4
        "grille_supply",         # 5
        "grille_return",         # 6
        "vav_box",               # 7
        "fan_exhaust",           # 8
        "air_handler",           # 9
        "fitting_elbow_90",      # 10
        "fitting_tee",           # 11
        "damper_volume",         # 12
        "annotation_dimension",  # 13
        "annotation_text",       # 14
        "annotation_flow_arrow"  # 15
    ]
    
    def __init__(self, model_path: str, device: str = "cuda"):
        """
        Initialize YOLO detector
        
        Args:
            model_path: Path to trained YOLOv9 weights (.pt file)
            device: "cuda" or "cpu"
        """
        self.device = device
        self.model_name = "YOLOv9-E"
        
        # Load model
        self.model = YOLO(model_path)
        self.model.to(device)
        
        self.classes = self.CLASSES
    
    def detect(
        self,
        image: np.ndarray,
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        img_size: int = 1920
    ) -> List[Dict]:
        """
        Detect HVAC components in image
        
        Args:
            image: Input image (BGR format)
            conf_threshold: Confidence threshold for detections
            iou_threshold: IoU threshold for NMS
            img_size: Input image size for model
            
        Returns:
            List of detections with bbox, class, confidence
        """
        # Run inference
        results = self.model.predict(
            image,
            conf=conf_threshold,
            iou=iou_threshold,
            imgsz=img_size,
            device=self.device,
            verbose=False
        )
        
        # Parse results
        detections = []
        
        for result in results:
            boxes = result.boxes
            
            for i in range(len(boxes)):
                # Get box coordinates (xyxy format)
                x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()
                
                # Convert to xywh format
                x = float(x1)
                y = float(y1)
                w = float(x2 - x1)
                h = float(y2 - y1)
                
                # Get class and confidence
                class_id = int(boxes.cls[i])
                confidence = float(boxes.conf[i])
                
                detection = {
                    'bbox': [x, y, w, h],
                    'class': class_id,
                    'class_name': self.CLASSES[class_id],
                    'confidence': confidence
                }
                
                detections.append(detection)
        
        return detections
    
    def detect_and_visualize(
        self,
        image: np.ndarray,
        conf_threshold: float = 0.5,
        save_path: str = None
    ) -> np.ndarray:
        """
        Detect components and draw bounding boxes
        
        Args:
            image: Input image
            conf_threshold: Confidence threshold
            save_path: Optional path to save visualization
            
        Returns:
            Image with drawn bounding boxes
        """
        detections = self.detect(image, conf_threshold=conf_threshold)
        
        # Create copy for drawing
        vis_image = image.copy()
        
        # Color map for different classes
        colors = self._get_colors(len(self.CLASSES))
        
        for det in detections:
            x, y, w, h = det['bbox']
            class_id = det['class']
            confidence = det['confidence']
            class_name = det['class_name']
            
            # Draw rectangle
            color = colors[class_id]
            cv2.rectangle(
                vis_image,
                (int(x), int(y)),
                (int(x + w), int(y + h)),
                color,
                2
            )
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size, _ = cv2.getTextSize(
                label,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                1
            )
            
            cv2.rectangle(
                vis_image,
                (int(x), int(y) - label_size[1] - 10),
                (int(x) + label_size[0], int(y)),
                color,
                -1
            )
            
            cv2.putText(
                vis_image,
                label,
                (int(x), int(y) - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
        
        if save_path:
            cv2.imwrite(save_path, vis_image)
        
        return vis_image
    
    def _get_colors(self, n_classes: int) -> List[tuple]:
        """Generate distinct colors for each class"""
        np.random.seed(42)
        colors = []
        for i in range(n_classes):
            colors.append(tuple(np.random.randint(0, 255, 3).tolist()))
        return colors
    
    @property
    def num_classes(self) -> int:
        """Get number of classes"""
        return len(self.CLASSES)
