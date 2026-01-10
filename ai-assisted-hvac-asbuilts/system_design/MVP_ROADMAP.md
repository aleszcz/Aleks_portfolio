# RevitAssist MVP Roadmap

## Overview

This document outlines the 6-week MVP development plan for RevitAssist, broken into weekly milestones with specific deliverables and success criteria.

**Goal:** Build a working proof-of-concept that demonstrates PDF → Revit automation with 80%+ accuracy

---

## MVP Scope

### What's IN MVP

✅ PDF HVAC drawing processing  
✅ Component extraction (ducts, equipment)  
✅ HVAC validation rules (airflow, sizing)  
✅ Revit-compatible JSON export  
✅ Simple web interface for upload/review  
✅ Warning/confidence reporting  

### What's NOT in MVP

❌ Direct Revit plugin (just JSON export)  
❌ 3D model generation (Revit does this)  
❌ Matterport integration  
❌ Multi-user/authentication  
❌ Batch processing  
❌ Advanced analytics dashboard  

---

## Phase 1: Core Extraction (Weeks 1-2)

### Week 1: Foundation & Proof-of-Concept

#### Objectives
- Set up development environment
- Test vision model APIs
- Process ONE real PDF successfully

#### Tasks

**Day 1-2: Setup**
- [ ] Initialize repository
- [ ] Set up Python virtual environment
- [ ] Install dependencies (Anthropic/OpenAI SDK, image processing libs)
- [ ] Obtain sample HVAC PDFs (3-5 different styles)
- [ ] Create API key configurations

**Day 3-4: Vision API Integration**
```python
# tasks/vision_integration.py

# Task 1: Test basic image analysis
def test_vision_api():
    """
    Verify API can extract basic information from HVAC drawing
    """
    # Convert PDF page to image
    image = convert_pdf_to_image("sample_hvac.pdf", page=1, dpi=300)
    
    # Call vision API
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
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
                        "data": encode_image(image)
                    }
                },
                {
                    "type": "text",
                    "text": "List all HVAC components visible in this drawing."
                }
            ]
        }]
    )
    
    print(response.content[0].text)
    # Verify it identifies ducts, equipment, annotations
```

**Day 5-7: Component Extraction**
```python
# src/parsers/vision_parser.py

class VisionParser:
    def extract_components(self, pdf_path: str) -> ComponentSet:
        """
        Extract structured HVAC components from PDF
        
        Steps:
        1. Convert PDF to high-res images
        2. For each page, extract:
           - Duct runs (start, end, dimensions, CFM)
           - Equipment (type, tag, location, specs)
           - Annotations and callouts
        3. Return as structured objects
        """
        components = ComponentSet()
        
        pages = self.preprocess_pdf(pdf_path)
        
        for page in pages:
            page_components = self._extract_page_components(page)
            components.merge(page_components)
        
        return components
```

#### Deliverables
- [ ] Working vision API integration
- [ ] Extract components from 1 sample PDF
- [ ] JSON output with ducts and equipment

#### Success Criteria
- ✅ Successfully processes PDF without errors
- ✅ Identifies 80%+ of major components (visual inspection)
- ✅ Outputs valid JSON structure

---

### Week 2: Accuracy & Reliability

#### Objectives
- Improve extraction accuracy
- Handle multiple PDF formats
- Add confidence scoring

#### Tasks

**Day 8-9: Prompt Engineering**
```python
# Refine extraction prompt for higher accuracy

EXTRACTION_PROMPT = """
Analyze this HVAC engineering drawing and extract all components.

For each DUCT RUN, provide:
- start_point: (x, y) pixel coordinates of duct start
- end_point: (x, y) pixel coordinates of duct end
- dimensions: width x height in inches (look for annotations like "14x8")
- cfm: airflow in CFM if annotated
- system_type: "supply", "return", or "exhaust" (infer from drawing context)

For each EQUIPMENT UNIT, provide:
- type: equipment type from: "air_handler", "exhaust_fan", "rtu", "vav_box", "diffuser"
- tag: equipment ID tag (e.g., "AHU-1", "EF-2", "VAV-101")
- location: (x, y) pixel coordinates
- capacity: CFM, tonnage, or HP if annotated
- notes: any additional specifications visible

For each ANNOTATION:
- text: annotation content
- location: (x, y) pixel coordinates
- associated_component: which component this annotation describes (if clear)

Output JSON with this structure:
{
  "ducts": [...],
  "equipment": [...],
  "annotations": [...]
}

IMPORTANT: 
- If unsure about a value, omit it rather than guessing
- Include a "confidence" field (0.0-1.0) for each extraction
- Note any ambiguities in a "notes" field
"""
```

