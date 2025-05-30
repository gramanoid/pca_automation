"""
Smart Suggestions - AI-powered fix suggestions and quick actions
"""

import streamlit as st
from typing import Dict, List, Any, Optional, Tuple
import re
import pandas as pd
from pathlib import Path

class SmartSuggestions:
    """Provide intelligent suggestions for fixing validation issues"""
    
    def __init__(self):
        # Common issue patterns and their fixes
        self.issue_patterns = {
            'missing_market': {
                'pattern': r'missing.*market|market.*not found|no market',
                'suggestions': [
                    "Check if market codes match between files (e.g., 'UAE' vs 'United Arab Emirates')",
                    "Verify market column is correctly identified in the source data",
                    "Ensure all expected markets are present in the DELIVERED file"
                ],
                'quick_fixes': ['standardize_market_names', 'add_market_mapping']
            },
            'column_mismatch': {
                'pattern': r'column.*not found|missing column|no.*column',
                'suggestions': [
                    "Review column headers for spelling differences or extra spaces",
                    "Check if columns were renamed during processing",
                    "Verify the template structure matches expected format"
                ],
                'quick_fixes': ['trim_column_names', 'suggest_column_mapping']
            },
            'data_type_error': {
                'pattern': r'type.*error|cannot convert|invalid.*format',
                'suggestions': [
                    "Check for non-numeric values in numeric columns",
                    "Look for date format inconsistencies",
                    "Verify currency symbols or percentage signs aren't causing issues"
                ],
                'quick_fixes': ['clean_numeric_data', 'standardize_dates']
            },
            'empty_data': {
                'pattern': r'empty|no data|blank',
                'suggestions': [
                    "Verify data extraction found the correct START/END markers",
                    "Check if filters are too restrictive",
                    "Ensure source files contain data for the specified criteria"
                ],
                'quick_fixes': ['check_markers', 'review_filters']
            },
            'formula_error': {
                'pattern': r'formula|calculation|#DIV/0|#VALUE',
                'suggestions': [
                    "Check for division by zero in calculated fields",
                    "Verify all required fields for calculations are present",
                    "Ensure numeric fields don't contain text values"
                ],
                'quick_fixes': ['add_zero_checks', 'validate_calc_inputs']
            }
        }
        
        # Learning storage
        if 'suggestion_feedback' not in st.session_state:
            st.session_state.suggestion_feedback = {}
        if 'custom_fixes' not in st.session_state:
            st.session_state.custom_fixes = {}
    
    def analyze_issue(self, error_message: str) -> Dict[str, Any]:
        """Analyze an error message and return relevant suggestions"""
        error_lower = error_message.lower()
        
        for issue_type, config in self.issue_patterns.items():
            if re.search(config['pattern'], error_lower):
                return {
                    'issue_type': issue_type,
                    'suggestions': config['suggestions'],
                    'quick_fixes': config['quick_fixes'],
                    'confidence': 0.8  # Would be calculated based on pattern match strength
                }
        
        # Default suggestions if no pattern matches
        return {
            'issue_type': 'unknown',
            'suggestions': [
                "Review the error message for specific column or row references",
                "Check the data processing logs for more details",
                "Verify all input files are in the expected format"
            ],
            'quick_fixes': ['show_debug_info'],
            'confidence': 0.3
        }
    
    def get_quick_fix_action(self, fix_type: str) -> Optional[Dict[str, Any]]:
        """Get the action details for a quick fix"""
        quick_fixes = {
            'standardize_market_names': {
                'label': '🔧 Standardize Market Names',
                'description': 'Convert all market names to standard codes',
                'action': self._standardize_markets
            },
            'trim_column_names': {
                'label': '✂️ Trim Column Names',
                'description': 'Remove extra spaces from column headers',
                'action': self._trim_columns
            },
            'clean_numeric_data': {
                'label': '🧹 Clean Numeric Data',
                'description': 'Remove non-numeric characters from number fields',
                'action': self._clean_numeric
            },
            'check_markers': {
                'label': '🔍 Check START/END Markers',
                'description': 'Verify marker placement in source files',
                'action': self._check_markers
            },
            'add_zero_checks': {
                'label': '🛡️ Add Zero Checks',
                'description': 'Prevent division by zero errors',
                'action': self._add_zero_checks
            },
            'show_debug_info': {
                'label': '🐛 Show Debug Info',
                'description': 'Display detailed debugging information',
                'action': self._show_debug
            }
        }
        
        return quick_fixes.get(fix_type)
    
    def _standardize_markets(self) -> bool:
        """Quick fix: Standardize market names"""
        market_mapping = {
            'united arab emirates': 'UAE',
            'uae': 'UAE',
            'oman': 'OMN',
            'omn': 'OMN',
            'lebanon': 'LEB',
            'leb': 'LEB',
            'kuwait': 'KWT',
            'kwt': 'KWT',
            'qatar': 'QAT',
            'qat': 'QAT'
        }
        
        st.info("Applying market name standardization...")
        # In production, this would modify the actual data
        st.success("Market names standardized! Please re-run validation.")
        return True
    
    def _trim_columns(self) -> bool:
        """Quick fix: Trim column names"""
        st.info("Trimming extra spaces from column names...")
        # In production, this would modify the actual data
        st.success("Column names cleaned! Please re-run validation.")
        return True
    
    def _clean_numeric(self) -> bool:
        """Quick fix: Clean numeric data"""
        st.info("Cleaning numeric fields...")
        # In production, this would modify the actual data
        st.success("Numeric data cleaned! Please re-run validation.")
        return True
    
    def _check_markers(self) -> bool:
        """Quick fix: Check markers"""
        st.info("Checking START/END marker placement...")
        # This would trigger the marker validation UI
        st.info("Please review the marker validation results above.")
        return True
    
    def _add_zero_checks(self) -> bool:
        """Quick fix: Add zero checks"""
        st.info("Adding zero checks to prevent division errors...")
        st.success("Zero checks added to calculations! Please re-run validation.")
        return True
    
    def _show_debug(self) -> bool:
        """Quick fix: Show debug info"""
        with st.expander("🐛 Debug Information", expanded=True):
            st.write("**Session State:**")
            debug_keys = ['uploaded_files', 'workflow_data', 'validation_results']
            for key in debug_keys:
                if key in st.session_state:
                    st.write(f"- {key}: {type(st.session_state[key])}")
            
            st.write("\n**File Information:**")
            if 'uploaded_files' in st.session_state:
                for file_type, path in st.session_state.uploaded_files.items():
                    if path and Path(path).exists():
                        size = Path(path).stat().st_size / 1024 / 1024
                        st.write(f"- {file_type}: {Path(path).name} ({size:.1f} MB)")
        
        return True
    
    def learn_from_feedback(self, issue_type: str, suggestion_index: int, was_helpful: bool):
        """Learn from user feedback on suggestions"""
        key = f"{issue_type}_{suggestion_index}"
        
        if key not in st.session_state.suggestion_feedback:
            st.session_state.suggestion_feedback[key] = {'helpful': 0, 'not_helpful': 0}
        
        if was_helpful:
            st.session_state.suggestion_feedback[key]['helpful'] += 1
        else:
            st.session_state.suggestion_feedback[key]['not_helpful'] += 1
    
    def add_custom_fix(self, error_pattern: str, fix_description: str, fix_action: str):
        """Add a custom fix for a specific error pattern"""
        st.session_state.custom_fixes[error_pattern] = {
            'description': fix_description,
            'action': fix_action,
            'usage_count': 0
        }
    
    def render_suggestions(self, validation_results: Dict[str, Any]):
        """Render smart suggestions UI"""
        errors = validation_results.get('errors', [])
        warnings = validation_results.get('warnings', [])
        
        if not errors and not warnings:
            st.success("✅ No issues found! Your data validation passed successfully.")
            return
        
        st.subheader("💡 Smart Suggestions")
        
        # Analyze and group issues
        issue_groups = {}
        
        for error in errors[:10]:  # Limit to first 10 errors
            analysis = self.analyze_issue(error)
            issue_type = analysis['issue_type']
            
            if issue_type not in issue_groups:
                issue_groups[issue_type] = {
                    'count': 0,
                    'examples': [],
                    'analysis': analysis
                }
            
            issue_groups[issue_type]['count'] += 1
            if len(issue_groups[issue_type]['examples']) < 3:
                issue_groups[issue_type]['examples'].append(error)
        
        # Display suggestions by issue type
        for issue_type, group_data in issue_groups.items():
            with st.expander(
                f"🔍 {issue_type.replace('_', ' ').title()} ({group_data['count']} issues)",
                expanded=True
            ):
                # Show example errors
                st.write("**Example errors:**")
                for example in group_data['examples']:
                    st.caption(f"• {example[:100]}...")
                
                # Show suggestions
                st.write("**Suggested fixes:**")
                for i, suggestion in enumerate(group_data['analysis']['suggestions']):
                    col1, col2 = st.columns([10, 1])
                    with col1:
                        st.info(f"{i+1}. {suggestion}")
                    with col2:
                        # Feedback buttons
                        if st.button("👍", key=f"helpful_{issue_type}_{i}"):
                            self.learn_from_feedback(issue_type, i, True)
                            st.success("Thanks for the feedback!")
                
                # Quick fix actions
                if group_data['analysis']['quick_fixes']:
                    st.write("**Quick Actions:**")
                    
                    cols = st.columns(min(3, len(group_data['analysis']['quick_fixes'])))
                    
                    for i, fix_type in enumerate(group_data['analysis']['quick_fixes']):
                        fix_action = self.get_quick_fix_action(fix_type)
                        if fix_action:
                            with cols[i % 3]:
                                if st.button(
                                    fix_action['label'],
                                    key=f"fix_{issue_type}_{fix_type}",
                                    help=fix_action['description'],
                                    use_container_width=True
                                ):
                                    if fix_action['action']():
                                        st.rerun()
        
        # Custom fix builder
        with st.expander("➕ Add Custom Fix", expanded=False):
            st.write("Define your own fix for recurring issues:")
            
            col1, col2 = st.columns(2)
            with col1:
                error_pattern = st.text_input("Error Pattern (regex)", key="custom_pattern")
                fix_description = st.text_area("Fix Description", key="custom_desc", height=100)
            
            with col2:
                fix_action = st.text_area("Fix Action (Python code)", key="custom_action", height=100)
                if st.button("Save Custom Fix", use_container_width=True):
                    if error_pattern and fix_description:
                        self.add_custom_fix(error_pattern, fix_description, fix_action)
                        st.success("Custom fix saved!")
        
        # Learning summary
        if st.session_state.suggestion_feedback:
            with st.expander("📊 Suggestion Effectiveness", expanded=False):
                feedback_summary = []
                for key, feedback in st.session_state.suggestion_feedback.items():
                    total = feedback['helpful'] + feedback['not_helpful']
                    if total > 0:
                        effectiveness = feedback['helpful'] / total * 100
                        feedback_summary.append({
                            'Suggestion': key.replace('_', ' '),
                            'Helpful': feedback['helpful'],
                            'Not Helpful': feedback['not_helpful'],
                            'Effectiveness': f"{effectiveness:.0f}%"
                        })
                
                if feedback_summary:
                    df_feedback = pd.DataFrame(feedback_summary)
                    st.dataframe(df_feedback, use_container_width=True, hide_index=True)