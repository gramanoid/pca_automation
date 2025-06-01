"""
PCA Automation - Interactive Feature Selection with Enhanced Debugging
Enable features using checkboxes in the sidebar - with verbose error logging!
"""

import streamlit as st
import pandas as pd
import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import time
import traceback
from typing import Dict, Tuple, Optional, Any

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Page configuration
st.set_page_config(
    page_title="PCA Media Plan Automation (Debug Mode)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.markdown('<h1 style="text-align: center; color: #1f77b4;">📊 PCA Automation (Debug Mode)</h1>', unsafe_allow_html=True)

# Initialize session state
if 'current_stage' not in st.session_state:
    st.session_state.current_stage = 1
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp(prefix="pca_automation_")
if 'workflow_data' not in st.session_state:
    st.session_state.workflow_data = {}
if 'file_validation' not in st.session_state:
    st.session_state.file_validation = {}
if 'feature_status' not in st.session_state:
    st.session_state.feature_status = {}
if 'debug_log' not in st.session_state:
    st.session_state.debug_log = []

def log_debug(message: str, level: str = "INFO"):
    """Add message to debug log"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    st.session_state.debug_log.append(f"[{timestamp}] [{level}] {message}")

# Feature selection in sidebar
with st.sidebar:
    st.header("🎛️ Feature Selection")
    st.info("Enable features one by one to test what works!")
    
    # Debug mode toggle
    debug_mode = st.checkbox("🐛 Debug Mode", value=True, help="Show detailed error information")
    
    st.divider()
    
    # Feature checkboxes
    features = {
        'DATA_PREVIEW': st.checkbox("📊 Data Preview", value=False, help="Show preview of uploaded files"),
        'FILE_VALIDATION': st.checkbox("✅ File Validation", value=False, help="Validate file structure and contents"),
        'PROGRESS_PERSISTENCE': st.checkbox("📈 Progress Tracking", value=False, help="Enhanced progress indicators"),
        'SMART_CACHING': st.checkbox("⚡ Smart Caching", value=False, help="Cache results for better performance"),
        'ERROR_RECOVERY': st.checkbox("🔧 Error Recovery", value=False, help="Enhanced error handling with recovery options"),
        'ENHANCED_VALIDATION': st.checkbox("📉 Enhanced Validation", value=False, help="Validation dashboard with charts"),
    }
    
    st.divider()
    
    # Show feature loading status
    if any(features.values()):
        st.subheader("Feature Status")
        for feature_name, enabled in features.items():
            if enabled:
                if st.session_state.feature_status.get(feature_name, {}).get('loaded', False):
                    st.success(f"✅ {feature_name.replace('_', ' ').title()}")
                elif st.session_state.feature_status.get(feature_name, {}).get('error'):
                    st.error(f"❌ {feature_name.replace('_', ' ').title()}")
                    if debug_mode or st.button(f"Show error", key=f"error_{feature_name}"):
                        error_info = st.session_state.feature_status[feature_name]
                        st.code(f"Error: {error_info.get('error', 'Unknown error')}", language="text")
                        if 'traceback' in error_info:
                            with st.expander("Full traceback"):
                                st.code(error_info['traceback'], language="python")
                else:
                    st.info(f"⏳ {feature_name.replace('_', ' ').title()}")

# Show debug log if enabled
if debug_mode:
    with st.expander("Debug Log", expanded=False):
        if st.session_state.debug_log:
            # Show last 50 entries
            for entry in st.session_state.debug_log[-50:]:
                st.text(entry)
        else:
            st.text("No debug entries yet")
        
        if st.button("Clear Log"):
            st.session_state.debug_log = []
            st.rerun()
        
        if st.button("Export Log"):
            log_content = "\n".join(st.session_state.debug_log)
            st.download_button(
                "Download Debug Log",
                log_content,
                f"pca_debug_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "text/plain"
            )

# Load features based on selections
loaded_features = {}
log_debug("Starting feature loading...")

# Try to load each enabled feature
if features['FILE_VALIDATION']:
    log_debug("Attempting to load FILE_VALIDATION feature...")
    try:
        from ui_components.file_upload import FileUploadComponent
        loaded_features['file_upload_component'] = FileUploadComponent()
        st.session_state.feature_status['FILE_VALIDATION'] = {'loaded': True}
        log_debug("FILE_VALIDATION loaded successfully", "SUCCESS")
    except Exception as e:
        error_msg = str(e)
        tb = traceback.format_exc()
        st.session_state.feature_status['FILE_VALIDATION'] = {
            'loaded': False, 
            'error': error_msg,
            'traceback': tb
        }
        log_debug(f"FILE_VALIDATION failed: {error_msg}", "ERROR")
        log_debug(f"Traceback: {tb}", "ERROR")

if features['PROGRESS_PERSISTENCE']:
    log_debug("Attempting to load PROGRESS_PERSISTENCE feature...")
    try:
        from ui_components.progress_display import ProgressDisplay
        STAGES = {1: "Data Upload", 2: "Data Processing", 3: "Template Mapping", 4: "Validation", 5: "Results"}
        loaded_features['progress_display'] = ProgressDisplay(STAGES)
        st.session_state.feature_status['PROGRESS_PERSISTENCE'] = {'loaded': True}
        log_debug("PROGRESS_PERSISTENCE loaded successfully", "SUCCESS")
    except Exception as e:
        error_msg = str(e)
        tb = traceback.format_exc()
        st.session_state.feature_status['PROGRESS_PERSISTENCE'] = {
            'loaded': False, 
            'error': error_msg,
            'traceback': tb
        }
        log_debug(f"PROGRESS_PERSISTENCE failed: {error_msg}", "ERROR")

if features['ENHANCED_VALIDATION']:
    log_debug("Attempting to load ENHANCED_VALIDATION feature...")
    try:
        # First try to import plotly
        log_debug("Importing plotly...")
        import plotly.graph_objects as go
        import plotly.express as px
        log_debug("Plotly imported successfully")
        
        # Then try the component
        from ui_components.validation_dashboard_enhanced import EnhancedValidationDashboard
        loaded_features['enhanced_validation_dashboard'] = EnhancedValidationDashboard()
        st.session_state.feature_status['ENHANCED_VALIDATION'] = {'loaded': True}
        log_debug("ENHANCED_VALIDATION loaded successfully", "SUCCESS")
    except Exception as e:
        error_msg = str(e)
        tb = traceback.format_exc()
        st.session_state.feature_status['ENHANCED_VALIDATION'] = {
            'loaded': False, 
            'error': error_msg,
            'traceback': tb
        }
        log_debug(f"ENHANCED_VALIDATION failed: {error_msg}", "ERROR")

if features['SMART_CACHING']:
    log_debug("Attempting to load SMART_CACHING feature...")
    try:
        from ui_components.smart_suggestions import SmartSuggestions
        loaded_features['smart_suggestions'] = SmartSuggestions()
        st.session_state.feature_status['SMART_CACHING'] = {'loaded': True}
        log_debug("SMART_CACHING loaded successfully", "SUCCESS")
    except Exception as e:
        error_msg = str(e)
        tb = traceback.format_exc()
        st.session_state.feature_status['SMART_CACHING'] = {
            'loaded': False, 
            'error': error_msg,
            'traceback': tb
        }
        log_debug(f"SMART_CACHING failed: {error_msg}", "ERROR")

if features['ERROR_RECOVERY']:
    log_debug("Attempting to load ERROR_RECOVERY feature...")
    try:
        from ui_components.error_recovery import ErrorRecoveryHandler, with_error_recovery
        loaded_features['error_recovery_handler'] = ErrorRecoveryHandler()
        loaded_features['with_error_recovery'] = with_error_recovery
        st.session_state.feature_status['ERROR_RECOVERY'] = {'loaded': True}
        log_debug("ERROR_RECOVERY loaded successfully", "SUCCESS")
    except Exception as e:
        error_msg = str(e)
        tb = traceback.format_exc()
        st.session_state.feature_status['ERROR_RECOVERY'] = {
            'loaded': False, 
            'error': error_msg,
            'traceback': tb
        }
        log_debug(f"ERROR_RECOVERY failed: {error_msg}", "ERROR")

# Continue with the rest of the app...
st.info(f"Debug mode is {'ON' if debug_mode else 'OFF'}. Loaded {len(loaded_features)} features.")

# Basic workflow implementation
st.header("Stage 1: Upload Files")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📋 Planned Data")
    planned_file = st.file_uploader("Upload PLANNED Excel file", type=['xlsx', 'xls'], key='planned')
    
    if planned_file and features['DATA_PREVIEW']:
        try:
            df = pd.read_excel(planned_file, nrows=10)
            with st.expander("Preview first 10 rows"):
                st.dataframe(df)
        except Exception as e:
            st.error(f"Preview error: {e}")

with col2:
    st.subheader("📊 Delivered Data")
    delivered_file = st.file_uploader("Upload DELIVERED Excel file", type=['xlsx', 'xls'], key='delivered')
    
    if delivered_file and features['DATA_PREVIEW']:
        try:
            df = pd.read_excel(delivered_file, nrows=10)
            with st.expander("Preview first 10 rows"):
                st.dataframe(df)
        except Exception as e:
            st.error(f"Preview error: {e}")

with col3:
    st.subheader("📝 Output Template")
    template_file = st.file_uploader("Upload OUTPUT TEMPLATE Excel file", type=['xlsx', 'xls'], key='template')
    
    if template_file and features['DATA_PREVIEW']:
        try:
            df = pd.read_excel(template_file, nrows=10)
            with st.expander("Preview first 10 rows"):
                st.dataframe(df)
        except Exception as e:
            st.error(f"Preview error: {e}")

# Show system information in debug mode
if debug_mode:
    with st.expander("System Information"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Python Version:**", sys.version)
            st.write("**Streamlit Version:**", st.__version__)
            st.write("**Working Directory:**", os.getcwd())
        with col2:
            st.write("**Platform:**", sys.platform)
            st.write("**Python Path (first 3):**")
            for p in sys.path[:3]:
                st.code(p, language="text")

st.info("This is a debug version to help identify issues. Use the debug log and error details to troubleshoot.")