**Day 10-11: Multi-Format Support**
- [ ] Test on scanned PDFs (low quality)
- [ ] Test on CAD-generated PDFs (high quality)
- [ ] Test on hand-marked drawings
- [ ] Add preprocessing for poor quality images

```python
# src/preprocessing/image_enhancer.py

def enhance_for_extraction(image: np.ndarray) -> np.ndarray:
    """
    Improve image quality for better extraction
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Deskew if needed
    if needs_deskew(gray):
        gray = deskew(gray)
    
    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(enhanced)
    
    return denoised
```

**Day 12-14: Confidence Scoring**
```python
# src/scoring/confidence.py

def calculate_component_confidence(component: Component, context: dict) -> float:
    """
    Score confidence based on multiple factors
    
    Factors:
    - Clarity of visual features (0-1)
    - Presence of annotations (0-1)
    - Consistency with nearby components (0-1)
    - Agreement with equipment schedule (0-1)
    """
    scores = []
    
    # Visual clarity
    if component.has_clear_boundaries():
        scores.append(0.9)
    else:
        scores.append(0.5)
    
    # Annotation present
    if component.has_annotation():
        scores.append(0.9)
    else:
        scores.append(0.6)  # Can still infer
    
    # Spatial consistency
    if component.fits_spatial_pattern(context):
        scores.append(0.85)
    else:
        scores.append(0.4)
    
    # Schedule cross-reference
    if component.matches_schedule(context.equipment_schedule):
        scores.append(1.0)
    else:
        scores.append(0.5)
    
    return sum(scores) / len(scores)
```

#### Deliverables
- [ ] Extraction works on 3+ different PDF formats
- [ ] Confidence scores assigned to each component
- [ ] Accuracy measured against ground truth

#### Success Criteria
- ✅ Accuracy >80% on manually verified test set
- ✅ Processing time <2 minutes per page
- ✅ Handles both clean and scanned PDFs

---

## Phase 2: HVAC Reasoning (Weeks 3-4)

### Week 3: Validation Rules

#### Objectives
- Implement domain-specific validation
- Flag common engineering errors
- Build test suite

#### Tasks

**Day 15-16: Airflow Validation**
```python
# src/reasoning/airflow_validator.py

class AirflowValidator:
    """
    Check airflow continuity and balance
    """
    
    def validate_system(self, components: ComponentSet) -> List[Warning]:
        warnings = []
        
        # Rule 1: Supply fan CFM = sum of branches
        for fan in components.get_supply_fans():
            branches = components.get_downstream_ducts(fan)
            total_branch_cfm = sum(d.cfm for d in branches if d.cfm)
            
            if abs(fan.cfm - total_branch_cfm) > 0.1 * fan.cfm:
                warnings.append(Warning(
                    severity="high",
                    component=fan.id,
                    message=f"Airflow mismatch: Fan {fan.cfm} CFM != Branches {total_branch_cfm} CFM",
                    recommendation="Verify fan capacity or check for missing branches"
                ))
        
        # Rule 2: Return airflow should equal supply (or less)
        supply_total = sum(f.cfm for f in components.get_supply_fans())
        return_total = sum(f.cfm for f in components.get_return_fans())
        
        if return_total > supply_total * 1.1:  # Allow some tolerance
            warnings.append(Warning(
                severity="medium",
                message=f"Return air {return_total} CFM exceeds supply {supply_total} CFM"
            ))
        
        return warnings
```

