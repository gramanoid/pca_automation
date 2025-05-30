"""
History Manager - Undo/Redo functionality for marker placement
"""

import streamlit as st
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class HistoryManager:
    """Manages history of marker placements for undo/redo functionality"""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        
        # Initialize history in session state if not exists
        if 'marker_history' not in st.session_state:
            st.session_state.marker_history = []
        if 'marker_history_index' not in st.session_state:
            st.session_state.marker_history_index = -1
    
    def add_state(self, state: Dict[str, Any], description: str = ""):
        """Add a new state to history"""
        # Remove any states after current index (for redo functionality)
        if st.session_state.marker_history_index < len(st.session_state.marker_history) - 1:
            st.session_state.marker_history = st.session_state.marker_history[:st.session_state.marker_history_index + 1]
        
        # Add new state
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'state': state.copy()
        }
        
        st.session_state.marker_history.append(history_entry)
        
        # Limit history size
        if len(st.session_state.marker_history) > self.max_history:
            st.session_state.marker_history.pop(0)
        else:
            st.session_state.marker_history_index += 1
    
    def can_undo(self) -> bool:
        """Check if undo is possible"""
        return st.session_state.marker_history_index > 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible"""
        return st.session_state.marker_history_index < len(st.session_state.marker_history) - 1
    
    def undo(self) -> Optional[Dict[str, Any]]:
        """Undo to previous state"""
        if self.can_undo():
            st.session_state.marker_history_index -= 1
            return st.session_state.marker_history[st.session_state.marker_history_index]['state']
        return None
    
    def redo(self) -> Optional[Dict[str, Any]]:
        """Redo to next state"""
        if self.can_redo():
            st.session_state.marker_history_index += 1
            return st.session_state.marker_history[st.session_state.marker_history_index]['state']
        return None
    
    def get_current_state(self) -> Optional[Dict[str, Any]]:
        """Get current state"""
        if 0 <= st.session_state.marker_history_index < len(st.session_state.marker_history):
            return st.session_state.marker_history[st.session_state.marker_history_index]['state']
        return None
    
    def clear_history(self):
        """Clear all history"""
        st.session_state.marker_history = []
        st.session_state.marker_history_index = -1
    
    def render_history_controls(self):
        """Render undo/redo buttons"""
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("↶ Undo", disabled=not self.can_undo(), use_container_width=True):
                state = self.undo()
                if state:
                    # Apply the state
                    for key, value in state.items():
                        st.session_state[key] = value
                    st.rerun()
        
        with col2:
            if st.button("↷ Redo", disabled=not self.can_redo(), use_container_width=True):
                state = self.redo()
                if state:
                    # Apply the state
                    for key, value in state.items():
                        st.session_state[key] = value
                    st.rerun()
        
        with col3:
            if self.can_undo() or self.can_redo():
                current = st.session_state.marker_history_index + 1
                total = len(st.session_state.marker_history)
                st.caption(f"History: {current}/{total}")
    
    def export_history(self) -> str:
        """Export history as JSON"""
        return json.dumps(st.session_state.marker_history, indent=2)
    
    def import_history(self, history_json: str):
        """Import history from JSON"""
        try:
            history = json.loads(history_json)
            st.session_state.marker_history = history
            st.session_state.marker_history_index = len(history) - 1
            return True
        except:
            return False