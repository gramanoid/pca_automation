"""
PCA Automation - Apple-Style Minimalist Design
Clean, intuitive interface with all features enabled
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

# Custom CSS for Apple-style design
st.markdown("""
<style>
    /* Apple-style color scheme */
    :root {
        --apple-bg: #FBFBFD;
        --apple-card: #FFFFFF;
        --apple-text: #1D1D1F;
        --apple-secondary: #86868B;
        --apple-blue: #0071E3;
        --apple-green: #34C759;
        --apple-yellow: #FFD60A;
        --apple-red: #FF3B30;
        --apple-border: #E5E5E7;
    }
    
    /* Clean background */
    .main {
        background-color: var(--apple-bg);
    }
    
    /* Card styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--apple-card);
        border-radius: 12px;
        padding: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    
    /* Button styling */
    .stButton > button {
        background-color: var(--apple-blue);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,113,227,0.2);
    }
    
    .stButton > button:hover {
        background-color: #0077ED;
        box-shadow: 0 4px 12px rgba(0,113,227,0.3);
        transform: translateY(-1px);
    }
    
    /* File uploader styling */
    .stFileUploader {
        background-color: var(--apple-card);
        border: 2px dashed var(--apple-border);
        border-radius: 12px;
        padding: 24px;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: var(--apple-blue);
    }
    
    /* Progress styling */
    .stProgress > div > div {
        background-color: var(--apple-blue);
    }
    
    /* Metric styling */
    .metric-container {
        background-color: var(--apple-card);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        text-align: center;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--apple-text);
        font-weight: 600;
    }
    
    /* Remove default Streamlit styling */
    .stAlert {
        background-color: var(--apple-card);
        border: 1px solid var(--apple-border);
        border-radius: 12px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--apple-card);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom container */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Stage indicator */
    .stage-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 2rem;
    }
    
    .stage-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin: 0 8px;
        transition: all 0.3s ease;
    }
    
    .stage-dot.active {
        background-color: var(--apple-blue);
        width: 32px;
        border-radius: 16px;
    }
    
    .stage-dot.completed {
        background-color: var(--apple-green);
    }
    
    .stage-dot.pending {
        background-color: var(--apple-border);
    }
    
    /* File upload cards */
    .upload-card {
        background-color: var(--apple-card);
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .upload-card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transform: translateY(-2px);
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
if 'stage_status' not in st.session_state:
    st.session_state.stage_status = {}

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

# Load all features without showing errors in UI
for feature in features:
    if feature == 'FILE_VALIDATION':
        try:
            from ui_components.file_upload import FileUploadComponent
            loaded_features['file_upload_component'] = FileUploadComponent()
            st.session_state.feature_status[feature] = {'loaded': True}
        except:
            st.session_state.feature_status[feature] = {'loaded': False}
    
    elif feature == 'PROGRESS_PERSISTENCE':
        try:
            from ui_components.progress_display import ProgressDisplay
            STAGES = {1: "Upload", 2: "Process", 3: "Map", 4: "Validate", 5: "Complete"}
            loaded_features['progress_display'] = ProgressDisplay(STAGES)
            st.session_state.feature_status[feature] = {'loaded': True}
        except:
            st.session_state.feature_status[feature] = {'loaded': False}
    
    elif feature == 'ENHANCED_VALIDATION':
        try:
            from ui_components.validation_dashboard_enhanced import EnhancedValidationDashboard
            loaded_features['enhanced_validation_dashboard'] = EnhancedValidationDashboard()
            st.session_state.feature_status[feature] = {'loaded': True}
        except:
            st.session_state.feature_status[feature] = {'loaded': False}
    
    elif feature == 'ERROR_RECOVERY':
        try:
            from ui_components.error_recovery import ErrorRecoveryHandler
            loaded_features['error_handler'] = ErrorRecoveryHandler()
            st.session_state.feature_status[feature] = {'loaded': True}
        except:
            st.session_state.feature_status[feature] = {'loaded': False}
    
    else:
        st.session_state.feature_status[feature] = {'loaded': True}

# Error handling wrapper
def handle_errors(func):
    """Error handling with optional recovery"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None
    return wrapper

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
        
        return True, "Valid file"
    except Exception as e:
        return False, f"Invalid file: {str(e)}"

# Sidebar with Apple-style navigation
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    
    # Stage progress with dots
    stages = ["Upload", "Process", "Map", "Validate", "Download"]
    
    for i, stage in enumerate(stages, 1):
        if i < st.session_state.current_stage:
            st.markdown(f"✅ **{stage}**")
        elif i == st.session_state.current_stage:
            st.markdown(f"🔵 **{stage}** ← Current")
        else:
            st.markdown(f"⚪ {stage}")
    
    st.markdown("---")
    
    # Simplified settings
    st.markdown("### ⚙️ Settings")
    st.checkbox("Enable AI Mapping", value=True, key="enable_llm_mapping", 
                help="Use AI to intelligently map data columns")
    
    # Progress indicator
    progress = (st.session_state.current_stage - 1) / 5
    st.progress(progress)
    st.caption(f"Step {st.session_state.current_stage} of 5")

# Main header with stage dots
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <h1 style='font-size: 2.5rem; margin-bottom: 0.5rem;'>PCA Automation</h1>
    <p style='color: #86868B; font-size: 1.1rem; margin-bottom: 1.5rem;'>Transform your media plans into insights</p>
</div>
""", unsafe_allow_html=True)