**Day 17-18: Sizing Validation**
```python
# src/reasoning/sizing_validator.py

class DuctSizingValidator:
    """
    Validate duct sizes per ASHRAE guidelines
    """
    
    VELOCITY_LIMITS = {
        "main_supply": (1500, 2000),      # Min, Max FPM
        "branch_supply": (800, 1500),
        "main_return": (1000, 1800),
        "branch_return": (600, 1200)
    }
    
    def validate_duct(self, duct: Duct) -> Optional[Warning]:
        if not (duct.cfm and duct.width and duct.height):
            return None  # Can't validate without dimensions
        
        # Calculate velocity
        area_sqft = (duct.width * duct.height) / 144
        velocity = duct.cfm / area_sqft
        
        # Get limits for this duct type
        duct_category = self._categorize_duct(duct)
        min_vel, max_vel = self.VELOCITY_LIMITS[duct_category]
        
        if velocity > max_vel:
            return Warning(
                severity="medium",
                component=duct.id,
                message=f"Velocity {velocity:.0f} FPM exceeds max {max_vel} FPM",
                recommendation=f"Increase size to {self._recommend_size(duct, max_vel)}"
            )
        
        if velocity < min_vel:
            return Warning(
                severity="low",
                component=duct.id,
                message=f"Velocity {velocity:.0f} FPM below min {min_vel} FPM (inefficient)"
            )
        
        return None
```

**Day 19-21: Connection Inference**
```python
# src/reasoning/connection_inferencer.py

class ConnectionInferencer:
    """
    Infer logical connections between components
    """
    
    def infer_connections(self, components: ComponentSet) -> List[InferredConnection]:
        inferred = []
        
        for duct in components.ducts:
            # Find equipment at start point
            start_equipment = self._find_nearby_equipment(
                duct.start_point, 
                components.equipment,
                max_distance=50  # pixels
            )
            
            # Find equipment at end point
            end_equipment = self._find_nearby_equipment(
                duct.end_point,
                components.equipment,
                max_distance=50
            )
            
            # Infer connection based on component types and airflow logic
            if start_equipment and self._is_valid_connection(start_equipment, duct):
                inferred.append(InferredConnection(
                    from_component=start_equipment.id,
                    to_component=duct.id,
                    connection_type="supply" if duct.system_type == "supply" else "return",
                    confidence=self._calculate_connection_confidence(start_equipment, duct)
                ))
        
        return inferred
    
    def _is_valid_connection(self, equipment: Equipment, duct: Duct) -> bool:
        """
        Check if connection makes logical sense
        """
        # Supply fan should connect to supply ducts
        if equipment.type == "supply_fan" and duct.system_type != "supply":
            return False
        
        # Return fan should connect to return ducts
        if equipment.type == "return_fan" and duct.system_type != "return":
            return False
        
        return True
```

#### Deliverables
- [ ] 3 core validation rules implemented
- [ ] Connection inference working
- [ ] Test suite with 20+ test cases

#### Success Criteria
- ✅ Detects 90%+ of intentionally introduced errors
- ✅ False positive rate <10%
- ✅ Provides actionable recommendations

---

### Week 4: Integration & Testing

#### Objectives
- Integrate all components
- End-to-end testing
- Performance optimization

#### Tasks

**Day 22-23: Component Integration**
```python
# src/processor.py

class HVACProcessor:
    """
    Main processing pipeline
    """
    
    def __init__(self):
        self.vision_parser = VisionParser()
        self.table_parser = TableParser()
        self.airflow_validator = AirflowValidator()
        self.sizing_validator = DuctSizingValidator()
        self.connection_inferencer = ConnectionInferencer()
    
    def process_drawing(self, pdf_path: str) -> ProcessingResult:
        """
        Complete PDF processing pipeline
        """
        # 1. Parse PDF
        components = self.vision_parser.extract_components(pdf_path)
        
        # 2. Extract schedules (if present)
        schedules = self.table_parser.extract_schedules(pdf_path)
        components.merge_schedules(schedules)
        
        # 3. Infer connections
        connections = self.connection_inferencer.infer_connections(components)
        components.add_connections(connections)
        
        # 4. Validate
        warnings = []
        warnings.extend(self.airflow_validator.validate_system(components))
        warnings.extend(self.sizing_validator.validate_all_ducts(components))
        
        # 5. Generate output
        return ProcessingResult(
            components=components,
            warnings=warnings,
            processing_time=time.time() - start_time
        )
```

