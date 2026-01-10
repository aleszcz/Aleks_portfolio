# RevitAssist Technical Architecture

## System Overview

RevitAssist processes HVAC as-built drawings through a multi-stage pipeline combining computer vision, domain-specific reasoning, and human validation to generate Revit-compatible structured data.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Input Layer                              │
├─────────────────────────────────────────────────────────────┤
│  • PDF Drawings (scanned, digital)                          │
│  • Equipment Schedules (tables, spreadsheets)               │
│  • Field Notes (text, photos)                               │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┴─────────────┐
    │   Preprocessing Layer     │
    │  • PDF to Image (300 DPI) │
    │  • Page segmentation      │
    │  • Quality checks         │
    └─────────────┬─────────────┘
                  │
    ┌─────────────┴─────────────────────────────┐
    │                                           │
┌───▼──────────────┐              ┌────────────▼────────┐
│  Vision Parser   │              │   Table Parser      │
├──────────────────┤              ├─────────────────────┤
│ • Component      │              │ • Equipment data    │
│   detection      │              │ • Specifications    │
│ • Dimension OCR  │              │ • Metadata          │
│ • Symbol recog.  │              │ • Cross-references  │
└───┬──────────────┘              └────────────┬────────┘
    │                                          │
    └────────────┬──────────────────────────────┘
                 │
    ┌────────────▼──────────────┐
    │   Entity Resolution       │
    │  • Component linking      │
    │  • Deduplication          │
    │  • Reference matching     │
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────┐
    │   HVAC Reasoning Engine   │
    ├───────────────────────────┤
    │ • Airflow validation      │
    │ • Sizing checks           │
    │ • Connection inference    │
    │ • Code compliance         │
    │ • Confidence scoring      │
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────┐
    │   Output Generator        │
    │  • Revit JSON schema      │
    │  • Warning reports        │
    │  • Confidence metadata    │
    └────────────┬──────────────┘
                 │
    ┌────────────┴─────────────────────────────┐
    │                                          │
┌───▼──────────────┐              ┌───────────▼────────┐
│  Web Interface   │              │  API Endpoints     │
│  • Upload        │              │  • REST API        │
│  • Validation UI │              │  • Webhooks        │
│  • Export        │              │  • Batch processing│
└──────────────────┘              └────────────────────┘
```

---

## Component Details

### 1. Preprocessing Layer

**Purpose:** Prepare PDFs for vision model processing

**Components:**

```python
class PDFPreprocessor:
    """
    Converts PDFs to high-quality images and performs quality checks
    """
    
    def process(self, pdf_path: str) -> List[ProcessedPage]:
        """
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of ProcessedPage objects with images and metadata
        """
        pages = []
        
        # Convert PDF to images at 300 DPI
        images = pdf_to_images(pdf_path, dpi=300)
        
        for idx, image in enumerate(images):
            # Quality checks
            if self._check_quality(image):
                # Deskew if needed
                if self._needs_deskew(image):
                    image = self._deskew(image)
                
                # Enhance contrast for better OCR
                image = self._enhance_contrast(image)
                
                pages.append(ProcessedPage(
                    page_number=idx + 1,
                    image=image,
                    quality_score=self._calculate_quality(image)
                ))
        
        return pages
    
    def _check_quality(self, image) -> bool:
        """Check if image quality is sufficient for processing"""
        # Check resolution, clarity, contrast
        pass
    
    def _deskew(self, image):
        """Correct rotation/skew in scanned documents"""
        pass
    
    def _enhance_contrast(self, image):
        """Improve contrast for better text/symbol recognition"""
        pass
