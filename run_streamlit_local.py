#!/usr/bin/env python3
"""
Simple script to run Streamlit locally with proper environment
"""
import subprocess
import sys
import os

# Set the app version
os.environ['APP_VERSION'] = 'interactive_debug'

# Run streamlit
print("🚀 Starting PCA Automation (Interactive Debug Mode)")
print("=" * 50)
print("The app will open in your browser at http://localhost:8501")
print("Press Ctrl+C to stop")
print("=" * 50)

try:
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
except KeyboardInterrupt:
    print("\n✅ App stopped")