**Day 24-25: Accuracy Testing**
```python
# tests/test_accuracy.py

def test_extraction_accuracy():
    """
    Measure accuracy against manually annotated ground truth
    """
    test_cases = [
        "tests/fixtures/hospital_hvac.pdf",
        "tests/fixtures/office_building.pdf",
        "tests/fixtures/retail_space.pdf"
    ]
    
    results = []
    
    for pdf in test_cases:
        # Load ground truth
        ground_truth = load_ground_truth(pdf.replace(".pdf", "_truth.json"))
        
        # Process with RevitAssist
        result = processor.process_drawing(pdf)
        
        # Calculate metrics
        metrics = calculate_accuracy(result.components, ground_truth)
        results.append(metrics)
    
    # Average across test cases
    avg_accuracy = sum(r.overall_accuracy for r in results) / len(results)
    
    print(f"Average Accuracy: {avg_accuracy:.1%}")
    print(f"Duct Accuracy: {sum(r.duct_accuracy for r in results) / len(results):.1%}")
    print(f"Equipment Accuracy: {sum(r.equipment_accuracy for r in results) / len(results):.1%}")
    
    assert avg_accuracy > 0.80  # MVP target
```

**Day 26-28: Performance Optimization**
- [ ] Profile code to find bottlenecks
- [ ] Optimize image processing
- [ ] Implement caching for API calls
- [ ] Parallel processing for multi-page PDFs

#### Deliverables
- [ ] Fully integrated processing pipeline
- [ ] Accuracy report on 5+ test PDFs
- [ ] Processing time <2 min per drawing

#### Success Criteria
- ✅ End-to-end processing works without errors
- ✅ Accuracy >80% on test set
- ✅ Processing time meets target

---

## Phase 3: User Interface (Weeks 5-6)

### Week 5: Web Interface

#### Objectives
- Build simple web UI
- Upload and processing workflow
- Results visualization

#### Tasks

**Day 29-31: Backend API**
```python
# src/web/api.py

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/api/upload")
async def upload_drawing(file: UploadFile = File(...)):
    """
    Upload and process HVAC drawing
    """
    # Save uploaded file
    pdf_path = save_upload(file)
    
    # Process
    processor = HVACProcessor()
    result = processor.process_drawing(pdf_path)
    
    # Store result with session ID
    session_id = generate_session_id()
    store_result(session_id, result)
    
    return JSONResponse({
        "session_id": session_id,
        "components_summary": {
            "ducts": len(result.components.ducts),
            "equipment": len(result.components.equipment),
            "warnings": len(result.warnings)
        },
        "processing_time": result.processing_time
    })

@app.get("/api/results/{session_id}")
async def get_results(session_id: str):
    """
    Retrieve processing results
    """
    result = load_result(session_id)
    
    return JSONResponse({
        "components": result.components.to_dict(),
        "warnings": [w.to_dict() for w in result.warnings],
        "stats": result.calculate_stats()
    })

@app.get("/api/export/{session_id}")
async def export_revit_json(session_id: str):
    """
    Download Revit-compatible JSON
    """
    result = load_result(session_id)
    revit_json = result.to_revit_format()
    
    return JSONResponse(revit_json)
```

