"""
PCA Automation - Professional Clean Design
Streamlined interface with all features enabled
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
from typing import Dict, Tuple, Optional, Any

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import enhanced progress tracking
from ui_components.enhanced_progress_tracker import get_progress_tracker, get_mapping_tracker
from ui_components.copy_button import copy_to_clipboard_button, error_display_with_copy

# Page configuration
st.set_page_config(
    page_title="PCA Automation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean professional design
st.markdown("""
<style>
    /* Import SF Pro font for Apple aesthetic */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Root variables - Light mode */
    :root {
        --primary-blue: #0066CC;
        --hover-blue: #0051A2;
        --success-green: #28A745;
        --error-red: #DC3545;
        --warning-yellow: #FFC107;
        --background: #F8F9FA;
        --card-bg: #FFFFFF;
        --text-primary: #212529;
        --text-secondary: #6C757D;
        --border-color: #DEE2E6;
        --shadow: 0 2px 4px rgba(0,0,0,0.08);
        --shadow-hover: 0 4px 8px rgba(0,0,0,0.12);
    }
    
    /* Dark mode variables */
    @media (prefers-color-scheme: dark) {
        :root {
            --primary-blue: #4A9EFF;
            --hover-blue: #3A8EEF;
            --success-green: #4CAF50;
            --error-red: #F44336;
            --warning-yellow: #FFB800;
            --background: #0E1117;
            --card-bg: #262730;
            --text-primary: #FAFAFA;
            --text-secondary: #A2A2A8;
            --border-color: #3E4049;
            --shadow: 0 2px 4px rgba(0,0,0,0.3);
            --shadow-hover: 0 4px 8px rgba(0,0,0,0.5);
        }
    }
    
    /* Streamlit's dark mode class */
    [data-testid="stAppViewContainer"][data-theme="dark"] {
        --primary-blue: #4A9EFF;
        --hover-blue: #3A8EEF;
        --success-green: #4CAF50;
        --error-red: #F44336;
        --warning-yellow: #FFB800;
        --background: #0E1117;
        --card-bg: #262730;
        --text-primary: #FAFAFA;
        --text-secondary: #A2A2A8;
        --border-color: #3E4049;
        --shadow: 0 2px 4px rgba(0,0,0,0.3);
        --shadow-hover: 0 4px 8px rgba(0,0,0,0.5);
    }
    
    /* Global styles */
    .stApp {
        background-color: var(--background);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: var(--card-bg) !important;
        border-right: 1px solid var(--border-color);
    }
    
    /* Dark mode sidebar */
    [data-theme="dark"] section[data-testid="stSidebar"] {
        background-color: #1A1C23 !important;
    }
    
    /* Sidebar content */
    section[data-testid="stSidebar"] .block-container {
        background-color: transparent !important;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: var(--primary-blue);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        box-shadow: var(--shadow);
    }
    
    .stButton > button:hover {
        background-color: var(--hover-blue);
        box-shadow: var(--shadow-hover);
        transform: translateY(-1px);
    }
    
    /* File uploader styling */
    .uploadedFile {
        background-color: rgba(0, 102, 204, 0.1);
        border: 1px solid var(--primary-blue);
        color: var(--primary-blue);
    }
    
    /* Dark mode file uploader */
    [data-theme="dark"] .uploadedFile {
        background-color: rgba(74, 158, 255, 0.1);
        border: 1px solid var(--primary-blue);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: var(--primary-blue);
        border-radius: 3px;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background-color: var(--card-bg);
        padding: 1rem;
        border-radius: 8px;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        font-weight: 500;
        color: var(--text-primary);
    }
    
    /* Success/Error/Warning messages */
    .stAlert > div {
        border-radius: 6px;
        font-size: 0.875rem;
    }
    
    /* File uploader */
    [data-testid="stFileUploadDropzone"] {
        background-color: var(--card-bg);
        border: 2px dashed var(--border-color);
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: var(--primary-blue);
        background-color: rgba(0, 102, 204, 0.05);
    }
    
    /* Dark mode file uploader hover */
    [data-theme="dark"] [data-testid="stFileUploadDropzone"]:hover {
        background-color: rgba(74, 158, 255, 0.05);
    }
    
    /* Custom containers */
    .upload-section {
        background-color: var(--card-bg);
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        height: 100%;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-weight: 600;
    }
    
    /* Progress dots */
    .progress-dots {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
        gap: 0.5rem;
    }
    
    .progress-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: var(--border-color);
        transition: all 0.3s ease;
    }
    
    .progress-dot.active {
        width: 28px;
        border-radius: 14px;
        background-color: var(--primary-blue);
    }
    
    .progress-dot.completed {
        background-color: var(--success-green);
    }
