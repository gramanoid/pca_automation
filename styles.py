"""
Centralized Styling for PCA Automation Streamlit App
"""

# Color palette
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#28a745',
    'warning': '#ffc107',
    'error': '#dc3545',
    'info': '#17a2b8',
    'dark': '#2c3e50',
    'light': '#f8f9fa',
    'muted': '#6c757d',
    'background': '#f0f2f6',
    'card_bg': '#ffffff',
    'border': '#e0e0e0'
}

# Font sizes
FONT_SIZES = {
    'h1': '2.5rem',
    'h2': '2rem',
    'h3': '1.75rem',
    'h4': '1.5rem',
    'body': '1rem',
    'small': '0.875rem',
    'tiny': '0.75rem'
}

# Spacing
SPACING = {
    'xs': '0.25rem',
    'sm': '0.5rem',
    'md': '1rem',
    'lg': '1.5rem',
    'xl': '2rem',
    'xxl': '3rem'
}

# Get all styles as CSS string
def get_css_styles():
    """Return complete CSS styles for the application"""
    return f"""
    <style>
        /* Main header */
        .main-header {{
            font-size: {FONT_SIZES['h1']};
            color: {COLORS['primary']};
            text-align: center;
            padding: {SPACING['md']} 0;
            border-bottom: 2px solid {COLORS['border']};
            margin-bottom: {SPACING['xl']};
            font-weight: 600;
        }}
        
        /* Stage headers */
        .stage-header {{
            font-size: {FONT_SIZES['h2']};
            color: {COLORS['dark']};
            margin-bottom: {SPACING['md']};
            font-weight: 500;
        }}
        
        /* Success message */
        .success-message {{
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: {SPACING['md']};
            border-radius: 0.25rem;
            margin: {SPACING['md']} 0;
            font-weight: 500;
        }}
        
        /* Error message */
        .error-message {{
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: {SPACING['md']};
            border-radius: 0.25rem;
            margin: {SPACING['md']} 0;
            font-weight: 500;
        }}
        
        /* Warning message */
        .warning-message {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: {SPACING['md']};
            border-radius: 0.25rem;
            margin: {SPACING['md']} 0;
            font-weight: 500;
        }}
        
        /* Info box */
        .info-box {{
            background-color: #e3f2fd;
            border: 1px solid #bbdefb;
            color: #0d47a1;
            padding: {SPACING['md']};
            border-radius: 0.25rem;
            margin: {SPACING['md']} 0;
        }}
        
        /* Sidebar styling */
        div[data-testid="stSidebar"] {{
            background-color: {COLORS['background']};
        }}
        
        /* Stage status colors */
        .stage-complete {{
            color: {COLORS['success']};
            font-weight: bold;
        }}
        
        .stage-current {{
            color: {COLORS['warning']};
            font-weight: bold;
        }}
        
        .stage-pending {{
            color: {COLORS['muted']};
        }}
        
        /* Card component */
        .card {{
            background-color: {COLORS['card_bg']};
            border: 1px solid {COLORS['border']};
            border-radius: 0.5rem;
            padding: {SPACING['lg']};
            margin: {SPACING['md']} 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .card-header {{
            font-size: {FONT_SIZES['h4']};
            color: {COLORS['dark']};
            margin-bottom: {SPACING['md']};
            font-weight: 500;
        }}
        
        /* Button styling enhancements */
        .stButton > button {{
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        
        /* Progress bar custom styling */
        .stProgress > div > div > div > div {{
            background-color: {COLORS['primary']};
        }}
        
        /* Metric styling */
        [data-testid="metric-container"] {{
            background-color: {COLORS['card_bg']};
            border: 1px solid {COLORS['border']};
            padding: {SPACING['sm']} {SPACING['md']};
            border-radius: 0.25rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}
        
        /* Table styling */
        .dataframe {{
            font-size: {FONT_SIZES['small']};
        }}
        
        /* Expander styling */
        .streamlit-expanderHeader {{
            font-weight: 500;
            font-size: {FONT_SIZES['body']};
        }}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: {SPACING['sm']};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            padding: {SPACING['sm']} {SPACING['md']};
            font-weight: 500;
        }}
        
        /* File uploader */
        .uploadedFile {{
            background-color: {COLORS['light']};
            border-radius: 0.25rem;
            padding: {SPACING['sm']};
        }}
        
        /* Validation specific styles */
        .validation-check {{
            display: flex;
            align-items: center;
            gap: {SPACING['sm']};
            padding: {SPACING['xs']} 0;
        }}
        
        .validation-passed {{
            color: {COLORS['success']};
        }}
        
        .validation-failed {{
            color: {COLORS['error']};
        }}
        
        .validation-warning {{
            color: {COLORS['warning']};
        }}
        
        /* Marker validation styles */
        .marker-input-container {{
            background-color: {COLORS['light']};
            border: 1px solid {COLORS['border']};
            border-radius: 0.25rem;
            padding: {SPACING['md']};
            margin: {SPACING['sm']} 0;
        }}
        
        .marker-instruction {{
            font-size: {FONT_SIZES['small']};
            color: {COLORS['muted']};
            margin-bottom: {SPACING['sm']};
        }}
        
        /* Dashboard card */
        .dashboard-card {{
            background-color: {COLORS['card_bg']};
            border: 1px solid {COLORS['border']};
            border-radius: 0.5rem;
            padding: {SPACING['md']};
            height: 100%;
            display: flex;
            flex-direction: column;
        }}
        
        .dashboard-metric {{
            font-size: {FONT_SIZES['h3']};
            color: {COLORS['primary']};
            font-weight: 600;
            margin: {SPACING['sm']} 0;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            color: {COLORS['muted']};
            padding: {SPACING['md']};
            font-size: {FONT_SIZES['small']};
        }}
        
        /* Responsive adjustments */
        @media (max-width: 768px) {{
            .main-header {{
                font-size: {FONT_SIZES['h2']};
            }}
            
            .stage-header {{
                font-size: {FONT_SIZES['h3']};
            }}
        }}
    </style>
    """

# Style presets for common components
STYLE_PRESETS = {
    'primary_button': {
        'background-color': COLORS['primary'],
        'color': 'white',
        'font-weight': '500',
        'border': 'none',
        'padding': f"{SPACING['sm']} {SPACING['md']}",
        'border-radius': '0.25rem',
        'cursor': 'pointer'
    },
    'secondary_button': {
        'background-color': 'white',
        'color': COLORS['primary'],
        'font-weight': '500',
        'border': f"1px solid {COLORS['primary']}",
        'padding': f"{SPACING['sm']} {SPACING['md']}",
        'border-radius': '0.25rem',
        'cursor': 'pointer'
    },
    'danger_button': {
        'background-color': COLORS['error'],
        'color': 'white',
        'font-weight': '500',
        'border': 'none',
        'padding': f"{SPACING['sm']} {SPACING['md']}",
        'border-radius': '0.25rem',
        'cursor': 'pointer'
    }
}

def apply_theme():
    """Apply the theme to the Streamlit app"""
    import streamlit as st
    st.markdown(get_css_styles(), unsafe_allow_html=True)