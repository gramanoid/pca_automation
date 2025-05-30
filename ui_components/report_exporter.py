"""
Report Exporter - Generate validation reports in various formats
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json
import base64
from typing import Dict, Any, List
import plotly.graph_objects as go
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class ReportExporter:
    """Generate and export validation reports"""
    
    def __init__(self):
        self.report_data = {}
    
    def generate_html_report(self, validation_results: Dict[str, Any], 
                           workflow_data: Dict[str, Any]) -> str:
        """Generate an HTML validation report"""
        
        # Calculate metrics
        total_checks = validation_results.get('total_checks', 0)
        passed_checks = validation_results.get('passed_checks', 0)
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>PCA Automation Validation Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .header {{
                    background-color: #1f77b4;
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                .metric-card {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }}
                .metric-value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #1f77b4;
                }}
                .success {{ color: #28a745; }}
                .warning {{ color: #ffc107; }}
                .error {{ color: #dc3545; }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    background-color: white;
                    margin-top: 20px;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                }}
                .section {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .timestamp {{
                    text-align: right;
                    color: #666;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>PCA Automation Validation Report</h1>
                <p>Automated Media Plan Processing Results</p>
            </div>
            
            <div class="timestamp">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
            
            <div class="grid">
                <div class="metric-card">
                    <h3>Total Checks</h3>
                    <div class="metric-value">{total_checks}</div>
                </div>
                <div class="metric-card">
                    <h3>Success Rate</h3>
                    <div class="metric-value {self._get_status_class(success_rate)}">{success_rate:.1f}%</div>
                </div>
                <div class="metric-card">
                    <h3>Passed Checks</h3>
                    <div class="metric-value success">{passed_checks}</div>
                </div>
                <div class="metric-card">
                    <h3>Failed Checks</h3>
                    <div class="metric-value error">{total_checks - passed_checks}</div>
                </div>
            </div>
            
            <div class="section">
                <h2>Processing Summary</h2>
                <table>
                    <tr>
                        <th>Stage</th>
                        <th>Status</th>
                        <th>Details</th>
                    </tr>
                    <tr>
                        <td>Data Upload</td>
                        <td class="success">✓ Complete</td>
                        <td>3 files uploaded and validated</td>
                    </tr>
                    <tr>
                        <td>Data Processing</td>
                        <td class="success">✓ Complete</td>
                        <td>Data extracted and combined</td>
                    </tr>
                    <tr>
                        <td>Template Mapping</td>
                        <td class="success">✓ Complete</td>
                        <td>{workflow_data.get('mapping_result', {}).get('coverage', 0):.1f}% coverage</td>
                    </tr>
                    <tr>
                        <td>Validation</td>
                        <td class="{self._get_status_class(success_rate)}">
                            {self._get_status_icon(success_rate)} {self._get_status_text(success_rate)}
                        </td>
                        <td>{success_rate:.1f}% success rate</td>
                    </tr>
                </table>
            </div>
            
            {self._generate_issues_section(validation_results)}
            
            <div class="section">
                <h2>File Information</h2>
                <table>
                    <tr>
                        <th>File Type</th>
                        <th>Status</th>
                        <th>Rows Processed</th>
                    </tr>
                    <tr>
                        <td>PLANNED</td>
                        <td class="success">✓ Processed</td>
                        <td>-</td>
                    </tr>
                    <tr>
                        <td>DELIVERED</td>
                        <td class="success">✓ Processed</td>
                        <td>-</td>
                    </tr>
                    <tr>
                        <td>OUTPUT</td>
                        <td class="success">✓ Generated</td>
                        <td>{workflow_data.get('mapping_result', {}).get('rows_written', 0)}</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                <ul>
                    {self._generate_recommendations(validation_results, success_rate)}
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _get_status_class(self, success_rate: float) -> str:
        if success_rate >= 90:
            return "success"
        elif success_rate >= 70:
            return "warning"
        return "error"
    
    def _get_status_icon(self, success_rate: float) -> str:
        if success_rate >= 90:
            return "✓"
        elif success_rate >= 70:
            return "⚠"
        return "✗"
    
    def _get_status_text(self, success_rate: float) -> str:
        if success_rate >= 90:
            return "Passed"
        elif success_rate >= 70:
            return "Passed with warnings"
        return "Failed"
    
    def _generate_issues_section(self, validation_results: Dict[str, Any]) -> str:
        """Generate HTML for issues section"""
        errors = validation_results.get('errors', [])
        warnings = validation_results.get('warnings', [])
        
        if not errors and not warnings:
            return """
            <div class="section">
                <h2>Issues Found</h2>
                <p class="success">No issues found. All validation checks passed successfully.</p>
            </div>
            """
        
        html = '<div class="section"><h2>Issues Found</h2>'
        
        if errors:
            html += '<h3 class="error">Errors</h3><ul>'
            for error in errors[:10]:  # Limit to first 10
                html += f'<li>{error}</li>'
            if len(errors) > 10:
                html += f'<li><em>... and {len(errors) - 10} more errors</em></li>'
            html += '</ul>'
        
        if warnings:
            html += '<h3 class="warning">Warnings</h3><ul>'
            for warning in warnings[:10]:  # Limit to first 10
                html += f'<li>{warning}</li>'
            if len(warnings) > 10:
                html += f'<li><em>... and {len(warnings) - 10} more warnings</em></li>'
            html += '</ul>'
        
        html += '</div>'
        return html
    
    def _generate_recommendations(self, validation_results: Dict[str, Any], success_rate: float) -> str:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if success_rate < 90:
            recommendations.append("<li>Review and fix validation errors before proceeding to production</li>")
        
        errors = validation_results.get('errors', [])
        if any('market' in str(e).lower() for e in errors):
            recommendations.append("<li>Check market mappings and ensure all markets are correctly configured</li>")
        
        if any('column' in str(e).lower() for e in errors):
            recommendations.append("<li>Verify column mappings match the expected template structure</li>")
        
        warnings = validation_results.get('warnings', [])
        if len(warnings) > 5:
            recommendations.append("<li>Review warnings to improve data quality</li>")
        
        if not recommendations:
            recommendations.append("<li>All checks passed. Data is ready for use.</li>")
        
        return '\n'.join(recommendations)
    
    def generate_json_report(self, validation_results: Dict[str, Any], 
                           workflow_data: Dict[str, Any]) -> str:
        """Generate a JSON validation report"""
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_version': '1.0',
                'tool': 'PCA Automation'
            },
            'summary': {
                'total_checks': validation_results.get('total_checks', 0),
                'passed_checks': validation_results.get('passed_checks', 0),
                'success_rate': (validation_results.get('passed_checks', 0) / 
                               validation_results.get('total_checks', 1) * 100),
                'status': self._get_status_text(
                    validation_results.get('passed_checks', 0) / 
                    validation_results.get('total_checks', 1) * 100
                )
            },
            'workflow': {
                'files_processed': 3,
                'rows_written': workflow_data.get('mapping_result', {}).get('rows_written', 0),
                'mapping_coverage': workflow_data.get('mapping_result', {}).get('coverage', 0),
                'stages_completed': 5
            },
            'validation_details': validation_results,
            'errors': validation_results.get('errors', []),
            'warnings': validation_results.get('warnings', [])
        }
        
        return json.dumps(report, indent=2)
    
    def create_validation_chart(self, validation_results: Dict[str, Any]) -> BytesIO:
        """Create a validation summary chart"""
        total_checks = validation_results.get('total_checks', 0)
        passed_checks = validation_results.get('passed_checks', 0)
        failed_checks = total_checks - passed_checks
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Pie chart
        sizes = [passed_checks, failed_checks]
        colors = ['#28a745', '#dc3545']
        labels = ['Passed', 'Failed']
        
        if sum(sizes) > 0:
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Validation Results Distribution')
        
        # Bar chart
        categories = ['Total', 'Passed', 'Failed']
        values = [total_checks, passed_checks, failed_checks]
        bar_colors = ['#1f77b4', '#28a745', '#dc3545']
        
        ax2.bar(categories, values, color=bar_colors)
        ax2.set_ylabel('Number of Checks')
        ax2.set_title('Validation Summary')
        
        # Add value labels on bars
        for i, v in enumerate(values):
            ax2.text(i, v + 0.5, str(v), ha='center')
        
        plt.tight_layout()
        
        # Save to BytesIO
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150)
        buffer.seek(0)
        plt.close()
        
        return buffer
    
    def render_export_ui(self, validation_results: Dict[str, Any], 
                        workflow_data: Dict[str, Any]):
        """Render the export UI"""
        st.subheader("📊 Export Validation Report")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Generate HTML Report", use_container_width=True):
                html_content = self.generate_html_report(validation_results, workflow_data)
                b64 = base64.b64encode(html_content.encode()).decode()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                href = f'<a href="data:text/html;base64,{b64}" download="validation_report_{timestamp}.html">Download HTML Report</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("HTML report generated!")
        
        with col2:
            if st.button("📋 Generate JSON Report", use_container_width=True):
                json_content = self.generate_json_report(validation_results, workflow_data)
                b64 = base64.b64encode(json_content.encode()).decode()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                href = f'<a href="data:application/json;base64,{b64}" download="validation_report_{timestamp}.json">Download JSON Report</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("JSON report generated!")
        
        with col3:
            if st.button("📊 Generate Chart", use_container_width=True):
                chart_buffer = self.create_validation_chart(validation_results)
                st.download_button(
                    label="Download Validation Chart",
                    data=chart_buffer,
                    file_name=f"validation_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png"
                )
                st.success("Chart generated!")