# Stage indicator dots
stage_html = "<div class='stage-indicator'>"
for i in range(1, 6):
    if i < st.session_state.current_stage:
        stage_html += "<div class='stage-dot completed'></div>"
    elif i == st.session_state.current_stage:
        stage_html += "<div class='stage-dot active'></div>"
    else:
        stage_html += "<div class='stage-dot pending'></div>"
stage_html += "</div>"
st.markdown(stage_html, unsafe_allow_html=True)

# Main content based on stage
if st.session_state.current_stage == 1:
    st.markdown("""
    <h2 style='text-align: center; margin-bottom: 1rem;'>📁 Upload Your Files</h2>
    <p style='text-align: center; color: #86868B; margin-bottom: 2rem;'>
        We need three files to get started. Don't worry, we'll guide you through each one.
    </p>
    """, unsafe_allow_html=True)
    
    # File upload cards
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        with st.container():
            st.markdown('<div class="upload-card">', unsafe_allow_html=True)
            st.markdown("### 📋 Media Plan")
            st.caption("Your planned media template with START/END markers")
            
            planned_file = st.file_uploader(
                "Choose file",
                type=['xlsx', 'xls'],
                key="planned_uploader",
                label_visibility="collapsed"
            )
            
            if planned_file:
                is_valid, message = validate_uploaded_file(planned_file, 'PLANNED')
                if is_valid:
                    st.success("✅ File uploaded", icon="✅")
                    save_uploaded_file(planned_file, 'PLANNED')
                    st.session_state.file_validation['PLANNED'] = True
                    
                    if features['DATA_PREVIEW']:
                        with st.expander("Preview data"):
                            planned_file.seek(0)
                            df = pd.read_excel(planned_file, sheet_name=0, nrows=5)
                            st.dataframe(df, use_container_width=True)
                else:
                    st.error(message, icon="❌")
                    st.session_state.file_validation['PLANNED'] = False
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown('<div class="upload-card">', unsafe_allow_html=True)
            st.markdown("### 📈 Platform Data")
            st.caption("Delivered data exports from platforms")
            
            delivered_file = st.file_uploader(
                "Choose file",
                type=['xlsx', 'xls'],
                key="delivered_uploader",
                label_visibility="collapsed"
            )
            
            if delivered_file:
                is_valid, message = validate_uploaded_file(delivered_file, 'DELIVERED')
                if is_valid:
                    st.success("✅ File uploaded", icon="✅")
                    save_uploaded_file(delivered_file, 'DELIVERED')
                    st.session_state.file_validation['DELIVERED'] = True
                    
                    if features['DATA_PREVIEW']:
                        with st.expander("Preview data"):
                            delivered_file.seek(0)
                            df = pd.read_excel(delivered_file, sheet_name=0, nrows=5)
                            st.dataframe(df, use_container_width=True)
                else:
                    st.error(message, icon="❌")
                    st.session_state.file_validation['DELIVERED'] = False
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        with st.container():
            st.markdown('<div class="upload-card">', unsafe_allow_html=True)
            st.markdown("### 📊 Output Template")
            st.caption("Empty Digital Tracker Report template")
            
            template_file = st.file_uploader(
                "Choose file",
                type=['xlsx', 'xls'],
                key="template_uploader",
                label_visibility="collapsed"
            )
            
            if template_file:
                is_valid, message = validate_uploaded_file(template_file, 'TEMPLATE')
                if is_valid:
                    st.success("✅ File uploaded", icon="✅")
                    save_uploaded_file(template_file, 'TEMPLATE')
                    st.session_state.file_validation['TEMPLATE'] = True
                    
                    if features['DATA_PREVIEW']:
                        with st.expander("Preview template"):
                            template_file.seek(0)
                            df = pd.read_excel(template_file, sheet_name=0, nrows=5)
                            st.dataframe(df, use_container_width=True)
                else:
                    st.error(message, icon="❌")
                    st.session_state.file_validation['TEMPLATE'] = False
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Check if ready to proceed
    st.markdown("<br>", unsafe_allow_html=True)
    
    all_uploaded = len(st.session_state.uploaded_files) == 3
    all_valid = all(st.session_state.file_validation.get(ft, False) for ft in ['PLANNED', 'DELIVERED', 'TEMPLATE'])
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if all_uploaded and all_valid:
            if st.button("Continue →", type="primary", use_container_width=True):
                st.session_state.current_stage = 2
                st.rerun()
        else:
            missing = [t for t in ['PLANNED', 'DELIVERED', 'TEMPLATE'] if t not in st.session_state.uploaded_files]
            if missing:
                st.info(f"📎 Please upload: {', '.join([m.replace('PLANNED', 'Media Plan').replace('DELIVERED', 'Platform Data').replace('TEMPLATE', 'Output Template') for m in missing])}")
            else:
                st.button("Continue →", type="primary", use_container_width=True, disabled=True)

