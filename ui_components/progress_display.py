"""
Progress Display Component for PCA Automation
Handles stage navigation and progress tracking
"""

import streamlit as st
from typing import Dict, Optional

class ProgressDisplay:
    """Component for displaying workflow progress and stage navigation"""
    
    def __init__(self, stages: Dict[int, str]):
        self.stages = stages
    
    def get_stage_icon(self, stage_num: int) -> str:
        """Get icon for stage based on its status"""
        current = st.session_state.current_stage
        status = st.session_state.stage_status.get(stage_num, 'pending')
        
        if status == 'completed':
            return "✅"
        elif stage_num == current:
            return "⏳"
        else:
            return "⭕"
    
    def get_stage_class(self, stage_num: int) -> str:
        """Get CSS class for stage based on its status"""
        status = st.session_state.stage_status.get(stage_num, 'pending')
        
        if status == 'completed':
            return "stage-complete"
        elif stage_num == st.session_state.current_stage:
            return "stage-current"
        else:
            return "stage-pending"
    
    def update_stage_status(self, stage_num: int, status: str):
        """Update the status of a stage"""
        # Don't overwrite 'completed' status with 'current'
        if st.session_state.stage_status.get(stage_num) == 'completed' and status == 'current':
            return
        st.session_state.stage_status[stage_num] = status
    
    def render_sidebar_navigation(self):
        """Render the sidebar navigation with stage buttons"""
        st.header("🧭 Navigation")
        
        # Stage selection with status indicators
        for stage_num, stage_name in self.stages.items():
            icon = self.get_stage_icon(stage_num)
            button_label = f"{icon} {stage_name}"
            
            # Style the current stage differently
            if stage_num == st.session_state.current_stage:
                button_label = f"**{button_label}**"
            
            # Determine if button should be disabled
            # Stage 1 is always enabled, others require previous stage completion
            is_disabled = False
            if stage_num > 1:
                # Check if previous stage is completed
                prev_status = st.session_state.stage_status.get(stage_num - 1, 'pending')
                is_disabled = prev_status != 'completed'
            
            if st.button(
                button_label, 
                key=f"stage_{stage_num}",
                disabled=is_disabled,
                use_container_width=True
            ):
                st.session_state.current_stage = stage_num
                st.rerun()
        
        st.divider()
        
        # Progress indicator
        completed_stages = sum(1 for status in st.session_state.stage_status.values() if status == 'completed')
        progress = completed_stages / len(self.stages)
        st.progress(progress)
        st.caption(f"Progress: {completed_stages}/{len(self.stages)} stages completed")
        
        # Add stage descriptions
        with st.expander("ℹ️ Stage Information", expanded=False):
            st.markdown("""
            **📁 Data Upload**: Upload and validate your input files
            
            **⚙️ Data Processing**: Extract and combine data from files
            
            **🔄 Template Mapping**: Map data to output template
            
            **✅ Validation**: Verify data accuracy and completeness
            
            **📊 Results**: Download final output and reports
            """)
    
    def render_stage_header(self, stage_num: int, icon: str = None):
        """Render the header for a specific stage"""
        stage_name = self.stages.get(stage_num, "Unknown Stage")
        
        # Update status if not already completed
        if st.session_state.stage_status.get(stage_num) != 'completed':
            self.update_stage_status(stage_num, 'current')
        
        # Use provided icon or default based on stage
        if not icon:
            stage_icons = {
                1: "📁",
                2: "⚙️",
                3: "🔄",
                4: "✅",
                5: "📊"
            }
            icon = stage_icons.get(stage_num, "📋")
        
        st.markdown(
            f'<h2 class="stage-header">{icon} Stage {stage_num}: {stage_name}</h2>', 
            unsafe_allow_html=True
        )
    
    def mark_stage_complete(self, stage_num: int):
        """Mark a stage as complete"""
        self.update_stage_status(stage_num, 'completed')
        st.session_state.processing_complete[stage_num] = True
    
    def can_proceed_to_next_stage(self, current_stage: int) -> bool:
        """Check if user can proceed to next stage"""
        return st.session_state.processing_complete.get(current_stage, False)
    
    def render_continue_button(self, current_stage: int, next_stage: int, 
                             button_text: Optional[str] = None):
        """Render continue button to next stage"""
        if not button_text:
            next_stage_name = self.stages.get(next_stage, "Next Stage")
            button_text = f"➡️ Continue to {next_stage_name}"
        
        if self.can_proceed_to_next_stage(current_stage):
            if st.button(button_text, use_container_width=True, type="primary"):
                st.session_state.current_stage = next_stage
                st.rerun()
    
    def render_progress_bar(self, value: float, text: str = ""):
        """Render a progress bar with optional text"""
        progress_bar = st.progress(value)
        if text:
            st.caption(text)
        return progress_bar
    
    def render_status_message(self, message: str, status_type: str = "info"):
        """Render a status message with appropriate styling"""
        if status_type == "success":
            st.markdown(f'<div class="success-message">{message}</div>', unsafe_allow_html=True)
        elif status_type == "error":
            st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)
        elif status_type == "warning":
            st.markdown(f'<div class="warning-message">{message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="info-box">{message}</div>', unsafe_allow_html=True)