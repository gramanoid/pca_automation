# Feature Flags Guide - Gradual Enhancement

## Overview

The `streamlit_app_gradual.py` allows you to enable features one by one through environment variables. This helps isolate which features cause issues on Streamlit Cloud.

## Available Features

### 1. FILE_VALIDATION
**Env Variable**: `ENABLE_FILE_VALIDATION=true`
- Validates Excel file structure
- Checks for required sheets
- Shows validation messages
- **Dependencies**: `ui_components.file_upload`

### 2. DATA_PREVIEW  
**Env Variable**: `ENABLE_DATA_PREVIEW=true`
- Shows preview of uploaded files
- Displays first 10-20 rows
- **Dependencies**: None (uses pandas)

### 3. PROGRESS_PERSISTENCE
**Env Variable**: `ENABLE_PROGRESS_PERSISTENCE=true`
- Enhanced progress tracking
- Visual stage indicators
- **Dependencies**: `ui_components.progress_display`

### 4. SMART_CACHING
**Env Variable**: `ENABLE_SMART_CACHING=true`
- Caches processing results
- Improves performance
- **Dependencies**: None (uses Streamlit cache)

### 5. ENHANCED_VALIDATION
**Env Variable**: `ENABLE_ENHANCED_VALIDATION=true`
- Validation dashboard with drill-down
- Charts and analytics
- **Dependencies**: `ui_components.validation_dashboard_enhanced`, `plotly`

### 6. ERROR_RECOVERY
**Env Variable**: `ENABLE_ERROR_RECOVERY=true`
- Intelligent error handling
- Recovery suggestions
- **Dependencies**: `ui_components.error_recovery`

### 7. MARKER_VALIDATION
**Env Variable**: `ENABLE_MARKER_VALIDATION=true`
- START/END marker validation
- Visual preview
- **Dependencies**: `ui_components.marker_validation`, `plotly`

### 8. CONFIG_PERSISTENCE
**Env Variable**: `ENABLE_CONFIG_PERSISTENCE=true`
- Save/load configurations
- Export/import settings
- **Dependencies**: `ui_components.config_persistence`

## Testing Order (Recommended)

Test features in this order, from simplest to most complex:

### Phase 1 - Basic Enhancements
1. **DATA_PREVIEW** - Just shows data, minimal risk
2. **SMART_CACHING** - Performance improvement
3. **FILE_VALIDATION** - Basic validation logic

### Phase 2 - UI Enhancements  
4. **PROGRESS_PERSISTENCE** - Visual improvements
5. **ERROR_RECOVERY** - Better error handling

### Phase 3 - Complex Features
6. **ENHANCED_VALIDATION** - Uses plotly charts
7. **MARKER_VALIDATION** - Complex UI component
8. **CONFIG_PERSISTENCE** - State management

## How to Enable Features

### On Streamlit Cloud

1. Go to your app settings
2. Navigate to "Advanced settings" 
3. Add environment variables:

```
ENABLE_DATA_PREVIEW = true
```

4. Save and reboot the app

### Locally

```bash
# Enable single feature
ENABLE_DATA_PREVIEW=true streamlit run streamlit_app_gradual.py

# Enable multiple features
ENABLE_DATA_PREVIEW=true ENABLE_FILE_VALIDATION=true streamlit run streamlit_app_gradual.py

# Or create .env file
echo "ENABLE_DATA_PREVIEW=true" > .env
echo "ENABLE_FILE_VALIDATION=true" >> .env
streamlit run streamlit_app_gradual.py
```

## Troubleshooting

### If a feature fails to load:
1. The app will show an error in the sidebar
2. The feature will be automatically disabled
3. The app will continue with basic functionality

### Common issues:
- **Import errors**: Missing dependencies or circular imports
- **plotly errors**: Heavy visualization library
- **Memory errors**: Too many features at once

## Current Status

Since the simple version is working, start by enabling:
1. `ENABLE_DATA_PREVIEW=true` (safest)
2. Then try `ENABLE_FILE_VALIDATION=true`
3. Continue based on what works

## Monitoring

The sidebar shows:
- ✅ Successfully loaded features
- ⭕ Disabled features  
- ✗ Failed features with error messages