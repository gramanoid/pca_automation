"""
PCA Automation - Gradual Enhancement Version
Allows enabling features one by one through environment variables
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

# Feature flags - can be set via environment variables
FEATURES = {
    'FILE_VALIDATION': os.getenv('ENABLE_FILE_VALIDATION', 'false').lower() == 'true',
    'DATA_PREVIEW': os.getenv('ENABLE_DATA_PREVIEW', 'false').lower() == 'true',
    'PROGRESS_PERSISTENCE': os.getenv('ENABLE_PROGRESS_PERSISTENCE', 'false').lower() == 'true',
    'SMART_CACHING': os.getenv('ENABLE_SMART_CACHING', 'false').lower() == 'true',
    'ENHANCED_VALIDATION': os.getenv('ENABLE_ENHANCED_VALIDATION', 'false').lower() == 'true',
    'ERROR_RECOVERY': os.getenv('ENABLE_ERROR_RECOVERY', 'false').lower() == 'true',
    'MARKER_VALIDATION': os.getenv('ENABLE_MARKER_VALIDATION', 'false').lower() == 'true',
    'CONFIG_PERSISTENCE': os.getenv('ENABLE_CONFIG_PERSISTENCE', 'false').lower() == 'true',
}

# Page configuration
st.set_page_config(
    page_title="PCA Media Plan Automation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.markdown('<h1 style="text-align: center; color: #1f77b4;">📊 PCA Automation</h1>', unsafe_allow_html=True)

# Show active features in sidebar
with st.sidebar:
    with st.expander("🎛️ Active Features", expanded=True):
        for feature, enabled in FEATURES.items():
            if enabled:
                st.success(f"✅ {feature.replace('_', ' ').title()}")
            else:
                st.text(f"⭕ {feature.replace('_', ' ').title()}")

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

# Import components based on features
if FEATURES['FILE_VALIDATION']:
    try:
        from ui_components.file_upload import FileUploadComponent
        file_upload_component = FileUploadComponent()
        st.sidebar.success("✓ File validation loaded")
    except Exception as e:
        st.sidebar.error(f"✗ File validation failed: {str(e)}")
        FEATURES['FILE_VALIDATION'] = False

if FEATURES['PROGRESS_PERSISTENCE']:
    try:
        from ui_components.progress_display import ProgressDisplay
        STAGES = {1: "Data Upload", 2: "Data Processing", 3: "Template Mapping", 4: "Validation", 5: "Results"}
        progress_display = ProgressDisplay(STAGES)
        st.sidebar.success("✓ Progress persistence loaded")
    except Exception as e:
        st.sidebar.error(f"✗ Progress persistence failed: {str(e)}")
        FEATURES['PROGRESS_PERSISTENCE'] = False

if FEATURES['ENHANCED_VALIDATION']:
    try:
        from ui_components.validation_dashboard_enhanced import EnhancedValidationDashboard
        enhanced_validation_dashboard = EnhancedValidationDashboard()
        st.sidebar.success("✓ Enhanced validation loaded")
    except Exception as e:
        st.sidebar.error(f"✗ Enhanced validation failed: {str(e)}")
        FEATURES['ENHANCED_VALIDATION'] = False

if FEATURES['ERROR_RECOVERY']:
    try:
        from ui_components.error_recovery import ErrorRecoveryHandler
        error_handler = ErrorRecoveryHandler()
        st.sidebar.success("✓ Error recovery loaded")
    except Exception as e:
        st.sidebar.error(f"✗ Error recovery failed: {str(e)}")
        FEATURES['ERROR_RECOVERY'] = False

# Basic error handling
def handle_errors(func):
    """Error handling with optional recovery"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if FEATURES['ERROR_RECOVERY'] and 'error_handler' in globals():
                context = {
                    'function': func.__name__,
                    'stage': st.session_state.get('current_stage', 'Unknown')
                }
                error_handler.render_error_recovery_ui(e, context)
            else:
                st.error(f"❌ Error: {str(e)}")
                if st.button("Show Details"):
                    st.code(str(e))
            return None
    return wrapper

