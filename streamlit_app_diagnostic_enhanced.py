"""
Enhanced Diagnostic Tool for PCA Automation
Tests imports, file operations, and feature compatibility
"""

import streamlit as st
import sys
import os
import traceback
import importlib
import tempfile
from pathlib import Path
from datetime import datetime
import json

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

st.set_page_config(page_title="PCA Diagnostic Tool", page_icon="🔍", layout="wide")

st.title("🔍 PCA Automation - Enhanced Diagnostic Tool")

# Sidebar for diagnostic options
with st.sidebar:
    st.header("Diagnostic Options")
    
    diagnostic_mode = st.selectbox(
        "Select Diagnostic Mode",
        ["Import Tests", "File System Tests", "Feature Tests", "Performance Tests", "Full Diagnostic"]
    )
    
    st.divider()
    
    # Export options
    if st.button("Export Diagnostic Report"):
        st.session_state['export_report'] = True

# Initialize session state
if 'test_results' not in st.session_state:
    st.session_state.test_results = {}

def test_import_with_details(module_path, display_name):
    """Enhanced import test with detailed error information"""
    result = {
        'name': display_name,
        'module': module_path,
        'success': False,
        'error': None,
        'error_type': None,
        'traceback': None,
        'timestamp': datetime.now().isoformat()
    }
    
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
        
        result['success'] = True
        return result
        
    except ImportError as e:
        result['error'] = str(e)
        result['error_type'] = 'ImportError'
        result['traceback'] = traceback.format_exc()
        return result
        
    except Exception as e:
        result['error'] = str(e)
        result['error_type'] = type(e).__name__
        result['traceback'] = traceback.format_exc()
        return result

def run_import_tests():
    """Run comprehensive import tests"""
    st.header("Import Diagnostic Tests")
    
    test_categories = {
        "Core Dependencies": [
            ("pandas", "Pandas"),
            ("numpy", "NumPy"),
            ("openpyxl", "OpenPyXL"),
            ("plotly", "Plotly"),
            ("plotly.graph_objects", "Plotly Graph Objects"),
            ("plotly.express", "Plotly Express"),
            ("streamlit", "Streamlit"),
            ("anthropic", "Anthropic (Claude API)"),
            ("jsonschema", "JSON Schema"),
        ],
        "Production Workflow": [
            ("production_workflow", "Production Workflow Base"),
            ("production_workflow.01_data_extraction.extract_and_combine_data", "Data Extraction"),
            ("production_workflow.02_data_processing.market_mapper", "Market Mapper"),
            ("production_workflow.03_template_mapping.map_to_template", "Template Mapping"),
            ("production_workflow.04_validation.validate_accuracy", "Validation"),
            ("production_workflow.05_monitoring.monitor_performance", "Performance Monitor"),
        ],
        "UI Components": [
            ("ui_components", "UI Components Base"),
            ("ui_components.file_upload", "File Upload Module"),
            ("ui_components.file_upload.FileUploadComponent", "File Upload Component"),
            ("ui_components.progress_display", "Progress Display Module"),
            ("ui_components.progress_display.ProgressDisplay", "Progress Display Component"),
            ("ui_components.smart_suggestions", "Smart Suggestions Module"),
            ("ui_components.smart_suggestions.SmartSuggestions", "Smart Suggestions Component"),
            ("ui_components.error_recovery", "Error Recovery Module"),
            ("ui_components.error_recovery.ErrorRecoveryHandler", "Error Recovery Handler"),
            ("ui_components.validation_dashboard_enhanced", "Enhanced Validation Module"),
            ("ui_components.validation_dashboard_enhanced.EnhancedValidationDashboard", "Enhanced Validation Dashboard"),
        ]
    }
    
    all_results = {}
    
    for category, tests in test_categories.items():
        st.subheader(f"📦 {category}")
        
        category_results = []
        
        for module_path, display_name in tests:
            col1, col2, col3 = st.columns([3, 1, 6])
            
            result = test_import_with_details(module_path, display_name)
            category_results.append(result)
            
            with col1:
                st.write(f"**{display_name}**")
            
            with col2:
                if result['success']:
                    st.success("✅ Pass")
                else:
                    st.error("❌ Fail")
            
            with col3:
                if not result['success']:
                    with st.expander("Error Details"):
                        st.code(result['error'], language="text")
                        if st.checkbox(f"Show traceback for {display_name}", key=f"tb_{module_path}"):
                            st.code(result['traceback'], language="python")
                else:
                    st.write("Import successful")
        
        all_results[category] = category_results
        
        # Category summary
        success_count = sum(1 for r in category_results if r['success'])
        total_count = len(category_results)
        
        if success_count == total_count:
            st.success(f"✅ All {total_count} imports successful")
        else:
            st.warning(f"⚠️ {success_count}/{total_count} imports successful")
    
    return all_results

