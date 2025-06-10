"""
Configuration Sidebar Component for PCA Automation
Handles configuration templates and settings management
"""

import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from production_workflow.utils.secure_api_key import get_api_key

class ConfigSidebar:
    """Component for managing configuration settings and templates"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_templates = {
            'Default': {
                'description': 'Standard configuration for most campaigns',
                'settings': {
                    'client_id': '',
                    'enable_llm_mapping': True,
                    'validation_strict_mode': False,
                    'auto_calculate_totals': True,
                    'market_sort_by': 'budget_desc'
                }
            },
            'Sensodyne Campaign': {
                'description': 'Optimized for Sensodyne multi-market campaigns',
                'settings': {
                    'client_id': 'SENSODYNE',
                    'enable_llm_mapping': True,
                    'validation_strict_mode': True,
                    'auto_calculate_totals': True,
                    'market_sort_by': 'budget_desc',
                    'expected_markets': ['UAE', 'OMN', 'LEB', 'KWT', 'QAT']
                }
            },
            'Multi-Market Analysis': {
                'description': 'Enhanced settings for complex multi-market campaigns',
                'settings': {
                    'client_id': '',
                    'enable_llm_mapping': True,
                    'validation_strict_mode': True,
                    'auto_calculate_totals': True,
                    'market_sort_by': 'alphabetical',
                    'include_market_comparison': True
                }
            },
            'Custom': {
                'description': 'Configure all settings manually',
                'settings': {}
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from config files"""
        config = {}
        config_path = self.project_root / "config" / "config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        return config
    
    def save_current_config(self, config_name: str):
        """Save current configuration as a template"""
        # Get current settings from session state
        current_config = {
            'client_id': os.getenv('CLIENT_ID', ''),
            'api_key_set': bool(get_api_key()),  # Use secure API key manager
            'enable_llm_mapping': st.session_state.get('enable_llm_mapping', True),
            'validation_strict_mode': st.session_state.get('validation_strict_mode', False),
            'auto_calculate_totals': st.session_state.get('auto_calculate_totals', True),
            'market_sort_by': st.session_state.get('market_sort_by', 'budget_desc')
        }
        
        # Save to session state
        if 'custom_configs' not in st.session_state:
            st.session_state.custom_configs = {}
        st.session_state.custom_configs[config_name] = current_config
        
        return current_config
    
    def apply_template(self, template_name: str):
        """Apply a configuration template"""
        if template_name in self.config_templates:
            settings = self.config_templates[template_name]['settings']
            
            # Apply settings
            for key, value in settings.items():
                if key == 'client_id' and value:
                    os.environ['CLIENT_ID'] = value
                else:
                    st.session_state[key] = value
            
            st.success(f"✅ Applied '{template_name}' configuration template")
    
    def render_configuration_section(self):
        """Render the configuration section in the sidebar"""
        with st.expander("⚙️ Configuration", expanded=False):
            # Configuration templates
            st.subheader("Configuration Templates")
            
            selected_template = st.selectbox(
                "Select Template",
                options=list(self.config_templates.keys()),
                index=0,
                help="Choose a pre-configured template or select 'Custom' for manual configuration"
            )
            
            # Show template description
            if selected_template in self.config_templates:
                st.caption(self.config_templates[selected_template]['description'])
            
            # Apply template button
            if selected_template != 'Custom':
                if st.button("Apply Template", use_container_width=True):
                    self.apply_template(selected_template)
                    st.rerun()
            
            st.divider()
            
            # Manual configuration
            st.subheader("Settings")
            
            # Client settings
            client_id = st.text_input(
                "Client ID", 
                value=os.getenv("CLIENT_ID", ""),
                help="Leave empty for default mappings",
                disabled=selected_template != 'Custom'
            )
            if client_id:
                os.environ["CLIENT_ID"] = client_id
            
            # API settings
            current_api_key = get_api_key()
            has_hardcoded_key = current_api_key and not os.getenv("ANTHROPIC_API_KEY")
            
            if has_hardcoded_key:
                st.success("🔐 Using secure team API key - No configuration needed!")
                st.caption("Your colleagues can use this app without entering any API key")
            elif current_api_key:
                st.info("🔑 Using API key from environment variable")
            else:
                st.warning("⚠️ No API key configured - AI mapping will be disabled")
            
            # Only show API key input in Custom mode
            if selected_template == 'Custom':
                st.divider()
                st.caption("Advanced: Override Team API Key")
                api_key = st.text_input(
                    "Personal API Key (Optional)",
                    value=os.getenv("ANTHROPIC_API_KEY", ""),
                    type="password",
                    help="Only enter if you want to use your own key instead of the team key",
                    placeholder="Leave empty to use team key"
                )
                if api_key:
                    os.environ["ANTHROPIC_API_KEY"] = api_key
                elif "ANTHROPIC_API_KEY" in os.environ and not api_key:
                    # Clear the environment variable if user empties the field
                    del os.environ["ANTHROPIC_API_KEY"]
            
            # Processing options
            st.subheader("Processing Options")
            
            enable_llm = st.checkbox(
                "Enable LLM Mapping",
                value=st.session_state.get('enable_llm_mapping', True),
                help="Use AI-powered column mapping for better accuracy",
                disabled=selected_template != 'Custom'
            )
            st.session_state['enable_llm_mapping'] = enable_llm
            
            strict_validation = st.checkbox(
                "Strict Validation Mode",
                value=st.session_state.get('validation_strict_mode', False),
                help="Fail on any validation warnings",
                disabled=selected_template != 'Custom'
            )
            st.session_state['validation_strict_mode'] = strict_validation
            
            auto_calc = st.checkbox(
                "Auto-Calculate Totals",
                value=st.session_state.get('auto_calculate_totals', True),
                help="Automatically calculate total rows from component data",
                disabled=selected_template != 'Custom'
            )
            st.session_state['auto_calculate_totals'] = auto_calc
            
            # Market sorting
            market_sort = st.selectbox(
                "Market Sort Order",
                options=['budget_desc', 'budget_asc', 'alphabetical'],
                index=['budget_desc', 'budget_asc', 'alphabetical'].index(
                    st.session_state.get('market_sort_by', 'budget_desc')
                ),
                format_func=lambda x: {
                    'budget_desc': 'By Budget (High to Low)',
                    'budget_asc': 'By Budget (Low to High)',
                    'alphabetical': 'Alphabetical'
                }[x],
                help="How to order markets in the output",
                disabled=selected_template != 'Custom'
            )
            st.session_state['market_sort_by'] = market_sort
            
            # Debug settings
            st.subheader("Debug Settings")
            debug_mode = st.checkbox(
                "Enable Debug Mode",
                value=st.session_state.get('debug_mode', False),
                help="Show detailed logging information"
            )
            if debug_mode:
                os.environ["EXCEL_EXTRACTOR_LOG_LEVEL"] = "DEBUG"
                os.environ["MAPPER_LOG_LEVEL"] = "DEBUG"
                st.session_state['debug_mode'] = True
            else:
                os.environ.pop("EXCEL_EXTRACTOR_LOG_LEVEL", None)
                os.environ.pop("MAPPER_LOG_LEVEL", None)
                st.session_state['debug_mode'] = False
            
            # Save custom configuration
            if selected_template == 'Custom':
                st.divider()
                config_name = st.text_input("Save Configuration As:", placeholder="My Custom Config")
                if st.button("💾 Save Configuration", use_container_width=True) and config_name:
                    saved_config = self.save_current_config(config_name)
                    st.success(f"✅ Configuration saved as '{config_name}'")
    
    def render_info_section(self):
        """Render information section in the sidebar"""
        with st.expander("ℹ️ Help & Information", expanded=False):
            st.markdown("""
            ### Quick Tips
            
            1. **File Requirements:**
               - PLANNED: Must have DV360, META, TIKTOK sheets
               - DELIVERED: Platform-specific data exports
               - TEMPLATE: Empty output template file
            
            2. **START/END Markers:**
               - Required for data extraction
               - System will guide you to add them if missing
            
            3. **Configuration Templates:**
               - Use pre-built templates for common scenarios
               - Create custom configurations for specific needs
            
            4. **API Key:**
               - Required for enhanced AI-powered mapping
               - Improves column matching accuracy
            
            ### Support & Resources
            
            📚 [Documentation](https://github.com/gramanoid/pca_automation)
            🐛 [Report Issue](https://github.com/gramanoid/pca_automation/issues)
            💬 [Discussions](https://github.com/gramanoid/pca_automation/discussions)
            """)
    
    def get_current_settings_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration settings"""
        return {
            'client_id': os.getenv('CLIENT_ID', 'Not Set'),
            'api_key_configured': bool(os.getenv('ANTHROPIC_API_KEY')),
            'llm_mapping_enabled': st.session_state.get('enable_llm_mapping', True),
            'validation_mode': 'Strict' if st.session_state.get('validation_strict_mode', False) else 'Normal',
            'market_sorting': st.session_state.get('market_sort_by', 'budget_desc'),
            'debug_mode': st.session_state.get('debug_mode', False)
        }