```

**Quality Thresholds:**
- Minimum resolution: 200 DPI
- Minimum contrast ratio: 3:1
- Maximum skew angle: 5°

---

### 2. Vision Parser

**Purpose:** Extract HVAC components from drawings using vision models

**Architecture:**

```python
class VisionParser:
    """
    Uses foundation models (Claude Vision, GPT-4V) to extract components
    """
    
    def __init__(self, model_provider: str = "anthropic"):
        self.model = self._initialize_model(model_provider)
    
    def extract_components(self, image: np.ndarray) -> ComponentSet:
        """
        Extract all HVAC components from drawing image
        
        Returns:
            ComponentSet containing ducts, equipment, annotations
        """
        # Prepare prompt
        prompt = self._build_extraction_prompt()
        
        # Call vision model
        response = self.model.analyze_image(
            image=image,
            prompt=prompt,
            output_format="json"
        )
        
        # Parse response
        components = self._parse_response(response)
        
        # Post-process
        components = self._clean_components(components)
        
        return components
    
    def _build_extraction_prompt(self) -> str:
        """
        Construct detailed prompt for vision model
        """
        return """
        Extract all HVAC components from this engineering drawing.
        
        For each DUCT RUN:
        - start_point: (x, y) coordinates in pixels
        - end_point: (x, y) coordinates
        - dimensions: width × height in inches (if annotated)
        - cfm: airflow in CFM (if annotated)
        - system_type: "supply", "return", "exhaust"
        
        For each EQUIPMENT UNIT:
        - type: "ahu", "exhaust_fan", "rtu", "vav", "diffuser"
        - tag: equipment ID (e.g., "AHU-1", "EF-2")
        - location: (x, y) coordinates
        - capacity: CFM, tonnage, or HP (if annotated)
        
        For CONNECTIONS:
        - from_component: component ID
        - to_component: component ID
        - connection_type: "duct", "control", "piping"
        
        Output as JSON with confidence scores (0-1) for each extraction.
        """
```

**Extraction Strategy:**

1. **Coarse Pass:** Identify all major components
2. **Fine Pass:** Extract detailed attributes for each component
3. **Relationship Pass:** Infer connections between components

**Confidence Scoring:**
```python
def calculate_confidence(extraction: Component) -> float:
    """
    Score extraction confidence based on multiple factors
    
    Factors:
    - Visual clarity (0-1)
    - Annotation presence (0-1)
    - Consistency with nearby components (0-1)
    """
    clarity_score = assess_visual_clarity(extraction.image_region)
    annotation_score = has_clear_annotations(extraction)
    consistency_score = check_spatial_consistency(extraction)
    
    # Weighted average
    confidence = (
        0.4 * clarity_score +
        0.3 * annotation_score +
        0.3 * consistency_score
    )
    
    return confidence
```

---

### 3. Table Parser

**Purpose:** Extract equipment metadata from schedules and tables

**Implementation:**

```python
class TableParser:
    """
    Extract structured data from equipment schedules
    """
    
    def extract_schedule(self, page_image: np.ndarray) -> List[EquipmentSpec]:
        """
        Parse equipment schedule tables
        
        Returns:
            List of EquipmentSpec objects with metadata
        """
        # Detect table regions
        tables = self._detect_tables(page_image)
        
        equipment_list = []
        
        for table in tables:
            # Extract table structure (rows, columns, headers)
            table_data = self._parse_table_structure(table)
            
            # Identify equipment schedule format
            if self._is_equipment_schedule(table_data):
                # Extract equipment specifications
                specs = self._extract_equipment_specs(table_data)
                equipment_list.extend(specs)
        
        return equipment_list
    
    def _detect_tables(self, image):
        """Detect table regions using line detection and structure analysis"""
        pass
    
    def _parse_table_structure(self, table_region):
        """Extract rows, columns, and cell contents"""
        # Use traditional CV (Hough lines) + OCR
        pass
    
    def _extract_equipment_specs(self, table_data):
        """
        Parse equipment specifications from table
        
        Common columns:
        - Tag/ID
        - Type
        - CFM/Capacity
        - Location
        - Notes/Comments
        """
        pass
