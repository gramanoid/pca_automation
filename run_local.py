#!/usr/bin/env python3
"""
Local testing script for PCA Automation
Run different versions of the Streamlit app locally
"""

import os
import sys
import subprocess
import platform

def check_requirements():
    """Check if streamlit is installed"""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def install_requirements():
    """Install requirements"""
    print("📦 Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ Requirements installed")

def main():
    print("PCA Automation - Local Testing")
    print("==============================")
    
    # Check if streamlit is installed
    if not check_requirements():
        print("⚠️  Streamlit not found")
        install = input("Install requirements? (y/n): ").lower()
        if install == 'y':
            install_requirements()
        else:
            print("Cannot run without streamlit. Exiting.")
            return
    
    print("\nSelect version to run:")
    print("1) Interactive (default) - Test features one by one")
    print("2) Fixed - Stable production version")
    print("3) Simple - Minimal version")
    print("4) Diagnostic - Test imports")
    print("5) Diagnostic Enhanced - Full diagnostics")
    print("6) Interactive Debug - Verbose debugging")
    print("7) Exit")
    
    choice = input("\nEnter choice (1-7) or press Enter for default: ").strip()
    
    version_map = {
        '1': 'interactive',
        '2': 'fixed',
        '3': 'simple',
        '4': 'diagnostic',
        '5': 'diagnostic_enhanced',
        '6': 'interactive_debug',
        '': 'interactive'  # default
    }
    
    if choice == '7':
        print("Exiting...")
        return
    
    app_version = version_map.get(choice, 'interactive')
    
    print(f"\n🚀 Running {app_version} version...")
    print("The app will open in your browser. Press Ctrl+C to stop.\n")
    
    # Set environment variable and run streamlit
    env = os.environ.copy()
    env['APP_VERSION'] = app_version
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"], env=env)
    except KeyboardInterrupt:
        print("\n\n✅ App stopped")

if __name__ == "__main__":
    main()