</style>
""", unsafe_allow_html=True)

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

# All features enabled by default
features = {
    'DATA_PREVIEW': True,
    'FILE_VALIDATION': True,
    'PROGRESS_PERSISTENCE': True,
    'SMART_CACHING': True,
    'ERROR_RECOVERY': True,
    'ENHANCED_VALIDATION': True,
}

# Load features silently
loaded_features = {}

# Try to load features without showing errors
for feature in features:
    try:
        if feature == 'FILE_VALIDATION':
            from ui_components.file_upload import FileUploadComponent
            loaded_features['file_upload_component'] = FileUploadComponent()
        elif feature == 'PROGRESS_PERSISTENCE':
            from ui_components.progress_display import ProgressDisplay
            STAGES = {1: "Upload", 2: "Process", 3: "Map", 4: "Validate", 5: "Complete"}
            loaded_features['progress_display'] = ProgressDisplay(STAGES)
        elif feature == 'ENHANCED_VALIDATION':
            from ui_components.validation_dashboard_enhanced import EnhancedValidationDashboard
            loaded_features['enhanced_validation_dashboard'] = EnhancedValidationDashboard()
        elif feature == 'ERROR_RECOVERY':
            from ui_components.error_recovery import ErrorRecoveryHandler
            loaded_features['error_handler'] = ErrorRecoveryHandler()
        st.session_state.feature_status[feature] = {'loaded': True}
    except:
        st.session_state.feature_status[feature] = {'loaded': False}

# Helper functions
def save_uploaded_file(uploaded_file, file_type: str) -> Optional[Path]:
    """Save uploaded file to temp directory"""
    if uploaded_file is not None:
        file_path = Path(st.session_state.temp_dir) / f"{file_type}_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.uploaded_files[file_type] = str(file_path)
        return file_path
    return None

def validate_uploaded_file(file, file_type: str) -> Tuple[bool, str]:
    """Basic file validation"""
    try:
        df = pd.read_excel(file, sheet_name=0, nrows=5)
        
        if file_type == "PLANNED":
            xl_file = pd.ExcelFile(file)
            required_sheets = ['DV360', 'META', 'TIKTOK']
            missing = [s for s in required_sheets if s not in xl_file.sheet_names]
            if missing:
                return False, f"Missing required sheets: {', '.join(missing)}"
        
        return True, "File is valid"
    except Exception as e:
        return False, f"Invalid file format"

# Sidebar
with st.sidebar:
    st.markdown("## Navigation")
    
    stages = ["📤 Upload", "⚙️ Process", "🗺️ Map", "✓ Validate", "📥 Download"]
    for i, stage in enumerate(stages, 1):
        if i < st.session_state.current_stage:
            st.success(f"~~{stage}~~", icon="✅")
        elif i == st.session_state.current_stage:
            st.info(f"**{stage}**", icon="▶")
        else:
            st.markdown(f"🔘 {stage}")
    
    st.divider()
    
    # Settings
    st.markdown("## Settings")
    st.checkbox("Enable AI Mapping", value=True, key="enable_llm_mapping")
    
    # Progress
    progress = (st.session_state.current_stage - 1) / 5
    st.progress(progress)
    st.caption(f"Step {st.session_state.current_stage} of 5")

# Main header
st.markdown("""
# PCA Automation
#### Transform your media plans into actionable insights
""")

# Global error notification
if 'error_logs' in st.session_state and st.session_state.error_logs:
    error_count = len(st.session_state.error_logs)
    latest_error = st.session_state.error_logs[-1]
    
    error_container = st.container()
    with error_container:
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.error(f"⚠️ **{error_count} Error{'s' if error_count > 1 else ''} Detected**")
        
        with col2:
            st.caption(f"Latest: {latest_error['stage']} - {latest_error['timestamp'].strftime('%H:%M:%S')}")
        
        with col3:
            if st.button("View Errors", key="view_errors_top"):
                st.session_state.show_error_details = True
        
        if st.session_state.get('show_error_details', False):
            # Show error details with copy functionality
            st.divider()
            
            # Format all errors for copying
            all_errors_text = "=== PCA AUTOMATION ERROR LOG ===\n\n"
            all_errors_text += f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            all_errors_text += f"Total errors: {error_count}\n\n"
            
            for i, error in enumerate(st.session_state.error_logs, 1):
                all_errors_text += f"--- Error {i} ---\n"
                all_errors_text += f"Stage: {error['stage']}\n"
                all_errors_text += f"Time: {error['timestamp'].strftime('%H:%M:%S')}\n"
                all_errors_text += f"Error: {error['error']}\n"
                if error.get('details'):
                    all_errors_text += f"\nStack Trace:\n{error['details']}\n"
                all_errors_text += "\n"
            
            # Display in markdown code block
            st.markdown("**Error Log:**")
            st.markdown(f"```\n{all_errors_text}\n```")
            
            # Copy button using the new component
            copy_to_clipboard_button(all_errors_text, "📋 Copy All Errors", key="global_errors_copy")
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Errors", key="clear_errors"):
                    st.session_state.error_logs = []
                    st.session_state.show_error_details = False
                    st.rerun()
            
            with col2:
                if st.button("Hide Details", key="hide_errors_top"):
                    st.session_state.show_error_details = False
                    st.rerun()
            
            st.divider()

# Progress dots
progress_html = '<div class="progress-dots">'
for i in range(1, 6):
    if i < st.session_state.current_stage:
        progress_html += '<div class="progress-dot completed"></div>'
    elif i == st.session_state.current_stage:
        progress_html += '<div class="progress-dot active"></div>'
    else:
        progress_html += '<div class="progress-dot"></div>'
progress_html += '</div>'
st.markdown(progress_html, unsafe_allow_html=True)

# Main content
if st.session_state.current_stage == 1:
    st.markdown("## 📁 Upload Your Files")
    st.markdown("Please upload the three required files below. Each file serves a specific purpose in the automation process.")
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        st.markdown("### 📋 Media Plan")
        st.caption("PLANNED file with START/END markers")
        
        planned_file = st.file_uploader(
            "Choose XLSX file",
            type=['xlsx', 'xls'],
            key="planned_uploader",
            help="Upload your media plan template"
        )
        
        if planned_file:
            is_valid, message = validate_uploaded_file(planned_file, 'PLANNED')
            if is_valid:
                st.success("File uploaded successfully")
                save_uploaded_file(planned_file, 'PLANNED')
                st.session_state.file_validation['PLANNED'] = True
                
                if features['DATA_PREVIEW']:
                    with st.expander("Preview"):
                        planned_file.seek(0)
                        df = pd.read_excel(planned_file, sheet_name=0, nrows=5)
                        st.dataframe(df, use_container_width=True)
            else:
                st.error(message)
                st.session_state.file_validation['PLANNED'] = False
    
    with col2:
        st.markdown("### 📊 Platform Data")
        st.caption("DELIVERED data from platforms")
        
        delivered_file = st.file_uploader(
            "Choose XLSX file",
            type=['xlsx', 'xls'],
            key="delivered_uploader",
            help="Upload your delivered data"
        )
        
        if delivered_file:
            is_valid, message = validate_uploaded_file(delivered_file, 'DELIVERED')
            if is_valid:
                st.success("File uploaded successfully")
                save_uploaded_file(delivered_file, 'DELIVERED')
                st.session_state.file_validation['DELIVERED'] = True
                
                if features['DATA_PREVIEW']:
                    with st.expander("Preview"):
                        delivered_file.seek(0)
                        df = pd.read_excel(delivered_file, sheet_name=0, nrows=5)
                        st.dataframe(df, use_container_width=True)
            else:
                st.error(message)
                st.session_state.file_validation['DELIVERED'] = False
    
    with col3:
        st.markdown("### 📄 Output Template")
        st.caption("Empty tracker template")
        
        template_file = st.file_uploader(
            "Choose XLSX file",
            type=['xlsx', 'xls'],
            key="template_uploader",
            help="Upload your output template"
        )
        
        if template_file:
            is_valid, message = validate_uploaded_file(template_file, 'TEMPLATE')
            if is_valid:
                st.success("File uploaded successfully")
                save_uploaded_file(template_file, 'TEMPLATE')
                st.session_state.file_validation['TEMPLATE'] = True
                
                if features['DATA_PREVIEW']:
                    with st.expander("Preview"):
                        template_file.seek(0)
                        df = pd.read_excel(template_file, sheet_name=0, nrows=5)
                        st.dataframe(df, use_container_width=True)
            else:
                st.error(message)
                st.session_state.file_validation['TEMPLATE'] = False
    
    # Continue button
    st.markdown("---")
    all_uploaded = len(st.session_state.uploaded_files) == 3
    all_valid = all(st.session_state.file_validation.get(ft, False) for ft in ['PLANNED', 'DELIVERED', 'TEMPLATE'])
    
    if all_uploaded and all_valid:
        if st.button("Continue to Processing →", type="primary", use_container_width=False):
            st.session_state.current_stage = 2
            st.rerun()
    else:
        missing = []
        if 'PLANNED' not in st.session_state.uploaded_files:
            missing.append("Media Plan")
        if 'DELIVERED' not in st.session_state.uploaded_files:
            missing.append("Platform Data")
        if 'TEMPLATE' not in st.session_state.uploaded_files:
            missing.append("Output Template")
        
        if missing:
            st.info(f"Please upload: {', '.join(missing)}")

elif st.session_state.current_stage == 2:
    st.markdown("## ⚙️ Data Processing")
    st.markdown("Extract and combine data from your uploaded files.")
    
    # Get trackers
    progress_tracker = get_progress_tracker()
    
    # Show any previous errors
    if progress_tracker.get_stage_status('processing') == 'error':
        st.error("⚠️ Previous processing attempt failed. Check the error log below.")
        progress_tracker.render_global_error_log()
        if st.button("🔄 Retry Processing", type="secondary"):
            progress_tracker.clear_stage_progress('processing')
            st.rerun()
    
    if features['SMART_CACHING']:
        @st.cache_data(ttl=3600, show_spinner=False)
        def cached_process_data(planned_path, delivered_path, output_dir):
            from production_workflow.utils.workflow_wrapper import WorkflowWrapper
            wrapper = WorkflowWrapper()
            return wrapper.extract_and_combine_data(
                planned_path=planned_path,
                delivered_path=delivered_path,
                output_dir=output_dir,
                combine=True
            )
    
    def process_data():
        """Process data with enhanced progress tracking"""
        try:
            from production_workflow.utils.workflow_wrapper import WorkflowWrapper
            wrapper = WorkflowWrapper()
            
            # Initialize progress tracking
            progress_tracker.start_stage_tracking('processing', 6)
            progress_placeholder = st.empty()
            
            planned_path = st.session_state.uploaded_files.get("PLANNED")
            delivered_path = st.session_state.uploaded_files.get("DELIVERED")
            output_dir = Path(st.session_state.temp_dir) / "output"
            output_dir.mkdir(exist_ok=True)
            
            # Progress steps
            processing_steps = [
                (0, "Initializing data extraction", "Preparing workspace"),
                (1, "Reading Media Plan (PLANNED)", f"Loading {Path(planned_path).name}"),
                (2, "Reading Platform Data (DELIVERED)", f"Loading {Path(delivered_path).name}"),
                (3, "Extracting platform sections", "Processing DV360, META, and TIKTOK data"),
                (4, "Combining data sources", "Merging PLANNED and DELIVERED data"),
                (5, "Saving combined output", "Writing COMBINED Excel file")
            ]
            
            # Update progress display
            with progress_placeholder.container():
                progress_tracker.update_progress('processing', 0, processing_steps[0][1], processing_steps[0][2])
                progress_tracker.render_detailed_progress('processing')
            
            # Simulate progress updates during processing
            def update_progress_during_processing():
                for i, (step, task, detail) in enumerate(processing_steps[1:4], 1):
                    time.sleep(0.5)
                    with progress_placeholder.container():
                        progress_tracker.update_progress('processing', i, task, detail)
                        progress_tracker.render_detailed_progress('processing')
            
            # Start progress updates in background
            import threading
            progress_thread = threading.Thread(target=update_progress_during_processing)
            progress_thread.start()
            
            # Actual processing
            start_time = time.time()
            if features['SMART_CACHING'] and 'cached_process_data' in globals():
                output_files = cached_process_data(planned_path, delivered_path, str(output_dir))
            else:
                output_files = wrapper.extract_and_combine_data(
                    planned_path=planned_path,
                    delivered_path=delivered_path,
                    output_dir=str(output_dir),
                    combine=True
                )
            
            # Wait for progress thread
            progress_thread.join()
            
            # Final progress updates
            with progress_placeholder.container():
                progress_tracker.update_progress('processing', 4, processing_steps[4][1], processing_steps[4][2])
                progress_tracker.render_detailed_progress('processing')
            
            time.sleep(0.5)
            
            with progress_placeholder.container():
                progress_tracker.update_progress('processing', 5, processing_steps[5][1], processing_steps[5][2])
                progress_tracker.render_detailed_progress('processing')
            
            duration = time.time() - start_time
            
            st.session_state.workflow_data['combined_file'] = output_files.get('combined')
            st.session_state.workflow_data['output_dir'] = str(output_dir)
            
            # Complete tracking with summary
            if output_files.get('combined') and os.path.exists(output_files['combined']):
                df = pd.read_excel(output_files['combined'])
                progress_tracker.complete_stage('processing', {
                    'Total Rows': f"{len(df):,}",
                    'Total Columns': len(df.columns),
                    'Platforms': len(df['Platform'].unique()) if 'Platform' in df else 'N/A',
                    'Duration': f"{duration:.1f}s"
                })
            
            return output_files
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            progress_tracker.add_error('processing', f"Processing failed: {str(e)}", error_details)
            
            with progress_placeholder.container():
                progress_tracker.render_detailed_progress('processing')
            
            st.error(f"❌ Processing error: {str(e)}")
            
            with st.expander("🔍 Error Details", expanded=True):
                st.code(error_details)
            
            return None
    
    # Show previous results if available
    if progress_tracker.get_stage_status('processing') == 'completed':
        st.success("✅ Processing already completed in this session")
        progress_tracker.render_stage_summary('processing')
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Re-process Data", type="secondary"):
                progress_tracker.clear_stage_progress('processing')
                st.rerun()
        with col2:
            if st.button("➡️ Continue to Mapping", type="primary"):
                st.session_state.current_stage = 3
                st.rerun()
    else:
        # Start processing button
        if st.button("🚀 Start Processing", type="primary", disabled=progress_tracker.get_stage_status('processing') == 'running'):
            result = process_data()
            
            if result:
                st.success("✅ Data processed successfully!")
                
                # Show summary
                progress_tracker.render_stage_summary('processing')
                
                # Auto-advance after brief pause
                time.sleep(2)
                st.session_state.current_stage = 3
                st.rerun()
        
        # Show info about the process
        with st.expander("ℹ️ What happens during processing?", expanded=False):
            st.markdown("""
            **The processing stage includes:**
            1. **Media Plan Loading** - Extract data from PLANNED file with START/END markers
            2. **Platform Data Loading** - Extract DELIVERED data from platforms
            3. **Section Extraction** - Identify DV360, META, and TIKTOK sections
            4. **Data Combination** - Merge PLANNED and DELIVERED data intelligently
            5. **Output Generation** - Create COMBINED Excel file for mapping
            
            **Expected Duration:** 10-30 seconds depending on file size
            """)

elif st.session_state.current_stage == 3:
    st.markdown("## 🗺️ Template Mapping")
    st.markdown("Map your combined data to the output template using AI.")
    
    # Get trackers
    progress_tracker = get_progress_tracker()
    mapping_tracker = get_mapping_tracker()
    
    # Show any previous errors
    if mapping_tracker.get_stage_status('mapping') == 'error':
        st.error("⚠️ Previous mapping attempt failed. Check the error log below.")
        mapping_tracker.render_global_error_log()
        if st.button("🔄 Retry Mapping", type="secondary"):
            mapping_tracker.clear_stage_progress('mapping')
            st.rerun()
    
    def map_to_template():
        """Map data to template with detailed progress tracking"""
        try:
            from production_workflow.utils.workflow_wrapper import WorkflowWrapper
            wrapper = WorkflowWrapper()
            
            # Initialize progress tracking
            mapping_tracker.start_mapping()
            progress_placeholder = st.empty()
            
            # Get files
            combined_file = st.session_state.workflow_data.get('combined_file')
            template_path = st.session_state.uploaded_files.get("TEMPLATE")
            output_dir = st.session_state.workflow_data.get('output_dir')
            output_file = Path(output_dir) / f"final_mapped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Check files exist
            if not combined_file or not os.path.exists(combined_file):
                raise FileNotFoundError(f"Combined file not found: {combined_file}")
            if not template_path or not os.path.exists(template_path):
                raise FileNotFoundError(f"Template file not found: {template_path}")
            
            # Update progress
            with progress_placeholder.container():
                mapping_tracker.update_mapping_step(0, f"Files verified: {Path(combined_file).name}")
                mapping_tracker.render_mapping_progress()
            
            # Simulate progress updates during mapping
            # In real implementation, WorkflowWrapper should provide progress callbacks
            def simulate_progress():
                steps = [
                    (1, "Loading Excel files and checking structure"),
                    (2, "Validating DV360, META, and TIKTOK data sections"),
                    (3, "Analyzing 50+ columns for intelligent mapping"),
                    (4, "Applying AI-powered column matching with Gemini 2.5 Pro"),
                    (5, "Writing mapped data to template (this may take 30-60 seconds)"),
                    (6, "Generating mapping report and validation metrics"),
                    (7, "Finalizing output and saving Excel file")
                ]
                
                for step, desc in steps[:-2]:  # Don't show last 2 steps during actual mapping
                    time.sleep(0.5)  # Brief pause for UI update
                    with progress_placeholder.container():
                        mapping_tracker.update_mapping_step(step, desc)
                        mapping_tracker.render_mapping_progress()
            
            # Start simulated progress in background
            import threading
            progress_thread = threading.Thread(target=simulate_progress)
            progress_thread.start()
            
            # Actual mapping
            start_time = time.time()
            result = wrapper.map_to_template(
                input_file=combined_file,
                template_file=template_path,
                output_file=str(output_file)
            )
            duration = time.time() - start_time
            
            # Wait for progress thread to finish
            progress_thread.join()
            
            # Final progress updates
            with progress_placeholder.container():
                mapping_tracker.update_mapping_step(6, "Processing complete, preparing results")
                mapping_tracker.render_mapping_progress()
            
            time.sleep(0.5)
            
            # Store results
            st.session_state.workflow_data['mapped_file'] = str(output_file)
            st.session_state.workflow_data['mapping_result'] = result
            
            # Complete tracking with summary
            mapping_tracker.complete_stage('mapping', {
                'Mapped Columns': f"{result.get('mapped_count', 0)}/{result.get('total_columns', 0)}",
                'Success Rate': f"{(result.get('mapped_count', 0) / max(result.get('total_columns', 1), 1) * 100):.0f}%",
                'Duration': f"{duration:.1f}s",
                'Output Size': f"{os.path.getsize(output_file) / 1024 / 1024:.1f} MB" if os.path.exists(output_file) else "N/A"
            })
            
            with progress_placeholder.container():
                mapping_tracker.update_mapping_step(7, "✅ Mapping completed successfully!")
                mapping_tracker.render_mapping_progress()
            
            return result, output_file
            
        except FileNotFoundError as e:
            mapping_tracker.add_error('mapping', "File not found", str(e))
            with progress_placeholder.container():
                mapping_tracker.render_mapping_progress()
            st.error(f"❌ {str(e)}")
            return None
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            mapping_tracker.add_error('mapping', f"Mapping failed: {str(e)}", error_details)
            
            with progress_placeholder.container():
                mapping_tracker.render_mapping_progress()
            
            # Create error report
            error_report_text = f"""=== MAPPING ERROR REPORT ===
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Stage: Template Mapping
Error: {str(e)}

