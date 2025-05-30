"""
PCA Automation - Streamlit Web Interface (Enhanced)
A user-friendly interface for the Planned vs Delivered automation workflow.
Phase 1 Enhancements: File validation, data preview, smart caching, progress indicators
"""

import streamlit as st
import pandas as pd
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import importlib
import time
from typing import Dict, Tuple, Optional, Any

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import workflow wrapper
from production_workflow.utils.workflow_wrapper import WorkflowWrapper

# Page configuration
st.set_page_config(
    page_title="PCA Media Plan Automation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 2rem;
    }
    .stage-header {
        font-size: 1.8rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #e3f2fd;
        border: 1px solid #bbdefb;
        color: #0d47a1;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    div[data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }
    .stage-complete {
        color: #28a745;
        font-weight: bold;
    }
    .stage-current {
        color: #ffc107;
        font-weight: bold;
    }
    .stage-pending {
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_stage' not in st.session_state:
    st.session_state.current_stage = 1
if 'workflow_data' not in st.session_state:
    st.session_state.workflow_data = {}
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = {}
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp(prefix="pca_automation_")
if 'stage_status' not in st.session_state:
    st.session_state.stage_status = {
        1: 'pending',  # Data Upload
        2: 'pending',  # Data Processing
        3: 'pending',  # Template Mapping
        4: 'pending',  # Validation
        5: 'pending'   # Results
    }
if 'file_validation' not in st.session_state:
    st.session_state.file_validation = {}

# Load configuration with caching
@st.cache_data(ttl=3600)
def load_config():
    """Load configuration from config files"""
    config = {}
    config_path = project_root / "config" / "config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    return config

# File validation functions
def validate_uploaded_file(file, file_type: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
    """
    Validate uploaded file format and structure
    
    Returns:
        Tuple of (is_valid, message, preview_df)
    """
    try:
        # Try to read the Excel file
        df_first_sheet = pd.read_excel(file, sheet_name=0, nrows=10)
        
        # Reset file pointer for further processing
        file.seek(0)
        
        # Type-specific validation
        if file_type == "PLANNED":
            # Check for required sheets
            xl_file = pd.ExcelFile(file)
            required_sheets = ['DV360', 'META', 'TIKTOK']
            missing_sheets = [sheet for sheet in required_sheets if sheet not in xl_file.sheet_names]
            
            if missing_sheets:
                return False, f"❌ Missing required sheets: {', '.join(missing_sheets)}", None
            
            # Check for START/END markers in each sheet
            for sheet in required_sheets:
                sheet_df = pd.read_excel(file, sheet_name=sheet, nrows=50)
                if not any('START' in str(cell) for cell in sheet_df.values.flatten()):
                    return False, f"❌ No START marker found in {sheet} sheet", None
            
            file.seek(0)
            return True, f"✅ Valid PLANNED file with {len(xl_file.sheet_names)} sheets", df_first_sheet
            
        elif file_type == "DELIVERED":
            # Check for platform data
            xl_file = pd.ExcelFile(file)
            platform_sheets = [s for s in xl_file.sheet_names if any(p in s.upper() for p in ['DV360', 'META', 'TIKTOK'])]
            
            if not platform_sheets:
                return False, "❌ No platform sheets found (DV360, META, or TIKTOK)", None
                
            file.seek(0)
            return True, f"✅ Valid DELIVERED file with {len(platform_sheets)} platform sheets", df_first_sheet
            
        elif file_type == "TEMPLATE":
            # Check if it's a valid Excel template
            if len(df_first_sheet.columns) < 10:
                return False, "❌ Template appears to have insufficient columns", None
                
            file.seek(0)
            return True, "✅ Valid OUTPUT TEMPLATE file", df_first_sheet
            
        else:
            file.seek(0)
            return True, "✅ File loaded successfully", df_first_sheet
            
    except Exception as e:
        return False, f"❌ Error reading file: {str(e)}", None

# Utility functions
def save_uploaded_file(uploaded_file, file_type):
    """Save uploaded file to temporary directory"""
    if uploaded_file is not None:
        file_path = Path(st.session_state.temp_dir) / f"{file_type}_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.uploaded_files[file_type] = file_path
        return file_path
    return None

def cleanup_temp_files():
    """Clean up temporary files on session end"""
    if hasattr(st.session_state, 'temp_dir') and os.path.exists(st.session_state.temp_dir):
        shutil.rmtree(st.session_state.temp_dir)

def get_stage_icon(stage_num: int) -> str:
    """Get icon for stage based on its status"""
    current = st.session_state.current_stage
    status = st.session_state.stage_status.get(stage_num, 'pending')
    
    if status == 'completed':
        return "✅"
    elif stage_num == current:
        return "⏳"
    else:
        return "⭕"

def update_stage_status(stage_num: int, status: str):
    """Update the status of a stage"""
    st.session_state.stage_status[stage_num] = status

# Cached processing functions
@st.cache_data(ttl=3600, show_spinner=False)
def cached_extract_and_combine(planned_path: str, delivered_path: str, output_dir: str) -> Dict[str, Any]:
    """Cached version of data extraction and combination"""
    wrapper = WorkflowWrapper()
    return wrapper.extract_and_combine_data(
        planned_path=planned_path,
        delivered_path=delivered_path,
        output_dir=output_dir,
        combine=True
    )

@st.cache_data(ttl=3600, show_spinner=False)
def cached_map_to_template(input_file: str, template_file: str, output_file: str) -> Dict[str, Any]:
    """Cached version of template mapping"""
    wrapper = WorkflowWrapper()
    return wrapper.map_to_template(
        input_file=input_file,
        template_file=template_file,
        output_file=output_file
    )

@st.cache_data(ttl=1800, show_spinner=False)
def load_excel_preview(file_path: str, nrows: int = 10) -> pd.DataFrame:
    """Load Excel file preview with caching"""
    return pd.read_excel(file_path, nrows=nrows)

# Header
st.markdown('<h1 class="main-header">📊 PCA Automation</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🧭 Navigation")
    
    # Stage selection with status indicators
    stages = {
        1: "Data Upload",
        2: "Data Processing", 
        3: "Template Mapping",
        4: "Validation",
        5: "Results & Download"
    }
    
    for stage_num, stage_name in stages.items():
        icon = get_stage_icon(stage_num)
        button_label = f"{icon} {stage_name}"
        
        # Style the current stage differently
        if stage_num == st.session_state.current_stage:
            button_label = f"**{button_label}**"
        
        if st.button(
            button_label, 
            key=f"stage_{stage_num}",
            disabled=stage_num > 1 and st.session_state.stage_status.get(stage_num - 1, 'pending') != 'completed',
            use_container_width=True
        ):
            st.session_state.current_stage = stage_num
    
    st.divider()
    
    # Progress indicator
    completed_stages = sum(1 for status in st.session_state.stage_status.values() if status == 'completed')
    progress = completed_stages / len(stages)
    st.progress(progress)
    st.caption(f"Progress: {completed_stages}/{len(stages)} stages completed")
    
    st.divider()
    
    # Configuration section
    with st.expander("⚙️ Configuration", expanded=False):
        config = load_config()
        
        st.subheader("Client Settings")
        client_id = st.text_input(
            "Client ID", 
            value=os.getenv("CLIENT_ID", ""),
            help="Leave empty for default mappings"
        )
        if client_id:
            os.environ["CLIENT_ID"] = client_id
        
        st.subheader("API Settings")
        api_key = st.text_input(
            "Anthropic API Key",
            value=os.getenv("ANTHROPIC_API_KEY", ""),
            type="password",
            help="Required for enhanced LLM mapping"
        )
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
        
        st.subheader("Debug Settings")
        debug_mode = st.checkbox("Enable Debug Mode", value=False)
        if debug_mode:
            os.environ["EXCEL_EXTRACTOR_LOG_LEVEL"] = "DEBUG"
            os.environ["MAPPER_LOG_LEVEL"] = "DEBUG"

# Main content area
if st.session_state.current_stage == 1:
    # Stage 1: Data Upload
    update_stage_status(1, 'current')
    st.markdown('<h2 class="stage-header">📁 Stage 1: Data Upload</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>Required Files:</strong><br>
    • <b>PLANNED File</b>: Media plan template with START/END markers (DV360, META, TIKTOK sheets)<br>
    • <b>DELIVERED File</b>: Platform data exports with R&F and Media sections<br>
    • <b>OUTPUT TEMPLATE</b>: Empty Digital Tracker Report template to be filled
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📋 PLANNED File")
        planned_file = st.file_uploader(
            "Upload PLANNED Excel file",
            type=['xlsx', 'xls'],
            key="planned_uploader",
            help="Media plan template (e.g., PLANNED_INPUT_TEMPLATE_*.xlsx)"
        )
        if planned_file:
            # Validate file
            is_valid, message, preview_df = validate_uploaded_file(planned_file, "PLANNED")
            st.session_state.file_validation["PLANNED"] = is_valid
            
            if is_valid:
                st.success(message)
                save_uploaded_file(planned_file, "PLANNED")
                
                # Show preview
                with st.expander("📊 Preview uploaded data"):
                    st.dataframe(preview_df, use_container_width=True)
            else:
                st.error(message)
    
    with col2:
        st.subheader("📈 DELIVERED File")
        delivered_file = st.file_uploader(
            "Upload DELIVERED Excel file",
            type=['xlsx', 'xls'],
            key="delivered_uploader",
            help="Platform data exports (e.g., DELIVERED_INPUT_TEMPLATE_*.xlsx)"
        )
        if delivered_file:
            # Validate file
            is_valid, message, preview_df = validate_uploaded_file(delivered_file, "DELIVERED")
            st.session_state.file_validation["DELIVERED"] = is_valid
            
            if is_valid:
                st.success(message)
                save_uploaded_file(delivered_file, "DELIVERED")
                
                # Show preview
                with st.expander("📊 Preview uploaded data"):
                    st.dataframe(preview_df, use_container_width=True)
            else:
                st.error(message)
    
    with col3:
        st.subheader("📄 OUTPUT TEMPLATE")
        template_file = st.file_uploader(
            "Upload OUTPUT TEMPLATE Excel file",
            type=['xlsx', 'xls'],
            key="template_uploader",
            help="Empty template to fill (e.g., OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx)"
        )
        if template_file:
            # Validate file
            is_valid, message, preview_df = validate_uploaded_file(template_file, "TEMPLATE")
            st.session_state.file_validation["TEMPLATE"] = is_valid
            
            if is_valid:
                st.success(message)
                save_uploaded_file(template_file, "TEMPLATE")
                
                # Show preview
                with st.expander("📊 Preview uploaded data"):
                    st.dataframe(preview_df, use_container_width=True)
            else:
                st.error(message)
    
    # Check if all files are uploaded and valid
    all_files_uploaded = all(key in st.session_state.uploaded_files for key in ["PLANNED", "DELIVERED", "TEMPLATE"])
    all_files_valid = all(st.session_state.file_validation.get(key, False) for key in ["PLANNED", "DELIVERED", "TEMPLATE"])
    
    if all_files_uploaded and all_files_valid:
        st.markdown('<div class="success-message">✅ All required files uploaded and validated! You can proceed to Data Processing.</div>', unsafe_allow_html=True)
        st.session_state.processing_complete[1] = True
        update_stage_status(1, 'completed')
        
        if st.button("➡️ Continue to Data Processing", use_container_width=True):
            st.session_state.current_stage = 2
            st.rerun()
    elif all_files_uploaded and not all_files_valid:
        invalid_files = [key for key in ["PLANNED", "DELIVERED", "TEMPLATE"] if not st.session_state.file_validation.get(key, False)]
        st.error(f"⚠️ Please fix validation errors for: {', '.join(invalid_files)}")
    else:
        missing_files = [key for key in ["PLANNED", "DELIVERED", "TEMPLATE"] if key not in st.session_state.uploaded_files]
        if missing_files:
            st.warning(f"⚠️ Please upload all required files. Missing: {', '.join(missing_files)}")

elif st.session_state.current_stage == 2:
    # Stage 2: Data Processing
    update_stage_status(2, 'current')
    st.markdown('<h2 class="stage-header">⚙️ Stage 2: Data Processing</h2>', unsafe_allow_html=True)
    
    st.info("This stage extracts data from your uploaded files and combines them for template mapping.")
    
    if st.button("🚀 Start Data Processing", use_container_width=True):
        try:
            with st.spinner("Extracting and combining data..."):
                # Create progress placeholders
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Get file paths
                planned_path = st.session_state.uploaded_files.get("PLANNED")
                delivered_path = st.session_state.uploaded_files.get("DELIVERED")
                output_dir = Path(st.session_state.temp_dir) / "output"
                output_dir.mkdir(exist_ok=True)
                
                # Update progress
                progress_bar.progress(20)
                status_text.text("📋 Processing PLANNED data...")
                
                # Use cached processing function
                output_files = cached_extract_and_combine(
                    str(planned_path),
                    str(delivered_path),
                    str(output_dir)
                )
                
                progress_bar.progress(80)
                status_text.text("🔄 Processing complete...")
                
                # Get combined output path
                combined_output = output_files.get('combined')
                
                progress_bar.progress(100)
                status_text.text("✅ Data processing complete!")
                
                # Store results
                st.session_state.workflow_data['combined_file'] = combined_output
                st.session_state.workflow_data['output_dir'] = str(output_dir)
                st.session_state.workflow_data['output_files'] = output_files
                st.session_state.processing_complete[2] = True
                update_stage_status(2, 'completed')
                
                # Show success message
                st.markdown('<div class="success-message">✅ Data processing completed successfully!</div>', unsafe_allow_html=True)
                
                # Display summary with preview
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Files Generated", len(output_files))
                    if 'planned' in output_files:
                        st.caption(f"✅ PLANNED data extracted")
                    if 'delivered' in output_files:
                        st.caption(f"✅ DELIVERED data extracted")
                with col2:
                    if 'combined' in output_files:
                        st.metric("Combined File", "Ready")
                        st.caption(f"✅ Data successfully combined")
                
                # Show preview of combined data
                if combined_output and os.path.exists(combined_output):
                    with st.expander("📊 Preview combined data"):
                        preview_df = load_excel_preview(combined_output, nrows=20)
                        st.dataframe(preview_df, use_container_width=True)
                        st.caption(f"Showing first 20 rows of {len(preview_df.columns)} columns")
                
                time.sleep(1)  # Brief pause for user to see success
                
        except Exception as e:
            st.markdown(f'<div class="error-message">❌ Error during data processing: {str(e)}</div>', unsafe_allow_html=True)
            st.error("Please check your input files and try again.")
    
    if st.session_state.processing_complete.get(2, False):
        if st.button("➡️ Continue to Template Mapping", use_container_width=True):
            st.session_state.current_stage = 3
            st.rerun()

elif st.session_state.current_stage == 3:
    # Stage 3: Template Mapping
    update_stage_status(3, 'current')
    st.markdown('<h2 class="stage-header">🔄 Stage 3: Template Mapping</h2>', unsafe_allow_html=True)
    
    st.info("This stage maps your combined data to the output template using intelligent column matching.")
    
    # Show API key status
    has_api_key = bool(os.getenv("ANTHROPIC_API_KEY"))
    if has_api_key:
        st.success("✅ Anthropic API key configured - Enhanced LLM mapping available")
    else:
        st.warning("⚠️ No API key set - Using rule-based mapping only")
    
    if st.button("🎯 Start Template Mapping", use_container_width=True):
        try:
            with st.spinner("Mapping data to template..."):
                # Create progress placeholders
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Get file paths
                combined_file = st.session_state.workflow_data.get('combined_file')
                template_path = st.session_state.uploaded_files.get("TEMPLATE")
                output_dir = st.session_state.workflow_data.get('output_dir')
                output_file = Path(output_dir) / f"final_mapped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
                progress_bar.progress(20)
                status_text.text("🔍 Analyzing template structure...")
                
                # Use cached mapping function
                result = cached_map_to_template(
                    combined_file,
                    str(template_path),
                    str(output_file)
                )
                
                progress_bar.progress(100)
                status_text.text("✅ Template mapping complete!")
                
                # Store results
                st.session_state.workflow_data['mapped_file'] = str(output_file)
                st.session_state.workflow_data['mapping_result'] = result
                st.session_state.processing_complete[3] = True
                update_stage_status(3, 'completed')
                
                # Show success message
                st.markdown('<div class="success-message">✅ Template mapping completed successfully!</div>', unsafe_allow_html=True)
                
                # Display mapping summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Columns Mapped", f"{result.get('mapped_count', 0)}/{result.get('total_columns', 0)}")
                with col2:
                    st.metric("Coverage", f"{result.get('coverage', 0):.1f}%")
                with col3:
                    st.metric("Rows Written", result.get('rows_written', 0))
                
                # Show unmapped columns if any
                unmapped = result.get('unmapped_columns', [])
                if unmapped:
                    with st.expander(f"⚠️ Unmapped Columns ({len(unmapped)})", expanded=False):
                        st.write(unmapped)
                
                # Preview mapped data
                if output_file and os.path.exists(output_file):
                    with st.expander("📊 Preview mapped template"):
                        preview_df = load_excel_preview(str(output_file), nrows=20)
                        st.dataframe(preview_df, use_container_width=True)
                
        except Exception as e:
            st.markdown(f'<div class="error-message">❌ Error during template mapping: {str(e)}</div>', unsafe_allow_html=True)
            st.error("Please check the error details and try again.")
    
    if st.session_state.processing_complete.get(3, False):
        if st.button("➡️ Continue to Validation", use_container_width=True):
            st.session_state.current_stage = 4
            st.rerun()

elif st.session_state.current_stage == 4:
    # Stage 4: Validation
    update_stage_status(4, 'current')
    st.markdown('<h2 class="stage-header">✅ Stage 4: Validation</h2>', unsafe_allow_html=True)
    
    st.info("This stage validates the accuracy and completeness of your mapped data.")
    
    if st.button("🔍 Run Validation", use_container_width=True):
        try:
            with st.spinner("Validating data..."):
                # Create progress placeholders
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Get file paths
                mapped_file = st.session_state.workflow_data.get('mapped_file')
                combined_file = st.session_state.workflow_data.get('combined_file')
                
                progress_bar.progress(25)
                status_text.text("📊 Loading mapped data...")
                
                # Create workflow wrapper instance
                wrapper = WorkflowWrapper()
                
                progress_bar.progress(50)
                status_text.text("🔍 Checking data accuracy...")
                
                # Run validation
                validation_results = wrapper.validate_data(
                    mapped_file=mapped_file,
                    source_file=combined_file
                )
                
                progress_bar.progress(75)
                status_text.text("📈 Analyzing results...")
                
                # Calculate metrics
                total_checks = validation_results.get('total_checks', 0)
                passed_checks = validation_results.get('passed_checks', 0)
                warnings = validation_results.get('warnings', [])
                errors = validation_results.get('errors', [])
                
                progress_bar.progress(100)
                status_text.text("✅ Validation complete!")
                
                # Store results
                st.session_state.workflow_data['validation_results'] = validation_results
                st.session_state.processing_complete[4] = True
                update_stage_status(4, 'completed')
                
                # Display validation results
                if errors:
                    st.markdown(f'<div class="error-message">❌ Validation found {len(errors)} errors</div>', unsafe_allow_html=True)
                elif warnings:
                    st.markdown(f'<div class="success-message">⚠️ Validation passed with {len(warnings)} warnings</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="success-message">✅ Validation passed - All checks successful!</div>', unsafe_allow_html=True)
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Checks", total_checks)
                with col2:
                    success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                with col3:
                    st.metric("Issues", len(warnings) + len(errors))
                
                # Show detailed results
                if errors:
                    with st.expander(f"❌ Errors ({len(errors)})", expanded=True):
                        for error in errors[:10]:  # Show first 10
                            st.error(error)
                        if len(errors) > 10:
                            st.warning(f"... and {len(errors) - 10} more errors")
                
                if warnings:
                    with st.expander(f"⚠️ Warnings ({len(warnings)})", expanded=False):
                        for warning in warnings[:10]:  # Show first 10
                            st.warning(warning)
                        if len(warnings) > 10:
                            st.info(f"... and {len(warnings) - 10} more warnings")
                
        except Exception as e:
            st.markdown(f'<div class="error-message">❌ Error during validation: {str(e)}</div>', unsafe_allow_html=True)
            st.error("Please check the error details and try again.")
    
    if st.session_state.processing_complete.get(4, False):
        if st.button("➡️ Continue to Results", use_container_width=True):
            st.session_state.current_stage = 5
            update_stage_status(5, 'completed')
            st.rerun()

elif st.session_state.current_stage == 5:
    # Stage 5: Results & Download
    update_stage_status(5, 'current')
    st.markdown('<h2 class="stage-header">📊 Stage 5: Results & Download</h2>', unsafe_allow_html=True)
    
    st.success("🎉 Workflow completed successfully!")
    
    # Summary of results
    st.subheader("📈 Processing Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Files Processed", 
            3,
            help="PLANNED, DELIVERED, and TEMPLATE files"
        )
    
    with col2:
        combined_rows = st.session_state.workflow_data.get('mapping_result', {}).get('rows_written', 0)
        st.metric("Total Rows", combined_rows)
    
    with col3:
        coverage = st.session_state.workflow_data.get('mapping_result', {}).get('coverage', 0)
        st.metric("Mapping Coverage", f"{coverage:.1f}%")
    
    with col4:
        validation_results = st.session_state.workflow_data.get('validation_results', {})
        total_checks = validation_results.get('total_checks', 0)
        passed_checks = validation_results.get('passed_checks', 0)
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 100
        st.metric("Validation Score", f"{success_rate:.1f}%")
    
    st.divider()
    
    # Download section
    st.subheader("📥 Download Results")
    
    mapped_file = st.session_state.workflow_data.get('mapped_file')
    if mapped_file and os.path.exists(mapped_file):
        with open(mapped_file, 'rb') as f:
            file_data = f.read()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("📄 Your populated template is ready for download!")
        with col2:
            st.download_button(
                label="⬇️ Download Excel File",
                data=file_data,
                file_name=f"PCA_Output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    # Reports section
    st.subheader("📋 Detailed Reports")
    
    # Get report files from output directory
    output_dir = Path(st.session_state.workflow_data.get('output_dir', ''))
    if output_dir.exists():
        report_files = list(output_dir.glob("*_REPORT.txt"))
        if report_files:
            tabs = st.tabs([f.stem for f in report_files])
            for tab, report_file in zip(tabs, report_files):
                with tab:
                    try:
                        with open(report_file, 'r') as f:
                            report_content = f.read()
                        st.text_area(
                            "Report Content",
                            value=report_content,
                            height=400,
                            key=f"report_{report_file.stem}"
                        )
                        st.download_button(
                            label=f"⬇️ Download {report_file.name}",
                            data=report_content,
                            file_name=report_file.name,
                            mime="text/plain",
                            key=f"download_{report_file.stem}"
                        )
                    except Exception as e:
                        st.error(f"Error reading report: {e}")
    
    # Final preview of results
    if mapped_file and os.path.exists(mapped_file):
        with st.expander("📊 Preview Final Output", expanded=False):
            try:
                final_df = load_excel_preview(mapped_file, nrows=50)
                st.dataframe(final_df, use_container_width=True)
                st.caption(f"Showing first 50 rows of final output")
            except Exception as e:
                st.error(f"Error loading preview: {e}")
    
    st.divider()
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Start New Process", use_container_width=True):
            # Reset session state
            cleanup_temp_files()
            for key in ['current_stage', 'workflow_data', 'uploaded_files', 'processing_complete', 'file_validation', 'stage_status']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.temp_dir = tempfile.mkdtemp(prefix="pca_automation_")
            st.session_state.current_stage = 1
            st.session_state.stage_status = {1: 'pending', 2: 'pending', 3: 'pending', 4: 'pending', 5: 'pending'}
            st.rerun()
    
    with col2:
        if st.button("📊 View Full Data", use_container_width=True):
            if mapped_file and os.path.exists(mapped_file):
                try:
                    df_full = pd.read_excel(mapped_file)
                    st.subheader("Full Dataset View")
                    st.dataframe(df_full, use_container_width=True)
                    st.caption(f"Total: {len(df_full)} rows × {len(df_full.columns)} columns")
                except Exception as e:
                    st.error(f"Error loading full data: {e}")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>PCA Automation v1.0 | 
    <a href='https://github.com/gramanoid/pca_automation' target='_blank'>GitHub</a> | 
    Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)

# Cleanup on app shutdown
import atexit
atexit.register(cleanup_temp_files)