**Day 32-33: Frontend Interface**
```html
<!-- templates/index.html -->

<!DOCTYPE html>
<html>
<head>
    <title>RevitAssist - HVAC Processing</title>
    <style>
        /* Simple, clean styling */
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .upload-zone { border: 2px dashed #ccc; padding: 40px; text-align: center; }
        .results-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .results-table th, .results-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .warning { background-color: #fff3cd; }
        .warning.high { background-color: #f8d7da; }
    </style>
</head>
<body>
    <h1>RevitAssist - HVAC PDF Processing</h1>
    
    <!-- Upload Section -->
    <div class="upload-zone" id="uploadZone">
        <p>Drag & drop HVAC PDF here or click to select</p>
        <input type="file" id="fileInput" accept="application/pdf" style="display:none">
        <button onclick="document.getElementById('fileInput').click()">Select PDF</button>
    </div>
    
    <!-- Processing Status -->
    <div id="processingStatus" style="display:none">
        <h2>Processing...</h2>
        <progress id="progressBar" value="0" max="100"></progress>
    </div>
    
    <!-- Results Section -->
    <div id="results" style="display:none">
        <h2>Extraction Results</h2>
        
        <div>
            <p><strong>Ducts extracted:</strong> <span id="ductCount">0</span></p>
            <p><strong>Equipment extracted:</strong> <span id="equipmentCount">0</span></p>
            <p><strong>Warnings:</strong> <span id="warningCount">0</span></p>
        </div>
        
        <h3>Components</h3>
        <table class="results-table" id="componentsTable">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Type</th>
                    <th>Properties</th>
                    <th>Confidence</th>
                </tr>
            </thead>
            <tbody id="componentsBody">
            </tbody>
        </table>
        
        <h3>Warnings & Recommendations</h3>
        <table class="results-table" id="warningsTable">
            <thead>
                <tr>
                    <th>Severity</th>
                    <th>Component</th>
                    <th>Issue</th>
                    <th>Recommendation</th>
                </tr>
            </thead>
            <tbody id="warningsBody">
            </tbody>
        </table>
        
        <button onclick="exportRevitJSON()">Export Revit JSON</button>
    </div>
    
    <script>
        // Handle file upload
        document.getElementById('fileInput').addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            // Show processing status
            document.getElementById('uploadZone').style.display = 'none';
            document.getElementById('processingStatus').style.display = 'block';
            
            // Upload and process
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            // Load and display results
            loadResults(data.session_id);
        });
        
        async function loadResults(sessionId) {
            const response = await fetch(`/api/results/${sessionId}`);
            const data = await response.json();
            
            // Display summary
            document.getElementById('ductCount').textContent = data.components.ducts.length;
            document.getElementById('equipmentCount').textContent = data.components.equipment.length;
            document.getElementById('warningCount').textContent = data.warnings.length;
            
            // Populate components table
            const tbody = document.getElementById('componentsBody');
            tbody.innerHTML = '';
            
            [...data.components.ducts, ...data.components.equipment].forEach(comp => {
                const row = tbody.insertRow();
                row.insertCell(0).textContent = comp.id;
                row.insertCell(1).textContent = comp.type;
                row.insertCell(2).textContent = formatProperties(comp.properties);
                row.insertCell(3).textContent = (comp.confidence * 100).toFixed(0) + '%';
            });
            
            // Populate warnings table
            const warnBody = document.getElementById('warningsBody');
            warnBody.innerHTML = '';
            
            data.warnings.forEach(warn => {
                const row = warnBody.insertRow();
                row.className = `warning ${warn.severity}`;
                row.insertCell(0).textContent = warn.severity;
                row.insertCell(1).textContent = warn.component || 'System';
                row.insertCell(2).textContent = warn.message;
                row.insertCell(3).textContent = warn.recommendation || '-';
            });
            
            // Show results
            document.getElementById('processingStatus').style.display = 'none';
            document.getElementById('results').style.display = 'block';
            
            // Store session ID for export
            window.currentSessionId = sessionId;
        }
        
        function formatProperties(props) {
            return Object.entries(props)
                .filter(([k, v]) => v !== null && v !== undefined)
                .map(([k, v]) => `${k}: ${v}`)
                .join(', ');
        }
        
        async function exportRevitJSON() {
            const response = await fetch(`/api/export/${window.currentSessionId}`);
            const json = await response.json();
            
            // Download as file
            const blob = new Blob([JSON.stringify(json, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'revit_export.json';
            a.click();
        }
    </script>
</body>
</html>
```

**Day 34-35: Testing & Refinement**
- [ ] User testing with 2-3 engineers
- [ ] Fix UI issues
- [ ] Add loading indicators
- [ ] Improve error messages

#### Deliverables
- [ ] Working web interface
- [ ] Upload → process → review workflow
- [ ] JSON export functionality

#### Success Criteria
- ✅ Can process PDF through web UI without errors
- ✅ Results display correctly
- ✅ Export generates valid Revit JSON

---

### Week 6: Documentation & Demo

#### Objectives
- Create documentation
- Record demo video
- Prepare for first pilot

#### Tasks

**Day 36-37: Documentation**
- [ ] README with setup instructions
- [ ] API documentation
- [ ] Architecture overview
- [ ] User guide (how to use the tool)

**Day 38-39: Demo Preparation**
- [ ] Select best sample PDF for demo
- [ ] Script 3-minute demo narrative
- [ ] Record screen capture video
- [ ] Create before/after comparison

**Demo Script:**
```
1. Show Problem (30 sec)
   - Open Revit, show blank project
   - Open PDF HVAC drawing (messy, complex)
   - "Normally takes 40 hours to manually enter this"

2. Show Solution (90 sec)
   - Upload PDF to RevitAssist
   - Wait ~45 seconds
   - Show results: 147 components extracted, 8 warnings
   - Highlight validation: "Airflow mismatch detected"
   - Export Revit JSON

3. Show Value (60 sec)
   - Side-by-side: Manual vs. AI time
   - Cost calculation: $4,000 → $400 saved
   - "4 hours validation vs. 40 hours manual entry"
```

