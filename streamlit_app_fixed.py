"""
PCA Automation - Fixed Streamlit Interface
Fixed version that properly handles stage transitions and download functionality
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
    page_title="PCA Media Plan Automation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.markdown('<h1 style="text-align: center; color: #1f77b4;">📊 PCA Automation</h1>', unsafe_allow_html=True)

# Initialize session state
if 'current_stage' not in st.session_state:
    st.session_state.current_stage = 1
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp(prefix="pca_automation_")
if 'validation_complete' not in st.session_state:
    st.session_state.validation_complete = False

# Sidebar
with st.sidebar:
    st.header("Navigation")
    stages = ["1. Data Upload", "2. Data Processing", "3. Template Mapping", "4. Validation", "5. Results"]
    
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
    
    with col1:
        st.subheader("📋 PLANNED File")
        planned_file = st.file_uploader(
            "Upload PLANNED Excel file",
            type=['xlsx', 'xls'],
            key="planned_uploader"
        )
        if planned_file:
            st.success("✅ PLANNED file uploaded")
            # Save file
            file_path = Path(st.session_state.temp_dir) / f"PLANNED_{planned_file.name}"
            with open(file_path, "wb") as f:
                f.write(planned_file.getbuffer())
            st.session_state.uploaded_files['PLANNED'] = str(file_path)
    
    with col2:
        st.subheader("📈 DELIVERED File")
        delivered_file = st.file_uploader(
            "Upload DELIVERED Excel file",
            type=['xlsx', 'xls'],
            key="delivered_uploader"
        )
        if delivered_file:
            st.success("✅ DELIVERED file uploaded")
            # Save file
            file_path = Path(st.session_state.temp_dir) / f"DELIVERED_{delivered_file.name}"
            with open(file_path, "wb") as f:
                f.write(delivered_file.getbuffer())
            st.session_state.uploaded_files['DELIVERED'] = str(file_path)
    
    with col3:
        st.subheader("📄 OUTPUT TEMPLATE")
        template_file = st.file_uploader(
            "Upload OUTPUT TEMPLATE Excel file",
            type=['xlsx', 'xls'],
            key="template_uploader"
        )
        if template_file:
            st.success("✅ TEMPLATE file uploaded")
            # Save file
            file_path = Path(st.session_state.temp_dir) / f"TEMPLATE_{template_file.name}"
            with open(file_path, "wb") as f:
                f.write(template_file.getbuffer())
            st.session_state.uploaded_files['TEMPLATE'] = str(file_path)
    
    # Check if all files are uploaded
    if len(st.session_state.uploaded_files) == 3:
        st.success("✅ All files uploaded successfully!")
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
    
    if st.button("🚀 Start Data Processing", type="primary", use_container_width=True):
        with st.spinner("Processing data..."):
            # Import workflow wrapper only when needed
            try:
                from production_workflow.utils.workflow_wrapper import WorkflowWrapper
                wrapper = WorkflowWrapper()
                
                # Get file paths
                planned_path = st.session_state.uploaded_files.get("PLANNED")
                delivered_path = st.session_state.uploaded_files.get("DELIVERED")
                output_dir = Path(st.session_state.temp_dir) / "output"
                output_dir.mkdir(exist_ok=True)
                
                # Process data
                output_files = wrapper.extract_and_combine_data(
                    planned_path=planned_path,
                    delivered_path=delivered_path,
                    output_dir=str(output_dir),
                    combine=True
                )
                
                st.session_state['combined_file'] = output_files.get('combined')
                st.session_state['output_dir'] = str(output_dir)
                
                st.success("✅ Data processing completed successfully!")
                time.sleep(1)
                st.session_state.current_stage = 3
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error during processing: {str(e)}")
                if st.session_state.get('debug_mode'):
                    st.exception(e)

elif st.session_state.current_stage == 3:
    st.header("Stage 3: Template Mapping")
    
    st.info("Map your combined data to the output template.")
    
    if st.button("🎯 Start Template Mapping", type="primary", use_container_width=True):
        with st.spinner("Mapping data to template..."):
            try:
                from production_workflow.utils.workflow_wrapper import WorkflowWrapper
                wrapper = WorkflowWrapper()
                
                # Get file paths
                combined_file = st.session_state.get('combined_file')
                template_path = st.session_state.uploaded_files.get("TEMPLATE")
                output_dir = st.session_state.get('output_dir')
                output_file = Path(output_dir) / f"final_mapped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
                # Map to template
                result = wrapper.map_to_template(
                    input_file=combined_file,
                    template_file=template_path,
                    output_file=str(output_file)
                )
                
                st.session_state['mapped_file'] = str(output_file)
                st.session_state['mapping_result'] = result
                
                st.success("✅ Template mapping completed successfully!")
                st.metric("Columns Mapped", f"{result.get('mapped_count', 0)}/{result.get('total_columns', 0)}")
                
                time.sleep(1)
                st.session_state.current_stage = 4
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error during mapping: {str(e)}")
                if st.session_state.get('debug_mode'):
                    st.exception(e)

elif st.session_state.current_stage == 4:
    st.header("Stage 4: Validation & Download")
    
    # Check if validation has been completed
    if not st.session_state.get('validation_complete', False):
        st.info("Validate the accuracy and completeness of your mapped data.")
        
        if st.button("🔍 Run Validation", type="primary", use_container_width=True):
            with st.spinner("Validating data..."):
                try:
                    from production_workflow.utils.workflow_wrapper import WorkflowWrapper
                    wrapper = WorkflowWrapper()
                    
                    # Get file paths
                    mapped_file = st.session_state.get('mapped_file')
                    combined_file = st.session_state.get('combined_file')
                    
                    # Run validation
                    validation_results = wrapper.validate_data(
                        mapped_file=mapped_file,
                        source_file=combined_file
                    )
                    
                    st.session_state['validation_results'] = validation_results
                    
                    # Display results
                    errors = validation_results.get('errors', [])
                    warnings = validation_results.get('warnings', [])
                    
                    if errors:
                        st.error(f"❌ Found {len(errors)} errors")
                    elif warnings:
                        st.warning(f"⚠️ Found {len(warnings)} warnings")
                    else:
                        st.success("✅ Validation passed!")
                    
                    # Mark validation as complete
                    st.session_state.validation_complete = True
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error during validation: {str(e)}")
                    if st.session_state.get('debug_mode'):
                        st.exception(e)
    
    else:
        # Validation is complete, show results and download
        st.success("🎉 Workflow completed successfully!")
        
        validation_results = st.session_state.get('validation_results', {})
        
        # Display validation summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Checks", validation_results.get('total_checks', 0))
        with col2:
            st.metric("Errors", len(validation_results.get('errors', [])))
        with col3:
            st.metric("Warnings", len(validation_results.get('warnings', [])))
        
        st.divider()
        
        # Download section
        st.subheader("📥 Download Your Results")
        
        mapped_file = st.session_state.get('mapped_file')
        if mapped_file and os.path.exists(mapped_file):
            with open(mapped_file, 'rb') as f:
                file_data = f.read()
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info("Your populated template is ready for download!")
            with col2:
                st.download_button(
                    label="⬇️ Download Excel",
                    data=file_data,
                    file_name=f"PCA_Output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        st.divider()
        
        # Option to start new process
        if st.button("🔄 Start New Process", type="primary", use_container_width=True):
            # Reset session state
            for key in ['current_stage', 'uploaded_files', 'combined_file', 'output_dir', 
                       'mapped_file', 'mapping_result', 'validation_results', 'validation_complete']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_stage = 1
            st.rerun()
        
        # Option to go to detailed results (stage 5)
        if st.button("📊 View Detailed Results", use_container_width=True):
            st.session_state.current_stage = 5
            st.rerun()

elif st.session_state.current_stage == 5:
    st.header("Stage 5: Detailed Results")
    
    st.info("Detailed analysis and reports for your processed data.")
    
    # Get results
    validation_results = st.session_state.get('validation_results', {})
    mapping_result = st.session_state.get('mapping_result', {})
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Summary", "⚠️ Issues", "📄 Reports"])
    
    with tab1:
        st.subheader("Processing Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Files Processed", 3)
        with col2:
            st.metric("Rows Processed", mapping_result.get('rows_written', 0))
        with col3:
            st.metric("Mapping Coverage", f"{mapping_result.get('coverage', 0):.1f}%")
        with col4:
            total_checks = validation_results.get('total_checks', 0)
            passed_checks = validation_results.get('passed_checks', 0)
            success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 100
            st.metric("Validation Score", f"{success_rate:.1f}%")
    
    with tab2:
        st.subheader("Validation Issues")
        
        errors = validation_results.get('errors', [])
        warnings = validation_results.get('warnings', [])
        
        if errors:
            st.error(f"Found {len(errors)} errors:")
            for error in errors:
                st.write(f"• {error}")
        else:
            st.success("No errors found!")
        
        if warnings:
            st.warning(f"Found {len(warnings)} warnings:")
            for warning in warnings:
                st.write(f"• {warning}")
        else:
            st.success("No warnings found!")
    
    with tab3:
        st.subheader("Download Reports")
        
        # Get report files from output directory
        output_dir = Path(st.session_state.get('output_dir', ''))
        if output_dir.exists():
            report_files = list(output_dir.glob("*_REPORT.txt"))
            if report_files:
                for report_file in report_files:
                    with st.expander(f"📄 {report_file.stem}"):
                        try:
                            with open(report_file, 'r') as f:
                                report_content = f.read()
                            st.text_area("Report content", report_content, height=200)
                            st.download_button(
                                label=f"⬇️ Download {report_file.name}",
                                data=report_content,
                                file_name=report_file.name,
                                mime="text/plain"
                            )
                        except Exception as e:
                            st.error(f"Error reading report: {e}")
            else:
                st.info("No report files generated.")
    
    st.divider()
    
    # Navigation options
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Download", use_container_width=True):
            st.session_state.current_stage = 4
            st.rerun()
    
    with col2:
        if st.button("🔄 Start New Process", type="primary", use_container_width=True):
            # Reset session state
            for key in ['current_stage', 'uploaded_files', 'combined_file', 'output_dir', 
                       'mapped_file', 'mapping_result', 'validation_results', 'validation_complete']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_stage = 1
            st.rerun()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #6c757d;'>
    PCA Automation v2.0 | 
    <a href='https://github.com/gramanoid/pca_automation' target='_blank'>GitHub</a>
</div>
""", unsafe_allow_html=True)