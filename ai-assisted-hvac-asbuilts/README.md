# RevitAssist: AI-Powered PDF to Revit Automation

## Overview

RevitAssist is an AI-assisted system that automates the manual sketching of HVAC as-built drawings into Revit, reducing 40-60 hours of tedious data entry per project to 4 hours of validation work.

**Market Problem:** MEP contractors waste $4,000-5,600 per project on manual Revit data entry from PDF drawings.

**Solution:** Multimodal AI that understands HVAC engineering logic and automates PDF → Revit sketching, saving 90% of manual labor while maintaining engineering accuracy through human-in-the-loop validation.

---

## The Problem

### Current Workflow Pain Points

```
PDF Drawing → Manual Sketching (40-60 hrs) → Revit 2D → Revit 3D → Coordination
                      ↑
                 PAIN POINT
```

**Issues:**
- 40-60 hours per project manually tracing PDFs into Revit
- Error-prone: typos in dimensions, missed components, incorrect metadata
- Cost: $4,000-5,600 per project in engineering labor ($100/hr × 40-60 hrs)
- Bottleneck for retrofit and modernization projects
- As-built data trapped in legacy formats (PDFs, scans, hand notes)

### Why Existing Solutions Don't Work

| Solution | What It Does | What It Doesn't Do |
|----------|--------------|-------------------|
| **Matterport** | 3D scans of existing buildings | Convert PDFs to Revit data |
| **Revit** | BIM software with 3D capabilities | Automate data entry from PDFs |
| **Generic OCR** | Extract text from PDFs | Understand HVAC/MEP logic |
| **RevitAssist** | **PDF → structured Revit data with HVAC reasoning** | **Nobody else does this** |

---

## Solution Overview

### What RevitAssist Does

**Input:** PDF HVAC as-built drawings, equipment schedules, field notes

**Process:**
1. **Multimodal Parsing**: Extract components, dimensions, annotations using vision models
2. **HVAC Reasoning**: Validate using domain constraints (airflow, sizing, codes)
3. **Structured Output**: Generate Revit-compatible JSON with confidence scores
4. **Human Validation**: Engineers review flagged issues, approve/correct in 4 hours

**Output:** 
- Revit-ready component data (ducts, equipment, connections, metadata)
- Flagged inconsistencies with explanations
- 80-90% automated accuracy

### Updated Workflow

```
PDF Drawing → AI Sketching (45 sec) → Validation (4 hrs) → Revit 2D → Revit 3D
     ↓                                      ↓
  Upload                            Review/Approve
```

**Time Saved:** 36-56 hours per project  
**Cost Saved:** $3,600-5,600 per project

---

## Key Features

### 1. Automated Component Extraction
- Ducts: centerlines, dimensions, CFM annotations
- Equipment: symbols, locations, capacities (AHU, EF, RTU, VAV)
- Connections: spatial relationships and logical flow
- Metadata: CFM, tonnage, pressure, dimensions

### 2. HVAC Reasoning Engine
Validates using domain constraints:
- Airflow continuity (supply fan CFM = branch total)
- Duct sizing logic (velocity, friction loss per ASHRAE)
- Equipment compatibility
- Code compliance checks

### 3. Intelligent Warnings
Flags inconsistencies with explanations:
- "Airflow mismatch: Supply fan 12,000 CFM, branches total 10,800 CFM"
- "Duct D-12 undersized: 12×8 for 2,400 CFM exceeds 2,000 FPM velocity"
- "Equipment AHU-3 listed in schedule but not found in drawing"

### 4. Human-in-the-Loop Validation
- Engineers review AI suggestions
- Focus on flagged warnings (~8-15 items per project)
- Bulk approve remaining components
- Total validation time: 4 hours

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    PDF Input Layer                          │
│  (Scanned drawings, equipment schedules, field notes)       │
└─────────────────────┬───────────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
┌────────▼─────────┐      ┌───────▼──────────┐
│  Vision Parser   │      │  Table Parser    │
│  (Claude/GPT-4V) │      │  (Schedules)     │
└────────┬─────────┘      └───────┬──────────┘
         │                         │
         └────────────┬────────────┘
                      │
              ┌───────▼────────┐
              │ HVAC Reasoning │
              │    Engine      │
              │  (Validation)  │
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │ Output Generator│
              │ (Revit JSON)   │
              └───────┬────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
┌────────▼─────────┐      ┌───────▼──────────┐
│  Web Interface   │      │  Revit Export    │
│  (Validation)    │      │     (JSON)       │
└──────────────────┘      └──────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.9+
- Anthropic API key or OpenAI API key
- Sample HVAC PDF drawings

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/revitassist.git
cd revitassist

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.template .env
# Edit .env and add your API keys
```

### Basic Usage

```python
from revitassist import HVACProcessor

