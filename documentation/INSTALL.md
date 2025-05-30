# Installation Guide

This guide provides detailed instructions for installing and setting up the Excel Data Extractor.

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **Memory**: At least 4GB RAM recommended
- **Storage**: 100MB free space for installation

### Python Installation

If you don't have Python installed:

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation: `python --version`

**macOS:**
```bash
# Using Homebrew
brew install python@3.11

# Or download from python.org
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip
```

## Installation Steps

### 1. Clone or Download the Project

**Option A: Using Git**
```bash
git clone <repository-url>
cd "Media Plan to Raw Data"
```

**Option B: Download ZIP**
1. Download the project as a ZIP file
2. Extract to your desired location
3. Open terminal/command prompt in the extracted folder

### 2. Create Virtual Environment (Recommended)

Creating a virtual environment keeps dependencies isolated:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

This installs:
- pandas (data processing)
- numpy (numerical operations)
- openpyxl (Excel file handling)
- unidecode (text normalization)

### 4. Verify Installation

```bash
# Test the installation
python main_scripts/excel_data_extractor.py --help
```

You should see the help message with usage instructions.

## Configuration

### 1. Check Configuration Files

Ensure these files exist in the project root:
- `config.json` - Main configuration
- `config/template_mapping_config.json` - Template mapping settings

### 2. Create Output Directory

The tool creates an output directory automatically, but you can create it manually:

```bash
mkdir output
```

### 3. Prepare Input Files

Place your input files in the `input/` directory:
- PLANNED files: `PLANNED_INPUT_TEMPLATE_*.xlsx`
- DELIVERED files: `DELIVERED_INPUT_TEMPLATE_*.xlsx`
- Template file: `OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx`

## Quick Test

Run a quick test to ensure everything is working:

```bash
# Extract from sample files
python main_scripts/excel_data_extractor.py \
  --planned input/PLANNED_INPUT_TEMPLATE_Final\ Media\ Plan\ Template_060525.xlsx \
  --delivered input/DELIVERED_INPUT_TEMPLATE_PCA\ -\ Sensodyne\ CW\ \(Q125\).xlsx \
  --output output/ \
  --combine
```

## Troubleshooting

### Common Issues

1. **"python: command not found"**
   - Python is not in PATH
   - Try `python3` instead of `python`
   - Reinstall Python with PATH option checked

2. **"No module named 'pandas'"**
   - Dependencies not installed
   - Run: `pip install -r requirements.txt`
   - Make sure virtual environment is activated

3. **Permission denied errors**
   - On Linux/macOS: Use `python3` and `pip3`
   - May need to use `sudo` for global installation (not recommended)

4. **Excel file errors**
   - Ensure input files are .xlsx format (not .xls)
   - Close files in Excel before processing
   - Check file permissions

### Environment Variables

Optional environment variables:
```bash
# Set logging level
export EXCEL_EXTRACTOR_LOG_LEVEL=DEBUG  # Linux/macOS
set EXCEL_EXTRACTOR_LOG_LEVEL=DEBUG     # Windows
```

## Updating

To update to a newer version:

```bash
# Pull latest changes (if using git)
git pull

# Update dependencies
pip install -r requirements.txt --upgrade
```

## Uninstallation

To remove the installation:

1. Deactivate virtual environment: `deactivate`
2. Delete the project folder
3. Remove Python (optional) through system settings

## Next Steps

After successful installation:
1. Read the [USER_GUIDE.md](USER_GUIDE.md) for usage instructions
2. Review sample files in the `input/` directory
3. Check `memory-bank/` for detailed documentation

## Support

If you encounter issues:
1. Check the log file: `logs/excel_processor.log`
2. Enable debug logging for more details
3. Ensure your input files match the expected format
4. Review the troubleshooting section above