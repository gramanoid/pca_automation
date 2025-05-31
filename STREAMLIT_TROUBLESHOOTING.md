# Streamlit App Troubleshooting Guide

## Current Issue: Dynamic Import Errors

### Problem
The app is showing "TypeError: Failed to fetch dynamically imported module" errors on Streamlit Cloud.

### Temporary Solution
We've created multiple versions of the app to isolate and fix the issue:

1. **streamlit_app.py** - Main entry point (redirects to simple version by default)
2. **streamlit_app_simple.py** - Simplified version with core functionality only
3. **streamlit_app_full.py** - Full version with all Phase 1 enhancements
4. **streamlit_app_debug.py** - Debug version to test individual components

## How to Use Different Versions

### On Streamlit Cloud
The app will automatically use the simple version. To switch versions:

1. Set environment variable in Streamlit Cloud:
   - Go to App Settings > Advanced settings
   - Add: `USE_SIMPLE_APP = false` to use full version
   - Add: `USE_SIMPLE_APP = true` (or omit) to use simple version

### Locally
```bash
# Use simple version (default)
streamlit run streamlit_app.py

# Use full version
USE_SIMPLE_APP=false streamlit run streamlit_app.py

# Use debug version
streamlit run streamlit_app_debug.py
```

## Common Issues and Solutions

### 1. Import Errors
- **Issue**: Components fail to import
- **Solution**: Check streamlit_app_debug.py to see which specific imports are failing
- **Fix**: We've added lazy loading for heavy imports in the simple version

### 2. File Upload Errors
- **Issue**: File upload boxes show errors
- **Solution**: The simple version uses basic file upload without advanced validation

### 3. Python Version Compatibility
- **Issue**: App fails on Python 3.13
- **Solution**: Ensure compatibility with Python 3.8-3.12

### 4. Missing Dependencies
- **Issue**: Package not found errors
- **Solution**: Check requirements.txt and ensure all packages are available on PyPI

## Features in Each Version

### Simple Version (streamlit_app_simple.py)
- ✅ File upload
- ✅ Data processing
- ✅ Template mapping
- ✅ Basic validation
- ✅ Download results
- ❌ Advanced UI components
- ❌ Marker validation
- ❌ Enhanced dashboards

### Full Version (streamlit_app_full.py)
- ✅ All simple version features
- ✅ Advanced file validation
- ✅ Marker validation with preview
- ✅ Configuration persistence
- ✅ Enhanced dashboards
- ✅ Smart suggestions
- ✅ Performance monitoring

## Debugging Steps

1. **Check Import Errors**:
   ```
   streamlit run streamlit_app_debug.py
   ```
   This will show which components are failing to import.

2. **Check Python Environment**:
   - Streamlit Cloud uses specific Python versions
   - Ensure compatibility with requirements.txt

3. **Check for Missing Files**:
   - Ensure all __init__.py files exist
   - Check that all imported modules are in the repository

4. **Simplify Imports**:
   - Use lazy loading for heavy components
   - Avoid circular imports
   - Use absolute imports instead of relative

## Gradual Migration Plan

Once the simple version works:

1. **Phase 1**: Add back basic UI enhancements
   - File validation
   - Progress indicators
   - Basic styling

2. **Phase 2**: Add data visualization
   - Preview components
   - Basic charts
   - Validation summaries

3. **Phase 3**: Add advanced features
   - Marker validation
   - Configuration persistence
   - Enhanced dashboards

## Contact

If issues persist, check:
- Streamlit Cloud logs
- GitHub Issues: https://github.com/gramanoid/pca_automation/issues