```

---

### 4. HVAC Reasoning Engine

**Purpose:** Validate extractions using domain-specific engineering rules

**Core Validation Rules:**

```python
class HVACReasoningEngine:
    """
    Validates HVAC system logic and flags inconsistencies
    """
    
    def validate_system(self, components: ComponentSet) -> ValidationReport:
        """
        Run all validation checks and return warnings
        """
        warnings = []
        
        # Rule 1: Airflow continuity
        warnings.extend(self._check_airflow_continuity(components))
        
        # Rule 2: Duct sizing
        warnings.extend(self._check_duct_sizing(components))
        
        # Rule 3: Equipment compatibility
        warnings.extend(self._check_equipment_compatibility(components))
        
        # Rule 4: Code compliance
        warnings.extend(self._check_code_compliance(components))
        
        return ValidationReport(warnings=warnings)
    
    def _check_airflow_continuity(self, components) -> List[Warning]:
        """
        Verify supply fan CFM equals sum of branch duct runs
        """
        warnings = []
        
        for system in components.get_systems():
            supply_fan = system.get_supply_fan()
            branches = system.get_supply_branches()
            
            fan_cfm = supply_fan.cfm
            total_branch_cfm = sum(b.cfm for b in branches if b.cfm)
            
            # Allow 10% tolerance for measurement uncertainty
            if abs(fan_cfm - total_branch_cfm) > 0.1 * fan_cfm:
                warnings.append(Warning(
                    type="airflow_mismatch",
                    severity="high",
                    component=supply_fan.id,
                    message=f"Supply fan {fan_cfm} CFM != branches {total_branch_cfm} CFM",
                    recommendation="Verify fan capacity or check for missing/extra branches"
                ))
        
        return warnings
    
    def _check_duct_sizing(self, components) -> List[Warning]:
        """
        Validate duct sizes using ASHRAE velocity guidelines
        """
        warnings = []
        
        for duct in components.ducts:
            if duct.cfm and duct.width and duct.height:
                # Calculate velocity
                area_sqft = (duct.width * duct.height) / 144
                velocity_fpm = duct.cfm / area_sqft
                
                # ASHRAE guidelines:
                # Main ducts: max 2000 FPM
                # Branch ducts: max 1500 FPM
                max_velocity = 2000 if duct.is_main else 1500
                
                if velocity_fpm > max_velocity:
                    warnings.append(Warning(
                        type="velocity_high",
                        severity="medium",
                        component=duct.id,
                        message=f"Velocity {velocity_fpm:.0f} FPM exceeds {max_velocity} FPM",
                        recommendation=f"Increase duct size or reduce CFM"
                    ))
                
                # Check for undersizing (velocity too low = inefficient)
                if velocity_fpm < 500:
                    warnings.append(Warning(
                        type="velocity_low",
                        severity="low",
                        component=duct.id,
                        message=f"Velocity {velocity_fpm:.0f} FPM may be inefficient",
                        recommendation="Consider reducing duct size"
                    ))
        
        return warnings
    
    def _check_equipment_compatibility(self, components) -> List[Warning]:
        """
        Verify equipment specifications are compatible
        """
        warnings = []
        
        # Example: Check VAV box capacity vs. downstream diffusers
        for vav in components.get_equipment_by_type("vav"):
            downstream_diffusers = components.get_downstream_components(vav)
            total_diffuser_cfm = sum(d.cfm for d in downstream_diffusers if d.cfm)
            
            if vav.max_cfm and total_diffuser_cfm > vav.max_cfm:
                warnings.append(Warning(
                    type="capacity_exceeded",
                    severity="high",
                    component=vav.id,
                    message=f"VAV max {vav.max_cfm} CFM < diffusers {total_diffuser_cfm} CFM"
                ))
        
        return warnings
    
    def _check_code_compliance(self, components) -> List[Warning]:
        """
        Check against building codes and standards
        """
        warnings = []
        
        # Example: Minimum ventilation rates per ASHRAE 62.1
        # (Would need building type, occupancy, etc.)
        
        return warnings
