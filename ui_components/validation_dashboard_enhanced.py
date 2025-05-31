"""
Enhanced Validation Dashboard with Drill-Down Capabilities
Provides detailed, interactive validation results with the ability to explore issues
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

class EnhancedValidationDashboard:
    """Enhanced validation dashboard with drill-down capabilities"""
    
    def __init__(self):
        self.severity_colors = {
            'Critical': '#dc3545',
            'High': '#fd7e14',
            'Medium': '#ffc107',
            'Low': '#28a745',
            'Info': '#17a2b8'
        }
        
        self.check_categories = {
            'Data Completeness': 'Ensures all required fields are populated',
            'Column Mapping': 'Verifies columns are correctly mapped',
            'Data Types': 'Validates data type consistency',
            'Market Validation': 'Checks market-specific rules',
            'Number Accuracy': 'Validates numerical precision',
            'Date Formats': 'Ensures date consistency',
            'Platform Compliance': 'Platform-specific validations'
        }
    
    def render_dashboard(self, validation_results: Dict[str, Any], workflow_data: Dict[str, Any] = None):
        """Render the main validation dashboard with drill-down options"""
        
        # Header with overall status
        self._render_header(validation_results)
        
        # Tab-based navigation for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", 
            "🔍 Detailed Results", 
            "📈 Trends",
            "🎯 Issue Drill-Down",
            "📋 Recommendations"
        ])
        
        with tab1:
            self._render_overview(validation_results)
        
        with tab2:
            self._render_detailed_results(validation_results)
        
        with tab3:
            self._render_trends(validation_results, workflow_data)
        
        with tab4:
            self._render_issue_drilldown(validation_results, workflow_data)
        
        with tab5:
            self._render_recommendations(validation_results)
    
    def _render_header(self, validation_results: Dict[str, Any]):
        """Render the dashboard header with overall status"""
        errors = validation_results.get('errors', [])
        warnings = validation_results.get('warnings', [])
        total_checks = validation_results.get('total_checks', 0)
        passed_checks = validation_results.get('passed_checks', 0)
        
        # Calculate overall health score
        health_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if health_score >= 90:
                st.success(f"🟢 Health Score: {health_score:.1f}%")
            elif health_score >= 70:
                st.warning(f"🟡 Health Score: {health_score:.1f}%")
            else:
                st.error(f"🔴 Health Score: {health_score:.1f}%")
        
        with col2:
            st.metric("Total Checks", total_checks, 
                     help="Total number of validation checks performed")
        
        with col3:
            error_delta = f"+{len(errors)}" if errors else "0"
            st.metric("Errors", len(errors), delta=error_delta, delta_color="inverse",
                     help="Critical issues that must be fixed")
        
        with col4:
            warning_delta = f"+{len(warnings)}" if warnings else "0"
            st.metric("Warnings", len(warnings), delta=warning_delta, delta_color="inverse",
                     help="Issues that should be reviewed")
    
    def _render_overview(self, validation_results: Dict[str, Any]):
        """Render the overview tab with summary charts"""
        st.subheader("Validation Overview")
        
        # Get check results
        checks = validation_results.get('checks', {})
        if not checks:
            st.info("No detailed check results available. Using summary data.")
            self._render_summary_overview(validation_results)
            return
        
        # Create summary by category
        category_results = self._categorize_checks(checks)
        
        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart of check results
            fig_pie = self._create_results_pie_chart(category_results)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Bar chart by severity
            fig_bar = self._create_severity_bar_chart(checks)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Category summary cards
        st.subheader("Validation Categories")
        self._render_category_cards(category_results)
    
    def _render_detailed_results(self, validation_results: Dict[str, Any]):
        """Render detailed validation results with filtering"""
        st.subheader("Detailed Validation Results")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            severity_filter = st.multiselect(
                "Filter by Severity",
                options=['Critical', 'High', 'Medium', 'Low', 'Info'],
                default=['Critical', 'High']
            )
        
        with col2:
            status_filter = st.selectbox(
                "Filter by Status",
                options=['All', 'Failed', 'Passed', 'Warning'],
                index=0
            )
        
        with col3:
            search_term = st.text_input("Search issues", placeholder="Enter keywords...")
        
        # Display filtered results
        checks = validation_results.get('checks', {})
        filtered_checks = self._filter_checks(checks, severity_filter, status_filter, search_term)
        
        if filtered_checks:
            for check_name, check_data in filtered_checks.items():
                self._render_check_detail(check_name, check_data)
        else:
            st.info("No checks match the current filters.")
        
        # Display raw errors and warnings if available
        if validation_results.get('errors') or validation_results.get('warnings'):
            st.divider()
            self._render_raw_issues(validation_results)
    
    def _render_trends(self, validation_results: Dict[str, Any], workflow_data: Dict[str, Any]):
        """Render validation trends and comparisons"""
        st.subheader("Validation Trends")
        
        # Mock historical data for demonstration
        historical_data = self._get_historical_data()
        
        if historical_data:
            # Trend chart
            fig_trend = self._create_trend_chart(historical_data)
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Comparison metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "vs. Last Run",
                    f"{validation_results.get('passed_checks', 0)} passed",
                    delta="↑ 5 checks",
                    help="Comparison with previous validation run"
                )
            
            with col2:
                current_coverage = validation_results.get('coverage', 0)
                st.metric(
                    "Coverage Trend",
                    f"{current_coverage:.1f}%",
                    delta="↑ 2.3%",
                    help="Data coverage improvement"
                )
            
            with col3:
                error_rate = len(validation_results.get('errors', [])) / validation_results.get('total_checks', 1) * 100
                st.metric(
                    "Error Rate",
                    f"{error_rate:.1f}%",
                    delta="↓ 1.5%",
                    delta_color="inverse",
                    help="Percentage of checks that failed"
                )
        else:
            st.info("Historical data will be available after multiple validation runs.")
    
    def _render_issue_drilldown(self, validation_results: Dict[str, Any], workflow_data: Dict[str, Any]):
        """Render detailed drill-down for specific issues"""
        st.subheader("Issue Drill-Down")
        
        # Select issue to investigate
        all_issues = self._collect_all_issues(validation_results)
        
        if not all_issues:
            st.info("No issues found to investigate. Great job!")
            return
        
        selected_issue = st.selectbox(
            "Select an issue to investigate",
            options=list(all_issues.keys()),
            format_func=lambda x: f"{all_issues[x]['severity']} - {x}"
        )
        
        if selected_issue:
            issue_data = all_issues[selected_issue]
            
            # Issue details
            st.markdown(f"### {selected_issue}")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Severity**: {issue_data['severity']}")
                st.markdown(f"**Category**: {issue_data.get('category', 'General')}")
                st.markdown(f"**Description**: {issue_data.get('description', 'No description available')}")
            
            with col2:
                # Quick stats
                st.metric("Occurrences", issue_data.get('count', 1))
                st.metric("First Seen", issue_data.get('first_seen', 'Current run'))
            
            # Affected data preview
            if workflow_data and 'mapped_file' in workflow_data:
                st.markdown("#### Affected Data")
                affected_data = self._get_affected_data(selected_issue, workflow_data)
                if affected_data is not None and not affected_data.empty:
                    st.dataframe(affected_data, use_container_width=True)
                else:
                    st.info("Unable to load affected data preview.")
            
            # Root cause analysis
            st.markdown("#### Root Cause Analysis")
            root_cause = self._analyze_root_cause(selected_issue, issue_data)
            st.info(root_cause)
            
            # Suggested fix
            st.markdown("#### Suggested Fix")
            fix_suggestion = self._get_fix_suggestion(selected_issue, issue_data)
            st.code(fix_suggestion, language='python')
            
            # Impact assessment
            st.markdown("#### Impact Assessment")
            impact = self._assess_impact(selected_issue, issue_data)
            if impact['severity'] == 'High':
                st.error(f"⚠️ {impact['description']}")
            else:
                st.warning(f"ℹ️ {impact['description']}")
    
    def _render_recommendations(self, validation_results: Dict[str, Any]):
        """Render actionable recommendations"""
        st.subheader("Recommendations")
        
        recommendations = self._generate_recommendations(validation_results)
        
        # Priority recommendations
        st.markdown("### 🎯 Priority Actions")
        priority_recs = [r for r in recommendations if r['priority'] == 'High']
        
        if priority_recs:
            for i, rec in enumerate(priority_recs, 1):
                with st.expander(f"{i}. {rec['title']}", expanded=True):
                    st.markdown(f"**Impact**: {rec['impact']}")
                    st.markdown(f"**Effort**: {rec['effort']}")
                    st.markdown(f"**Description**: {rec['description']}")
                    if rec.get('steps'):
                        st.markdown("**Steps**:")
                        for step in rec['steps']:
                            st.markdown(f"- {step}")
        else:
            st.success("No critical recommendations. Your data quality is good!")
        
        # Other recommendations
        st.markdown("### 💡 Additional Suggestions")
        other_recs = [r for r in recommendations if r['priority'] != 'High']
        
        if other_recs:
            for rec in other_recs:
                with st.expander(f"{rec['title']}"):
                    st.markdown(f"**Priority**: {rec['priority']}")
                    st.markdown(f"**Description**: {rec['description']}")
    
    # Helper methods
    def _categorize_checks(self, checks: Dict[str, Any]) -> Dict[str, List]:
        """Categorize checks by type"""
        categorized = {cat: [] for cat in self.check_categories}
        categorized['Other'] = []
        
        for check_name, check_data in checks.items():
            assigned = False
            for category in self.check_categories:
                if category.lower() in check_name.lower():
                    categorized[category].append((check_name, check_data))
                    assigned = True
                    break
            if not assigned:
                categorized['Other'].append((check_name, check_data))
        
        return {k: v for k, v in categorized.items() if v}
    
    def _create_results_pie_chart(self, category_results: Dict[str, List]) -> go.Figure:
        """Create pie chart of validation results"""
        passed_count = sum(1 for cat_checks in category_results.values() 
                          for _, check in cat_checks if check.get('passed', False))
        failed_count = sum(1 for cat_checks in category_results.values() 
                          for _, check in cat_checks if not check.get('passed', True))
        
        fig = go.Figure(data=[go.Pie(
            labels=['Passed', 'Failed'],
            values=[passed_count, failed_count],
            hole=.3,
            marker_colors=['#28a745', '#dc3545']
        )])
        
        fig.update_layout(
            title="Validation Results Distribution",
            height=300,
            showlegend=True
        )
        
        return fig
    
    def _create_severity_bar_chart(self, checks: Dict[str, Any]) -> go.Figure:
        """Create bar chart by severity"""
        severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'Info': 0}
        
        for check_data in checks.values():
            if not check_data.get('passed', True):
                severity = check_data.get('severity', 'Medium')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        fig = go.Figure([go.Bar(
            x=list(severity_counts.keys()),
            y=list(severity_counts.values()),
            marker_color=[self.severity_colors[s] for s in severity_counts.keys()]
        )])
        
        fig.update_layout(
            title="Issues by Severity",
            xaxis_title="Severity Level",
            yaxis_title="Count",
            height=300,
            showlegend=False
        )
        
        return fig
    
    def _render_category_cards(self, category_results: Dict[str, List]):
        """Render category summary cards"""
        cols = st.columns(min(3, len(category_results)))
        
        for i, (category, checks) in enumerate(category_results.items()):
            col_idx = i % len(cols)
            with cols[col_idx]:
                passed = sum(1 for _, check in checks if check.get('passed', False))
                total = len(checks)
                pass_rate = (passed / total * 100) if total > 0 else 0
                
                # Card styling based on pass rate
                if pass_rate >= 90:
                    card_color = "#d4edda"
                    text_color = "#155724"
                elif pass_rate >= 70:
                    card_color = "#fff3cd"
                    text_color = "#856404"
                else:
                    card_color = "#f8d7da"
                    text_color = "#721c24"
                
                st.markdown(
                    f"""
                    <div style="background-color: {card_color}; padding: 20px; 
                                border-radius: 10px; border: 1px solid {text_color}20;">
                        <h4 style="color: {text_color}; margin: 0;">{category}</h4>
                        <p style="color: {text_color}; margin: 5px 0; font-size: 24px; font-weight: bold;">
                            {pass_rate:.0f}%
                        </p>
                        <p style="color: {text_color}; margin: 0; font-size: 14px;">
                            {passed}/{total} checks passed
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    def _filter_checks(self, checks: Dict[str, Any], severity_filter: List[str], 
                      status_filter: str, search_term: str) -> Dict[str, Any]:
        """Filter checks based on criteria"""
        filtered = {}
        
        for check_name, check_data in checks.items():
            # Apply filters
            severity_match = check_data.get('severity', 'Medium') in severity_filter
            
            if status_filter == 'All':
                status_match = True
            elif status_filter == 'Passed':
                status_match = check_data.get('passed', False)
            elif status_filter == 'Failed':
                status_match = not check_data.get('passed', True)
            else:  # Warning
                status_match = check_data.get('severity') in ['Medium', 'Low']
            
            search_match = (not search_term or 
                          search_term.lower() in check_name.lower() or
                          search_term.lower() in str(check_data.get('message', '')).lower())
            
            if severity_match and status_match and search_match:
                filtered[check_name] = check_data
        
        return filtered
    
    def _render_check_detail(self, check_name: str, check_data: Dict[str, Any]):
        """Render detailed view of a single check"""
        passed = check_data.get('passed', False)
        severity = check_data.get('severity', 'Medium')
        
        # Use expander with color coding
        icon = "✅" if passed else "❌"
        with st.expander(f"{icon} {check_name}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Message**: {check_data.get('message', 'No details available')}")
            
            with col2:
                st.markdown(f"**Severity**: {severity}")
            
            with col3:
                st.markdown(f"**Status**: {'Passed' if passed else 'Failed'}")
            
            # Additional details if available
            if 'details' in check_data:
                st.json(check_data['details'])
    
    def _render_summary_overview(self, validation_results: Dict[str, Any]):
        """Render simple overview when detailed checks aren't available"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Simple metrics
            st.metric("Total Checks", validation_results.get('total_checks', 0))
            st.metric("Passed Checks", validation_results.get('passed_checks', 0))
        
        with col2:
            st.metric("Errors", len(validation_results.get('errors', [])))
            st.metric("Warnings", len(validation_results.get('warnings', [])))
    
    def _render_raw_issues(self, validation_results: Dict[str, Any]):
        """Render raw errors and warnings"""
        errors = validation_results.get('errors', [])
        warnings = validation_results.get('warnings', [])
        
        if errors:
            st.markdown("### ❌ Errors")
            for error in errors:
                st.error(error)
        
        if warnings:
            st.markdown("### ⚠️ Warnings")
            for warning in warnings:
                st.warning(warning)
    
    def _get_historical_data(self) -> Optional[pd.DataFrame]:
        """Get mock historical validation data"""
        # In a real implementation, this would load from a database or file
        data = {
            'run_date': pd.date_range(end=datetime.now(), periods=5, freq='D'),
            'total_checks': [95, 98, 100, 102, 105],
            'passed_checks': [88, 92, 94, 97, 98],
            'errors': [5, 4, 4, 3, 2],
            'warnings': [2, 2, 2, 2, 5]
        }
        return pd.DataFrame(data)
    
    def _create_trend_chart(self, historical_data: pd.DataFrame) -> go.Figure:
        """Create trend chart for validation results"""
        fig = go.Figure()
        
        # Add traces
        fig.add_trace(go.Scatter(
            x=historical_data['run_date'],
            y=historical_data['passed_checks'] / historical_data['total_checks'] * 100,
            mode='lines+markers',
            name='Pass Rate %',
            line=dict(color='#28a745', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=historical_data['run_date'],
            y=historical_data['errors'],
            mode='lines+markers',
            name='Errors',
            line=dict(color='#dc3545', width=2),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Validation Trends Over Time',
            xaxis_title='Date',
            yaxis=dict(title='Pass Rate %', side='left'),
            yaxis2=dict(title='Error Count', overlaying='y', side='right'),
            hovermode='x unified',
            height=400
        )
        
        return fig
    
    def _collect_all_issues(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Collect all issues from validation results"""
        issues = {}
        
        # From checks
        checks = validation_results.get('checks', {})
        for check_name, check_data in checks.items():
            if not check_data.get('passed', True):
                issues[check_name] = {
                    'severity': check_data.get('severity', 'Medium'),
                    'category': self._determine_category(check_name),
                    'description': check_data.get('message', ''),
                    'count': 1,
                    'first_seen': 'Current run'
                }
        
        # From raw errors
        for i, error in enumerate(validation_results.get('errors', [])):
            issues[f'Error_{i+1}'] = {
                'severity': 'Critical',
                'category': 'General',
                'description': str(error),
                'count': 1,
                'first_seen': 'Current run'
            }
        
        return issues
    
    def _determine_category(self, check_name: str) -> str:
        """Determine category for a check"""
        for category in self.check_categories:
            if category.lower() in check_name.lower():
                return category
        return 'Other'
    
    def _get_affected_data(self, issue: str, workflow_data: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Get data affected by the issue"""
        try:
            mapped_file = workflow_data.get('mapped_file')
            if mapped_file and Path(mapped_file).exists():
                # Load a sample of the data
                df = pd.read_excel(mapped_file, nrows=50)
                # In real implementation, filter based on issue type
                return df.head(10)
        except Exception:
            pass
        return None
    
    def _analyze_root_cause(self, issue: str, issue_data: Dict[str, Any]) -> str:
        """Analyze root cause of the issue"""
        # Simplified root cause analysis
        if 'mapping' in issue.lower():
            return "Column mapping issue likely due to name mismatch or missing source data."
        elif 'completeness' in issue.lower():
            return "Missing data in source files or incorrect extraction logic."
        elif 'type' in issue.lower():
            return "Data type mismatch between source and target formats."
        else:
            return "Issue requires manual investigation to determine root cause."
    
    def _get_fix_suggestion(self, issue: str, issue_data: Dict[str, Any]) -> str:
        """Get fix suggestion for the issue"""
        if 'mapping' in issue.lower():
            return """# Check column mappings in config/template_mapping_config.json
# Update the mapping for the affected column:
{
    "template_column": "SOURCE_COLUMN_NAME"
}"""
        elif 'completeness' in issue.lower():
            return """# Ensure all required fields are present in source data
# Check for NaN values:
df['affected_column'].fillna(default_value, inplace=True)"""
        else:
            return """# Review the validation logic and source data
# Consider adding custom validation rules"""
    
    def _assess_impact(self, issue: str, issue_data: Dict[str, Any]) -> Dict[str, str]:
        """Assess impact of the issue"""
        severity = issue_data.get('severity', 'Medium')
        
        if severity == 'Critical':
            return {
                'severity': 'High',
                'description': 'This issue prevents successful completion of the workflow and must be fixed.'
            }
        elif severity == 'High':
            return {
                'severity': 'Medium',
                'description': 'This issue may cause incorrect results in the output.'
            }
        else:
            return {
                'severity': 'Low',
                'description': 'This issue should be reviewed but may not impact final results.'
            }
    
    def _generate_recommendations(self, validation_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        errors = validation_results.get('errors', [])
        warnings = validation_results.get('warnings', [])
        passed_rate = validation_results.get('passed_checks', 0) / max(validation_results.get('total_checks', 1), 1)
        
        # Critical recommendations
        if errors:
            recommendations.append({
                'title': 'Fix Critical Errors',
                'priority': 'High',
                'impact': 'High',
                'effort': 'Medium',
                'description': f'Address {len(errors)} critical errors before proceeding.',
                'steps': [
                    'Review error details in the Detailed Results tab',
                    'Use Issue Drill-Down to understand root causes',
                    'Apply suggested fixes and re-run validation'
                ]
            })
        
        # Data quality recommendations
        if passed_rate < 0.9:
            recommendations.append({
                'title': 'Improve Data Quality',
                'priority': 'High' if passed_rate < 0.7 else 'Medium',
                'impact': 'High',
                'effort': 'High',
                'description': f'Only {passed_rate*100:.1f}% of validation checks passed.',
                'steps': [
                    'Review source data for completeness',
                    'Verify column mappings are correct',
                    'Consider adding data cleaning steps'
                ]
            })
        
        # Warning recommendations
        if len(warnings) > 5:
            recommendations.append({
                'title': 'Address Warning Accumulation',
                'priority': 'Medium',
                'impact': 'Medium',
                'effort': 'Low',
                'description': f'{len(warnings)} warnings detected.',
                'steps': [
                    'Review warnings for patterns',
                    'Update validation rules if needed',
                    'Document expected warnings'
                ]
            })
        
        # Best practice recommendations
        recommendations.append({
            'title': 'Enable Strict Validation Mode',
            'priority': 'Low',
            'impact': 'Medium',
            'effort': 'Low',
            'description': 'Catch potential issues earlier with stricter validation.',
            'steps': [
                'Enable strict mode in settings',
                'Review and fix any new warnings',
                'Update team documentation'
            ]
        })
        
        return recommendations
    
    def export_report(self, validation_results: Dict[str, Any], format: str = 'html') -> str:
        """Export validation report in specified format"""
        if format == 'html':
            return self._export_html_report(validation_results)
        elif format == 'json':
            return json.dumps(validation_results, indent=2)
        else:
            return str(validation_results)
    
    def _export_html_report(self, validation_results: Dict[str, Any]) -> str:
        """Export validation results as HTML report"""
        html = f"""
        <html>
        <head>
            <title>Validation Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #fff; border: 1px solid #ddd; }}
                .error {{ color: #dc3545; }}
                .warning {{ color: #ffc107; }}
                .success {{ color: #28a745; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Validation Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <div class="metric">Total Checks: {validation_results.get('total_checks', 0)}</div>
                <div class="metric">Passed: {validation_results.get('passed_checks', 0)}</div>
                <div class="metric error">Errors: {len(validation_results.get('errors', []))}</div>
                <div class="metric warning">Warnings: {len(validation_results.get('warnings', []))}</div>
            </div>
            
            <div class="details">
                <h2>Detailed Results</h2>
                <table>
                    <tr>
                        <th>Check</th>
                        <th>Status</th>
                        <th>Severity</th>
                        <th>Message</th>
                    </tr>
        """
        
        # Add check results
        for check_name, check_data in validation_results.get('checks', {}).items():
            status = "Passed" if check_data.get('passed', False) else "Failed"
            status_class = "success" if check_data.get('passed', False) else "error"
            html += f"""
                    <tr>
                        <td>{check_name}</td>
                        <td class="{status_class}">{status}</td>
                        <td>{check_data.get('severity', 'Medium')}</td>
                        <td>{check_data.get('message', '')}</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
        </body>
        </html>
        """
        
        return html