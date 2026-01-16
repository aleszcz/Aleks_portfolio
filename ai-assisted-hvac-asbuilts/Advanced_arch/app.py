"""
RevitAssist AI Backend
Main API server for HVAC drawing processing
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import time
import os

from processors.hvac_processor import HVACProcessor
from models.yolo_detector import YOLODetector
from models.spatial_reasoner import SpatialReasoner
from utils.validator import HVACValidator

app = FastAPI(title="RevitAssist AI Backend", version="1.0.0")

# Enable CORS for Revit plugin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI models
processor = None

@app.on_event("startup")
async def startup_event():
    """Load AI models on startup"""
    global processor
    print("Loading AI models...")
    processor = HVACProcessor(
        model_path="./models/weights/yolov9_hvac.pt",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    print("Models loaded successfully!")

# Request/Response models
class ProcessingRequest(BaseModel):
    file_path: str
    drawing_type: str = "hvac_plan"
    level: Optional[str] = None
    scale: Optional[str] = None
    processing_mode: str = "standard"

class HVACComponent(BaseModel):
    id: str
    type: str
    sub_type: str
    bounding_box: List[float]  # [x, y, width, height]
    confidence: float
    properties: Dict[str, str]
    revit_family: str

class Connection(BaseModel):
    from_component: str
    to_component: str
    connection_type: str
    confidence: float

class ValidationIssue(BaseModel):
    severity: str  # "ERROR", "WARNING", "INFO"
    message: str
    component_id: Optional[str] = None

class ProcessingResult(BaseModel):
    components: List[HVACComponent]
    connections: List[Connection]
    issues: List[ValidationIssue]
    average_confidence: float
    processing_time: float
    detected_scale: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": "1.0.0",
        "models_loaded": processor is not None
    }

@app.post("/api/process", response_model=ProcessingResult)
async def process_drawing(request: ProcessingRequest):
    """
    Process HVAC drawing and detect components
    
    Args:
        request: Processing request with file path and settings
        
    Returns:
        ProcessingResult with detected components, connections, and issues
    """
    if processor is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        start_time = time.time()
        
        # Process drawing
        result = processor.process_drawing(
            pdf_path=request.file_path,
            drawing_type=request.drawing_type,
            level_name=request.level,
            scale=request.scale,
            mode=request.processing_mode
        )
        
        processing_time = time.time() - start_time
        
        # Convert to response format
        return ProcessingResult(
            components=[
                HVACComponent(
                    id=comp.id,
                    type=comp.type,
                    sub_type=comp.sub_type,
                    bounding_box=comp.bbox,
                    confidence=comp.confidence,
                    properties=comp.properties,
                    revit_family=comp.revit_family
                )
                for comp in result.components
            ],
            connections=[
                Connection(
                    from_component=conn.from_id,
                    to_component=conn.to_id,
                    connection_type=conn.conn_type,
                    confidence=conn.confidence
                )
                for conn in result.connections
            ],
            issues=[
                ValidationIssue(
                    severity=issue.severity,
                    message=issue.message,
                    component_id=issue.component_id
                )
                for issue in result.issues
            ],
            average_confidence=result.avg_confidence,
            processing_time=processing_time,
            detected_scale=result.scale
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_drawing(file: UploadFile = File(...)):
    """
    Upload drawing file for processing
    
    Args:
        file: Uploaded PDF or image file
        
    Returns:
        File path for processing
    """
    # Save uploaded file
    upload_dir = "./uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {"file_path": file_path, "filename": file.filename}

@app.get("/api/models/status")
async def models_status():
    """Get status of loaded models"""
    if processor is None:
        return {"status": "not_loaded"}
    
    return {
        "status": "loaded",
        "detector": processor.detector.model_name,
        "detector_classes": len(processor.detector.classes),
        "device": str(processor.device)
    }

if __name__ == "__main__":
    import torch
    
    # Start server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
