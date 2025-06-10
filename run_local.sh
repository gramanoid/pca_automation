#!/bin/bash

echo "PCA Automation - Local Testing Script"
echo "===================================="

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Virtual environment found"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "✅ Virtual environment found (.venv)"
    source .venv/bin/activate
else
    echo "⚠️  No virtual environment found"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created"
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
    echo "✅ Requirements installed"
else
    echo "✅ Streamlit is already installed"
fi

# Display options
echo ""
echo "Select version to run:"
echo "1) Interactive (default) - Test features one by one"
echo "2) Fixed - Stable production version"
echo "3) Simple - Minimal version"
echo "4) Diagnostic - Test imports"
echo "5) Diagnostic Enhanced - Full diagnostics"
echo "6) Interactive Debug - Verbose debugging"
echo ""
read -p "Enter choice (1-6) or press Enter for default: " choice

case $choice in
    1|"")
        echo "🚀 Running Interactive version..."
        APP_VERSION=interactive streamlit run streamlit_app.py
        ;;
    2)
        echo "🚀 Running Fixed version..."
        APP_VERSION=fixed streamlit run streamlit_app.py
        ;;
    3)
        echo "🚀 Running Simple version..."
        APP_VERSION=simple streamlit run streamlit_app.py
        ;;
    4)
        echo "🚀 Running Diagnostic version..."
        APP_VERSION=diagnostic streamlit run streamlit_app.py
        ;;
    5)
        echo "🚀 Running Enhanced Diagnostic version..."
        APP_VERSION=diagnostic_enhanced streamlit run streamlit_app.py
        ;;
    6)
        echo "🚀 Running Interactive Debug version..."
        APP_VERSION=interactive_debug streamlit run streamlit_app.py
        ;;
    *)
        echo "Invalid choice. Running default Interactive version..."
        APP_VERSION=interactive streamlit run streamlit_app.py
        ;;
esac