# PCA Automation

Transform your media plans into actionable insights with AI-powered data mapping.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## What It Does

PCA Automation streamlines the process of converting media plan data (PLANNED vs DELIVERED) into standardized reporting templates. It handles complex data from multiple advertising platforms (DV360, META, TIKTOK) and automatically maps them to your output template.

## Quick Start

### Option 1: Web App (Recommended)

1. Visit the [live app](https://your-app-url.streamlit.app)
2. Upload your files:
   - **Media Plan** (PLANNED file with START/END markers)
   - **Platform Data** (DELIVERED data from platforms)
   - **Output Template** (Empty tracker template)
3. Click through the workflow - all processing is automatic
4. Download your completed report

### Option 2: Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app_interactive.py

# Open http://localhost:8501 in your browser
```

## Key Features

### 📊 **Smart Data Processing**
- Automatically extracts data from PLANNED and DELIVERED Excel files
- Handles multiple platforms: DV360, META, TIKTOK
- Identifies regions, objectives, and campaigns automatically
- 100% data coverage with no manual intervention

### 🤖 **AI-Powered Mapping** (Infrastructure Ready)
- OpenRouter integration with Gemini 2.5 Pro configured
- Currently uses enhanced rule-based mapping for reliability
- Maps 50+ column variations automatically
- Handles platform-specific data structures

### 📈 **Enhanced Progress Tracking**
- Real-time progress bars for each processing stage
- Detailed step-by-step status updates
- Error tracking with one-click copy for debugging
- Persistent progress across sessions

### 🔒 **Secure Team Collaboration**
- Encrypted API key management
- Team-wide configuration - no individual setup needed
- Support for multiple LLM providers

### 🎨 **Professional UI/UX**
- Clean, minimalist design
- Dark mode support
- Mobile-responsive layout
- Easy "Start Over" functionality

## Workflow Steps

1. **📤 Upload** - Validate and upload your three Excel files
2. **⚙️ Process** - Extract and combine data from sources
3. **🗺️ Map** - Intelligently map data to output template
4. **✅ Validate** - Check data accuracy and completeness
5. **📥 Download** - Get your completed report

## Project Structure

```
├── streamlit_app_interactive.py    # Main application
├── production_workflow/            # Core processing logic
│   ├── 01_data_extraction/        # Data extraction modules
│   ├── 03_template_mapping/       # Template mapping logic
│   └── 04_validation/             # Data validation
├── ui_components/                 # UI components
├── config/                        # Configuration files
├── input/                         # Sample input files
└── documentation/                 # Detailed documentation
```

## Requirements

- Python 3.8+
- 4GB RAM minimum
- Modern web browser
- Excel files in .xlsx format

## Configuration

The app works out of the box with pre-configured settings. For advanced users:

- Client-specific rules: `config/client_mapping_rules.json`
- Template structure: `config/template_mapping_config.json`

## Support

- **Documentation**: See [`documentation/INDEX.md`](documentation/INDEX.md) for detailed guides
- **Issues**: [GitHub Issues](https://github.com/gramanoid/pca_automation/issues)
- **Updates**: Check [RELEASE_NOTES.md](RELEASE_NOTES.md) for latest changes

## License

Proprietary - For authorized use only

---

**Built with** ❤️ **using Streamlit, Python, and AI**