Stack Trace:
{error_details}

Environment:
- Combined File: {combined_file}
- Template File: {template_path}
- Output File: {output_file}
- AI Mapping Enabled: {st.session_state.get('enable_llm_mapping', True)}
"""
            
            # Use the error display component
            error_display_with_copy("Mapping Failed", error_report_text, key="mapping_error")
            
            # Show quick fixes if applicable
            if "API" in str(e) or "api" in str(e):
                st.info("💡 **Possible Fix:** Check your API key configuration in the sidebar")
            elif "file" in str(e).lower() or "path" in str(e).lower():
                st.info("💡 **Possible Fix:** Ensure all files are properly uploaded and accessible")
            elif "timeout" in str(e).lower():
                st.info("💡 **Possible Fix:** The AI processing timed out. Try again or contact support")
            
            return None
    
    # Show previous results if available
    if mapping_tracker.get_stage_status('mapping') == 'completed':
        st.success("✅ Mapping already completed in this session")
        mapping_tracker.render_stage_summary('mapping')
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Re-run Mapping", type="secondary"):
                mapping_tracker.clear_stage_progress('mapping')
                st.rerun()
        with col2:
            if st.button("➡️ Continue to Validation", type="primary"):
                st.session_state.current_stage = 4
                st.rerun()
    else:
        # Start mapping button
        if st.button("🚀 Start Mapping", type="primary", disabled=mapping_tracker.get_stage_status('mapping') == 'running'):
            result = map_to_template()
            
            if result:
                mapping_result, output_file = result
                st.success("✅ Template mapping completed!")
                
                # Show summary
                mapping_tracker.render_stage_summary('mapping')
                
                # Auto-advance after brief pause
                time.sleep(2)
                st.session_state.current_stage = 4
                st.rerun()
        
        # Show info about the process
        with st.expander("ℹ️ What happens during mapping?", expanded=False):
            st.markdown("""
            **The mapping process includes:**
            1. **Data Loading** - Read the combined Excel file with all platform data
            2. **Structure Validation** - Verify DV360, META, and TIKTOK sections exist
            3. **Column Analysis** - Identify 50+ columns that need mapping
            4. **AI Mapping** - Use Gemini 2.5 Pro to intelligently match columns
            5. **Template Writing** - Populate the output template with mapped data
            6. **Report Generation** - Create detailed mapping metrics
            7. **Quality Check** - Verify all required fields are populated
            
            **Expected Duration:** 30-90 seconds depending on data size
            """)
    
    # Always show error log if errors exist
    if st.session_state.error_logs:
        mapping_tracker.render_global_error_log()

elif st.session_state.current_stage == 4:
    st.markdown("## ✓ Data Validation")
    st.markdown("Validate the accuracy and completeness of your mapped data.")
    
    # Get trackers
    progress_tracker = get_progress_tracker()
    
    # Show any previous errors
    if progress_tracker.get_stage_status('validation') == 'error':
        st.error("⚠️ Previous validation attempt failed. Check the error log below.")
        progress_tracker.render_global_error_log()
        if st.button("🔄 Retry Validation", type="secondary"):
            progress_tracker.clear_stage_progress('validation')
            st.rerun()
    
    def validate_data():
        """Validate data with enhanced progress tracking"""
        try:
            from production_workflow.utils.workflow_wrapper import WorkflowWrapper
            wrapper = WorkflowWrapper()
            
            # Initialize progress tracking
            progress_tracker.start_stage_tracking('validation', 5)
            progress_placeholder = st.empty()
            
            mapped_file = st.session_state.workflow_data.get('mapped_file')
            combined_file = st.session_state.workflow_data.get('combined_file')
            
            # Validation steps
            validation_steps = [
                (0, "Loading mapped data", f"Reading {Path(mapped_file).name}"),
                (1, "Loading source data", f"Reading {Path(combined_file).name}"),
                (2, "Checking data completeness", "Verifying all required fields are populated"),
                (3, "Validating data accuracy", "Comparing mapped values against source"),
                (4, "Generating validation report", "Creating detailed validation metrics")
            ]
            
            # Update progress display
            with progress_placeholder.container():
                progress_tracker.update_progress('validation', 0, validation_steps[0][1], validation_steps[0][2])
                progress_tracker.render_detailed_progress('validation')
            
            # Simulate progress updates during validation
            def update_progress_during_validation():
                for i, (step, task, detail) in enumerate(validation_steps[1:4], 1):
                    time.sleep(0.5)
                    with progress_placeholder.container():
                        progress_tracker.update_progress('validation', i, task, detail)
                        progress_tracker.render_detailed_progress('validation')
            
            # Start progress updates in background
            import threading
            progress_thread = threading.Thread(target=update_progress_during_validation)
            progress_thread.start()
            
            # Actual validation
            start_time = time.time()
            validation_results = wrapper.validate_data(
                mapped_file=mapped_file,
                source_file=combined_file
            )
            duration = time.time() - start_time
            
            # Wait for progress thread
            progress_thread.join()
            
            # Final progress update
            with progress_placeholder.container():
                progress_tracker.update_progress('validation', 4, validation_steps[4][1], validation_steps[4][2])
                progress_tracker.render_detailed_progress('validation')
            
            st.session_state.workflow_data['validation_results'] = validation_results
            
            # Complete tracking with summary
            errors = validation_results.get('errors', [])
            warnings = validation_results.get('warnings', [])
            accuracy = validation_results.get('passed_checks', 0) / max(validation_results.get('total_checks', 1), 1) * 100
            
            progress_tracker.complete_stage('validation', {
                'Total Checks': validation_results.get('total_checks', 0),
                'Passed': validation_results.get('passed_checks', 0),
                'Errors': len(errors),
                'Warnings': len(warnings),
                'Accuracy': f"{accuracy:.0f}%",
                'Duration': f"{duration:.1f}s"
            })
            
            return validation_results
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            progress_tracker.add_error('validation', f"Validation failed: {str(e)}", error_details)
            
            with progress_placeholder.container():
                progress_tracker.render_detailed_progress('validation')
            
            st.error(f"❌ Validation error: {str(e)}")
            
            with st.expander("🔍 Error Details", expanded=True):
                st.code(error_details)
            
            return None
    
    # Show previous results if available
    if progress_tracker.get_stage_status('validation') == 'completed':
        st.success("✅ Validation already completed in this session")
        progress_tracker.render_stage_summary('validation')
        
        validation_results = st.session_state.workflow_data.get('validation_results', {})
        errors = validation_results.get('errors', [])
        warnings = validation_results.get('warnings', [])
        
        # Show errors/warnings if any
        if errors:
            with st.expander(f"❌ Errors ({len(errors)})", expanded=True):
                for error in errors[:5]:  # Show first 5 errors
                    st.error(error)
                if len(errors) > 5:
                    st.caption(f"... and {len(errors) - 5} more errors")
        
        if warnings:
            with st.expander(f"⚠️ Warnings ({len(warnings)})", expanded=False):
                for warning in warnings[:5]:  # Show first 5 warnings
                    st.warning(warning)
                if len(warnings) > 5:
                    st.caption(f"... and {len(warnings) - 5} more warnings")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Re-validate", type="secondary"):
                progress_tracker.clear_stage_progress('validation')
                st.rerun()
        with col2:
            if st.button("➡️ Continue to Download", type="primary"):
                st.session_state.current_stage = 5
                st.rerun()
    else:
        # Start validation button
        if st.button("🚀 Run Validation", type="primary", disabled=progress_tracker.get_stage_status('validation') == 'running'):
            validation_results = validate_data()
            
            if validation_results:
                errors = validation_results.get('errors', [])
                
                if not errors:
                    st.success("✅ All validation checks passed!")
                else:
                    st.error(f"Found {len(errors)} errors")
                
                # Show summary
                progress_tracker.render_stage_summary('validation')
                
                # Show enhanced validation dashboard if available
                if features['ENHANCED_VALIDATION'] and 'enhanced_validation_dashboard' in loaded_features:
                    with st.expander("📊 Detailed Validation Results", expanded=True):
                        loaded_features['enhanced_validation_dashboard'].render_dashboard(validation_results, st.session_state.workflow_data)
                
                # Auto-advance after brief pause
                time.sleep(2)
                st.session_state.current_stage = 5
                st.rerun()
        
        # Show info about the process
        with st.expander("ℹ️ What happens during validation?", expanded=False):
            st.markdown("""
            **The validation stage includes:**
            1. **Data Loading** - Load both mapped output and source data
            2. **Completeness Check** - Verify all required fields are populated
            3. **Accuracy Check** - Compare mapped values against source data
            4. **Consistency Check** - Ensure data formats and values are consistent
            5. **Report Generation** - Create detailed validation metrics
            
            **Expected Duration:** 5-15 seconds depending on data size
            """)

elif st.session_state.current_stage == 5:
    st.markdown("## 🎉 Complete!")
    st.success("Your data has been successfully processed and is ready for download.")
    
    # Download section
    mapped_file = st.session_state.workflow_data.get('mapped_file')
    if mapped_file and os.path.exists(mapped_file):
        with open(mapped_file, 'rb') as f:
            file_data = f.read()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📥 Download Final Report",
                data=file_data,
                file_name=f"PCA_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            if st.button("Start New Analysis", type="secondary", use_container_width=True):
                # Reset session state
                for key in ['current_stage', 'uploaded_files', 'workflow_data', 'file_validation']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.current_stage = 1
                st.rerun()