# Sidebar navigation
with st.sidebar:
    st.header("Navigation")
    stages = ["1. Data Upload", "2. Data Processing", "3. Template Mapping", "4. Validation", "5. Results"]
    
    if FEATURES['PROGRESS_PERSISTENCE'] and 'progress_display' in globals():
        progress_display.render_sidebar_progress()
    else:
        # Simple progress display
        for i, stage in enumerate(stages, 1):
            if i < st.session_state.current_stage:
                st.success(f"✅ {stage}")
            elif i == st.session_state.current_stage:
                st.info(f"▶️ {stage}")
            else:
                st.text(f"⏸️ {stage}")
    
    st.divider()
    
    st.header("Settings")
    st.checkbox("Enable LLM Mapping", value=True, key="enable_llm_mapping")
    st.checkbox("Strict Validation Mode", value=False, key="validation_strict_mode")
    st.checkbox("Debug Mode", value=False, key="debug_mode")

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
        # Try to read first sheet
        df = pd.read_excel(file, sheet_name=0, nrows=5)
        
        if file_type == "PLANNED":
            # Check for required sheets
            xl_file = pd.ExcelFile(file)
            required_sheets = ['DV360', 'META', 'TIKTOK']
            missing = [s for s in required_sheets if s not in xl_file.sheet_names]
            if missing:
                return False, f"Missing sheets: {', '.join(missing)}"
        
        return True, "File is valid"
    except Exception as e:
        return False, f"Invalid file: {str(e)}"

# Main content
if st.session_state.current_stage == 1:
    st.header("Stage 1: Data Upload")
    
    st.info("""
    Please upload the following files:
    - **PLANNED File**: Media plan template with START/END markers
    - **DELIVERED File**: Platform data exports
    - **OUTPUT TEMPLATE**: Empty Digital Tracker Report template
    """)
    
    col1, col2, col3 = st.columns(3)
    
    # PLANNED file upload
    with col1:
        st.subheader("📋 PLANNED File")
        
        if FEATURES['FILE_VALIDATION'] and 'file_upload_component' in globals():
            # Use enhanced file upload
            result = file_upload_component.render_file_upload('PLANNED', col1)
            if result['uploaded'] and result['valid']:
                st.session_state.file_validation['PLANNED'] = True
        else:
            # Basic file upload
            planned_file = st.file_uploader(
                "Upload PLANNED Excel file",
                type=['xlsx', 'xls'],
                key="planned_uploader"
            )
            if planned_file:
                if FEATURES['FILE_VALIDATION']:
                    # Basic validation
                    is_valid, message = validate_uploaded_file(planned_file, 'PLANNED')
                    if is_valid:
                        st.success(f"✅ {message}")
                        save_uploaded_file(planned_file, 'PLANNED')
                        st.session_state.file_validation['PLANNED'] = True
                    else:
                        st.error(f"❌ {message}")
                        st.session_state.file_validation['PLANNED'] = False
                else:
                    st.success("✅ File uploaded")
                    save_uploaded_file(planned_file, 'PLANNED')
                    st.session_state.file_validation['PLANNED'] = True
                
                # Data preview
                if FEATURES['DATA_PREVIEW'] and st.session_state.file_validation.get('PLANNED', False):
                    with st.expander("Preview data"):
                        df = pd.read_excel(planned_file, sheet_name=0, nrows=10)
                        st.dataframe(df)
    
    # DELIVERED file upload
    with col2:
        st.subheader("📈 DELIVERED File")
        
        delivered_file = st.file_uploader(
            "Upload DELIVERED Excel file",
            type=['xlsx', 'xls'],
            key="delivered_uploader"
        )
        if delivered_file:
            if FEATURES['FILE_VALIDATION']:
                is_valid, message = validate_uploaded_file(delivered_file, 'DELIVERED')
                if is_valid:
                    st.success(f"✅ {message}")
                    save_uploaded_file(delivered_file, 'DELIVERED')
                    st.session_state.file_validation['DELIVERED'] = True
                else:
                    st.error(f"❌ {message}")
                    st.session_state.file_validation['DELIVERED'] = False
            else:
                st.success("✅ File uploaded")
                save_uploaded_file(delivered_file, 'DELIVERED')
                st.session_state.file_validation['DELIVERED'] = True
            
            if FEATURES['DATA_PREVIEW'] and st.session_state.file_validation.get('DELIVERED', False):
                with st.expander("Preview data"):
                    df = pd.read_excel(delivered_file, sheet_name=0, nrows=10)
                    st.dataframe(df)
    
    # TEMPLATE file upload
    with col3:
        st.subheader("📄 OUTPUT TEMPLATE")
        
        template_file = st.file_uploader(
            "Upload OUTPUT TEMPLATE Excel file",
            type=['xlsx', 'xls'],
            key="template_uploader"
        )
        if template_file:
            st.success("✅ Template uploaded")
            save_uploaded_file(template_file, 'TEMPLATE')
            st.session_state.file_validation['TEMPLATE'] = True
            
            if FEATURES['DATA_PREVIEW']:
                with st.expander("Preview template"):
                    df = pd.read_excel(template_file, sheet_name=0, nrows=10)
                    st.dataframe(df)
    
    # Check if all files are uploaded
    all_uploaded = len(st.session_state.uploaded_files) == 3
    
    if FEATURES['FILE_VALIDATION']:
        all_valid = all(st.session_state.file_validation.get(ft, False) for ft in ['PLANNED', 'DELIVERED', 'TEMPLATE'])
        can_proceed = all_uploaded and all_valid
    else:
        can_proceed = all_uploaded
    
    if can_proceed:
        st.success("✅ All files uploaded successfully!")
        
        # Marker validation if enabled
        if FEATURES['MARKER_VALIDATION']:
            st.warning("⚠️ Marker validation is enabled but not implemented in gradual version yet")
        
        if st.button("Continue to Data Processing", type="primary", use_container_width=True):
            st.session_state.current_stage = 2
            st.rerun()
    else:
        missing = [t for t in ['PLANNED', 'DELIVERED', 'TEMPLATE'] if t not in st.session_state.uploaded_files]
        if missing:
            st.warning(f"⚠️ Please upload: {', '.join(missing)}")