elif st.session_state.current_stage == 2:
    st.markdown("""
    <h2 style='text-align: center; margin-bottom: 1rem;'>⚡ Processing Your Data</h2>
    <p style='text-align: center; color: #86868B; margin-bottom: 2rem;'>
        We'll extract and combine your data into a unified format
    </p>
    """, unsafe_allow_html=True)
    
    # Cache function if smart caching is enabled
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
    
    @handle_errors
    def process_data():
        """Process data with error handling"""
        from production_workflow.utils.workflow_wrapper import WorkflowWrapper
        wrapper = WorkflowWrapper()
        
        planned_path = st.session_state.uploaded_files.get("PLANNED")
        delivered_path = st.session_state.uploaded_files.get("DELIVERED")
        output_dir = Path(st.session_state.temp_dir) / "output"
        output_dir.mkdir(exist_ok=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔍 Analyzing media plan structure...")
        progress_bar.progress(25)
        time.sleep(0.5)
        
        status_text.text("📊 Extracting platform data...")
        progress_bar.progress(50)
        time.sleep(0.5)
        
        status_text.text("🔗 Combining data sources...")
        progress_bar.progress(75)
        
        if features['SMART_CACHING'] and 'cached_process_data' in globals():
            output_files = cached_process_data(planned_path, delivered_path, str(output_dir))
        else:
            output_files = wrapper.extract_and_combine_data(
                planned_path=planned_path,
                delivered_path=delivered_path,
                output_dir=str(output_dir),
                combine=True
            )
        
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
        st.session_state.workflow_data['combined_file'] = output_files.get('combined')
        st.session_state.workflow_data['output_dir'] = str(output_dir)
        
        return output_files
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start Processing", type="primary", use_container_width=True):
            result = process_data()
            
            if result:
                st.success("✅ Data processed successfully!")
                
                # Show quick stats
                if st.session_state.workflow_data.get('combined_file'):
                    df = pd.read_excel(st.session_state.workflow_data['combined_file'])
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Rows", f"{len(df):,}")
                    with col2:
                        st.metric("Columns", len(df.columns))
                    with col3:
                        st.metric("Data Points", f"{df.size:,}")
                
                time.sleep(1.5)
                st.session_state.current_stage = 3
                st.rerun()

elif st.session_state.current_stage == 3:
    st.markdown("""
    <h2 style='text-align: center; margin-bottom: 1rem;'>🎯 Mapping to Template</h2>
    <p style='text-align: center; color: #86868B; margin-bottom: 2rem;'>
        Using AI to intelligently map your data to the output template
    </p>
    """, unsafe_allow_html=True)
    
    @handle_errors
    def map_to_template():
        """Map data to template"""
        from production_workflow.utils.workflow_wrapper import WorkflowWrapper
        wrapper = WorkflowWrapper()
        
        combined_file = st.session_state.workflow_data.get('combined_file')
        template_path = st.session_state.uploaded_files.get("TEMPLATE")
        output_dir = st.session_state.workflow_data.get('output_dir')
        output_file = Path(output_dir) / f"final_mapped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🤖 Analyzing template structure...")
        progress_bar.progress(33)
        time.sleep(0.5)
        
        status_text.text("🧩 Mapping data columns...")
        progress_bar.progress(66)
        
        result = wrapper.map_to_template(
            input_file=combined_file,
            template_file=template_path,
            output_file=str(output_file)
        )
        
        progress_bar.progress(100)
        status_text.text("✅ Mapping complete!")
        
        st.session_state.workflow_data['mapped_file'] = str(output_file)
        st.session_state.workflow_data['mapping_result'] = result
        
        return result, output_file
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start Mapping", type="primary", use_container_width=True):
            result = map_to_template()
            
            if result:
                mapping_result, _ = result
                st.success("✅ Template mapping completed!")
                
                # Show mapping stats
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Columns Mapped", 
                             f"{mapping_result.get('mapped_count', 0)}/{mapping_result.get('total_columns', 0)}")
                with col2:
                    success_rate = (mapping_result.get('mapped_count', 0) / max(mapping_result.get('total_columns', 1), 1)) * 100
                    st.metric("Success Rate", f"{success_rate:.0f}%")
                
                time.sleep(1.5)
                st.session_state.current_stage = 4
                st.rerun()

