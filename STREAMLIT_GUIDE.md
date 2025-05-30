# Streamlit Web Interface Guide

## Overview

The Streamlit web interface provides a user-friendly way to run the Media Plan to Raw Data Automation workflow without using the command line. It guides users through each stage of the process with visual feedback and progress tracking.

## Installation

1. **Install Dependencies**
   ```bash
   # Ensure you're in the project directory
   cd "/path/to/Media Plan to Raw Data"
   
   # Install all requirements including Streamlit
   pip install -r requirements.txt
   ```

2. **Verify Installation**
   ```bash
   streamlit --version
   ```

## Running the Application

1. **Start the Streamlit App**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Access the Interface**
   - The app will automatically open in your default web browser
   - Default URL: `http://localhost:8501`
   - If it doesn't open automatically, navigate to the URL shown in the terminal

## Using the Application

### Stage 1: Data Upload
1. Upload your three required Excel files:
   - **PLANNED File**: Media plan template (e.g., `PLANNED_INPUT_TEMPLATE_*.xlsx`)
   - **DELIVERED File**: Platform data exports (e.g., `DELIVERED_INPUT_TEMPLATE_*.xlsx`)
   - **OUTPUT TEMPLATE**: Empty template to fill (e.g., `OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx`)

2. Once all files are uploaded, you'll see a success message and can proceed to the next stage

### Stage 2: Data Processing
1. Click "Start Data Processing" to extract and combine data from your uploaded files
2. Watch the progress bar and status updates
3. Review the processing metrics when complete

### Stage 3: Template Mapping
1. Optional: Configure API settings in the sidebar for enhanced LLM mapping
2. Click "Start Template Mapping" to map your data to the output template
3. Review mapping coverage and any unmapped columns

### Stage 4: Validation
1. Click "Run Validation" to check data accuracy
2. Review validation results, including any errors or warnings
3. Check the validation score and success rate

### Stage 5: Results & Download
1. Review the processing summary
2. Download your populated Excel template
3. View detailed reports for each processing stage
4. Start a new process or preview the data

## Configuration Options

Access configuration options in the sidebar:

### Client Settings
- **Client ID**: Set a specific client ID for custom mapping rules
- Leave empty to use default mappings

### API Settings
- **Anthropic API Key**: Required for enhanced LLM column mapping
- Provides intelligent mapping for unknown columns

### Debug Settings
- **Enable Debug Mode**: Turn on detailed logging for troubleshooting

## Features

### Progress Tracking
- Real-time progress bars for each operation
- Status messages showing current processing step
- Time estimates for long-running operations

### Error Handling
- User-friendly error messages
- Detailed error logs available in debug mode
- Suggestions for resolving common issues

### Session Management
- Maintains state between stages
- Prevents accidental data loss
- Allows navigation between completed stages

### File Management
- Automatic handling of temporary files
- Secure file uploads with validation
- Cleanup on session end

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure you've installed all requirements: `pip install -r requirements.txt`
   - Check that you're running from the project root directory

2. **File upload failures**
   - Verify file format is .xlsx or .xls
   - Check file size (large files may take time)
   - Ensure files aren't corrupted or password-protected

3. **Processing errors**
   - Enable debug mode in sidebar for detailed logs
   - Check that uploaded files match expected formats
   - Review error messages for specific issues

4. **Slow performance**
   - Large files may take several minutes to process
   - Check system resources (RAM, CPU)
   - Consider processing smaller batches

### Advanced Options

1. **Custom Port**
   ```bash
   streamlit run streamlit_app.py --server.port 8502
   ```

2. **Network Access**
   ```bash
   streamlit run streamlit_app.py --server.address 0.0.0.0
   ```

3. **Headless Mode** (no browser auto-open)
   ```bash
   streamlit run streamlit_app.py --server.headless true
   ```

## Best Practices

1. **File Preparation**
   - Ensure input files follow the expected format
   - Remove any password protection from Excel files
   - Close files in Excel before uploading

2. **Performance**
   - Use the latest version of Chrome or Firefox
   - Clear browser cache if experiencing issues
   - Process large files during off-peak hours

3. **Security**
   - Don't share API keys in screenshots
   - Use environment variables for sensitive data
   - Clear temporary files after processing

## Integration with CLI

The Streamlit app uses the same underlying workflow modules as the CLI:
- `production_workflow/01_data_extraction/`
- `production_workflow/03_template_mapping/`
- `production_workflow/04_validation/`
- `production_workflow/05_monitoring/`

This ensures consistency between web and command-line interfaces.

## Support

For issues or questions:
1. Check the error messages in the app
2. Enable debug mode for detailed logs
3. Review the [main documentation](documentation/INDEX.md)
4. Check GitHub issues at https://github.com/gramanoid/pca_automation

---

**Note**: The Streamlit interface is designed for ease of use while maintaining all the power and accuracy of the command-line workflow.