elif st.session_state.current_stage == 2:
    st.header("Stage 2: Data Processing")
    
    st.info("Click the button below to extract and combine data from your uploaded files.")
    
    @handle_errors
    def process_data():
        """Process data with error handling"""
        from production_workflow.utils.workflow_wrapper import WorkflowWrapper
        wrapper = WorkflowWrapper()
        
        # Get file paths
        planned_path = st.session_state.uploaded_files.get("PLANNED")
        delivered_path = st.session_state.uploaded_files.get("DELIVERED")
        output_dir = Path(st.session_state.temp_dir) / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Processing PLANNED data...")
        progress_bar.progress(25)
        
        # Process data
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
    
    if st.button("🚀 Start Data Processing", type="primary", use_container_width=True):
        with st.spinner("Processing data..."):
            result = process_data()
            
            if result:
                st.success("✅ Data processing completed successfully!")
                
                # Preview if enabled
                if FEATURES['DATA_PREVIEW'] and st.session_state.workflow_data.get('combined_file'):
                    with st.expander("Preview combined data"):
                        df = pd.read_excel(st.session_state.workflow_data['combined_file'], nrows=20)
                        st.dataframe(df)
                
                time.sleep(1)
                st.session_state.current_stage = 3
                st.rerun()

elif st.session_state.current_stage == 3:
    st.header("Stage 3: Template Mapping")
    
    st.info("Map your combined data to the output template.")
    
    @handle_errors
    def map_to_template():
        """Map data to template"""
        from production_workflow.utils.workflow_wrapper import WorkflowWrapper
        wrapper = WorkflowWrapper()
        
        # Get file paths
        combined_file = st.session_state.workflow_data.get('combined_file')
        template_path = st.session_state.uploaded_files.get("TEMPLATE")
        output_dir = st.session_state.workflow_data.get('output_dir')
        output_file = Path(output_dir) / f"final_mapped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Map to template
        result = wrapper.map_to_template(
            input_file=combined_file,
            template_file=template_path,
            output_file=str(output_file)
        )
        
        st.session_state.workflow_data['mapped_file'] = str(output_file)
        st.session_state.workflow_data['mapping_result'] = result
        
        return result, output_file
    
    if st.button("🎯 Start Template Mapping", type="primary", use_container_width=True):
        with st.spinner("Mapping data to template..."):
            result = map_to_template()
            
            if result:
                mapping_result, output_file = result
                st.success("✅ Template mapping completed successfully!")
                st.metric("Columns Mapped", f"{mapping_result.get('mapped_count', 0)}/{mapping_result.get('total_columns', 0)}")
                
                time.sleep(1)
                st.session_state.current_stage = 4
                st.rerun()

