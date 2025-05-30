"""
Configuration Persistence - Save/Load configurations using browser localStorage
"""

import streamlit as st
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import base64

class ConfigPersistence:
    """Manages configuration persistence using Streamlit's session state and export/import"""
    
    def __init__(self):
        # Initialize saved configs in session state
        if 'saved_configs' not in st.session_state:
            st.session_state.saved_configs = {}
        if 'last_used_config' not in st.session_state:
            st.session_state.last_used_config = None
    
    def save_config(self, name: str, config: Dict[str, Any], description: str = ""):
        """Save a configuration"""
        config_entry = {
            'name': name,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'config': config.copy()
        }
        
        st.session_state.saved_configs[name] = config_entry
        st.session_state.last_used_config = name
        
        return True
    
    def load_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a configuration by name"""
        if name in st.session_state.saved_configs:
            st.session_state.last_used_config = name
            return st.session_state.saved_configs[name]['config']
        return None
    
    def delete_config(self, name: str) -> bool:
        """Delete a saved configuration"""
        if name in st.session_state.saved_configs:
            del st.session_state.saved_configs[name]
            if st.session_state.last_used_config == name:
                st.session_state.last_used_config = None
            return True
        return False
    
    def list_configs(self) -> List[Dict[str, Any]]:
        """List all saved configurations"""
        configs = []
        for name, entry in st.session_state.saved_configs.items():
            configs.append({
                'name': name,
                'description': entry.get('description', ''),
                'timestamp': entry.get('timestamp', ''),
                'is_last_used': name == st.session_state.last_used_config
            })
        return sorted(configs, key=lambda x: x['timestamp'], reverse=True)
    
    def export_configs(self) -> str:
        """Export all configurations as JSON"""
        export_data = {
            'version': '1.0',
            'exported_at': datetime.now().isoformat(),
            'configs': st.session_state.saved_configs,
            'last_used': st.session_state.last_used_config
        }
        return json.dumps(export_data, indent=2)
    
    def import_configs(self, json_data: str) -> bool:
        """Import configurations from JSON"""
        try:
            data = json.loads(json_data)
            
            # Validate version
            if data.get('version') != '1.0':
                st.error("Incompatible configuration version")
                return False
            
            # Import configs
            imported_configs = data.get('configs', {})
            for name, config in imported_configs.items():
                st.session_state.saved_configs[name] = config
            
            # Set last used
            if data.get('last_used') in st.session_state.saved_configs:
                st.session_state.last_used_config = data.get('last_used')
            
            return True
        except Exception as e:
            st.error(f"Error importing configurations: {str(e)}")
            return False
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get current configuration from session state"""
        config = {
            'client_id': st.session_state.get('client_id', ''),
            'enable_llm_mapping': st.session_state.get('enable_llm_mapping', True),
            'validation_strict_mode': st.session_state.get('validation_strict_mode', False),
            'auto_calculate_totals': st.session_state.get('auto_calculate_totals', True),
            'market_sort_by': st.session_state.get('market_sort_by', 'budget_desc'),
            'debug_mode': st.session_state.get('debug_mode', False)
        }
        return config
    
    def apply_config(self, config: Dict[str, Any]):
        """Apply a configuration to session state"""
        for key, value in config.items():
            st.session_state[key] = value
    
    def render_persistence_ui(self):
        """Render the configuration persistence UI"""
        st.subheader("💾 Configuration Management")
        
        # Save current configuration
        with st.expander("Save Current Configuration", expanded=False):
            col1, col2 = st.columns([3, 1])
            with col1:
                config_name = st.text_input("Configuration Name", key="save_config_name")
                config_desc = st.text_area("Description (optional)", key="save_config_desc", height=60)
            with col2:
                st.write("")  # Spacing
                st.write("")
                if st.button("💾 Save", use_container_width=True):
                    if config_name:
                        current_config = self.get_current_config()
                        if self.save_config(config_name, current_config, config_desc):
                            st.success(f"Configuration '{config_name}' saved!")
                            st.rerun()
                    else:
                        st.error("Please enter a configuration name")
        
        # Load saved configurations
        saved_configs = self.list_configs()
        if saved_configs:
            st.subheader("📂 Saved Configurations")
            
            for config in saved_configs:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        st.write(f"**{config['name']}**")
                        if config['description']:
                            st.caption(config['description'])
                    
                    with col2:
                        timestamp = datetime.fromisoformat(config['timestamp'])
                        st.caption(f"Saved: {timestamp.strftime('%Y-%m-%d %H:%M')}")
                        if config['is_last_used']:
                            st.caption("🔸 Last used")
                    
                    with col3:
                        if st.button("Load", key=f"load_{config['name']}", use_container_width=True):
                            loaded_config = self.load_config(config['name'])
                            if loaded_config:
                                self.apply_config(loaded_config)
                                st.success(f"Configuration '{config['name']}' loaded!")
                                st.rerun()
                    
                    with col4:
                        if st.button("🗑️", key=f"delete_{config['name']}", use_container_width=True):
                            if self.delete_config(config['name']):
                                st.success(f"Configuration '{config['name']}' deleted!")
                                st.rerun()
        
        # Export/Import
        st.subheader("📤 Export/Import Configurations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export All Configurations", use_container_width=True):
                json_data = self.export_configs()
                b64 = base64.b64encode(json_data.encode()).decode()
                href = f'<a href="data:application/json;base64,{b64}" download="pca_configs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json">Download Configuration File</a>'
                st.markdown(href, unsafe_allow_html=True)
        
        with col2:
            uploaded_file = st.file_uploader("Import Configuration File", type=['json'])
            if uploaded_file:
                json_data = uploaded_file.read().decode('utf-8')
                if self.import_configs(json_data):
                    st.success("Configurations imported successfully!")
                    st.rerun()
    
    def inject_local_storage_script(self):
        """Inject JavaScript for localStorage persistence"""
        # This would require custom components or JavaScript injection
        # For now, we rely on Streamlit's session state
        pass