# Initialize processor
processor = HVACProcessor(api_key="your_api_key")

# Process PDF drawing
result = processor.process_drawing("path/to/hvac_drawing.pdf")

# Review results
print(f"Extracted {len(result.ducts)} ducts")
print(f"Extracted {len(result.equipment)} equipment units")
print(f"Found {len(result.warnings)} warnings")

# Export to Revit JSON
result.export_revit_json("output/revit_data.json")
```

---

## Project Structure

```
revitassist/
├── src/
│   ├── parsers/
│   │   ├── vision_parser.py      # PDF → components extraction
│   │   ├── table_parser.py       # Equipment schedule extraction
│   │   └── text_parser.py        # Annotation extraction
│   ├── reasoning/
│   │   ├── hvac_validator.py     # Domain constraint validation
│   │   ├── airflow_checker.py    # Airflow continuity rules
│   │   └── sizing_checker.py     # Duct sizing validation
│   ├── exporters/
│   │   ├── revit_exporter.py     # Generate Revit JSON
│   │   └── json_schema.py        # Output format definitions
│   └── web/
│       ├── app.py                # Web interface
│       └── api.py                # REST API
├── tests/
│   ├── test_parsers.py
│   ├── test_validation.py
│   └── fixtures/                 # Sample PDFs for testing
├── docs/
│   ├── ARCHITECTURE.md           # Technical architecture
│   ├── API_SPEC.md              # API documentation
│   ├── MARKET_ANALYSIS.md       # Market opportunity
│   └── MVP_ROADMAP.md           # Implementation plan
├── requirements.txt
├── .env.template
└── README.md
```

---

## Output Format

### Revit-Compatible JSON

```json
{
  "project_info": {
    "name": "Building_123_HVAC_AsBuilt",
    "units": "imperial"
  },
  "ducts": [
    {
      "id": "D-1",
      "start_point": {"x": 120.5, "y": 45.2, "z": 10.0},
      "end_point": {"x": 145.8, "y": 45.2, "z": 10.0},
      "width": 14,
      "height": 8,
      "cfm": 2400,
      "system": "supply",
      "confidence": 0.95
    }
  ],
  "equipment": [
    {
      "id": "AHU-1",
      "type": "air_handler",
      "location": {"x": 100.0, "y": 50.0, "z": 12.0},
      "cfm": 12000,
      "static_pressure": 2.5,
      "confidence": 0.98
    }
  ],
  "warnings": [
    {
      "component_id": "D-12",
      "issue": "CFM mismatch with supply fan",
      "severity": "medium",
      "recommendation": "Verify supply fan capacity or branch takeoff"
    }
  ]
}
```

---

## Performance Metrics

### Target Metrics

- **Extraction Accuracy:** >90% for components
- **Validation Accuracy:** >95% for flagged errors
- **Processing Time:** <60 seconds per drawing
- **False Positive Rate:** <5%
- **Time Savings:** 30-50 hours per project (75-85% reduction)

---

## Development Roadmap

### Phase 1: MVP (Weeks 1-6)
- ✅ Core PDF parsing with vision models
- ✅ Basic HVAC validation rules
- ✅ JSON export for Revit
- ✅ Simple web interface

### Phase 2: Production (Weeks 7-12)
- [ ] Advanced validation rules
- [ ] Batch processing
- [ ] User authentication
- [ ] Project management dashboard

### Phase 3: Extensions (Months 4-6)
- [ ] Matterport point cloud integration
- [ ] Direct Revit plugin
- [ ] Other MEP systems (plumbing, electrical)
- [ ] Feedback loop for model improvement

See [MVP_ROADMAP.md](docs/MVP_ROADMAP.md) for detailed timeline.

---

## Market Opportunity

- **TAM:** $100B+ MEP construction market
- **Target:** 50,000+ MEP firms in US
- **Savings per project:** $3,600-5,600
- **Annual savings (mid-size firm):** $400K

See [MARKET_ANALYSIS.md](docs/MARKET_ANALYSIS.md) for details.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

---

## License

[Your chosen license]

---

## Documentation

- [Technical Architecture](docs/ARCHITECTURE.md)
- [API Specification](docs/API_SPEC.md)
- [Market Analysis](docs/MARKET_ANALYSIS.md)
- [MVP Roadmap](docs/MVP_ROADMAP.md)

---

## Contact

For questions or support: [contact information]

---

**Status:** 🚧 In Development  
**Last Updated:** January 2025
