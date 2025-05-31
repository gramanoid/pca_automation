"""
PCA Automation - Streamlit Web Interface
Supports simple, gradual, and full versions based on environment settings
"""

import streamlit as st
import os

# Check which version to use
APP_VERSION = os.getenv("APP_VERSION", "fixed").lower()

if APP_VERSION == "simple":
    # Import and run the simple version (most stable)
    exec(open("streamlit_app_simple.py").read())
elif APP_VERSION == "fixed":
    # Import and run the fixed version (default - fixes stage 5 issue)
    exec(open("streamlit_app_fixed.py").read())
elif APP_VERSION == "interactive":
    # Import and run the interactive version (feature selection)
    exec(open("streamlit_app_interactive.py").read())
elif APP_VERSION == "gradual":
    # Import and run the gradual enhancement version
    exec(open("streamlit_app_gradual.py").read())
elif APP_VERSION == "full":
    # Import and run the full version (all features)
    exec(open("streamlit_app_full.py").read())
else:
    # Default to fixed if unknown version
    st.warning(f"Unknown APP_VERSION: {APP_VERSION}. Using fixed version.")
    exec(open("streamlit_app_fixed.py").read())