def run_file_system_tests():
    """Test file system operations and permissions"""
    st.header("File System Diagnostic Tests")
    
    tests = []
    
    # Test 1: Check working directory
    st.subheader("Working Directory")
    cwd = Path.cwd()
    st.code(str(cwd))
    tests.append({"test": "Working Directory", "result": str(cwd), "success": True})
    
    # Test 2: Check if we can create temp files
    st.subheader("Temporary File Creation")
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("test")
            tmp_path = tmp.name
        os.unlink(tmp_path)
        st.success("✅ Can create temporary files")
        tests.append({"test": "Temp File Creation", "result": "Success", "success": True})
    except Exception as e:
        st.error(f"❌ Cannot create temporary files: {e}")
        tests.append({"test": "Temp File Creation", "result": str(e), "success": False})
    
    # Test 3: Check project structure
    st.subheader("Project Structure")
    required_dirs = [
        "production_workflow",
        "ui_components",
        "config",
        "input",
        "output",
        "documentation"
    ]
    
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            st.success(f"✅ {dir_name}/ exists")
            tests.append({"test": f"{dir_name} directory", "result": "Exists", "success": True})
        else:
            st.error(f"❌ {dir_name}/ missing")
            tests.append({"test": f"{dir_name} directory", "result": "Missing", "success": False})
    
    # Test 4: Check critical files
    st.subheader("Critical Files")
    critical_files = [
        "requirements.txt",
        "config.json",
        "streamlit_app.py",
        "ui_components/__init__.py"
    ]
    
    for file_name in critical_files:
        file_path = project_root / file_name
        if file_path.exists():
            st.success(f"✅ {file_name} exists")
            tests.append({"test": f"{file_name}", "result": "Exists", "success": True})
        else:
            st.error(f"❌ {file_name} missing")
            tests.append({"test": f"{file_name}", "result": "Missing", "success": False})
    
    return tests

def run_feature_tests():
    """Test specific feature functionality"""
    st.header("Feature Functionality Tests")
    
    feature_tests = []
    
    # Test 1: Session State
    st.subheader("Session State Management")
    try:
        if 'test_value' not in st.session_state:
            st.session_state.test_value = 0
        st.session_state.test_value += 1
        st.success(f"✅ Session state working (counter: {st.session_state.test_value})")
        feature_tests.append({"test": "Session State", "result": "Working", "success": True})
    except Exception as e:
        st.error(f"❌ Session state error: {e}")
        feature_tests.append({"test": "Session State", "result": str(e), "success": False})
    
    # Test 2: File Upload Widget
    st.subheader("File Upload Widget")
    try:
        uploaded_file = st.file_uploader("Test file upload", type=['xlsx', 'xls'])
        if uploaded_file:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
        else:
            st.info("📎 No file uploaded yet")
        feature_tests.append({"test": "File Upload Widget", "result": "Working", "success": True})
    except Exception as e:
        st.error(f"❌ File upload error: {e}")
        feature_tests.append({"test": "File Upload Widget", "result": str(e), "success": False})
    
    # Test 3: Data Processing
    st.subheader("Data Processing Capability")
    try:
        import pandas as pd
        test_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        st.dataframe(test_data)
        st.success("✅ Can create and display DataFrames")
        feature_tests.append({"test": "DataFrame Display", "result": "Working", "success": True})
    except Exception as e:
        st.error(f"❌ DataFrame error: {e}")
        feature_tests.append({"test": "DataFrame Display", "result": str(e), "success": False})
    
    # Test 4: Plotly Charts
    st.subheader("Plotly Visualization")
    try:
        import plotly.graph_objects as go
        fig = go.Figure(data=[go.Bar(x=['A', 'B', 'C'], y=[1, 2, 3])])
        st.plotly_chart(fig)
        st.success("✅ Plotly charts working")
        feature_tests.append({"test": "Plotly Charts", "result": "Working", "success": True})
    except Exception as e:
        st.error(f"❌ Plotly error: {e}")
        feature_tests.append({"test": "Plotly Charts", "result": str(e), "success": False})
    
    return feature_tests

