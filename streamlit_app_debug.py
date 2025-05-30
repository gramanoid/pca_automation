"""
Debug version of Streamlit app to test basic functionality
"""

import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

st.set_page_config(
    page_title="PCA Media Plan Automation - Debug",
    page_icon="📊",
    layout="wide"
)

st.title("PCA Automation - Debug Mode")

# Test basic imports
st.header("Testing Imports")

try:
    from production_workflow.utils.workflow_wrapper import WorkflowWrapper
    st.success("✅ WorkflowWrapper imported successfully")
except Exception as e:
    st.error(f"❌ WorkflowWrapper import failed: {str(e)}")

# Test individual UI components
st.header("Testing UI Components")

components_to_test = [
    "FileUploadComponent",
    "ProgressDisplay",
    "ValidationDashboard",
    "ConfigSidebar",
    "MarkerValidationComponent",
    "ConfigPersistence",
    "ReportExporter",
    "PerformanceMonitor",
    "EnhancedDashboard",
    "SmartSuggestions"
]

for component_name in components_to_test:
    try:
        exec(f"from ui_components import {component_name}")
        st.success(f"✅ {component_name} imported successfully")
    except Exception as e:
        st.error(f"❌ {component_name} import failed: {str(e)}")

# Test styles import
try:
    from styles import apply_theme
    st.success("✅ Styles imported successfully")
except Exception as e:
    st.error(f"❌ Styles import failed: {str(e)}")

# Test file upload functionality
st.header("Testing File Upload")

uploaded_file = st.file_uploader(
    "Upload a test Excel file",
    type=['xlsx', 'xls'],
    key="test_uploader"
)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=0, nrows=5)
        st.success("✅ File read successfully")
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ File read failed: {str(e)}")

# Show Python version and packages
st.header("Environment Info")
st.write(f"Python version: {sys.version}")
st.write(f"Streamlit version: {st.__version__}")

# Show session state
st.header("Session State")
st.json(dict(st.session_state))