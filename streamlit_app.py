"""
Media Plan to Raw Data Automation - Streamlit Web Interface
A user-friendly interface for the Planned vs Delivered automation workflow.
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

# Load configuration
@st.cache_data
def load_config():
    """Load configuration from config files"""
    config = {}
    config_path = project_root / "config" / "config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    return config

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

# Header
st.markdown('<h1 class="main-header">📊 Media Plan to Raw Data Automation</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🧭 Navigation")
    
    # Stage selection
    stages = {
        1: "📁 Data Upload",
        2: "⚙️ Data Processing", 
        3: "🔄 Template Mapping",
        4: "✅ Validation",
        5: "📊 Results & Download"
    }
    
    for stage_num, stage_name in stages.items():
        if st.button(
            stage_name, 
            key=f"stage_{stage_num}",
            disabled=stage_num > 1 and not st.session_state.processing_complete.get(stage_num - 1, False),
            use_container_width=True
        ):
            st.session_state.current_stage = stage_num
    
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
            save_uploaded_file(planned_file, "PLANNED")
            st.success(f"✅ Uploaded: {planned_file.name}")
    
    with col2:
        st.subheader("📈 DELIVERED File")
        delivered_file = st.file_uploader(
            "Upload DELIVERED Excel file",
            type=['xlsx', 'xls'],
            key="delivered_uploader",
            help="Platform data exports (e.g., DELIVERED_INPUT_TEMPLATE_*.xlsx)"
        )
        if delivered_file:
            save_uploaded_file(delivered_file, "DELIVERED")
            st.success(f"✅ Uploaded: {delivered_file.name}")
    
    with col3:
        st.subheader("📄 OUTPUT TEMPLATE")
        template_file = st.file_uploader(
            "Upload OUTPUT TEMPLATE Excel file",
            type=['xlsx', 'xls'],
            key="template_uploader",
            help="Empty template to fill (e.g., OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx)"
        )
        if template_file:
            save_uploaded_file(template_file, "TEMPLATE")
            st.success(f"✅ Uploaded: {template_file.name}")
    
    # Check if all files are uploaded
    all_files_uploaded = all(key in st.session_state.uploaded_files for key in ["PLANNED", "DELIVERED", "TEMPLATE"])
    
    if all_files_uploaded:
        st.markdown('<div class="success-message">✅ All required files uploaded! You can proceed to Data Processing.</div>', unsafe_allow_html=True)
        st.session_state.processing_complete[1] = True
        
        if st.button("➡️ Continue to Data Processing", type="primary", use_container_width=True):
            st.session_state.current_stage = 2
            st.rerun()
    else:
        missing_files = [key for key in ["PLANNED", "DELIVERED", "TEMPLATE"] if key not in st.session_state.uploaded_files]
        st.warning(f"⚠️ Please upload all required files. Missing: {', '.join(missing_files)}")

elif st.session_state.current_stage == 2:
    # Stage 2: Data Processing
    st.markdown('<h2 class="stage-header">⚙️ Stage 2: Data Processing</h2>', unsafe_allow_html=True)
    
    st.info("This stage extracts data from your uploaded files and combines them for template mapping.")
    
    if st.button("🚀 Start Data Processing", type="primary", use_container_width=True):
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
                
                # Create workflow wrapper instance
                wrapper = WorkflowWrapper()
                
                # Process and combine data
                output_files = wrapper.extract_and_combine_data(
                    planned_path=str(planned_path),
                    delivered_path=str(delivered_path),
                    output_dir=str(output_dir),
                    combine=True
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
                st.session_state.processing_complete[2] = True
                
                # Show success message
                st.markdown('<div class="success-message">✅ Data processing completed successfully!</div>', unsafe_allow_html=True)
                
                # Display summary
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Planned Rows", wrapper.metrics.get('planned_rows', 0))
                    st.metric("Delivered Rows", wrapper.metrics.get('delivered_rows', 0))
                with col2:
                    st.metric("Combined Rows", wrapper.metrics.get('combined_rows', 0))
                    st.metric("Files Generated", len(output_files))
                
                time.sleep(1)  # Brief pause for user to see success
                
        except Exception as e:
            st.markdown(f'<div class="error-message">❌ Error during data processing: {str(e)}</div>', unsafe_allow_html=True)
            st.error("Please check your input files and try again.")
    
    if st.session_state.processing_complete.get(2, False):
        if st.button("➡️ Continue to Template Mapping", type="primary", use_container_width=True):
            st.session_state.current_stage = 3
            st.rerun()

elif st.session_state.current_stage == 3:
    # Stage 3: Template Mapping
    st.markdown('<h2 class="stage-header">🔄 Stage 3: Template Mapping</h2>', unsafe_allow_html=True)
    
    st.info("This stage maps your combined data to the output template using intelligent column matching.")
    
    # Show API key status
    has_api_key = bool(os.getenv("ANTHROPIC_API_KEY"))
    if has_api_key:
        st.success("✅ Anthropic API key configured - Enhanced LLM mapping available")
    else:
        st.warning("⚠️ No API key set - Using rule-based mapping only")
    
    if st.button("🎯 Start Template Mapping", type="primary", use_container_width=True):
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
                
                # Create workflow wrapper instance
                wrapper = WorkflowWrapper()
                
                progress_bar.progress(40)
                status_text.text("🔄 Mapping data to template...")
                
                # Perform mapping
                result = wrapper.map_to_template(
                    input_file=combined_file,
                    template_file=str(template_path),
                    output_file=str(output_file)
                )
                
                progress_bar.progress(100)
                status_text.text("✅ Template mapping complete!")
                
                # Store results
                st.session_state.workflow_data['mapped_file'] = str(output_file)
                st.session_state.workflow_data['mapping_result'] = result
                st.session_state.processing_complete[3] = True
                
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
                
        except Exception as e:
            st.markdown(f'<div class="error-message">❌ Error during template mapping: {str(e)}</div>', unsafe_allow_html=True)
            st.error("Please check the error details and try again.")
    
    if st.session_state.processing_complete.get(3, False):
        if st.button("➡️ Continue to Validation", type="primary", use_container_width=True):
            st.session_state.current_stage = 4
            st.rerun()

elif st.session_state.current_stage == 4:
    # Stage 4: Validation
    st.markdown('<h2 class="stage-header">✅ Stage 4: Validation</h2>', unsafe_allow_html=True)
    
    st.info("This stage validates the accuracy and completeness of your mapped data.")
    
    if st.button("🔍 Run Validation", type="primary", use_container_width=True):
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
        if st.button("➡️ Continue to Results", type="primary", use_container_width=True):
            st.session_state.current_stage = 5
            st.rerun()

elif st.session_state.current_stage == 5:
    # Stage 5: Results & Download
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
    
    st.divider()
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Start New Process", type="primary", use_container_width=True):
            # Reset session state
            cleanup_temp_files()
            for key in ['current_stage', 'workflow_data', 'uploaded_files', 'processing_complete']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.temp_dir = tempfile.mkdtemp(prefix="pca_automation_")
            st.rerun()
    
    with col2:
        if st.button("📊 View Data Preview", use_container_width=True):
            if mapped_file and os.path.exists(mapped_file):
                try:
                    df_preview = pd.read_excel(mapped_file, nrows=100)
                    st.subheader("Data Preview (First 100 rows)")
                    st.dataframe(df_preview, use_container_width=True)
                except Exception as e:
                    st.error(f"Error loading preview: {e}")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>Media Plan to Raw Data Automation v1.0 | 
    <a href='https://github.com/gramanoid/pca_automation' target='_blank'>GitHub</a> | 
    Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)

# Cleanup on app shutdown
import atexit
atexit.register(cleanup_temp_files)