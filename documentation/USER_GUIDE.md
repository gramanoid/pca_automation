# User Guide - Media Plan to Raw Data Automation

*Last Updated: May 29, 2025*

## Overview

This production-ready system automates the conversion of media planning data into a standardized output format with 100% data coverage and high accuracy.

**📍 Quick Reference**: For technical documentation, see [`INDEX.md`](INDEX.md)

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Input File Formats](#input-file-formats)
5. [Basic Usage](#basic-usage)
6. [Advanced Usage](#advanced-usage)
7. [Output Files](#output-files)
8. [Features & Capabilities](#features--capabilities)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

## Prerequisites

- Python 3.8 or higher
- Required Python packages (install with `pip install -r requirements.txt`)
- Excel files in the correct format:
  - **PLANNED**: Media plan template (e.g., `PLANNED_INPUT_TEMPLATE_Final Media Plan Template_060525.xlsx`)
  - **DELIVERED**: Platform data exports (e.g., `DELIVERED_INPUT_TEMPLATE_PCA - Sensodyne CW (Q125).xlsx`)
  - **OUTPUT TEMPLATE**: Empty template file (e.g., `OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx`)

## Installation

1. Clone or download this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

Run the complete workflow:

```bash
# Option 1: Run complete automated workflow
python production_workflow/orchestration/run_complete_workflow.py

# Option 2: Run steps manually
# Step 1: Extract and combine data
python production_workflow/01_data_extraction/extract_and_combine_data.py \
  --planned input/PLANNED_*.xlsx \
  --delivered input/DELIVERED_*.xlsx \
  --output output/ \
  --combine

# Step 2: Map to output template
python production_workflow/03_template_mapping/map_to_template.py \
  --input output/COMBINED_*.xlsx \
  --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
  --output output/final_mapped.xlsx
```

## Input File Formats

### PLANNED Files
- **Format**: Media plan template with START/END markers
- **Platforms**: DV360, META, TIKTOK sheets
- **Structure**:
  - Row 3: START/END markers define data regions
  - Row 4: Column headers
  - Row 5+: Data rows (each ending with END marker)

### DELIVERED Files
- **Format**: Platform data exports with two sections per sheet
- **Sections**:
  1. **R&F (Reach & Frequency)** - Rows 4-9
     - 6 metrics × 5 markets matrix
     - Metrics in rows, markets in columns
  2. **Media Section** - Starting from Row 14
     - Individual line items per market
     - Standard column format

## Basic Usage

### Step 1: Prepare Your Files
Place your input files in the `input/` directory:
- **PLANNED file**: Your media plan Excel file
  - Must contain: Campaign info, markets, platforms, objectives
  - Supports: DV360, META, TIKTOK platforms
- **DELIVERED file**: Your platform data export  
  - Must contain: Media delivery data and R&F sheets
  - Handles multiple platform exports in one file
- **OUTPUT_TEMPLATE**: The empty template to fill
  - Standard Digital Tracker Report format
  - Will be populated with all data automatically

### Step 2: Run the Extraction
```bash
python production_workflow/01_data_extraction/extract_and_combine_data.py \
  --planned input/PLANNED_*.xlsx \
  --delivered input/DELIVERED_*.xlsx \
  --output output/ \
  --combine
```

This will create:
- `PLANNED_[timestamp].xlsx` - Normalized planned data
- `DELIVERED_[timestamp].xlsx` - Normalized delivered data
- `COMBINED_[timestamp].xlsx` - Merged data ready for mapping

**Features:**
- Automatic region detection
- Platform identification
- R&F data normalization
- Progress tracking
- Comprehensive error handling

### Step 3: Run the Mapping
```bash
python production_workflow/03_template_mapping/map_to_template.py \
  --input output/COMBINED_*.xlsx \
  --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
  --output output/final_mapped.xlsx
```

This will:
1. Load the COMBINED data file
2. Map 100% of data columns to the template
3. Write all template headers and context
4. Position data in exact template structure
5. Create comprehensive reports

## Advanced Usage

### Client-Specific Configuration
```bash
# Use client-specific mapping rules
export CLIENT_ID=sensodyne
python production_workflow/03_template_mapping/map_to_template.py \
  --input output/COMBINED_*.xlsx \
  --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
  --output output/final_mapped.xlsx
```

### Enhanced Mapping with Claude API
```bash
# Set API key for unknown column mapping
export ANTHROPIC_API_KEY=your_api_key_here
python production_workflow/03_template_mapping/map_to_template.py \
  --input output/COMBINED_*.xlsx \
  --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
  --output output/final_mapped.xlsx
```

### Debug Mode
```bash
# Enable detailed logging
export EXCEL_EXTRACTOR_LOG_LEVEL=DEBUG
python production_workflow/01_data_extraction/extract_and_combine_data.py \
  --planned input/PLANNED_*.xlsx \
  --delivered input/DELIVERED_*.xlsx \
  --output output/ \
  --combine
```

### Processing Only PLANNED or DELIVERED
```bash
# PLANNED only
python production_workflow/01_data_extraction/extract_and_combine_data.py \
  --planned input/PLANNED_*.xlsx \
  --output output/

# DELIVERED only  
python production_workflow/01_data_extraction/extract_and_combine_data.py \
  --delivered input/DELIVERED_*.xlsx \
  --output output/
```

## Output Files

The system creates several output files:

### 1. Extraction Outputs (in `output/`)
- `PLANNED_[timestamp].xlsx` - Normalized planned data
- `DELIVERED_[timestamp].xlsx` - Normalized delivered data with R&F
- `COMBINED_[timestamp].xlsx` - Merged data ready for mapping

### 2. Mapping Outputs
- `final_mapped.xlsx` - Fully populated template with:
  - Campaign headers (name, dates, budgets)
  - Market columns (ordered by budget)
  - Platform sections (DV360, META, TIKTOK)
  - All metrics (Campaign Level, Awareness, Consideration, Purchase)
  - Additional context data
   
### 3. Reports
- `*_COMPREHENSIVE_REPORT.txt` - Complete mapping details
- `*_VALIDATION_REPORT.txt` - Data quality checks
- `*_PERFORMANCE_REPORT.txt` - Processing metrics

## Features & Capabilities

### Data Coverage
- ✅ **100% column mapping** (36/36 columns)
- ✅ **All template sections** populated
- ✅ **Platform support**: DV360, META, TIKTOK
- ✅ **Market support**: Dynamic (up to 5 markets)
- ✅ **R&F data**: Special handling for metrics

### Data Quality
- ✅ **Number precision**: Proper decimal handling
- ✅ **Calculation validation**: CTR, CPM, CPC checks
- ✅ **Error handling**: Comprehensive validation
- ✅ **Missing data**: Smart defaults

### Performance
- ✅ **Progress tracking**: Real-time progress bars
- ✅ **Performance monitoring**: Detailed metrics
- ✅ **Memory efficient**: Handles large files
- ✅ **Fast processing**: ~20 seconds total

## Troubleshooting

### Common Issues

1. **"File not found" errors**
   - Ensure files are in the `input/` directory
   - Check file naming matches the pattern
   - Use wildcards: `PLANNED_*.xlsx`

2. **"Missing columns" errors**
   - Verify your files have the required columns
   - Check Excel sheet names (especially for R&F data)
   - Review validation report for details

3. **Mapping issues**
   - Check comprehensive report for unmapped columns
   - Review client configuration if using CLIENT_ID
   - Enable debug logging for details

4. **Number accuracy issues**
   - System automatically handles precision
   - Check validation report for anomalies
   - Currency: 2 decimals, Counts: integers

### Log Files
Detailed logs are saved to:
- `logs/excel_processor.log`
- `production_workflow/05_monitoring/logs/` (various logs)

### Getting Help
- Check logs in `logs/` and `production_workflow/05_monitoring/logs/`
- Review comprehensive reports in `output/`
- See [OPERATIONAL_RUNBOOK.md](OPERATIONAL_RUNBOOK.md) for production issues

## Best Practices

1. **Always use the latest files**
   - Place new files in `input/` directory
   - Archive old outputs regularly

2. **Review reports**
   - Check comprehensive report for coverage
   - Review validation report for data quality
   - Monitor performance report for issues

3. **Client configurations**
   - Set CLIENT_ID for client-specific rules
   - Update `config/client_mapping_rules.json` as needed

4. **Production deployment**
   - Use `python3 deploy.py` to create deployment package
   - Test with sample data first
   - Keep backups of successful outputs

## Support

For issues or questions:
1. Check [INDEX.md](../INDEX.md) for documentation
2. Review logs in `main_scripts/logs/`
3. See [OPERATIONAL_RUNBOOK.md](OPERATIONAL_RUNBOOK.md) for troubleshooting
4. Check archived documentation for historical context

---

**Remember**: The system is designed for simplicity and accuracy. If something seems complex, there's probably a simpler way!