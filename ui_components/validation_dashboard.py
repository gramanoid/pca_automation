"""
Validation Dashboard Component for PCA Automation
Provides visual representation of validation results
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any, Optional

class ValidationDashboard:
    """Component for displaying validation results in a dashboard format"""
    
    def __init__(self):
        self.theme_colors = {
            'success': '#28a745',
            'error': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'primary': '#1f77b4',
            'secondary': '#ff7f0e'
        }
    
    def create_validation_pie_chart(self, passed: int, failed: int, warnings: int = 0) -> go.Figure:
        """Create a pie chart showing validation results"""
        labels = []
        values = []
        colors = []
        
        if passed > 0:
            labels.append('Passed')
            values.append(passed)
            colors.append(self.theme_colors['success'])
        
        if failed > 0:
            labels.append('Failed')
            values.append(failed)
            colors.append(self.theme_colors['error'])
        
        if warnings > 0:
            labels.append('Warnings')
            values.append(warnings)
            colors.append(self.theme_colors['warning'])
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker_colors=colors,
            textinfo='label+percent',
            textposition='auto',
            hovertemplate='%{label}: %{value} checks<br>%{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title='Validation Results Distribution',
            height=300,
            showlegend=True,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    def create_quality_score_gauge(self, score: float) -> go.Figure:
        """Create a gauge chart for data quality score"""
        # Determine color based on score
        if score >= 90:
            color = self.theme_colors['success']
        elif score >= 70:
            color = self.theme_colors['warning']
        else:
            color = self.theme_colors['error']
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Data Quality Score", 'font': {'size': 20}},
            delta = {'reference': 100, 'increasing': {'color': "green"}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig
    
    def create_validation_details_df(self, validation_results: Dict[str, Any]) -> pd.DataFrame:
        """Create a dataframe with validation details"""
        details = []
        
        # Add check results
        checks = validation_results.get('checks', {})
        for check_name, check_result in checks.items():
            details.append({
                'Check': check_name,
                'Status': '✅ Passed' if check_result.get('passed', False) else '❌ Failed',
                'Message': check_result.get('message', ''),
                'Severity': check_result.get('severity', 'Info')
            })
        
        # Add warnings
        for warning in validation_results.get('warnings', []):
            details.append({
                'Check': 'Data Warning',
                'Status': '⚠️ Warning',
                'Message': warning,
                'Severity': 'Warning'
            })
        
        # Add errors
        for error in validation_results.get('errors', []):
            details.append({
                'Check': 'Data Error',
                'Status': '❌ Error',
                'Message': error,
                'Severity': 'Error'
            })
        
        return pd.DataFrame(details)
    
    def render_validation_summary_cards(self, validation_results: Dict[str, Any]):
        """Render summary cards for validation results"""
        col1, col2, col3, col4 = st.columns(4)
        
        total_checks = validation_results.get('total_checks', 0)
        passed_checks = validation_results.get('passed_checks', 0)
        warnings = len(validation_results.get('warnings', []))
        errors = len(validation_results.get('errors', []))
        
        with col1:
            st.metric(
                "Total Checks",
                total_checks,
                help="Total number of validation checks performed"
            )
        
        with col2:
            success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
            st.metric(
                "Success Rate",
                f"{success_rate:.1f}%",
                delta=f"{passed_checks}/{total_checks} passed",
                delta_color="normal" if success_rate >= 90 else "inverse"
            )
        
        with col3:
            st.metric(
                "Warnings",
                warnings,
                delta=None if warnings == 0 else f"{warnings} issues",
                delta_color="inverse" if warnings > 0 else "off"
            )
        
        with col4:
            st.metric(
                "Errors",
                errors,
                delta=None if errors == 0 else f"{errors} critical",
                delta_color="inverse" if errors > 0 else "off"
            )
    
    def render_validation_dashboard(self, validation_results: Dict[str, Any]):
        """Render the complete validation dashboard"""
        st.markdown("### 📊 Validation Results Dashboard")
        
        # Summary cards
        self.render_validation_summary_cards(validation_results)
        
        st.markdown("---")
        
        # Visual charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            total_checks = validation_results.get('total_checks', 0)
            passed_checks = validation_results.get('passed_checks', 0)
            failed_checks = total_checks - passed_checks
            warnings = len(validation_results.get('warnings', []))
            
            fig_pie = self.create_validation_pie_chart(passed_checks, failed_checks, warnings)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Quality score gauge
            success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
            fig_gauge = self.create_quality_score_gauge(success_rate)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Detailed results table
        st.markdown("### 📋 Detailed Validation Results")
        
        # Create tabs for different result types
        tabs = st.tabs(["All Results", "Errors Only", "Warnings Only", "Passed Checks"])
        
        df_details = self.create_validation_details_df(validation_results)
        
        with tabs[0]:
            if not df_details.empty:
                st.dataframe(
                    df_details,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Status": st.column_config.TextColumn(width="small"),
                        "Severity": st.column_config.TextColumn(width="small")
                    }
                )
            else:
                st.info("No validation results to display")
        
        with tabs[1]:
            errors_df = df_details[df_details['Status'].str.contains('Error')]
            if not errors_df.empty:
                st.dataframe(errors_df, use_container_width=True, hide_index=True)
            else:
                st.success("No errors found!")
        
        with tabs[2]:
            warnings_df = df_details[df_details['Status'].str.contains('Warning')]
            if not warnings_df.empty:
                st.dataframe(warnings_df, use_container_width=True, hide_index=True)
            else:
                st.success("No warnings found!")
        
        with tabs[3]:
            passed_df = df_details[df_details['Status'].str.contains('Passed')]
            if not passed_df.empty:
                st.dataframe(passed_df, use_container_width=True, hide_index=True)
            else:
                st.info("No passed checks to display")
    
    def render_quick_stats(self, validation_results: Dict[str, Any]):
        """Render quick statistics in a compact format"""
        total_checks = validation_results.get('total_checks', 0)
        passed_checks = validation_results.get('passed_checks', 0)
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Create a colored progress bar based on success rate
        progress_color = "green" if success_rate >= 90 else "orange" if success_rate >= 70 else "red"
        
        st.markdown(f"""
        <div style="text-align: center;">
            <h4>Validation Score: {success_rate:.1f}%</h4>
            <div style="background-color: #e0e0e0; border-radius: 10px; padding: 3px;">
                <div style="background-color: {progress_color}; width: {success_rate}%; 
                           height: 20px; border-radius: 7px;"></div>
            </div>
            <p style="margin-top: 10px;">{passed_checks} of {total_checks} checks passed</p>
        </div>
        """, unsafe_allow_html=True)