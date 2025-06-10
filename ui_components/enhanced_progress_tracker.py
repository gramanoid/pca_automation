"""
Enhanced Progress Tracker for PCA Automation
Provides detailed progress visualization and error tracking
"""

import streamlit as st
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

class EnhancedProgressTracker:
    """Enhanced progress tracking with detailed status updates and error logging"""
    
    def __init__(self):
        # Initialize progress state if not exists
        if 'progress_details' not in st.session_state:
            st.session_state.progress_details = {}
        
        if 'error_logs' not in st.session_state:
            st.session_state.error_logs = []
        
        if 'stage_timings' not in st.session_state:
            st.session_state.stage_timings = {}
    
    def start_stage_tracking(self, stage: str, total_steps: int = 1):
        """Start tracking a stage with detailed progress"""
        st.session_state.progress_details[stage] = {
            'status': 'running',
            'current_step': 0,
            'total_steps': total_steps,
            'steps_completed': [],
            'current_task': '',
            'start_time': datetime.now(),
            'errors': [],
            'warnings': []
        }
        st.session_state.stage_timings[stage] = {
            'start': datetime.now(),
            'end': None,
            'duration': None
        }
    
    def update_progress(self, stage: str, step: int, task: str, details: str = ""):
        """Update progress for a specific stage"""
        if stage in st.session_state.progress_details:
            progress = st.session_state.progress_details[stage]
            progress['current_step'] = step
            progress['current_task'] = task
            if details:
                progress['steps_completed'].append({
                    'step': step,
                    'task': task,
                    'details': details,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
    
    def complete_stage(self, stage: str, summary: Dict[str, any] = None):
        """Mark a stage as complete with optional summary"""
        if stage in st.session_state.progress_details:
            progress = st.session_state.progress_details[stage]
            progress['status'] = 'completed'
            progress['summary'] = summary or {}
            
        if stage in st.session_state.stage_timings:
            timing = st.session_state.stage_timings[stage]
            timing['end'] = datetime.now()
            timing['duration'] = (timing['end'] - timing['start']).total_seconds()
    
    def add_error(self, stage: str, error: str, details: str = ""):
        """Add an error to the current stage"""
        error_entry = {
            'stage': stage,
            'error': error,
            'details': details,
            'timestamp': datetime.now()
        }
        
        # Add to global error log
        st.session_state.error_logs.append(error_entry)
        
        # Add to stage-specific errors
        if stage in st.session_state.progress_details:
            st.session_state.progress_details[stage]['errors'].append(error_entry)
            st.session_state.progress_details[stage]['status'] = 'error'
    
    def add_warning(self, stage: str, warning: str):
        """Add a warning to the current stage"""
        if stage in st.session_state.progress_details:
            st.session_state.progress_details[stage]['warnings'].append({
                'warning': warning,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
    
    def render_detailed_progress(self, stage: str):
        """Render detailed progress visualization for a stage"""
        if stage not in st.session_state.progress_details:
            return
        
        progress = st.session_state.progress_details[stage]
        
        # Create columns for layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Progress bar
            if progress['total_steps'] > 0:
                progress_value = progress['current_step'] / progress['total_steps']
                st.progress(progress_value)
                st.caption(f"Step {progress['current_step']} of {progress['total_steps']}: {progress['current_task']}")
            
            # Detailed steps completed
            if progress['steps_completed']:
                with st.expander("📋 Completed Steps", expanded=True):
                    for step in progress['steps_completed']:
                        st.markdown(f"**[{step['timestamp']}]** Step {step['step']}: {step['task']}")
                        if step['details']:
                            st.caption(f"↳ {step['details']}")
        
        with col2:
            # Status indicator
            if progress['status'] == 'running':
                st.info(f"🔄 Status: Running")
            elif progress['status'] == 'completed':
                st.success(f"✅ Status: Completed")
            elif progress['status'] == 'error':
                st.error(f"❌ Status: Error")
            
            # Timing info
            if stage in st.session_state.stage_timings:
                timing = st.session_state.stage_timings[stage]
                if timing['duration']:
                    st.metric("Duration", f"{timing['duration']:.1f}s")
                else:
                    elapsed = (datetime.now() - timing['start']).total_seconds()
                    st.metric("Elapsed", f"{elapsed:.1f}s")
        
        # Show errors if any
        if progress['errors']:
            st.error(f"**Errors Encountered ({len(progress['errors'])})**")
            for error in progress['errors']:
                with st.expander(f"❌ {error['error']}", expanded=True):
                    st.write(f"**Time:** {error['timestamp'].strftime('%H:%M:%S')}")
                    if error['details']:
                        st.code(error['details'])
        
        # Show warnings if any
        if progress['warnings']:
            st.warning(f"**Warnings ({len(progress['warnings'])})**")
            for warning in progress['warnings']:
                st.caption(f"⚠️ [{warning['timestamp']}] {warning['warning']}")
    
    def render_stage_summary(self, stage: str):
        """Render a summary of the stage results"""
        if stage not in st.session_state.progress_details:
            return
        
        progress = st.session_state.progress_details[stage]
        
        if progress.get('summary'):
            st.subheader("📊 Stage Summary")
            
            # Create metrics columns
            cols = st.columns(len(progress['summary']))
            for i, (key, value) in enumerate(progress['summary'].items()):
                with cols[i]:
                    # Format the key nicely
                    display_key = key.replace('_', ' ').title()
                    st.metric(display_key, value)
    
    def render_global_error_log(self):
        """Render all errors from all stages with copy functionality"""
        if st.session_state.error_logs:
            with st.expander(f"🚨 Error Log ({len(st.session_state.error_logs)} errors)", expanded=True):
                # Add copy all errors button
                all_errors_text = self._format_all_errors_for_copy()
                st.text_area(
                    "📋 Copy All Errors (Click to select all, then Ctrl+C)",
                    value=all_errors_text,
                    height=150,
                    key="copy_all_errors"
                )
                
                st.divider()
                
                # Show individual errors
                for i, error in enumerate(reversed(st.session_state.error_logs)):
                    col1, col2 = st.columns([5, 1])
                    
                    with col1:
                        st.error(f"**[{error['timestamp'].strftime('%H:%M:%S')}] Stage: {error['stage']}**")
                        st.write(error['error'])
                    
                    with col2:
                        # Format error for copying
                        error_text = f"Error in {error['stage']} at {error['timestamp'].strftime('%H:%M:%S')}:\n{error['error']}"
                        if error['details']:
                            error_text += f"\n\nDetails:\n{error['details']}"
                        
                        st.text_area(
                            "Copy",
                            value=error_text,
                            height=100,
                            key=f"copy_error_{i}",
                            label_visibility="collapsed"
                        )
                    
                    if error['details']:
                        with st.expander("Stack Trace", expanded=False):
                            st.code(error['details'])
                    
                    st.divider()
    
    def _format_all_errors_for_copy(self) -> str:
        """Format all errors for easy copying"""
        errors_text = "=== PCA AUTOMATION ERROR LOG ===\n\n"
        errors_text += f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        errors_text += f"Total errors: {len(st.session_state.error_logs)}\n\n"
        
        for i, error in enumerate(st.session_state.error_logs, 1):
            errors_text += f"--- Error {i} ---\n"
            errors_text += f"Stage: {error['stage']}\n"
            errors_text += f"Time: {error['timestamp'].strftime('%H:%M:%S')}\n"
            errors_text += f"Error: {error['error']}\n"
            if error['details']:
                errors_text += f"Stack Trace:\n{error['details']}\n"
            errors_text += "\n"
        
        return errors_text
    
    def get_stage_status(self, stage: str) -> str:
        """Get the current status of a stage"""
        if stage in st.session_state.progress_details:
            return st.session_state.progress_details[stage]['status']
        return 'pending'
    
    def clear_stage_progress(self, stage: str):
        """Clear progress for a specific stage"""
        if stage in st.session_state.progress_details:
            del st.session_state.progress_details[stage]
        if stage in st.session_state.stage_timings:
            del st.session_state.stage_timings[stage]


class MappingProgressTracker(EnhancedProgressTracker):
    """Specialized progress tracker for the mapping stage"""
    
    def __init__(self):
        super().__init__()
        self.mapping_steps = [
            "Initializing mapper",
            "Loading combined data",
            "Validating data structure",
            "Analyzing columns",
            "Applying AI mapping",
            "Writing to template",
            "Generating report",
            "Finalizing output"
        ]
    
    def start_mapping(self):
        """Initialize mapping progress tracking"""
        self.start_stage_tracking('mapping', len(self.mapping_steps))
    
    def update_mapping_step(self, step_index: int, details: str = ""):
        """Update mapping progress with predefined steps"""
        if 0 <= step_index < len(self.mapping_steps):
            self.update_progress(
                'mapping',
                step_index + 1,
                self.mapping_steps[step_index],
                details
            )
    
    def render_mapping_progress(self):
        """Render specialized mapping progress view"""
        st.subheader("🗺️ Mapping Progress")
        
        # Show current operation
        if 'mapping' in st.session_state.progress_details:
            progress = st.session_state.progress_details['mapping']
            
            # Main progress
            col1, col2, col3 = st.columns([2, 3, 1])
            
            with col1:
                st.metric("Current Step", f"{progress['current_step']}/{progress['total_steps']}")
            
            with col2:
                if progress['total_steps'] > 0:
                    progress_pct = (progress['current_step'] / progress['total_steps']) * 100
                    st.metric("Progress", f"{progress_pct:.0f}%")
            
            with col3:
                if 'mapping' in st.session_state.stage_timings:
                    elapsed = (datetime.now() - st.session_state.stage_timings['mapping']['start']).total_seconds()
                    st.metric("Time", f"{elapsed:.0f}s")
            
            # Progress bar with label
            progress_value = progress['current_step'] / progress['total_steps'] if progress['total_steps'] > 0 else 0
            st.progress(progress_value)
            st.info(f"🔄 {progress['current_task']}")
            
            # Step breakdown
            with st.expander("📋 Detailed Steps", expanded=True):
                for i, step_name in enumerate(self.mapping_steps):
                    if i < progress['current_step']:
                        st.success(f"✅ {step_name}")
                    elif i == progress['current_step'] - 1:
                        st.warning(f"🔄 {step_name} (in progress)")
                    else:
                        st.caption(f"⏳ {step_name}")
            
            # Show any errors immediately with copy functionality
            if progress['errors']:
                st.error("**❌ Mapping Error Detected**")
                latest_error = progress['errors'][-1]
                
                # Format error for easy copying
                error_text = f"=== MAPPING ERROR ===\nTime: {latest_error['timestamp'].strftime('%H:%M:%S')}\nError: {latest_error['error']}\n"
                if latest_error.get('details'):
                    error_text += f"\nStack Trace:\n{latest_error['details']}"
                
                # Show error with copy button
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.error(latest_error['error'])
                with col2:
                    st.text_area(
                        "Copy",
                        value=error_text,
                        height=100,
                        key="mapping_error_copy_quick",
                        label_visibility="collapsed"
                    )
                
                if latest_error.get('details'):
                    with st.expander("📋 Full Stack Trace (Click to expand)", expanded=False):
                        st.code(latest_error['details'])
                        st.caption("💡 Tip: Triple-click to select all, then Ctrl+C to copy")


def get_progress_tracker() -> EnhancedProgressTracker:
    """Get or create the global progress tracker instance"""
    if 'progress_tracker' not in st.session_state:
        st.session_state.progress_tracker = EnhancedProgressTracker()
    return st.session_state.progress_tracker


def get_mapping_tracker() -> MappingProgressTracker:
    """Get or create the mapping progress tracker instance"""
    if 'mapping_tracker' not in st.session_state:
        st.session_state.mapping_tracker = MappingProgressTracker()
    return st.session_state.mapping_tracker