elif st.session_state.current_stage == 4:
    st.markdown("""
    <h2 style='text-align: center; margin-bottom: 1rem;'>✅ Validating Results</h2>
    <p style='text-align: center; color: #86868B; margin-bottom: 2rem;'>
        Ensuring data accuracy and completeness
    </p>
    """, unsafe_allow_html=True)
    
    @handle_errors
    def validate_data():
        """Validate data"""
        from production_workflow.utils.workflow_wrapper import WorkflowWrapper
        wrapper = WorkflowWrapper()
        
        mapped_file = st.session_state.workflow_data.get('mapped_file')
        combined_file = st.session_state.workflow_data.get('combined_file')
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔍 Checking data integrity...")
        progress_bar.progress(33)
        time.sleep(0.5)
        
        status_text.text("📊 Validating calculations...")
        progress_bar.progress(66)
        
        validation_results = wrapper.validate_data(
            mapped_file=mapped_file,
            source_file=combined_file
        )
        
        progress_bar.progress(100)
        status_text.text("✅ Validation complete!")
        
        st.session_state.workflow_data['validation_results'] = validation_results
        return validation_results
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Run Validation", type="primary", use_container_width=True):
            validation_results = validate_data()
            
            if validation_results:
                errors = validation_results.get('errors', [])
                warnings = validation_results.get('warnings', [])
                
                if not errors and not warnings:
                    st.success("✅ All validation checks passed!")
                else:
                    if errors:
                        st.error(f"Found {len(errors)} errors")
                    if warnings:
                        st.warning(f"Found {len(warnings)} warnings")
                
                # Show validation metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Checks", validation_results.get('total_checks', 0))
                with col2:
                    st.metric("Passed", validation_results.get('passed_checks', 0))
                with col3:
                    accuracy = (validation_results.get('passed_checks', 0) / max(validation_results.get('total_checks', 1), 1)) * 100
                    st.metric("Accuracy", f"{accuracy:.0f}%")
                
                time.sleep(1.5)
                st.session_state.current_stage = 5
                st.rerun()

elif st.session_state.current_stage == 5:
    st.markdown("""
    <h2 style='text-align: center; margin-bottom: 1rem;'>🎉 All Done!</h2>
    <p style='text-align: center; color: #86868B; margin-bottom: 2rem;'>
        Your data has been successfully processed and is ready to download
    </p>
    """, unsafe_allow_html=True)
    
    # Success animation placeholder
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem;'>
            <div style='font-size: 4rem;'>✅</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Download button
        mapped_file = st.session_state.workflow_data.get('mapped_file')
        if mapped_file and os.path.exists(mapped_file):
            with open(mapped_file, 'rb') as f:
                file_data = f.read()
            
            st.download_button(
                label="⬇️  Download Your Report",
                data=file_data,
                file_name=f"PCA_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Start New Analysis", type="secondary", use_container_width=True):
            # Reset session state
            for key in ['current_stage', 'uploaded_files', 'workflow_data', 'file_validation']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_stage = 1
            st.rerun()

# Minimal footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #86868B; font-size: 0.9rem;'>
    Made with ❤️ for better media planning
</div>
""", unsafe_allow_html=True)