"""
PCA Automation - Streamlit Web Interface
Supports simple, gradual, and full versions based on environment settings
"""

import streamlit as st
import os

# Check which version to use
APP_VERSION = os.getenv("APP_VERSION", "simple").lower()

if APP_VERSION == "simple":
    # Import and run the simple version (default, most stable)
    exec(open("streamlit_app_simple.py").read())
elif APP_VERSION == "gradual":
    # Import and run the gradual enhancement version
    exec(open("streamlit_app_gradual.py").read())
elif APP_VERSION == "full":
    # Import and run the full version (all features)
    exec(open("streamlit_app_full.py").read())
else:
    # Default to simple if unknown version
    st.warning(f"Unknown APP_VERSION: {APP_VERSION}. Using simple version.")
    exec(open("streamlit_app_simple.py").read())