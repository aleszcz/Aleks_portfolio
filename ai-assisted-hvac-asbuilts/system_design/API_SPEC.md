# RevitAssist API Specification

## Overview

RevitAssist provides a RESTful API for processing HVAC as-built drawings and generating Revit-compatible structured data.

**Base URL:** `https://api.revitassist.com/v1`  
**Authentication:** API key via header  
**Data Format:** JSON  
**Rate Limits:** 100 requests/hour (free tier), unlimited (paid tiers)

---

## Authentication

### API Key

All requests require an API key in the Authorization header:

```http
Authorization: Bearer <your_api_key>
```

**Getting an API Key:**
```bash
curl -X POST https://api.revitassist.com/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "company": "ABC Engineering"
  }'
```

**Response:**
```json
{
  "api_key": "ra_live_abc123...",
  "tier": "free",
  "rate_limit": 100
}
```

---

## Core Endpoints

### 1. Upload Drawing

**Endpoint:** `POST /drawings/upload`

**Description:** Upload PDF HVAC drawing for processing

**Request:**
```http
POST /v1/drawings/upload
Authorization: Bearer ra_live_abc123...
Content-Type: multipart/form-data

file: <binary_pdf_data>
project_name: "Hospital_Wing_A_Retrofit" (optional)
options: {
  "validate_airflow": true,
  "validate_sizing": true,
  "infer_connections": true,
  "confidence_threshold": 0.7
}
```

**Response:**
```json
{
  "drawing_id": "drw_xyz789",
  "status": "processing",
  "estimated_completion": "2025-01-09T10:35:00Z",
  "webhook_url": "https://your-site.com/webhooks/revitassist" (optional)
}
```

**Status Codes:**
- `202 Accepted` - Processing started
- `400 Bad Request` - Invalid file format
- `413 Payload Too Large` - File exceeds 50MB limit
- `429 Too Many Requests` - Rate limit exceeded

---

### 2. Get Processing Status

**Endpoint:** `GET /drawings/{drawing_id}/status`

**Description:** Check processing status and progress

**Request:**
```http
GET /v1/drawings/drw_xyz789/status
Authorization: Bearer ra_live_abc123...
```

**Response:**
```json
{
  "drawing_id": "drw_xyz789",
  "status": "processing",
  "progress": {
    "current_stage": "validation",
    "percent_complete": 75,
    "stages_completed": ["preprocessing", "extraction", "inference"],
    "stages_remaining": ["validation", "output_generation"]
  },
  "estimated_completion": "2025-01-09T10:35:00Z"
}
```

**Status Values:**
- `queued` - Waiting in processing queue
- `processing` - Currently being processed
- `completed` - Processing finished successfully
- `failed` - Processing failed (see error details)

---

### 3. Get Results

**Endpoint:** `GET /drawings/{drawing_id}/results`

**Description:** Retrieve extraction results and warnings

**Request:**
```http
GET /v1/drawings/drw_xyz789/results
Authorization: Bearer ra_live_abc123...
```

**Response:**
```json
{
  "drawing_id": "drw_xyz789",
  "project_name": "Hospital_Wing_A_Retrofit",
  "processed_at": "2025-01-09T10:34:27Z",
  "processing_time_seconds": 47,
  
  "summary": {
    "total_ducts": 147,
    "total_equipment": 23,
    "total_connections": 165,
    "warnings_count": 8,
    "average_confidence": 0.89
  },
  
  "components": {
    "ducts": [
      {
        "id": "D-1",
        "type": "rectangular",
        "system": "supply",
        "geometry": {
          "start_point": {"x": 120.5, "y": 45.2, "z": 10.0},
          "end_point": {"x": 145.8, "y": 45.2, "z": 10.0}
        },
        "properties": {
          "width": 14,
          "height": 8,
          "cfm": 2400,
          "material": "galvanized_steel"
        },
        "metadata": {
          "confidence": 0.95,
          "source": "extracted",
          "extraction_method": "vision_model"
        }
      }
    ],
    
    "equipment": [
      {
        "id": "AHU-1",
        "type": "air_handler",
        "location": {"x": 100.0, "y": 50.0, "z": 12.0},
        "properties": {
          "cfm": 12000,
          "static_pressure": 2.5,
          "motor_hp": 15,
          "voltage": "480V/3Ph"
        },
        "metadata": {
          "confidence": 0.98,
          "schedule_reference": "Equipment Schedule Sheet M-2"
        }
      }
    ],
    
    "connections": [
      {
        "from": "AHU-1",
        "to": "D-1",
        "type": "supply_duct",
        "confidence": 0.92
      }
    ]
  },
  
  "warnings": [
    {
      "id": "warn_1",
      "severity": "high",
      "type": "airflow_mismatch",
      "component": "AHU-1",
      "message": "Supply fan 12,000 CFM does not match branch total 10,800 CFM",
      "recommendation": "Verify fan capacity or check for missing branches",
      "affected_components": ["AHU-1", "D-1", "D-2", "D-3"]
    },
    {
      "id": "warn_2",
      "severity": "medium",
      "type": "velocity_high",
      "component": "D-12",
      "message": "Duct velocity 2,247 FPM exceeds recommended 2,000 FPM",
      "recommendation": "Increase duct size from 12x8 to 14x8"
    }
  ]
}
```

