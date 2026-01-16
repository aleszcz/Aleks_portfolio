"""
Spatial Reasoner for HVAC Components
Infers connections between detected components
"""

import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
import networkx as nx

@dataclass
class SpatialConnection:
    """Spatial connection between components"""
    from_id: str
    to_id: str
    conn_type: str
    confidence: float
    distance: float

class SpatialReasoner:
    """
    Infers spatial relationships and connections between HVAC components
    Uses graph neural network approach
    """
    
    def __init__(self, max_connection_distance: float = 100.0):
        """
        Initialize spatial reasoner
        
        Args:
            max_connection_distance: Maximum pixel distance for connections
        """
        self.max_distance = max_connection_distance
        
        # Connection rules by component type
        self.connection_rules = {
            ("equipment", "air_handler"): ["duct"],
            ("duct", "supply_rectangular"): ["duct", "diffuser", "vav_box"],
            ("duct", "return_rectangular"): ["duct", "grille", "equipment"],
            ("vav_box", "standard"): ["duct", "diffuser"],
            ("diffuser", "ceiling_square"): ["duct", "vav_box"],
            ("diffuser", "ceiling_round"): ["duct", "vav_box"]
        }
    
    def infer_connections(
        self,
        components: List,
        image: np.ndarray = None
    ) -> List[SpatialConnection]:
        """
        Infer connections between components
        
        Args:
            components: List of detected components
            image: Original image (for line detection)
            
        Returns:
            List of inferred connections
        """
        connections = []
        
        # Build spatial graph
        graph = self._build_spatial_graph(components)
        
        # Find potential connections
        for comp1 in components:
            for comp2 in components:
                if comp1.id == comp2.id:
                    continue
                
                # Check if connection is possible
                if self._can_connect(comp1, comp2):
                    # Calculate connection confidence
                    confidence = self._calculate_connection_confidence(
                        comp1, comp2, image
                    )
                    
                    if confidence > 0.5:
                        # Determine connection type
                        conn_type = self._infer_connection_type(comp1, comp2)
                        
                        # Calculate distance
                        distance = self._euclidean_distance(
                            comp1.center, comp2.center
                        )
                        
                        connection = SpatialConnection(
                            from_id=comp1.id,
                            to_id=comp2.id,
                            conn_type=conn_type,
                            confidence=confidence,
                            distance=distance
                        )
                        
                        connections.append(connection)
        
        # Remove duplicate/conflicting connections
        connections = self._prune_connections(connections)
        
        return connections
    
    def _build_spatial_graph(self, components: List) -> nx.Graph:
        """Build graph representation of components"""
        G = nx.Graph()
        
        # Add nodes
        for comp in components:
            G.add_node(
                comp.id,
                type=comp.type,
                sub_type=comp.sub_type,
                center=comp.center,
                bbox=comp.bbox
            )
        
        # Add edges based on proximity
        for i, comp1 in enumerate(components):
            for comp2 in components[i+1:]:
                distance = self._euclidean_distance(
                    comp1.center, comp2.center
                )
                
                if distance < self.max_distance:
                    G.add_edge(
                        comp1.id,
                        comp2.id,
                        distance=distance
                    )
        
        return G
    
    def _can_connect(self, comp1, comp2) -> bool:
        """Check if two components can be connected"""
        key = (comp1.type, comp1.sub_type)
        
        if key in self.connection_rules:
            allowed_types = self.connection_rules[key]
            return comp2.type in allowed_types
        
        return False
    
    def _calculate_connection_confidence(
        self,
        comp1,
        comp2,
        image: np.ndarray
    ) -> float:
        """Calculate confidence of connection between components"""
        # Base confidence on distance
        distance = self._euclidean_distance(comp1.center, comp2.center)
        distance_score = 1.0 - min(distance / self.max_distance, 1.0)
        
        # Check alignment (horizontal or vertical)
        alignment_score = self._calculate_alignment(comp1, comp2)
        
        # Check for connecting lines in image
        line_score = 0.0
        if image is not None:
            line_score = self._detect_connecting_line(
                comp1.center, comp2.center, image
            )
        
        # Weighted combination
        confidence = (
            0.3 * distance_score +
            0.3 * alignment_score +
            0.4 * line_score
        )
        
        return confidence
    
    def _calculate_alignment(self, comp1, comp2) -> float:
        """Calculate alignment score (horizontal or vertical)"""
        x1, y1 = comp1.center
        x2, y2 = comp2.center
        
        # Check horizontal alignment
        h_diff = abs(y1 - y2)
        h_threshold = max(comp1.bbox[3], comp2.bbox[3]) / 2
        
        # Check vertical alignment
        v_diff = abs(x1 - x2)
        v_threshold = max(comp1.bbox[2], comp2.bbox[2]) / 2
        
        if h_diff < h_threshold:
            return 1.0  # Horizontally aligned
        elif v_diff < v_threshold:
            return 1.0  # Vertically aligned
        else:
            return 0.5  # Diagonal
    
    def _detect_connecting_line(
        self,
        pt1: Tuple[float, float],
        pt2: Tuple[float, float],
        image: np.ndarray
    ) -> float:
        """
        Detect if there's a line connecting two points
        Uses Hough line detection
        """
        try:
            import cv2
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Create region of interest
            x1, y1 = int(pt1[0]), int(pt1[1])
            x2, y2 = int(pt2[0]), int(pt2[1])
            
            # Expand ROI slightly
            margin = 20
            x_min = max(0, min(x1, x2) - margin)
            x_max = min(gray.shape[1], max(x1, x2) + margin)
            y_min = max(0, min(y1, y2) - margin)
            y_max = min(gray.shape[0], max(y1, y2) + margin)
            
            roi = gray[y_min:y_max, x_min:x_max]
            
            # Edge detection
            edges = cv2.Canny(roi, 50, 150)
            
            # Hough line detection
            lines = cv2.HoughLinesP(
                edges,
                rho=1,
                theta=np.pi/180,
                threshold=50,
                minLineLength=30,
                maxLineGap=10
            )
            
            if lines is not None and len(lines) > 0:
                return 0.8  # Line detected
            else:
                return 0.2  # No line detected
                
        except Exception:
            return 0.5  # Default if detection fails
    
    def _infer_connection_type(self, comp1, comp2) -> str:
        """Infer type of connection (supply, return, exhaust)"""
        # Simple heuristic based on component types
        if "supply" in comp1.sub_type or "supply" in comp2.sub_type:
            return "supply"
        elif "return" in comp1.sub_type or "return" in comp2.sub_type:
            return "return"
        elif "exhaust" in comp1.type or "exhaust" in comp2.type:
            return "exhaust"
        else:
            return "supply"  # Default
    
    def _prune_connections(
        self,
        connections: List[SpatialConnection]
    ) -> List[SpatialConnection]:
        """Remove duplicate and low-confidence connections"""
        # Sort by confidence
        connections.sort(key=lambda x: x.confidence, reverse=True)
        
        # Remove duplicates (keep highest confidence)
        seen_pairs = set()
        pruned = []
        
        for conn in connections:
            pair = tuple(sorted([conn.from_id, conn.to_id]))
            
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                pruned.append(conn)
        
        return pruned
    
    @staticmethod
    def _euclidean_distance(
        pt1: Tuple[float, float],
        pt2: Tuple[float, float]
    ) -> float:
        """Calculate Euclidean distance between two points"""
        return np.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)
