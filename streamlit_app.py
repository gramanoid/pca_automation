"""
PCA Automation - Streamlit Web Interface
Temporarily using simplified version while debugging import issues
"""

import streamlit as st
import os

# Check if we should use the simple version
USE_SIMPLE_VERSION = os.getenv("USE_SIMPLE_APP", "true").lower() == "true"

if USE_SIMPLE_VERSION:
    # Import and run the simple version
    exec(open("streamlit_app_simple.py").read())
else:
    # Import and run the full version
    exec(open("streamlit_app_full.py").read())