```

**Inference Rules:**

```python
class ConnectionInferencer:
    """
    Infer missing connections using spatial and logical reasoning
    """
    
    def infer_connections(self, components: ComponentSet) -> List[InferredConnection]:
        """
        Suggest likely connections based on:
        - Spatial proximity
        - Airflow direction
        - Component types
        - Size compatibility
        """
        inferred = []
        
        for component in components:
            # Find potential connection points
            candidates = self._find_connection_candidates(component, components)
            
            # Score each candidate
            for candidate in candidates:
                score = self._score_connection(component, candidate)
                
                if score > 0.7:  # High confidence threshold
                    inferred.append(InferredConnection(
                        from_component=component,
                        to_component=candidate,
                        confidence=score,
                        reasoning=self._explain_inference(component, candidate, score)
                    ))
        
        return inferred
    
    def _score_connection(self, comp1, comp2) -> float:
        """
        Calculate connection likelihood
        
        Factors:
        - Distance (closer = higher score)
        - Alignment (colinear = higher score)
        - Type compatibility (duct→diffuser = valid)
        - Size compatibility (similar sizes = higher score)
        - Airflow direction (supply→return makes sense)
        """
        distance_score = self._distance_score(comp1, comp2)
        alignment_score = self._alignment_score(comp1, comp2)
        type_score = self._type_compatibility(comp1, comp2)
        size_score = self._size_compatibility(comp1, comp2)
        
        # Weighted combination
        total_score = (
            0.3 * distance_score +
            0.2 * alignment_score +
            0.3 * type_score +
            0.2 * size_score
        )
        
        return total_score
```

---

### 5. Output Generator

**Purpose:** Generate Revit-compatible JSON and reports

**Schema Definition:**

```python
class RevitExporter:
    """
    Generate Revit-compatible JSON output
    """
    
    def export(self, components: ComponentSet, warnings: List[Warning]) -> dict:
        """
        Create structured JSON for Revit import
        """
        return {
            "project_info": self._generate_project_info(components),
            "ducts": self._export_ducts(components.ducts),
            "equipment": self._export_equipment(components.equipment),
            "connections": self._export_connections(components.connections),
            "warnings": self._export_warnings(warnings),
            "metadata": self._generate_metadata(components)
        }
    
    def _export_ducts(self, ducts: List[Duct]) -> List[dict]:
        """
        Export duct data in Revit-compatible format
        """
        return [
            {
                "id": duct.id,
                "geometry": {
                    "start_point": {"x": duct.start.x, "y": duct.start.y, "z": duct.start.z},
                    "end_point": {"x": duct.end.x, "y": duct.end.y, "z": duct.end.z}
                },
                "properties": {
                    "width": duct.width,
                    "height": duct.height,
                    "cfm": duct.cfm,
                    "system_type": duct.system_type,
                    "material": duct.material or "Galvanized Steel"  # default
                },
                "metadata": {
                    "confidence": duct.confidence,
                    "source": duct.source,  # "extracted" or "inferred"
                    "extraction_method": duct.extraction_method
                }
            }
            for duct in ducts
        ]
    
    def _export_equipment(self, equipment: List[Equipment]) -> List[dict]:
        """
        Export equipment data
        """
        return [
            {
                "id": equip.id,
                "type": equip.type,
                "location": {"x": equip.x, "y": equip.y, "z": equip.z},
                "properties": {
                    "cfm": equip.cfm,
                    "static_pressure": equip.static_pressure,
                    "motor_hp": equip.motor_hp,
                    "voltage": equip.voltage
                },
                "metadata": {
                    "confidence": equip.confidence,
                    "schedule_reference": equip.schedule_ref
                }
            }
            for equip in equipment
        ]
```

**JSON Schema:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RevitAssist HVAC Export",
  "type": "object",
  "required": ["project_info", "ducts", "equipment"],
  "properties": {
    "project_info": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "units": {"enum": ["imperial", "metric"]},
        "coordinate_system": {"type": "string"}
      }
    },
    "ducts": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "geometry"],
        "properties": {
          "id": {"type": "string"},
          "geometry": {
            "type": "object",
            "required": ["start_point", "end_point"],
            "properties": {
              "start_point": {
                "type": "object",
                "properties": {
                  "x": {"type": "number"},
                  "y": {"type": "number"},
                  "z": {"type": "number"}
                }
              }
            }
          },
          "properties": {
            "type": "object",
            "properties": {
              "width": {"type": "number"},
              "height": {"type": "number"},
              "cfm": {"type": "number"}
            }
          }
        }
      }
    }
  }
}
```

---

## Data Flow

### Processing Pipeline