---

### 4. Export to Revit

**Endpoint:** `GET /drawings/{drawing_id}/export/revit`

**Description:** Download Revit-compatible JSON

**Request:**
```http
GET /v1/drawings/drw_xyz789/export/revit
Authorization: Bearer ra_live_abc123...
```

**Response:** JSON file download

```json
{
  "revit_version": "2024",
  "export_format": "revitassist_v1",
  "project_info": {
    "name": "Hospital_Wing_A_Retrofit",
    "units": "imperial",
    "coordinate_system": "project_base_point"
  },
  "ducts": [...],
  "equipment": [...],
  "connections": [...],
  "metadata": {
    "generated_at": "2025-01-09T10:34:27Z",
    "confidence_threshold": 0.7,
    "excluded_low_confidence_count": 3
  }
}
```

---

### 5. Provide Feedback

**Endpoint:** `POST /drawings/{drawing_id}/feedback`

**Description:** Submit corrections to improve future accuracy

**Request:**
```http
POST /v1/drawings/drw_xyz789/feedback
Authorization: Bearer ra_live_abc123...
Content-Type: application/json

{
  "component_id": "D-1",
  "correction_type": "dimension",
  "original_value": {"width": 14, "height": 8},
  "corrected_value": {"width": 16, "height": 8},
  "notes": "OCR misread 16 as 14"
}
```

**Response:**
```json
{
  "feedback_id": "fb_456",
  "status": "accepted",
  "message": "Thank you for the correction. This will improve future processing."
}
```

---

## Webhook Events

### Setup

Configure webhook URL in your account settings or per-request:

```http
POST /v1/drawings/upload
...
webhook_url: "https://your-site.com/webhooks/revitassist"
```

### Events

**Processing Completed:**
```json
{
  "event": "drawing.processing.completed",
  "drawing_id": "drw_xyz789",
  "timestamp": "2025-01-09T10:34:27Z",
  "data": {
    "status": "completed",
    "summary": {
      "total_ducts": 147,
      "total_equipment": 23,
      "warnings_count": 8
    }
  }
}
```

**Processing Failed:**
```json
{
  "event": "drawing.processing.failed",
  "drawing_id": "drw_xyz789",
  "timestamp": "2025-01-09T10:34:27Z",
  "data": {
    "error_code": "vision_api_error",
    "error_message": "Rate limit exceeded on vision API",
    "retry_possible": true
  }
}
```

---

## Data Models

### Duct Object

```typescript
interface Duct {
  id: string;                    // Unique identifier
  type: "rectangular" | "round"; // Duct shape
  system: "supply" | "return" | "exhaust" | "outside_air";
  
  geometry: {
    start_point: Point3D;
    end_point: Point3D;
    elevation?: number;          // Z-coordinate if different
  };
  
  properties: {
    width?: number;              // Inches (rectangular)
    height?: number;             // Inches (rectangular)
    diameter?: number;           // Inches (round)
    cfm?: number;                // Airflow
    material?: string;           // "galvanized_steel", "stainless", etc.
    insulation?: {
      type: string;
      thickness: number;         // Inches
    };
  };
  
  metadata: {
    confidence: number;          // 0.0-1.0
    source: "extracted" | "inferred" | "schedule";
    extraction_method?: string;
    schedule_reference?: string;
    notes?: string;
  };
}
```

### Equipment Object

