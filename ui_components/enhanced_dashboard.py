"""
Enhanced Dashboard - Time-series views and historical comparisons
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import numpy as np

class EnhancedDashboard:
    """Enhanced dashboard with time-series and comparison features"""
    
    def __init__(self):
        # Initialize history in session state
        if 'validation_history' not in st.session_state:
            st.session_state.validation_history = []
        if 'dashboard_settings' not in st.session_state:
            st.session_state.dashboard_settings = {
                'show_trend': True,
                'comparison_window': 7,  # days
                'metric_focus': 'success_rate'
            }
    
    def save_validation_run(self, validation_results: Dict[str, Any], 
                           workflow_data: Dict[str, Any]):
        """Save current validation run to history"""
        run_data = {
            'timestamp': datetime.now().isoformat(),
            'success_rate': (validation_results.get('passed_checks', 0) / 
                           validation_results.get('total_checks', 1) * 100),
            'total_checks': validation_results.get('total_checks', 0),
            'passed_checks': validation_results.get('passed_checks', 0),
            'errors': len(validation_results.get('errors', [])),
            'warnings': len(validation_results.get('warnings', [])),
            'rows_processed': workflow_data.get('mapping_result', {}).get('rows_written', 0),
            'coverage': workflow_data.get('mapping_result', {}).get('coverage', 0),
            'processing_time': sum(
                m.get('duration', 0) 
                for m in st.session_state.get('performance_metrics', {}).get('stage_timings', {}).values()
            )
        }
        
        st.session_state.validation_history.append(run_data)
        
        # Limit history size
        max_history = 100
        if len(st.session_state.validation_history) > max_history:
            st.session_state.validation_history = st.session_state.validation_history[-max_history:]
    
    def create_time_series_chart(self, metric: str = 'success_rate') -> go.Figure:
        """Create time series chart for selected metric"""
        history = st.session_state.validation_history
        
        if not history:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Create figure
        fig = go.Figure()
        
        # Add main metric line
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df[metric],
            mode='lines+markers',
            name=self._get_metric_label(metric),
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=8)
        ))
        
        # Add trend line if enabled
        if st.session_state.dashboard_settings['show_trend'] and len(df) > 3:
            z = np.polyfit(range(len(df)), df[metric], 1)
            p = np.poly1d(z)
            trend_values = p(range(len(df)))
            
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=trend_values,
                mode='lines',
                name='Trend',
                line=dict(color='red', width=1, dash='dash')
            ))
        
        # Add threshold lines for success rate
        if metric == 'success_rate':
            fig.add_hline(y=90, line_dash="dash", line_color="green", 
                         annotation_text="Target (90%)")
            fig.add_hline(y=70, line_dash="dash", line_color="orange", 
                         annotation_text="Warning (70%)")
        
        fig.update_layout(
            title=f"{self._get_metric_label(metric)} Over Time",
            xaxis_title="Date",
            yaxis_title=self._get_metric_label(metric),
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def create_comparison_chart(self, current_results: Dict[str, Any]) -> go.Figure:
        """Create comparison chart with previous runs"""
        history = st.session_state.validation_history
        
        if not history:
            return None
        
        # Get comparison window
        window_days = st.session_state.dashboard_settings['comparison_window']
        cutoff_date = datetime.now() - timedelta(days=window_days)
        
        # Filter history
        recent_runs = [
            run for run in history 
            if datetime.fromisoformat(run['timestamp']) > cutoff_date
        ]
        
        if not recent_runs:
            return None
        
        # Calculate averages
        avg_success = np.mean([r['success_rate'] for r in recent_runs])
        avg_errors = np.mean([r['errors'] for r in recent_runs])
        avg_warnings = np.mean([r['warnings'] for r in recent_runs])
        
        # Current values
        current_success = (current_results.get('passed_checks', 0) / 
                         current_results.get('total_checks', 1) * 100)
        current_errors = len(current_results.get('errors', []))
        current_warnings = len(current_results.get('warnings', []))
        
        # Create comparison data
        categories = ['Success Rate', 'Errors', 'Warnings']
        current_values = [current_success, current_errors, current_warnings]
        avg_values = [avg_success, avg_errors, avg_warnings]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Current Run',
            x=categories,
            y=current_values,
            marker_color='#1f77b4'
        ))
        
        fig.add_trace(go.Bar(
            name=f'{window_days}-Day Average',
            x=categories,
            y=avg_values,
            marker_color='#ff7f0e'
        ))
        
        fig.update_layout(
            title=f"Current vs {window_days}-Day Average",
            yaxis_title="Value",
            barmode='group',
            height=400
        )
        
        return fig
    
    def create_column_impact_chart(self, validation_results: Dict[str, Any]) -> go.Figure:
        """Show which columns have improved or degraded"""
        # This would require column-level tracking in validation results
        # For now, create a sample visualization
        
        # Sample data - in production, this would come from actual column validation
        columns = ['Market', 'Campaign', 'Budget', 'Impressions', 'Clicks', 'CPM']
        improvements = [5, -2, 3, 0, -1, 4]  # Percentage change
        
        colors = ['green' if x >= 0 else 'red' for x in improvements]
        
        fig = go.Figure(go.Bar(
            x=columns,
            y=improvements,
            marker_color=colors,
            text=[f"{x:+.0f}%" for x in improvements],
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Column Quality Changes",
            yaxis_title="Change (%)",
            height=300,
            yaxis=dict(range=[-10, 10])
        )
        
        fig.add_hline(y=0, line_color="black", line_width=1)
        
        return fig
    
    def _get_metric_label(self, metric: str) -> str:
        """Get human-readable label for metric"""
        labels = {
            'success_rate': 'Success Rate (%)',
            'total_checks': 'Total Checks',
            'passed_checks': 'Passed Checks',
            'errors': 'Error Count',
            'warnings': 'Warning Count',
            'rows_processed': 'Rows Processed',
            'coverage': 'Coverage (%)',
            'processing_time': 'Processing Time (s)'
        }
        return labels.get(metric, metric)
    
    def render_enhanced_dashboard(self, validation_results: Dict[str, Any], 
                                workflow_data: Dict[str, Any]):
        """Render the enhanced dashboard"""
        st.subheader("📊 Enhanced Analytics Dashboard")
        
        # Save current run
        self.save_validation_run(validation_results, workflow_data)
        
        # Dashboard settings
        with st.expander("⚙️ Dashboard Settings", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                metric = st.selectbox(
                    "Primary Metric",
                    options=['success_rate', 'total_checks', 'errors', 'warnings', 
                            'rows_processed', 'coverage', 'processing_time'],
                    format_func=self._get_metric_label,
                    index=0
                )
                st.session_state.dashboard_settings['metric_focus'] = metric
            
            with col2:
                window = st.slider(
                    "Comparison Window (days)",
                    min_value=1,
                    max_value=30,
                    value=st.session_state.dashboard_settings['comparison_window']
                )
                st.session_state.dashboard_settings['comparison_window'] = window
            
            with col3:
                show_trend = st.checkbox(
                    "Show Trend Line",
                    value=st.session_state.dashboard_settings['show_trend']
                )
                st.session_state.dashboard_settings['show_trend'] = show_trend
        
        # Key insights
        if len(st.session_state.validation_history) > 1:
            col1, col2, col3, col4 = st.columns(4)
            
            # Calculate insights
            recent_success_rates = [
                r['success_rate'] for r in st.session_state.validation_history[-5:]
            ]
            trend = "📈 Improving" if recent_success_rates[-1] > recent_success_rates[0] else "📉 Declining"
            
            with col1:
                st.metric(
                    "Current Success Rate",
                    f"{recent_success_rates[-1]:.1f}%",
                    delta=f"{recent_success_rates[-1] - recent_success_rates[-2]:.1f}%" if len(recent_success_rates) > 1 else None
                )
            
            with col2:
                avg_success = np.mean(recent_success_rates)
                st.metric(
                    "5-Run Average",
                    f"{avg_success:.1f}%"
                )
            
            with col3:
                st.metric(
                    "Trend",
                    trend
                )
            
            with col4:
                best_run = max(r['success_rate'] for r in st.session_state.validation_history)
                st.metric(
                    "Best Run",
                    f"{best_run:.1f}%"
                )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            time_series = self.create_time_series_chart(metric)
            if time_series:
                st.plotly_chart(time_series, use_container_width=True)
            else:
                st.info("No historical data available yet")
        
        with col2:
            comparison = self.create_comparison_chart(validation_results)
            if comparison:
                st.plotly_chart(comparison, use_container_width=True)
            else:
                st.info("No comparison data available yet")
        
        # Column impact (if available)
        if validation_results.get('column_metrics'):
            impact_chart = self.create_column_impact_chart(validation_results)
            st.plotly_chart(impact_chart, use_container_width=True)
        
        # Historical data table
        if st.session_state.validation_history:
            with st.expander("📋 Historical Data", expanded=False):
                df_history = pd.DataFrame(st.session_state.validation_history)
                df_history['timestamp'] = pd.to_datetime(df_history['timestamp'])
                df_history = df_history.sort_values('timestamp', ascending=False)
                
                # Format columns
                display_cols = ['timestamp', 'success_rate', 'total_checks', 
                              'errors', 'warnings', 'processing_time']
                df_display = df_history[display_cols].head(20)
                
                # Rename columns
                df_display.columns = ['Date/Time', 'Success %', 'Checks', 
                                    'Errors', 'Warnings', 'Time (s)']
                
                # Format values
                df_display['Success %'] = df_display['Success %'].apply(lambda x: f"{x:.1f}%")
                df_display['Time (s)'] = df_display['Time (s)'].apply(lambda x: f"{x:.1f}s")
                df_display['Date/Time'] = df_display['Date/Time'].dt.strftime('%Y-%m-%d %H:%M')
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Export historical data
        if st.button("📥 Export Historical Data", use_container_width=True):
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'history': st.session_state.validation_history,
                'summary': {
                    'total_runs': len(st.session_state.validation_history),
                    'average_success_rate': np.mean([r['success_rate'] for r in st.session_state.validation_history]),
                    'best_run': max(r['success_rate'] for r in st.session_state.validation_history) if st.session_state.validation_history else 0
                }
            }
            
            json_str = json.dumps(export_data, indent=2)
            st.download_button(
                label="Download Historical Data (JSON)",
                data=json_str,
                file_name=f"validation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )