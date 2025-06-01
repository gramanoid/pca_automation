"""
Diagnostic app to test which features can be imported on Streamlit Cloud
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

st.set_page_config(page_title="PCA Diagnostic Tool", page_icon="🔍", layout="wide")

st.title("🔍 PCA Automation - Import Diagnostic Tool")

st.info("This tool tests which features can be successfully imported in the Streamlit Cloud environment.")

# Test imports
st.header("Import Test Results")

def test_import(module_path, display_name):
    """Test if a module can be imported and display result"""
    col1, col2, col3 = st.columns([3, 1, 4])
    
    with col1:
        st.write(f"**{display_name}**")
    
    try:
        if module_path.startswith('ui_components.'):
            parts = module_path.split('.')
            if len(parts) == 3:  # ui_components.module.Class
                module = __import__(f"{parts[0]}.{parts[1]}", fromlist=[parts[2]])
                getattr(module, parts[2])
            else:  # ui_components.module
                __import__(module_path)
        else:
            __import__(module_path)
        
        with col2:
            st.success("✅ Success")
        with col3:
            st.write("Import successful")
        return True
    except ImportError as e:
        with col2:
            st.error("❌ Failed")
        with col3:
            st.code(str(e), language="text")
        return False
    except Exception as e:
        with col2:
            st.error("❌ Error")
        with col3:
            st.code(f"{type(e).__name__}: {str(e)}", language="text")
        return False

# Core dependencies
st.subheader("1. Core Dependencies")
test_import("pandas", "Pandas")
test_import("numpy", "NumPy")
test_import("openpyxl", "OpenPyXL")
test_import("plotly", "Plotly")
test_import("plotly.graph_objects", "Plotly Graph Objects")
test_import("plotly.express", "Plotly Express")

# Production workflow modules
st.subheader("2. Production Workflow Modules")
test_import("production_workflow.01_data_extraction.extract_and_combine_data", "Data Extraction")
test_import("production_workflow.02_data_processing.market_mapper", "Market Mapper")
test_import("production_workflow.03_template_mapping.map_to_template", "Template Mapping")
test_import("production_workflow.04_validation.validate_accuracy", "Validation")

# UI Components
st.subheader("3. UI Components")
components_to_test = [
    ("ui_components.file_upload", "File Upload Base"),
    ("ui_components.file_upload.FileUploadComponent", "File Upload Component"),
    ("ui_components.progress_display", "Progress Display Base"),
    ("ui_components.progress_display.ProgressDisplay", "Progress Display Component"),
    ("ui_components.smart_suggestions", "Smart Suggestions Base"),
    ("ui_components.smart_suggestions.SmartSuggestions", "Smart Suggestions Component"),
    ("ui_components.error_recovery", "Error Recovery Base"),
    ("ui_components.error_recovery.ErrorRecoveryHandler", "Error Recovery Handler"),
    ("ui_components.validation_dashboard", "Validation Dashboard Base"),
    ("ui_components.validation_dashboard_enhanced", "Enhanced Validation Base"),
    ("ui_components.validation_dashboard_enhanced.EnhancedValidationDashboard", "Enhanced Validation Component"),
]

results = {}
for module_path, display_name in components_to_test:
    results[module_path] = test_import(module_path, display_name)

# Summary
st.header("Summary")

col1, col2 = st.columns(2)

with col1:
    successful = sum(1 for v in results.values() if v)
    st.metric("Successful Imports", f"{successful}/{len(results)}")

with col2:
    failed = sum(1 for v in results.values() if not v)
    st.metric("Failed Imports", f"{failed}/{len(results)}")

# Environment info
st.header("Environment Information")
col1, col2, col3 = st.columns(3)

with col1:
    st.write("**Python Version:**")
    st.code(sys.version)

with col2:
    st.write("**Streamlit Version:**")
    st.code(st.__version__)

with col3:
    st.write("**Working Directory:**")
    st.code(str(Path.cwd()))

# Python path
st.subheader("Python Path")
for i, path in enumerate(sys.path[:5]):
    st.code(f"{i}: {path}")

# Recommendations
st.header("Recommendations")

if failed > 0:
    st.warning("""
    Some imports failed. Common causes:
    1. Missing dependencies in requirements.txt
    2. Import order issues
    3. Circular imports
    4. Missing __init__.py files
    """)
else:
    st.success("All imports successful! The app should work correctly on Streamlit Cloud.")

# File structure check
st.header("File Structure Check")

ui_components_path = project_root / "ui_components"
if ui_components_path.exists():
    st.success(f"✅ ui_components directory exists")
    
    # Check for __init__.py
    init_file = ui_components_path / "__init__.py"
    if init_file.exists():
        st.success(f"✅ ui_components/__init__.py exists")
    else:
        st.error(f"❌ ui_components/__init__.py missing")
    
    # List Python files
    with st.expander("UI Components Files"):
        py_files = list(ui_components_path.glob("*.py"))
        for file in sorted(py_files):
            st.write(f"- {file.name}")
else:
    st.error(f"❌ ui_components directory not found")