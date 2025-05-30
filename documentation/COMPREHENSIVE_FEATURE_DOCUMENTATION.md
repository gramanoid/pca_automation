# Comprehensive Feature Documentation
**Last Updated: May 29, 2025**

## Table of Contents
1. [System Overview](#system-overview)
2. [Core Features](#core-features)
3. [Recent Enhancements](#recent-enhancements)
4. [Configuration & Setup](#configuration--setup)
5. [Workflow Execution](#workflow-execution)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Feature Verification Checklist](#feature-verification-checklist)

---

## System Overview

The Media Plan to Raw Data automation system processes Excel files containing media planning and delivery data, extracting and normalizing the data, then mapping it to a standardized output template with 100% accuracy.

### Key Achievements
- ✅ **100% Data Coverage**: All 36 columns mapped successfully
- ✅ **Fast Performance**: Complete workflow in ~4.35 seconds
- ✅ **Smart R&F Handling**: Special logic for Reach & Frequency data
- ✅ **Enhanced Reporting**: Professional context section with insights
- ✅ **Template Protection**: Validates template integrity before processing

---

## Core Features

### 1. Data Extraction (`excel_data_extractor.py`)
**Purpose**: Extract data from PLANNED and DELIVERED Excel files

**Key Features**:
- Handles multiple sheet formats (DV360, META, TIKTOK)
- Automatic format detection using markers
- R&F data normalization
- Platform-specific handling
- Combines data into unified format

**Usage**:
```bash
python3 main_scripts/excel_data_extractor.py \
    --planned input/PLANNED_INPUT_TEMPLATE_*.xlsx \
    --delivered input/DELIVERED_INPUT_TEMPLATE_*.xlsx \
    --output output/ \
    --combine
```

### 2. Template Mapping (`simple_llm_mapper.py`)
**Purpose**: Map extracted data to standardized output template

**Key Features**:
- 100% column coverage (36/36 columns)
- Claude API integration for unknown mappings
- Client-specific mapping rules
- Number precision handling
- Enhanced context section
- Template protection validation
- Progress tracking (8 steps to 100%)

**Usage**:
```bash
python3 main_scripts/simple_llm_mapper.py \
    --input output/COMBINED_*.xlsx \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
    --output output/final_mapped.xlsx
```

### 3. Template Protection (`protect_excel_template.py`)
**Purpose**: Protect Excel template from accidental modification

**Key Features**:
- Selective cell protection
- Manual entry cells remain editable
- Column/row resizing allowed
- Password protection optional

**Usage**:
```bash
python3 main_scripts/protect_excel_template.py \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
    --mode script \
    --manual-cells C16 C17 C54 C55 C92 C93
```

---

## Recent Enhancements (May 29, 2025)

### 1. Progress Bar Fix
- **Issue**: Progress stopped at 75% (6/8 steps)
- **Fix**: Added missing progress updates in map_data()
- **Result**: Now reaches 100% with all 8 steps tracked

### 2. Template Protection Validation
- **Feature**: Extensive logging when template is modified
- **Implementation**: Checks protected cells (A3, A4, B16, B17)
- **Warnings**: Clear error messages if template compromised

### 3. Enhanced Context Section
- **Location**: Starts at row 125 in output
- **Contents**:
  - Campaign Overview with metrics
  - Platform Performance Summary table
  - Campaign Elements & Targeting (with emojis)
  - Data Quality Report
- **Styling**: Professional colors, borders, smart formatting

### 4. Platform Structure Updates
- **DV360**: Rows 15-42 (Purchase now has 6 metrics)
- **META**: Rows 53-80 (shifted down by 1)
- **TIKTOK**: Rows 91-118 (shifted up by 1)
- **Markets**: Now supports 6 markets including Jordan

---

## Configuration & Setup

### Environment Variables
```bash
# Required for enhanced mappings
export ANTHROPIC_API_KEY=your_api_key_here

# Optional client-specific rules
export CLIENT_ID=sensodyne

# Optional debug logging
export EXCEL_EXTRACTOR_LOG_LEVEL=DEBUG
```

### Configuration Files

#### `config/client_mapping_rules.json`
```json
{
  "clients": {
    "sensodyne": {
      "column_overrides": {
        "CUSTOM_FIELD": "Target Column"
      }
    }
  }
}
```

#### `config/template_mapping_config.json`
- Template-specific mapping configurations
- Platform row definitions
- Market column mappings

---

## Workflow Execution

### Complete Workflow (Timed)
```bash
python3 run_complete_timed_workflow.py
```

**Workflow Steps**:
1. **Template Protection** (optional)
2. **Data Extraction** (~2.0s)
3. **Template Mapping** (~2.3s)
**Total Time**: ~4.35 seconds

### Individual Steps

#### Step 1: Extract Data
```bash
python3 main_scripts/excel_data_extractor.py \
    --planned input/PLANNED_*.xlsx \
    --delivered input/DELIVERED_*.xlsx \
    --output output/ \
    --combine
```

#### Step 2: Map to Template
```bash
python3 main_scripts/simple_llm_mapper.py \
    --input output/COMBINED_*.xlsx \
    --template input/OUTPUT_TEMPLATE_*.xlsx \
    --output output/final_mapped.xlsx
```

---

## Troubleshooting Guide

### Common Issues & Solutions

#### 1. Template Protection Violations
**Error**: "TEMPLATE PROTECTION VIOLATION: Cell A3: Expected 'Budget (Planned)', found 'PLANNED BUDGET'"

**Solution**: Use an unmodified template file. The script expects specific labels in cells:
- A3: "Budget (Planned)"
- A4: "Budget (Actual)"
- B16: "Census TA"
- B17: "TA Population"

#### 2. Progress Bar Stops at 75%
**Issue**: Progress shows 6/8 instead of 8/8

**Solution**: Update to latest version of simple_llm_mapper.py with 8 progress steps

#### 3. API Key Missing
**Warning**: "No Anthropic API key found. LLM features will be disabled."

**Solution**: Set environment variable:
```bash
export ANTHROPIC_API_KEY=your_key_here
```

#### 4. R&F Data Not Mapping
**Issue**: Reach & Frequency data showing as 0 or missing

**Solution**: Ensure R&F sheets are properly named (e.g., "DV360 R&F") and contain correct metric names in PLATFORM column

---

## Feature Verification Checklist

### Data Extraction ✅
- [ ] Processes PLANNED files correctly
- [ ] Processes DELIVERED MEDIA files correctly
- [ ] Processes DELIVERED R&F files correctly
- [ ] Combines all data into single output
- [ ] Handles all 3 platforms (DV360, META, TIKTOK)
- [ ] Maintains Source_Type and Source_Sheet tags

### Template Mapping ✅
- [ ] Achieves 100% coverage (36/36 columns)
- [ ] Maps all platform data correctly
- [ ] Handles R&F data special cases
- [ ] Writes market headers dynamically
- [ ] Applies currency formatting
- [ ] Applies percentage formatting
- [ ] Bold formatting for Purchase totals
- [ ] Progress bar reaches 100%

### Enhanced Features ✅
- [ ] Template protection validation works
- [ ] Enhanced context section displays
- [ ] Platform performance summary calculates
- [ ] Data quality metrics show
- [ ] Claude API integration (when available)
- [ ] Client-specific rules apply

### Performance ✅
- [ ] Complete workflow < 5 seconds
- [ ] Memory usage tracked
- [ ] Performance reports generated
- [ ] Error handling comprehensive

---

## Maintenance Guidelines

### Adding New Features
1. Always backup existing working code
2. Test with regression suite
3. Update documentation
4. Update CLAUDE.md
5. Create feature tests

### Debugging
1. Check logs in `main_scripts/logs/`
2. Enable debug logging: `export EXCEL_EXTRACTOR_LOG_LEVEL=DEBUG`
3. Review validation reports
4. Check comprehensive reports

### Version Control
- Current version: 2.0
- Major changes require version bump
- Keep changelog updated

---

## File Structure Reference

```
project/
├── main_scripts/
│   ├── excel_data_extractor.py      # Core extraction
│   ├── simple_llm_mapper.py         # Enhanced mapper
│   ├── protect_excel_template.py    # Template protection
│   ├── production_error_handler.py  # Error handling
│   └── performance_monitor.py       # Performance tracking
├── config/
│   ├── client_mapping_rules.json    # Client configurations
│   └── template_mapping_config.json # Template settings
├── documentation/
│   ├── COMPREHENSIVE_FEATURE_DOCUMENTATION.md  # This file
│   ├── RF_DATA_HANDLING_GUIDE.md    # R&F specifics
│   └── ENHANCED_CONTEXT_SECTION_GUIDE.md # Context details
└── run_complete_timed_workflow.py   # Full workflow runner
```

---

## Contact & Support

For issues or questions:
1. Check this documentation first
2. Review error logs
3. Consult CLAUDE.md for AI-specific guidance
4. Create issue in project repository

**Remember**: Always use unmodified templates and maintain proper backups!