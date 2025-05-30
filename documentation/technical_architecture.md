# Technical Architecture

**Last Updated:** May 29, 2025  
**Status:** Production Ready - v1.0.0

## System Overview

The Media Plan to Raw Data Automation system is a production-ready Python application that processes media planning data from Excel files and maps it to standardized output templates with 100% data coverage.

## Core Technologies

* **Python 3.8+**: Main development language
* **pandas 2.0+**: Data manipulation and analysis
* **openpyxl 3.1+**: Excel file operations (.xlsx)
* **numpy**: Numerical operations
* **anthropic**: Claude API integration (optional)
* **tqdm**: Progress tracking
* **psutil**: Performance monitoring

## Architecture Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Input Layer                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   PLANNED   │  │  DELIVERED   │  │ OUTPUT TEMPLATE  │  │
│  │    Excel    │  │    Excel     │  │     Excel        │  │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘  │
└─────────┼────────────────┼───────────────────┼─────────────┘
          │                │                   │
┌─────────▼────────────────▼───────────────────▼─────────────┐
│                    Processing Layer                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Excel Data Extractor                       │   │
│  │  - Format Detection (PLANNED/DELIVERED)              │   │
│  │  - Region Detection (START/END markers)              │   │
│  │  - R&F Data Normalization                           │   │
│  │  - Platform Identification                          │   │
│  │  - Data Validation                                  │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        │                                     │
│  ┌─────────────────────▼───────────────────────────────┐   │
│  │           Simple LLM Mapper                          │   │
│  │  - 100% Column Mapping                              │   │
│  │  - Template Structure Detection                     │   │
│  │  - Number Precision Handling                        │   │
│  │  - Client-Specific Rules                           │   │
│  │  - LLM Enhancement (Optional)                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────────────────────┐
│                     Support Components                       │
│  ┌──────────────┐  ┌────────────────┐  ┌───────────────┐   │
│  │    Error     │  │  Performance   │  │    Number     │   │
│  │   Handler    │  │    Monitor     │  │  Precision    │   │
│  └──────────────┘  └────────────────┘  └───────────────┘   │
└─────────────────────────────────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────────────────────┐
│                      Output Layer                            │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   Mapped    │  │   Reports    │  │      Logs        │   │
│  │  Template   │  │   (3 types) │  │   (detailed)     │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Excel Data Extractor (`excel_data_extractor.py`)
- **Purpose**: Extract and normalize data from PLANNED and DELIVERED formats
- **Key Features**:
  - Auto-detection of file formats
  - START/END marker recognition
  - R&F data special handling
  - Platform alias resolution
  - Progress tracking

### 2. Simple LLM Mapper (`simple_llm_mapper.py`)
- **Purpose**: Map extracted data to output template with 100% coverage
- **Key Features**:
  - Dynamic template structure detection
  - Intelligent column mapping
  - Number precision handling
  - Client-specific rules support
  - Optional Claude API integration

### 3. Production Error Handler (`production_error_handler.py`)
- **Purpose**: Comprehensive error handling and validation
- **Key Features**:
  - Data structure validation
  - Missing data handling
  - Error recovery mechanisms
  - Detailed error reporting

### 4. Performance Monitor (`performance_monitor.py`)
- **Purpose**: Track system performance and progress
- **Key Features**:
  - Real-time progress bars
  - Memory usage tracking
  - Operation timing
  - Performance metrics logging

## Data Flow

```
1. Input Files
   ├── PLANNED.xlsx → Extract regions by platform
   └── DELIVERED.xlsx → Extract media + R&F data

2. Extraction Phase
   ├── Detect format type
   ├── Find data regions
   ├── Normalize column names
   └── Combine into COMBINED.xlsx

3. Mapping Phase
   ├── Load template structure
   ├── Map 36 data columns
   ├── Apply precision rules
   └── Write to exact positions

4. Output Generation
   ├── Populated template
   ├── Validation report
   ├── Performance report
   └── Comprehensive mapping report
```

## Configuration System

### 1. Client Mapping Rules (`config/client_mapping_rules.json`)
```json
{
  "clients": {
    "sensodyne": {
      "column_overrides": {
        "BUDGET_LOCAL": "Net Spend"
      },
      "value_transformations": {
        "MARKET": {
          "UAE": "United Arab Emirates"
        }
      }
    }
  }
}
```

### 2. Template Mapping Config (`config/template_mapping_config.json`)
- Platform structure definitions
- Row/column coordinates
- Metric mappings

### 3. Environment Variables
- `CLIENT_ID`: Select client-specific rules
- `ANTHROPIC_API_KEY`: Enable LLM enhancement
- `EXCEL_EXTRACTOR_LOG_LEVEL`: Debug logging

## Key Algorithms

### 1. Region Detection
```python
def find_markers(worksheet, start_markers, end_markers):
    # Scan for START/END markers
    # Build boundary box
    # Validate completeness
    return regions
```

### 2. R&F Data Normalization
```python
def normalize_rf_table(rf_data):
    # Pivot metric rows to columns
    # Map to standard names
    # Tag with Source_Sheet
    return normalized_data
```

### 3. Number Precision
```python
def fix_precision(value, column):
    # Apply Decimal rounding
    # Currency: 2 decimals
    # Counts: 0 decimals
    # Percentages: 2 decimals
    return precise_value
```

## Performance Characteristics

- **Extraction Speed**: ~2.3 seconds for typical files
- **Mapping Speed**: ~17 seconds including all reports
- **Memory Usage**: <200MB for standard datasets
- **Scalability**: Handles 10,000+ rows efficiently

## Security Considerations

- Input validation on all Excel files
- No execution of Excel macros
- Sanitization of file paths
- Secure API key handling
- Comprehensive error logging

## Deployment Architecture

```
deployment/
├── media_plan_automation_[timestamp].zip
    ├── scripts/           # Core Python scripts
    ├── config/           # Configuration files
    ├── documentation/    # User guides
    ├── requirements.txt  # Dependencies
    ├── setup_windows.bat # Windows installer
    └── setup_unix.sh     # Unix installer
```

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.8+ | Core development |
| Data Processing | pandas | 2.0+ | DataFrame operations |
| Excel Operations | openpyxl | 3.1+ | Read/write Excel |
| Numerical | numpy | 1.24+ | Array operations |
| AI Integration | anthropic | 0.25+ | Claude API |
| Progress | tqdm | 4.66+ | Progress bars |
| Monitoring | psutil | 5.9+ | System metrics |
| HTTP | requests | 2.31+ | API calls |

## Future Architecture Considerations

1. **Web Interface**: Flask/FastAPI for REST API
2. **Database**: PostgreSQL for audit trails
3. **Queue System**: Celery for async processing
4. **Cloud Storage**: S3/Azure Blob integration
5. **Containerization**: Docker for deployment

---

For implementation details, see [INDEX.md](../INDEX.md)