```typescript
interface Equipment {
  id: string;                    // Equipment tag (e.g., "AHU-1")
  type: EquipmentType;           // See enum below
  
  location: Point3D;
  
  properties: {
    cfm?: number;
    static_pressure?: number;    // Inches w.g.
    motor_hp?: number;
    voltage?: string;            // "208V/1Ph", "480V/3Ph", etc.
    capacity_tons?: number;      // For cooling equipment
    btu_output?: number;         // For heating equipment
    manufacturer?: string;
    model_number?: string;
  };
  
  metadata: {
    confidence: number;
    schedule_reference?: string;
    installation_notes?: string;
  };
}

enum EquipmentType {
  "air_handler",
  "exhaust_fan",
  "supply_fan",
  "return_fan",
  "roof_top_unit",
  "vav_box",
  "diffuser",
  "grille",
  "damper",
  "heat_exchanger",
  "humidifier",
  "filter"
}
```

### Connection Object

```typescript
interface Connection {
  from: string;                  // Component ID
  to: string;                    // Component ID
  type: "supply_duct" | "return_duct" | "control_wire" | "piping";
  confidence: number;            // 0.0-1.0
  properties?: {
    flow_direction?: "forward" | "reverse";
    valve_type?: string;
    control_sequence?: string;
  };
}
```

### Warning Object

```typescript
interface Warning {
  id: string;
  severity: "low" | "medium" | "high";
  type: WarningType;             // See enum below
  component?: string;            // Affected component ID
  message: string;               // Human-readable description
  recommendation?: string;       // Suggested fix
  affected_components?: string[]; // All related components
  rule_id?: string;              // Validation rule that triggered
}

enum WarningType {
  "airflow_mismatch",
  "velocity_high",
  "velocity_low",
  "sizing_error",
  "missing_connection",
  "component_conflict",
  "code_violation",
  "missing_data",
  "low_confidence"
}
```

### Point3D

```typescript
interface Point3D {
  x: number;  // Pixels or feet (depending on context)
  y: number;
  z: number;
}
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "invalid_file_format",
    "message": "File must be a valid PDF",
    "details": {
      "file_type_detected": "image/jpeg",
      "allowed_types": ["application/pdf"]
    },
    "request_id": "req_abc123",
    "timestamp": "2025-01-09T10:34:27Z"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `invalid_api_key` | 401 | API key missing or invalid |
| `rate_limit_exceeded` | 429 | Too many requests |
| `invalid_file_format` | 400 | File is not a valid PDF |
| `file_too_large` | 413 | File exceeds 50MB limit |
| `processing_failed` | 500 | Internal processing error |
| `vision_api_error` | 503 | External vision API unavailable |
| `insufficient_credits` | 402 | Account out of credits |
| `drawing_not_found` | 404 | Drawing ID does not exist |

---

## Rate Limits

### Tiers

| Tier | Requests/Hour | Max File Size | Concurrent Processing |
|------|---------------|---------------|----------------------|
| **Free** | 100 | 10 MB | 1 |
| **Professional** | 1,000 | 50 MB | 5 |
| **Enterprise** | Unlimited | 100 MB | 20 |

### Rate Limit Headers

Every response includes rate limit information:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 73
X-RateLimit-Reset: 1673274000
```

---

## Batch Processing

### Upload Multiple Drawings

**Endpoint:** `POST /drawings/batch`

**Request:**
```http
POST /v1/drawings/batch
Authorization: Bearer ra_live_abc123...
Content-Type: multipart/form-data

files: [<pdf1>, <pdf2>, <pdf3>]
project_name: "Hospital_Retrofit_Project"
```

**Response:**
```json
{
  "batch_id": "batch_789",
  "drawings": [
    {"drawing_id": "drw_001", "filename": "floor_1.pdf", "status": "queued"},
    {"drawing_id": "drw_002", "filename": "floor_2.pdf", "status": "queued"},
    {"drawing_id": "drw_003", "filename": "floor_3.pdf", "status": "queued"}
  ],
  "webhook_url": "https://your-site.com/webhooks/batch-complete"
}
```

### Get Batch Status

**Endpoint:** `GET /drawings/batch/{batch_id}/status`

**Response:**
```json
{
  "batch_id": "batch_789",
  "status": "processing",
  "progress": {
    "total": 3,
    "completed": 1,
    "processing": 1,
    "queued": 1,
    "failed": 0
  },
  "drawings": [
    {"drawing_id": "drw_001", "status": "completed"},
    {"drawing_id": "drw_002", "status": "processing"},
    {"drawing_id": "drw_003", "status": "queued"}
  ]
}
```

---

## Revit Import Guide

### Using Exported JSON in Revit

**Method 1: Manual Import (MVP)**

1. Download Revit JSON from API
2. Open Revit project
3. Use custom Revit add-in to read JSON (to be provided)
4. Review and place components