**Day 40-42: First Pilot Setup**
- [ ] Identify 2-3 local MEP firms
- [ ] Prepare pilot proposal
- [ ] Schedule kickoff meetings
- [ ] Set up feedback collection

#### Deliverables
- [ ] Complete documentation
- [ ] 3-minute demo video
- [ ] Pilot agreement template
- [ ] Feedback collection form

#### Success Criteria
- ✅ All documentation complete
- ✅ Demo video recorded and polished
- ✅ 1+ pilot customer committed

---

## Success Metrics

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Extraction Accuracy** | >80% | Manual comparison to ground truth |
| **Processing Time** | <2 min/page | Automated timing |
| **Validation Accuracy** | >90% | Detect intentional errors in test set |
| **False Positive Rate** | <10% | Warnings that are incorrect |

### Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Time Savings** | 30-50 hrs/project | Before/after time tracking |
| **Cost Savings** | $3,000-5,000/project | Labor cost calculation |
| **User Satisfaction** | >80% would use again | Post-pilot survey |
| **Pilot Conversion** | 1+ paying customer | Sales tracking |

---

## Risk Mitigation

### Technical Risks

**Risk:** Vision API accuracy too low  
**Mitigation:**
- Use multiple test PDFs during development
- Iterate on prompts weekly
- Have fallback to simpler OCR if needed

**Risk:** Processing too slow  
**Mitigation:**
- Profile code early (Week 4)
- Implement caching
- Consider parallel processing

**Risk:** PDF quality varies too much  
**Mitigation:**
- Set minimum quality requirements
- Offer re-scanning service as add-on
- Document quality thresholds

### Schedule Risks

**Risk:** Vision API integration takes longer than expected  
**Mitigation:**
- Week 1 Day 1-2: Test API immediately
- Have backup timeline if needed
- Focus on core features first

**Risk:** Validation rules more complex than anticipated  
**Mitigation:**
- Start with 2-3 simple rules (Week 3)
- Add more rules in future iterations
- MVP can have limited validation

---

## Post-MVP Roadmap (Weeks 7-12)

### Week 7-8: Pilot Execution
- Run 3-5 real projects through system
- Collect detailed feedback
- Measure actual time/cost savings
- Iterate based on feedback

### Week 9-10: Production Hardening
- Add error handling
- Implement logging and monitoring
- Create admin dashboard
- Add user authentication

### Week 11-12: Feature Expansion
- Table extraction improvements
- Additional validation rules
- Batch processing
- First version of Revit plugin (optional)

---

## Resource Requirements

### Development Team (MVP)

**Minimum viable team:**
- 1 ML Engineer (full-time, 6 weeks)
- 1 MEP Domain Expert (part-time, 10 hours/week for validation)

**Tooling costs:**
- Anthropic/OpenAI API: ~$500/month during development
- Cloud hosting: ~$100/month (if deploying web version)
- PDF samples: Free (from pilot customers)

**Total MVP Cost Estimate:** $30K-40K (labor) + $600 (APIs/hosting)

---

## Go/No-Go Decision Points

### End of Week 2
**Question:** Is extraction accuracy >70%?  
**If NO:** Extend Week 2 by 3-5 days OR pivot to simpler OCR approach  
**If YES:** Proceed to Week 3

### End of Week 4
**Question:** Does validation catch >80% of test errors?  
**If NO:** Simplify validation rules, focus on 2-3 most important  
**If YES:** Proceed to Week 5

### End of Week 6
**Question:** Does complete pipeline work end-to-end?  
**If NO:** Extend 1-2 weeks before pilots  
**If YES:** Launch pilots

---

## Appendix: Development Environment Setup

### Prerequisites
```bash
# Required software
- Python 3.9+
- Git
- Visual Studio Code (recommended)

# System requirements
- 8GB RAM minimum
- 20GB free disk space
- Internet connection for API calls
```

### Initial Setup
```bash
# Clone repository
git clone https://github.com/your-org/revitassist.git
cd revitassist

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.template .env
# Edit .env and add API keys

# Verify installation
python -m pytest tests/test_setup.py
```

---

**Document Version:** 1.0  
**Last Updated:** January 2025
