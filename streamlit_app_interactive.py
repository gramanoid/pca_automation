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
    
    /* Root variables */
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
        background-color: var(--card-bg);
        border-right: 1px solid var(--border-color);
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
        background-color: #E8F4FD;
        border: 1px solid #B8E0FF;
        color: var(--primary-blue);
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
        background-color: var(--background);
        border-radius: 6px;
        font-weight: 500;
    }
    
    /* Success/Error/Warning messages */
    .stAlert > div {
        border-radius: 6px;
        font-size: 0.875rem;
    }
    
    /* File uploader */
    [data-testid="stFileUploadDropzone"] {
        background-color: var(--background);
        border: 2px dashed var(--border-color);
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: var(--primary-blue);
        background-color: #F0F7FF;
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
        """Process data with error handling"""
        try:
            from production_workflow.utils.workflow_wrapper import WorkflowWrapper
            wrapper = WorkflowWrapper()
            
            planned_path = st.session_state.uploaded_files.get("PLANNED")
            delivered_path = st.session_state.uploaded_files.get("DELIVERED")
            output_dir = Path(st.session_state.temp_dir) / "output"
            output_dir.mkdir(exist_ok=True)
            
            with st.spinner("Processing your data..."):
                if features['SMART_CACHING'] and 'cached_process_data' in globals():
                    output_files = cached_process_data(planned_path, delivered_path, str(output_dir))
                else:
                    output_files = wrapper.extract_and_combine_data(
                        planned_path=planned_path,
                        delivered_path=delivered_path,
                        output_dir=str(output_dir),
                        combine=True
                    )
            
            st.session_state.workflow_data['combined_file'] = output_files.get('combined')
            st.session_state.workflow_data['output_dir'] = str(output_dir)
            
            return output_files
        except Exception as e:
            st.error(f"Processing error: {str(e)}")
            return None
    
    if st.button("Start Processing", type="primary"):
        result = process_data()
        
        if result:
            st.success("✅ Data processed successfully!")
            
            # Show stats
            if st.session_state.workflow_data.get('combined_file'):
                df = pd.read_excel(st.session_state.workflow_data['combined_file'])
                col1, col2, col3 = st.columns(3)
                col1.metric("Rows", f"{len(df):,}")
                col2.metric("Columns", len(df.columns))
                col3.metric("Platforms", len(df['Platform'].unique()) if 'Platform' in df else 0)
            
            time.sleep(1)
            st.session_state.current_stage = 3
            st.rerun()

elif st.session_state.current_stage == 3:
    st.markdown("## 🗺️ Template Mapping")
    st.markdown("Map your combined data to the output template using AI.")
    
    def map_to_template():
        """Map data to template"""
        try:
            from production_workflow.utils.workflow_wrapper import WorkflowWrapper
            wrapper = WorkflowWrapper()
            
            combined_file = st.session_state.workflow_data.get('combined_file')
            template_path = st.session_state.uploaded_files.get("TEMPLATE")
            output_dir = st.session_state.workflow_data.get('output_dir')
            output_file = Path(output_dir) / f"final_mapped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            with st.spinner("Mapping data to template..."):
                result = wrapper.map_to_template(
                    input_file=combined_file,
                    template_file=template_path,
                    output_file=str(output_file)
                )
            
            st.session_state.workflow_data['mapped_file'] = str(output_file)
            st.session_state.workflow_data['mapping_result'] = result
            
            return result, output_file
        except Exception as e:
            st.error(f"Mapping error: {str(e)}")
            return None
    
    if st.button("Start Mapping", type="primary"):
        result = map_to_template()
        
        if result:
            mapping_result, _ = result
            st.success("✅ Template mapping completed!")
            
            # Show results
            col1, col2 = st.columns(2)
            col1.metric("Mapped Columns", f"{mapping_result.get('mapped_count', 0)}/{mapping_result.get('total_columns', 0)}")
            col2.metric("Success Rate", f"{(mapping_result.get('mapped_count', 0) / max(mapping_result.get('total_columns', 1), 1) * 100):.0f}%")
            
            time.sleep(1)
            st.session_state.current_stage = 4
            st.rerun()

elif st.session_state.current_stage == 4:
    st.markdown("## ✓ Data Validation")
    st.markdown("Validate the accuracy and completeness of your mapped data.")
    
    def validate_data():
        """Validate data"""
        try:
            from production_workflow.utils.workflow_wrapper import WorkflowWrapper
            wrapper = WorkflowWrapper()
            
            mapped_file = st.session_state.workflow_data.get('mapped_file')
            combined_file = st.session_state.workflow_data.get('combined_file')
            
            with st.spinner("Validating data..."):
                validation_results = wrapper.validate_data(
                    mapped_file=mapped_file,
                    source_file=combined_file
                )
            
            st.session_state.workflow_data['validation_results'] = validation_results
            return validation_results
        except Exception as e:
            st.error(f"Validation error: {str(e)}")
            return None
    
    if st.button("Run Validation", type="primary"):
        validation_results = validate_data()
        
        if validation_results:
            errors = validation_results.get('errors', [])
            warnings = validation_results.get('warnings', [])
            
            if not errors:
                st.success("✅ All validation checks passed!")
            else:
                st.error(f"Found {len(errors)} errors")
            
            # Show metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Checks", validation_results.get('total_checks', 0))
            col2.metric("Passed", validation_results.get('passed_checks', 0))
            col3.metric("Accuracy", f"{(validation_results.get('passed_checks', 0) / max(validation_results.get('total_checks', 1), 1) * 100):.0f}%")
            
            if features['ENHANCED_VALIDATION'] and 'enhanced_validation_dashboard' in loaded_features:
                with st.expander("Detailed Results"):
                    loaded_features['enhanced_validation_dashboard'].render_dashboard(validation_results, st.session_state.workflow_data)
            
            time.sleep(1)
            st.session_state.current_stage = 5
            st.rerun()

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