def run_performance_tests():
    """Test performance and resource limits"""
    st.header("Performance and Resource Tests")
    
    perf_tests = []
    
    # Test 1: Memory availability
    st.subheader("Memory Information")
    try:
        import psutil
        memory = psutil.virtual_memory()
        st.metric("Total Memory", f"{memory.total / (1024**3):.2f} GB")
        st.metric("Available Memory", f"{memory.available / (1024**3):.2f} GB")
        st.metric("Memory Usage", f"{memory.percent}%")
        perf_tests.append({"test": "Memory Check", "result": f"{memory.percent}% used", "success": True})
    except Exception as e:
        st.error(f"❌ Cannot check memory: {e}")
        perf_tests.append({"test": "Memory Check", "result": str(e), "success": False})
    
    # Test 2: CPU information
    st.subheader("CPU Information")
    try:
        import platform
        st.write(f"**Platform:** {platform.platform()}")
        st.write(f"**Processor:** {platform.processor()}")
        st.write(f"**Python Version:** {platform.python_version()}")
        perf_tests.append({"test": "CPU Info", "result": platform.platform(), "success": True})
    except Exception as e:
        st.error(f"❌ Cannot check CPU: {e}")
        perf_tests.append({"test": "CPU Info", "result": str(e), "success": False})
    
    return perf_tests

# Main diagnostic logic
if diagnostic_mode == "Import Tests":
    results = run_import_tests()
    st.session_state.test_results['imports'] = results

elif diagnostic_mode == "File System Tests":
    results = run_file_system_tests()
    st.session_state.test_results['filesystem'] = results

elif diagnostic_mode == "Feature Tests":
    results = run_feature_tests()
    st.session_state.test_results['features'] = results

elif diagnostic_mode == "Performance Tests":
    results = run_performance_tests()
    st.session_state.test_results['performance'] = results

elif diagnostic_mode == "Full Diagnostic":
    st.info("Running all diagnostic tests...")
    
    with st.expander("Import Tests", expanded=True):
        st.session_state.test_results['imports'] = run_import_tests()
    
    with st.expander("File System Tests", expanded=True):
        st.session_state.test_results['filesystem'] = run_file_system_tests()
    
    with st.expander("Feature Tests", expanded=True):
        st.session_state.test_results['features'] = run_feature_tests()
    
    with st.expander("Performance Tests", expanded=True):
        st.session_state.test_results['performance'] = run_performance_tests()

# Export functionality
if st.session_state.get('export_report', False):
    st.header("Diagnostic Report")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'platform': sys.platform,
        'python_version': sys.version,
        'streamlit_version': st.__version__,
        'working_directory': str(Path.cwd()),
        'test_results': st.session_state.test_results
    }
    
    # Display as JSON
    st.json(report)
    
    # Download button
    st.download_button(
        label="Download Diagnostic Report",
        data=json.dumps(report, indent=2),
        file_name=f"pca_diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )
    
    st.session_state['export_report'] = False

# Summary and Recommendations
st.header("Summary and Recommendations")

# Calculate overall health
if st.session_state.test_results:
    total_tests = 0
    successful_tests = 0
    
    for category, results in st.session_state.test_results.items():
        if isinstance(results, dict):
            for subcategory, tests in results.items():
                if isinstance(tests, list):
                    total_tests += len(tests)
                    successful_tests += sum(1 for t in tests if t.get('success', False))
        elif isinstance(results, list):
            total_tests += len(results)
            successful_tests += sum(1 for t in results if t.get('success', False))
    
    if total_tests > 0:
        health_score = (successful_tests / total_tests) * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tests", total_tests)
        with col2:
            st.metric("Successful", successful_tests)
        with col3:
            st.metric("Health Score", f"{health_score:.1f}%")
        
        if health_score == 100:
            st.success("🎉 All tests passed! The application should work correctly.")
        elif health_score >= 80:
            st.warning("⚠️ Most tests passed. Some features may have issues.")
        else:
            st.error("❌ Significant issues detected. Review failed tests above.")
        
        # Specific recommendations
        st.subheader("Recommendations")
        
        if 'imports' in st.session_state.test_results:
            failed_imports = []
            for category, tests in st.session_state.test_results['imports'].items():
                for test in tests:
                    if not test['success']:
                        failed_imports.append(test['module'])
            
            if failed_imports:
                st.warning("**Failed Imports:**")
                for imp in failed_imports:
                    st.write(f"- {imp}")
                st.info("Check requirements.txt and ensure all dependencies are installed.")
else:
    st.info("Run diagnostic tests to see recommendations.")