**Method 2: Direct Plugin (Future)**

RevitAssist Revit plugin will automatically:
- Fetch results from API
- Place components in active project
- Highlight warnings for review

### JSON to Revit Mapping

| RevitAssist Field | Revit Parameter |
|-------------------|-----------------|
| `duct.width` | Duct Size - Width |
| `duct.height` | Duct Size - Height |
| `duct.cfm` | Flow (CFM) |
| `duct.system` | System Classification |
| `equipment.type` | Family Type |
| `equipment.cfm` | Air Flow |
| `equipment.id` | Mark |

---

## Code Examples

### Python

```python
import requests
import time

# Configuration
API_KEY = "ra_live_abc123..."
BASE_URL = "https://api.revitassist.com/v1"

# Upload drawing
def process_drawing(pdf_path):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    with open(pdf_path, "rb") as f:
        files = {"file": f}
        data = {
            "project_name": "My Project",
            "options": {
                "validate_airflow": True,
                "validate_sizing": True
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/drawings/upload",
            headers=headers,
            files=files,
            json={"options": data["options"]}
        )
        
        drawing_id = response.json()["drawing_id"]
    
    # Wait for completion
    while True:
        status_response = requests.get(
            f"{BASE_URL}/drawings/{drawing_id}/status",
            headers=headers
        )
        
        status = status_response.json()["status"]
        
        if status == "completed":
            break
        elif status == "failed":
            raise Exception("Processing failed")
        
        time.sleep(5)  # Check every 5 seconds
    
    # Get results
    results = requests.get(
        f"{BASE_URL}/drawings/{drawing_id}/results",
        headers=headers
    ).json()
    
    # Export to Revit JSON
    revit_json = requests.get(
        f"{BASE_URL}/drawings/{drawing_id}/export/revit",
        headers=headers
    ).json()
    
    # Save to file
    with open("revit_export.json", "w") as f:
        json.dump(revit_json, f, indent=2)
    
    return results

# Usage
results = process_drawing("hvac_floor_plan.pdf")
print(f"Extracted {results['summary']['total_ducts']} ducts")
print(f"Found {results['summary']['warnings_count']} warnings")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const API_KEY = 'ra_live_abc123...';
const BASE_URL = 'https://api.revitassist.com/v1';

async function processDrawing(pdfPath) {
  const headers = { 'Authorization': `Bearer ${API_KEY}` };
  
  // Upload
  const form = new FormData();
  form.append('file', fs.createReadStream(pdfPath));
  form.append('options', JSON.stringify({
    validate_airflow: true,
    validate_sizing: true
  }));
  
  const uploadResponse = await axios.post(
    `${BASE_URL}/drawings/upload`,
    form,
    { headers: {...headers, ...form.getHeaders()} }
  );
  
  const drawingId = uploadResponse.data.drawing_id;
  
  // Poll for completion
  let status = 'processing';
  while (status === 'processing' || status === 'queued') {
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    const statusResponse = await axios.get(
      `${BASE_URL}/drawings/${drawingId}/status`,
      { headers }
    );
    
    status = statusResponse.data.status;
  }
  
  // Get results
  const results = await axios.get(
    `${BASE_URL}/drawings/${drawingId}/results`,
    { headers }
  );
  
  // Export Revit JSON
  const revitJson = await axios.get(
    `${BASE_URL}/drawings/${drawingId}/export/revit`,
    { headers }
  );
  
  fs.writeFileSync('revit_export.json', JSON.stringify(revitJson.data, null, 2));
  
  return results.data;
}

// Usage
processDrawing('hvac_floor_plan.pdf')
  .then(results => {
    console.log(`Extracted ${results.summary.total_ducts} ducts`);
    console.log(`Found ${results.summary.warnings_count} warnings`);
  });
```

---

## Versioning

**Current Version:** `v1`

**Version Header:**
```http
X-API-Version: v1
```

**Breaking Changes:**
- New major version (v2, v3, etc.)
- Minimum 6 months notice before deprecation
- Both versions supported during transition

**Non-Breaking Changes:**
- New optional fields
- New endpoints
- Bug fixes
- Performance improvements

---

## Support

**Documentation:** https://docs.revitassist.com  
**API Status:** https://status.revitassist.com  
**Support Email:** support@revitassist.com  

**Response Times:**
- Free tier: Best effort (48-72 hours)
- Professional: 24 hours
- Enterprise: 4 hours

---

**Document Version:** 1.0  
**Last Updated:** January 2025  
**API Version:** v1