```
1. PDF Upload
   ↓
2. Preprocessing (PDF → Images, 300 DPI)
   ↓
3. Parallel Processing:
   ├─→ Vision Parser (extract components from drawings)
   └─→ Table Parser (extract equipment schedules)
   ↓
4. Entity Resolution (link drawing components to schedule data)
   ↓
5. HVAC Reasoning (validate, infer connections, flag warnings)
   ↓
6. Output Generation (Revit JSON + validation report)
   ↓
7. Human Review (web interface)
   ↓
8. Export (download Revit JSON)
```

### Timing Breakdown (Target)

| Stage | Time | Notes |
|-------|------|-------|
| Preprocessing | 5-10 sec | PDF → images |
| Vision parsing | 30-40 sec | Per page, parallel processing |
| Table parsing | 5-10 sec | Schedule extraction |
| Entity resolution | 2-5 sec | Linking components |
| HVAC reasoning | 5-10 sec | Validation rules |
| Output generation | 1-2 sec | JSON formatting |
| **Total** | **45-60 sec** | For typical 5-page drawing set |

---

## Technology Stack

### Core Dependencies

```
# requirements.txt

# Vision and NLP
anthropic>=0.8.0
openai>=1.0.0
transformers>=4.30.0

# Image processing
Pillow>=10.0.0
opencv-python>=4.8.0
pdf2image>=1.16.0
pytesseract>=0.3.10

# Data processing
pandas>=2.0.0
numpy>=1.24.0
pydantic>=2.0.0

# Web framework
fastapi>=0.100.0
uvicorn>=0.23.0
python-multipart>=0.0.6

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

### Infrastructure

- **Compute:** CPU-based (vision models called via API)
- **Storage:** Local filesystem or S3 for PDFs
- **Database:** PostgreSQL for project metadata (optional)
- **Caching:** Redis for API response caching (optional)

---

## Scalability Considerations

### Horizontal Scaling

**Bottlenecks:**
- Vision model API calls (rate-limited)
- PDF → image conversion (CPU-intensive)

**Solutions:**
- Queue-based architecture (Celery + Redis)
- Multiple worker processes
- API request batching

### Performance Optimization

```python
# Parallel processing of pages
from concurrent.futures import ThreadPoolExecutor

def process_multi_page_pdf(pdf_path: str) -> ComponentSet:
    """
    Process multi-page PDF in parallel
    """
    pages = preprocess_pdf(pdf_path)
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Process pages in parallel
        futures = [
            executor.submit(vision_parser.extract_components, page.image)
            for page in pages
        ]
        
        # Collect results
        results = [f.result() for f in futures]
    
    # Merge components from all pages
    merged = merge_component_sets(results)
    
    return merged
```

---

## Error Handling

### Error Categories

1. **Input Errors**
   - Invalid PDF format
   - Poor image quality
   - Missing required data

2. **Processing Errors**
   - Vision model API failures
   - Parsing errors
   - Validation failures

3. **Output Errors**
   - Invalid JSON structure
   - Missing required fields

### Error Recovery Strategy

```python
class ErrorHandler:
    """
    Graceful error handling with fallbacks
    """
    
    def handle_vision_api_failure(self, error):
        """
        If primary API fails, try backup or fallback to simpler extraction
        """
        if "rate_limit" in str(error):
            # Wait and retry
            time.sleep(60)
            return retry_with_backoff()
        
        elif "timeout" in str(error):
            # Fall back to simpler OCR-based extraction
            return fallback_to_ocr()
        
        else:
            # Log error and mark for manual review
            log_error(error)
            return mark_for_manual_review()
```

---

## Security & Privacy

### Data Handling

- PDFs processed in memory (not permanently stored by default)
- Optional encrypted storage for sensitive projects
- API keys stored in environment variables
- No data sent to third parties (except vision model APIs)

### Compliance

- Follow industry standards for document handling
- Audit logs for all processing activities
- Data retention policies configurable

---

## Testing Strategy

### Unit Tests

```python
# tests/test_validation.py

