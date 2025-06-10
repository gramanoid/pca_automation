"""
PCA Automation - Streamlit Web Interface
Supports simple, gradual, and full versions based on environment settings
"""

import os

# Check which version to use
APP_VERSION = os.getenv("APP_VERSION", "interactive").lower()

if APP_VERSION == "simple":
    # Import and run the simple version (most stable)
    exec(open("streamlit_app_simple.py", encoding='utf-8').read())
elif APP_VERSION == "fixed":
    # Import and run the fixed version (default - fixes stage 5 issue)
    exec(open("streamlit_app_fixed.py", encoding='utf-8').read())
elif APP_VERSION == "interactive":
    # Import and run the interactive version (feature selection)
    exec(open("streamlit_app_interactive.py", encoding='utf-8').read())
elif APP_VERSION == "gradual":
    # Import and run the gradual enhancement version
    exec(open("streamlit_app_gradual.py", encoding='utf-8').read())
elif APP_VERSION == "full":
    # Import and run the full version (all features)
    exec(open("streamlit_app_full.py", encoding='utf-8').read())
elif APP_VERSION == "diagnostic":
    # Import and run the diagnostic version for testing
    exec(open("streamlit_app_diagnostic.py", encoding='utf-8').read())
elif APP_VERSION == "diagnostic_enhanced":
    # Import and run the enhanced diagnostic version
    exec(open("streamlit_app_diagnostic_enhanced.py", encoding='utf-8').read())
elif APP_VERSION == "interactive_debug":
    # Import and run the interactive debug version
    exec(open("streamlit_app_interactive_debug.py", encoding='utf-8').read())
else:
    # Default to interactive if unknown version
    print(f"Unknown APP_VERSION: {APP_VERSION}. Using interactive version.")
    exec(open("streamlit_app_interactive.py", encoding='utf-8').read())