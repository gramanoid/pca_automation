"""
Performance Monitor - Track timing, memory usage, and file sizes
"""

import streamlit as st
import time
import psutil
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

class PerformanceMonitor:
    """Monitor and display performance metrics"""
    
    def __init__(self):
        # Initialize performance tracking in session state
        if 'performance_metrics' not in st.session_state:
            st.session_state.performance_metrics = {
                'stage_timings': {},
                'memory_usage': [],
                'file_sizes': {},
                'start_time': datetime.now(),
                'warnings': []
            }
        
        # File size thresholds (in MB)
        self.size_thresholds = {
            'warning': 50,  # 50 MB
            'critical': 100  # 100 MB
        }
        
        # Memory usage threshold (in %)
        self.memory_threshold = 80
    
    def start_stage(self, stage_name: str):
        """Start timing a stage"""
        st.session_state.performance_metrics['stage_timings'][stage_name] = {
            'start': time.time(),
            'end': None,
            'duration': None
        }
    
    def end_stage(self, stage_name: str):
        """End timing a stage"""
        if stage_name in st.session_state.performance_metrics['stage_timings']:
            end_time = time.time()
            start_time = st.session_state.performance_metrics['stage_timings'][stage_name]['start']
            duration = end_time - start_time
            
            st.session_state.performance_metrics['stage_timings'][stage_name]['end'] = end_time
            st.session_state.performance_metrics['stage_timings'][stage_name]['duration'] = duration
            
            # Check if stage took too long
            if duration > 30:  # More than 30 seconds
                warning = f"Stage '{stage_name}' took {duration:.1f} seconds"
                st.session_state.performance_metrics['warnings'].append({
                    'type': 'timing',
                    'message': warning,
                    'timestamp': datetime.now()
                })
    
    def check_memory_usage(self):
        """Check current memory usage"""
        memory_percent = psutil.virtual_memory().percent
        
        # Record memory usage
        st.session_state.performance_metrics['memory_usage'].append({
            'timestamp': datetime.now(),
            'percent': memory_percent,
            'available_mb': psutil.virtual_memory().available / (1024 * 1024)
        })
        
        # Check threshold
        if memory_percent > self.memory_threshold:
            warning = f"High memory usage: {memory_percent:.1f}%"
            st.session_state.performance_metrics['warnings'].append({
                'type': 'memory',
                'message': warning,
                'timestamp': datetime.now()
            })
            st.warning(warning)
        
        return memory_percent
    
    def check_file_size(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Check file size and warn if too large"""
        try:
            size_bytes = os.path.getsize(file_path)
            size_mb = size_bytes / (1024 * 1024)
            
            result = {
                'path': file_path,
                'type': file_type,
                'size_bytes': size_bytes,
                'size_mb': size_mb,
                'warning': None
            }
            
            # Store file size
            st.session_state.performance_metrics['file_sizes'][file_type] = result
            
            # Check thresholds
            if size_mb > self.size_thresholds['critical']:
                result['warning'] = 'critical'
                warning = f"{file_type} file is very large: {size_mb:.1f} MB"
                st.session_state.performance_metrics['warnings'].append({
                    'type': 'file_size',
                    'message': warning,
                    'timestamp': datetime.now()
                })
                st.error(f"⚠️ {warning}")
            elif size_mb > self.size_thresholds['warning']:
                result['warning'] = 'warning'
                warning = f"{file_type} file is large: {size_mb:.1f} MB"
                st.warning(f"⚠️ {warning}")
            
            return result
        except Exception as e:
            return {
                'error': str(e),
                'path': file_path,
                'type': file_type
            }
    
    def get_stage_summary(self) -> List[Dict[str, Any]]:
        """Get summary of stage timings"""
        summary = []
        for stage, timing in st.session_state.performance_metrics['stage_timings'].items():
            if timing['duration'] is not None:
                summary.append({
                    'stage': stage,
                    'duration': timing['duration'],
                    'duration_str': self._format_duration(timing['duration'])
                })
        return summary
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.0f}s"
    
    def create_performance_chart(self) -> go.Figure:
        """Create a performance timeline chart"""
        stages = self.get_stage_summary()
        
        if not stages:
            return None
        
        # Create Gantt-like chart
        fig = go.Figure()
        
        y_labels = []
        for i, stage in enumerate(stages):
            y_labels.append(stage['stage'])
            
            fig.add_trace(go.Bar(
                x=[stage['duration']],
                y=[i],
                orientation='h',
                name=stage['stage'],
                text=stage['duration_str'],
                textposition='inside',
                hovertemplate=f"{stage['stage']}: {stage['duration_str']}<extra></extra>"
            ))
        
        fig.update_layout(
            title="Stage Processing Times",
            xaxis_title="Duration (seconds)",
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(len(y_labels))),
                ticktext=y_labels
            ),
            height=300,
            showlegend=False,
            margin=dict(l=150, r=20, t=40, b=40)
        )
        
        return fig
    
    def create_memory_chart(self) -> go.Figure:
        """Create memory usage chart"""
        memory_data = st.session_state.performance_metrics['memory_usage']
        
        if not memory_data:
            return None
        
        # Extract data
        timestamps = [m['timestamp'] for m in memory_data]
        percentages = [m['percent'] for m in memory_data]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=percentages,
            mode='lines+markers',
            name='Memory Usage',
            line=dict(color='#ff6b6b', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 107, 0.2)'
        ))
        
        # Add threshold line
        fig.add_hline(
            y=self.memory_threshold,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Warning Threshold ({self.memory_threshold}%)"
        )
        
        fig.update_layout(
            title="Memory Usage Over Time",
            xaxis_title="Time",
            yaxis_title="Memory Usage (%)",
            height=300,
            yaxis=dict(range=[0, 100]),
            margin=dict(l=60, r=20, t=40, b=40)
        )
        
        return fig
    
    def render_performance_dashboard(self):
        """Render the performance monitoring dashboard"""
        st.subheader("⚡ Performance Metrics")
        
        # Check current memory
        current_memory = self.check_memory_usage()
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_time = sum(s['duration'] for s in self.get_stage_summary() if s['duration'])
            st.metric(
                "Total Processing Time",
                self._format_duration(total_time) if total_time > 0 else "0s"
            )
        
        with col2:
            st.metric(
                "Current Memory Usage",
                f"{current_memory:.1f}%",
                delta=f"{current_memory - 50:.1f}%" if current_memory > 50 else None,
                delta_color="inverse"
            )
        
        with col3:
            file_count = len(st.session_state.performance_metrics['file_sizes'])
            total_size = sum(f.get('size_mb', 0) for f in st.session_state.performance_metrics['file_sizes'].values())
            st.metric(
                "Total File Size",
                f"{total_size:.1f} MB",
                help=f"{file_count} files processed"
            )
        
        with col4:
            warning_count = len(st.session_state.performance_metrics['warnings'])
            st.metric(
                "Performance Warnings",
                warning_count,
                delta=None if warning_count == 0 else f"{warning_count} issues",
                delta_color="inverse" if warning_count > 0 else "off"
            )
        
        # Charts
        if self.get_stage_summary():
            col1, col2 = st.columns(2)
            
            with col1:
                perf_chart = self.create_performance_chart()
                if perf_chart:
                    st.plotly_chart(perf_chart, use_container_width=True)
            
            with col2:
                mem_chart = self.create_memory_chart()
                if mem_chart:
                    st.plotly_chart(mem_chart, use_container_width=True)
        
        # Warnings
        if st.session_state.performance_metrics['warnings']:
            with st.expander("⚠️ Performance Warnings", expanded=True):
                for warning in st.session_state.performance_metrics['warnings'][-5:]:  # Show last 5
                    warning_time = warning['timestamp'].strftime('%H:%M:%S')
                    st.warning(f"[{warning_time}] {warning['message']}")
        
        # Detailed metrics
        with st.expander("📊 Detailed Metrics", expanded=False):
            # Stage timings table
            if self.get_stage_summary():
                st.write("**Stage Timings:**")
                df_stages = pd.DataFrame(self.get_stage_summary())
                df_stages = df_stages[['stage', 'duration_str']].rename(
                    columns={'stage': 'Stage', 'duration_str': 'Duration'}
                )
                st.dataframe(df_stages, use_container_width=True, hide_index=True)
            
            # File sizes table
            if st.session_state.performance_metrics['file_sizes']:
                st.write("**File Sizes:**")
                file_data = []
                for file_type, info in st.session_state.performance_metrics['file_sizes'].items():
                    if 'size_mb' in info:
                        file_data.append({
                            'File Type': file_type,
                            'Size': f"{info['size_mb']:.1f} MB",
                            'Status': '⚠️ Large' if info.get('warning') else '✅ OK'
                        })
                if file_data:
                    df_files = pd.DataFrame(file_data)
                    st.dataframe(df_files, use_container_width=True, hide_index=True)
    
    def export_performance_report(self) -> str:
        """Export performance metrics as JSON"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_duration': sum(s['duration'] for s in self.get_stage_summary() if s['duration']),
            'stage_timings': self.get_stage_summary(),
            'memory_usage': {
                'peak': max(m['percent'] for m in st.session_state.performance_metrics['memory_usage']) if st.session_state.performance_metrics['memory_usage'] else 0,
                'average': sum(m['percent'] for m in st.session_state.performance_metrics['memory_usage']) / len(st.session_state.performance_metrics['memory_usage']) if st.session_state.performance_metrics['memory_usage'] else 0
            },
            'file_sizes': st.session_state.performance_metrics['file_sizes'],
            'warnings': [
                {
                    'type': w['type'],
                    'message': w['message'],
                    'timestamp': w['timestamp'].isoformat()
                }
                for w in st.session_state.performance_metrics['warnings']
            ]
        }
        
        return json.dumps(report, indent=2)