def test_airflow_continuity_check():
    """Test that airflow mismatches are correctly flagged"""
    components = ComponentSet([
        SupplyFan(id="SF-1", cfm=10000),
        Duct(id="D-1", cfm=3000),
        Duct(id="D-2", cfm=3000),
        Duct(id="D-3", cfm=3000)
        # Total: 9000 CFM, should flag 10% mismatch
    ])
    
    validator = HVACReasoningEngine()
    warnings = validator._check_airflow_continuity(components)
    
    assert len(warnings) == 1
    assert warnings[0].type == "airflow_mismatch"
```

### Integration Tests

```python
def test_end_to_end_processing():
    """Test complete pipeline with sample PDF"""
    processor = HVACProcessor()
    result = processor.process_drawing("tests/fixtures/sample_hvac.pdf")
    
    assert len(result.ducts) > 0
    assert len(result.equipment) > 0
    assert result.validation_report is not None
```

### Accuracy Tests

```python
def test_extraction_accuracy():
    """Measure extraction accuracy against ground truth"""
    ground_truth = load_ground_truth("tests/fixtures/annotated_drawing.json")
    
    result = processor.process_drawing("tests/fixtures/test_drawing.pdf")
    
    accuracy = calculate_accuracy(result, ground_truth)
    
    assert accuracy.ducts > 0.90  # 90% duct extraction accuracy
    assert accuracy.equipment > 0.95  # 95% equipment accuracy
```

---

## Monitoring & Observability

### Metrics to Track

- **Processing time** per drawing
- **Extraction accuracy** (when ground truth available)
- **Validation warning rate**
- **API success/failure rates**
- **User corrections** (for model improvement)

### Logging

```python
import logging
import structlog

logger = structlog.get_logger()

def process_drawing(pdf_path: str):
    logger.info("processing_started", pdf=pdf_path)
    
    try:
        result = processor.process(pdf_path)
        
        logger.info(
            "processing_completed",
            pdf=pdf_path,
            ducts_extracted=len(result.ducts),
            equipment_extracted=len(result.equipment),
            warnings=len(result.warnings),
            processing_time_sec=result.processing_time
        )
        
        return result
    
    except Exception as e:
        logger.error("processing_failed", pdf=pdf_path, error=str(e))
        raise
```

---

## Future Architectural Enhancements

### 1. Feedback Loop

```python
class FeedbackCollector:
    """
    Collect user corrections to improve model over time
    """
    
    def record_correction(self, original: Component, corrected: Component):
        """
        Log corrections for retraining
        """
        self.corrections_db.insert({
            "timestamp": datetime.now(),
            "component_type": original.type,
            "original_value": original.to_dict(),
            "corrected_value": corrected.to_dict(),
            "correction_type": classify_correction(original, corrected)
        })
```

### 2. Direct Revit Plugin

```python
# Future: Direct Revit API integration via pyRevit

class RevitDirectPlacer:
    """
    Place components directly in Revit model (not just JSON export)
    """
    
    def place_duct(self, duct: Duct, revit_doc):
        """
        Create actual Revit duct element
        """
        # Use Revit API to create duct family instance
        pass
```

### 3. Matterport Integration

```python
class PointCloudValidator:
    """
    Validate AI extractions against 3D scans
    """
    
    def validate_against_scan(self, components: ComponentSet, point_cloud):
        """
        Check if extracted components match physical reality
        """
        discrepancies = []
        
        for equipment in components.equipment:
            # Check if equipment exists in point cloud at expected location
            if not self._find_in_point_cloud(equipment, point_cloud):
                discrepancies.append(f"Equipment {equipment.id} not found in scan")
        
        return discrepancies
```

---

## Appendix: Example API Calls

### Vision Model API

```python
# Example: Using Anthropic Claude for component extraction

import anthropic
import base64

def extract_with_claude(image_path: str) -> dict:
    client = anthropic.Anthropic(api_key="your_key")
    
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data
                    }
                },
                {
                    "type": "text",
                    "text": "Extract all HVAC components from this drawing as JSON..."
                }
            ]
        }]
    )
    
    return json.loads(response.content[0].text)
```

---

**Document Version:** 1.0  
**Last Updated:** January 2025