elif st.session_state.current_stage == 4:
    st.header("Stage 4: Validation")
    
    st.info("Validate the accuracy and completeness of your mapped data.")
    
    @handle_errors
    def validate_data():
        """Validate data"""
        from production_workflow.utils.workflow_wrapper import WorkflowWrapper
        wrapper = WorkflowWrapper()
        
        # Get file paths
        mapped_file = st.session_state.workflow_data.get('mapped_file')
        combined_file = st.session_state.workflow_data.get('combined_file')
        
        # Run validation
        validation_results = wrapper.validate_data(
            mapped_file=mapped_file,
            source_file=combined_file
        )
        
        st.session_state.workflow_data['validation_results'] = validation_results
        return validation_results
    
    if st.button("🔍 Run Validation", type="primary", use_container_width=True):
        with st.spinner("Validating data..."):
            validation_results = validate_data()
            
            if validation_results:
                # Display results
                errors = validation_results.get('errors', [])
                warnings = validation_results.get('warnings', [])
                
                if errors:
                    st.error(f"❌ Found {len(errors)} errors")
                elif warnings:
                    st.warning(f"⚠️ Found {len(warnings)} warnings")
                else:
                    st.success("✅ Validation passed!")
                
                # Use enhanced dashboard if available
                if FEATURES['ENHANCED_VALIDATION'] and 'enhanced_validation_dashboard' in globals():
                    enhanced_validation_dashboard.render_dashboard(validation_results, st.session_state.workflow_data)
                else:
                    # Basic display
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Checks", validation_results.get('total_checks', 0))
                    with col2:
                        st.metric("Passed Checks", validation_results.get('passed_checks', 0))
                    
                    if errors:
                        with st.expander("Errors"):
                            for error in errors:
                                st.error(error)
                    
                    if warnings:
                        with st.expander("Warnings"):
                            for warning in warnings:
                                st.warning(warning)
                
                time.sleep(1)
                st.session_state.current_stage = 5
                st.rerun()

elif st.session_state.current_stage == 5:
    st.header("Stage 5: Results & Download")
    
    st.success("🎉 Workflow completed successfully!")
    
    # Download section
    mapped_file = st.session_state.workflow_data.get('mapped_file')
    if mapped_file and os.path.exists(mapped_file):
        with open(mapped_file, 'rb') as f:
            file_data = f.read()
        
        st.download_button(
            label="⬇️ Download Final Excel File",
            data=file_data,
            file_name=f"PCA_Output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    if st.button("🔄 Start New Process", type="primary", use_container_width=True):
        # Reset session state
        for key in ['current_stage', 'uploaded_files', 'workflow_data', 'file_validation']:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.current_stage = 1
        st.rerun()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #6c757d;'>
    PCA Automation - Gradual Enhancement Mode | 
    <a href='https://github.com/gramanoid/pca_automation' target='_blank'>GitHub</a>
</div>
""", unsafe_allow_html=True)