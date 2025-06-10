@echo off
echo PCA Automation - Local Testing Script
echo ====================================

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Virtual environment found
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo Virtual environment found ^(.venv^)
    call .venv\Scripts\activate.bat
) else (
    echo No virtual environment found
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Virtual environment created
)

REM Check if streamlit is installed
where streamlit >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing requirements...
    pip install -r requirements.txt
    echo Requirements installed
) else (
    echo Streamlit is already installed
)

echo.
echo Select version to run:
echo 1^) Interactive ^(default^) - Test features one by one
echo 2^) Fixed - Stable production version
echo 3^) Simple - Minimal version
echo 4^) Diagnostic - Test imports
echo 5^) Diagnostic Enhanced - Full diagnostics
echo 6^) Interactive Debug - Verbose debugging
echo.
set /p choice="Enter choice (1-6) or press Enter for default: "

if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    echo Running Interactive version...
    set APP_VERSION=interactive
    streamlit run streamlit_app.py
) else if "%choice%"=="2" (
    echo Running Fixed version...
    set APP_VERSION=fixed
    streamlit run streamlit_app.py
) else if "%choice%"=="3" (
    echo Running Simple version...
    set APP_VERSION=simple
    streamlit run streamlit_app.py
) else if "%choice%"=="4" (
    echo Running Diagnostic version...
    set APP_VERSION=diagnostic
    streamlit run streamlit_app.py
) else if "%choice%"=="5" (
    echo Running Enhanced Diagnostic version...
    set APP_VERSION=diagnostic_enhanced
    streamlit run streamlit_app.py
) else if "%choice%"=="6" (
    echo Running Interactive Debug version...
    set APP_VERSION=interactive_debug
    streamlit run streamlit_app.py
) else (
    echo Invalid choice. Running default Interactive version...
    set APP_VERSION=interactive
    streamlit run streamlit_app.py
)