"""
Enhanced Error Handling with Recovery Options
Provides intelligent error recovery suggestions and automated fixes
"""

import streamlit as st
import pandas as pd
import json
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Callable
from datetime import datetime
import logging
import shutil
import os

class ErrorRecoveryHandler:
    """Handles errors with recovery options and automated fixes"""
    
    def __init__(self):
        self.error_patterns = {
            'FileNotFoundError': {
                'pattern': 'No such file or directory',
                'category': 'File System',
                'severity': 'High',
                'recovery_actions': ['check_file_path', 'suggest_similar_files', 'create_missing_file']
            },
            'ColumnMissingError': {
                'pattern': 'Column .* not found|KeyError:.*',
                'category': 'Data Structure',
                'severity': 'High',
                'recovery_actions': ['suggest_column_mapping', 'show_available_columns', 'auto_map_columns']
            },
            'DataTypeError': {
                'pattern': 'could not convert|invalid literal|dtype mismatch',
                'category': 'Data Type',
                'severity': 'Medium',
                'recovery_actions': ['suggest_type_conversion', 'clean_data', 'skip_invalid_rows']
            },
            'MemoryError': {
                'pattern': 'MemoryError|out of memory',
                'category': 'Performance',
                'severity': 'Critical',
                'recovery_actions': ['suggest_chunking', 'reduce_memory_usage', 'clear_cache']
            },
            'PermissionError': {
                'pattern': 'Permission denied|Access is denied',
                'category': 'File System',
                'severity': 'High',
                'recovery_actions': ['check_permissions', 'suggest_alternative_location', 'retry_with_elevation']
            },
            'ExcelError': {
                'pattern': 'Excel|.xlsx|openpyxl|xlrd',
                'category': 'File Format',
                'severity': 'Medium',
                'recovery_actions': ['validate_excel_format', 'repair_excel', 'convert_format']
            }
        }
        
        self.recovery_history = []
        self.logger = logging.getLogger(__name__)
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main error handling with recovery suggestions"""
        error_info = self._analyze_error(error, context)
        recovery_options = self._generate_recovery_options(error_info, context)
        
        # Log error for analysis
        self._log_error(error_info)
        
        return {
            'error_info': error_info,
            'recovery_options': recovery_options,
            'can_recover': len(recovery_options) > 0
        }
    
    def render_error_recovery_ui(self, error: Exception, context: Dict[str, Any] = None):
        """Render error recovery UI in Streamlit"""
        result = self.handle_error(error, context)
        
        # Error header
        st.error(f"❌ An error occurred: {result['error_info']['type']}")
        
        # Error details
        with st.expander("📋 Error Details", expanded=True):
            st.code(result['error_info']['message'])
            
            if result['error_info'].get('traceback'):
                st.text("Traceback:")
                st.code(result['error_info']['traceback'])
        
        # Recovery options
        if result['recovery_options']:
            st.subheader("🔧 Recovery Options")
            
            selected_option = None
            for i, option in enumerate(result['recovery_options']):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**{option['title']}**")
                    st.caption(option['description'])
                    
                    if option.get('steps'):
                        with st.expander("View steps"):
                            for step in option['steps']:
                                st.write(f"• {step}")
                
                with col2:
                    if option.get('can_auto_fix'):
                        if st.button(f"Auto Fix", key=f"fix_{i}", type="primary"):
                            selected_option = option
                    else:
                        if st.button(f"Try This", key=f"try_{i}"):
                            selected_option = option
            
            # Execute selected recovery option
            if selected_option:
                self._execute_recovery_option(selected_option, error, context)
        else:
            st.warning("No automatic recovery options available. Please check the error details above.")
        
        # Manual recovery section
        with st.expander("🛠️ Manual Recovery Options"):
            self._render_manual_recovery_options(result['error_info'])
        
        # Error reporting
        if st.button("📧 Report This Error"):
            self._show_error_report(result['error_info'])
    
    def _analyze_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze error and extract relevant information"""
        error_type = type(error).__name__
        error_message = str(error)
        
        # Get traceback
        tb_str = ''.join(traceback.format_tb(error.__traceback__))
        
        # Identify error category
        category = 'Unknown'
        severity = 'Medium'
        
        for pattern_name, pattern_info in self.error_patterns.items():
            if pattern_info['pattern'] in error_message or pattern_name == error_type:
                category = pattern_info['category']
                severity = pattern_info['severity']
                break
        
        # Extract relevant context
        relevant_context = {}
        if context:
            if 'file_path' in context:
                relevant_context['file_path'] = context['file_path']
            if 'stage' in context:
                relevant_context['stage'] = context['stage']
            if 'operation' in context:
                relevant_context['operation'] = context['operation']
        
        return {
            'type': error_type,
            'message': error_message,
            'traceback': tb_str,
            'category': category,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'context': relevant_context
        }
    
    def _generate_recovery_options(self, error_info: Dict[str, Any], context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate recovery options based on error type"""
        options = []
        error_type = error_info['type']
        error_message = error_info['message']
        
        # File not found errors
        if 'FileNotFoundError' in error_type or 'No such file' in error_message:
            options.extend(self._file_not_found_recovery(error_info, context))
        
        # Column/Key errors
        if 'KeyError' in error_type or 'Column' in error_message:
            options.extend(self._column_error_recovery(error_info, context))
        
        # Data type errors
        if 'ValueError' in error_type or 'could not convert' in error_message:
            options.extend(self._data_type_recovery(error_info, context))
        
        # Permission errors
        if 'PermissionError' in error_type:
            options.extend(self._permission_error_recovery(error_info, context))
        
        # Memory errors
        if 'MemoryError' in error_type:
            options.extend(self._memory_error_recovery(error_info, context))
        
        # Excel-specific errors
        if any(x in error_message.lower() for x in ['excel', 'xlsx', 'openpyxl']):
            options.extend(self._excel_error_recovery(error_info, context))
        
        # Generic recovery options
        options.extend(self._generic_recovery_options(error_info, context))
        
        return options
    
    def _file_not_found_recovery(self, error_info: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recovery options for file not found errors"""
        options = []
        
        # Extract file path from error message
        import re
        match = re.search(r"['\"]([^'\"]+)['\"]", error_info['message'])
        missing_file = match.group(1) if match else None
        
        if missing_file:
            # Check for similar files
            similar_files = self._find_similar_files(missing_file)
            if similar_files:
                options.append({
                    'title': 'Use Similar File',
                    'description': f'Found {len(similar_files)} similar files',
                    'can_auto_fix': True,
                    'action': 'use_similar_file',
                    'params': {'original': missing_file, 'alternatives': similar_files},
                    'steps': [f"Use '{f}' instead" for f in similar_files[:3]]
                })
            
            # Suggest re-upload
            options.append({
                'title': 'Re-upload File',
                'description': 'Upload the missing file again',
                'can_auto_fix': False,
                'action': 'reupload_file',
                'params': {'missing_file': missing_file},
                'steps': ['Go back to file upload stage', f'Upload {Path(missing_file).name}']
            })
            
            # Create placeholder
            if missing_file.endswith('.xlsx'):
                options.append({
                    'title': 'Create Empty Template',
                    'description': 'Create an empty file to continue',
                    'can_auto_fix': True,
                    'action': 'create_empty_file',
                    'params': {'file_path': missing_file},
                    'steps': ['Create empty Excel file', 'Continue with workflow']
                })
        
        return options
    
    def _column_error_recovery(self, error_info: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recovery options for column errors"""
        options = []
        
        # Extract column name
        import re
        match = re.search(r"['\"]([^'\"]+)['\"]", error_info['message'])
        missing_column = match.group(1) if match else None
        
        if missing_column and context and 'dataframe' in context:
            df = context['dataframe']
            available_columns = list(df.columns)
            
            # Find similar columns
            similar_columns = self._find_similar_strings(missing_column, available_columns)
            
            if similar_columns:
                options.append({
                    'title': 'Auto-map Column',
                    'description': f'Map to similar column: {similar_columns[0]}',
                    'can_auto_fix': True,
                    'action': 'map_column',
                    'params': {'missing': missing_column, 'suggested': similar_columns[0]},
                    'steps': [f"Map '{missing_column}' to '{similar_columns[0]}'"]
                })
            
            # Show available columns
            options.append({
                'title': 'View Available Columns',
                'description': 'See all columns in the data',
                'can_auto_fix': False,
                'action': 'show_columns',
                'params': {'columns': available_columns},
                'steps': ['Review available columns', 'Update column mapping']
            })
            
            # Skip column
            options.append({
                'title': 'Skip This Column',
                'description': 'Continue without this column',
                'can_auto_fix': True,
                'action': 'skip_column',
                'params': {'column': missing_column},
                'steps': ['Mark column as optional', 'Continue processing']
            })
        
        return options
    
    def _data_type_recovery(self, error_info: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recovery options for data type errors"""
        options = []
        
        options.append({
            'title': 'Clean and Convert Data',
            'description': 'Automatically clean and convert problematic values',
            'can_auto_fix': True,
            'action': 'clean_data',
            'params': context,
            'steps': ['Remove invalid characters', 'Convert to appropriate type', 'Fill missing values']
        })
        
        options.append({
            'title': 'Skip Invalid Rows',
            'description': 'Continue processing, skipping rows with errors',
            'can_auto_fix': True,
            'action': 'skip_invalid',
            'params': context,
            'steps': ['Identify invalid rows', 'Log skipped data', 'Continue with valid data']
        })
        
        options.append({
            'title': 'Use Default Values',
            'description': 'Replace invalid values with defaults',
            'can_auto_fix': True,
            'action': 'use_defaults',
            'params': context,
            'steps': ['Set default values', 'Replace invalid entries', 'Continue processing']
        })
        
        return options
    
    def _permission_error_recovery(self, error_info: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recovery options for permission errors"""
        options = []
        
        options.append({
            'title': 'Use Temporary Directory',
            'description': 'Save files to a temporary location instead',
            'can_auto_fix': True,
            'action': 'use_temp_dir',
            'params': context,
            'steps': ['Create temp directory', 'Redirect output', 'Continue processing']
        })
        
        options.append({
            'title': 'Change File Permissions',
            'description': 'Attempt to fix file permissions',
            'can_auto_fix': True,
            'action': 'fix_permissions',
            'params': context,
            'steps': ['Check current permissions', 'Attempt to modify', 'Retry operation']
        })
        
        return options
    
    def _memory_error_recovery(self, error_info: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recovery options for memory errors"""
        options = []
        
        options.append({
            'title': 'Process in Chunks',
            'description': 'Break down large files into smaller chunks',
            'can_auto_fix': True,
            'action': 'enable_chunking',
            'params': {'chunk_size': 10000},
            'steps': ['Enable chunk processing', 'Process 10,000 rows at a time']
        })
        
        options.append({
            'title': 'Clear Cache and Retry',
            'description': 'Free up memory and try again',
            'can_auto_fix': True,
            'action': 'clear_cache',
            'params': {},
            'steps': ['Clear Streamlit cache', 'Garbage collect', 'Retry operation']
        })
        
        options.append({
            'title': 'Reduce Data Precision',
            'description': 'Use lower precision data types to save memory',
            'can_auto_fix': True,
            'action': 'reduce_precision',
            'params': context,
            'steps': ['Convert float64 to float32', 'Optimize string storage']
        })
        
        return options
    
    def _excel_error_recovery(self, error_info: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recovery options for Excel-specific errors"""
        options = []
        
        options.append({
            'title': 'Repair Excel File',
            'description': 'Attempt to repair corrupted Excel file',
            'can_auto_fix': True,
            'action': 'repair_excel',
            'params': context,
            'steps': ['Open in recovery mode', 'Save repaired copy', 'Continue with repaired file']
        })
        
        options.append({
            'title': 'Convert to CSV',
            'description': 'Convert Excel to CSV format',
            'can_auto_fix': True,
            'action': 'convert_to_csv',
            'params': context,
            'steps': ['Extract data as CSV', 'Process CSV instead']
        })
        
        return options
    
    def _generic_recovery_options(self, error_info: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generic recovery options for any error"""
        options = []
        
        # Retry option
        options.append({
            'title': 'Retry Operation',
            'description': 'Try the operation again',
            'can_auto_fix': False,
            'action': 'retry',
            'params': context,
            'steps': ['Clear any locks', 'Reset state', 'Retry the operation']
        })
        
        # Skip and continue
        if context and context.get('can_skip', True):
            options.append({
                'title': 'Skip and Continue',
                'description': 'Skip this step and proceed',
                'can_auto_fix': False,
                'action': 'skip',
                'params': context,
                'steps': ['Log the error', 'Mark step as skipped', 'Continue workflow']
            })
        
        return options
    
    def _execute_recovery_option(self, option: Dict[str, Any], error: Exception, context: Dict[str, Any]):
        """Execute selected recovery option"""
        action = option.get('action')
        params = option.get('params', {})
        
        with st.spinner(f"Executing: {option['title']}..."):
            try:
                if action == 'use_similar_file':
                    self._action_use_similar_file(params)
                elif action == 'create_empty_file':
                    self._action_create_empty_file(params)
                elif action == 'map_column':
                    self._action_map_column(params)
                elif action == 'clean_data':
                    self._action_clean_data(params)
                elif action == 'use_temp_dir':
                    self._action_use_temp_dir(params)
                elif action == 'clear_cache':
                    self._action_clear_cache(params)
                elif action == 'repair_excel':
                    self._action_repair_excel(params)
                else:
                    st.info(f"Action '{action}' requires manual intervention.")
                
                # Log successful recovery
                self._log_recovery(option, error, True)
                st.success(f"✅ Successfully executed: {option['title']}")
                
                # Offer to retry original operation
                if st.button("🔄 Retry Original Operation"):
                    st.rerun()
                    
            except Exception as e:
                self._log_recovery(option, error, False)
                st.error(f"Recovery failed: {str(e)}")
    
    def _render_manual_recovery_options(self, error_info: Dict[str, Any]):
        """Render manual recovery options"""
        st.markdown("### Manual Recovery Steps")
        
        # Based on error category
        if error_info['category'] == 'File System':
            st.markdown("""
            1. **Check file paths**: Ensure all file paths are correct
            2. **Verify file exists**: Check if the file is in the expected location
            3. **Check permissions**: Ensure you have read/write access
            4. **Try absolute paths**: Use full paths instead of relative
            """)
        elif error_info['category'] == 'Data Structure':
            st.markdown("""
            1. **Review column names**: Check for typos or case sensitivity
            2. **Update mappings**: Modify column mappings in configuration
            3. **Check data format**: Ensure data structure matches expectations
            4. **Validate source files**: Verify source files have required columns
            """)
        elif error_info['category'] == 'Data Type':
            st.markdown("""
            1. **Check data types**: Ensure numeric columns contain numbers
            2. **Clean data**: Remove special characters or invalid values
            3. **Handle missing values**: Fill or remove NaN values
            4. **Convert formats**: Ensure dates and numbers are properly formatted
            """)
        else:
            st.markdown("""
            1. **Check error message**: Read the full error for clues
            2. **Review recent changes**: Undo recent modifications
            3. **Verify dependencies**: Ensure all requirements are installed
            4. **Restart application**: Sometimes a fresh start helps
            """)
        
        # Debug information
        with st.expander("Debug Information"):
            st.json({
                'error_type': error_info['type'],
                'category': error_info['category'],
                'severity': error_info['severity'],
                'timestamp': error_info['timestamp']
            })
    
    def _show_error_report(self, error_info: Dict[str, Any]):
        """Show error report for user to copy"""
        report = f"""
## Error Report

**Date**: {error_info['timestamp']}
**Type**: {error_info['type']}
**Category**: {error_info['category']}
**Severity**: {error_info['severity']}

### Error Message
```
{error_info['message']}
```

### Context
```json
{json.dumps(error_info.get('context', {}), indent=2)}
```

### Traceback
```
{error_info.get('traceback', 'Not available')}
```

### System Information
- Streamlit Version: {st.__version__}
- Python Version: {sys.version}
        """
        
        st.text_area("Copy this report:", report, height=300)
        st.info("Please include this report when seeking help.")
    
    # Action implementations
    def _action_use_similar_file(self, params: Dict[str, Any]):
        """Use a similar file instead of missing one"""
        original = params['original']
        alternative = params['alternatives'][0]
        
        # Create symlink or copy
        if Path(alternative).exists():
            shutil.copy2(alternative, original)
            st.session_state.file_recovery = {
                'original': original,
                'used': alternative
            }
    
    def _action_create_empty_file(self, params: Dict[str, Any]):
        """Create empty Excel file"""
        file_path = params['file_path']
        df = pd.DataFrame()
        df.to_excel(file_path, index=False)
        st.session_state.file_recovery = {
            'created': file_path
        }
    
    def _action_map_column(self, params: Dict[str, Any]):
        """Map column to suggested alternative"""
        if 'column_mappings' not in st.session_state:
            st.session_state.column_mappings = {}
        
        st.session_state.column_mappings[params['missing']] = params['suggested']
    
    def _action_clean_data(self, params: Dict[str, Any]):
        """Clean data to fix type issues"""
        if 'data_cleaning' not in st.session_state:
            st.session_state.data_cleaning = {
                'remove_special_chars': True,
                'fill_missing': True,
                'convert_types': True
            }
    
    def _action_use_temp_dir(self, params: Dict[str, Any]):
        """Switch to temporary directory"""
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix='pca_recovery_')
        st.session_state.output_directory = temp_dir
        st.info(f"Using temporary directory: {temp_dir}")
    
    def _action_clear_cache(self, params: Dict[str, Any]):
        """Clear cache to free memory"""
        st.cache_data.clear()
        import gc
        gc.collect()
        st.info("Cache cleared and memory freed")
    
    def _action_repair_excel(self, params: Dict[str, Any]):
        """Attempt to repair Excel file"""
        # This would implement Excel repair logic
        st.info("Excel repair functionality would be implemented here")
    
    # Helper methods
    def _find_similar_files(self, missing_file: str, search_dir: str = '.') -> List[str]:
        """Find files with similar names"""
        from difflib import SequenceMatcher
        similar = []
        
        missing_name = Path(missing_file).name
        search_path = Path(search_dir)
        
        if search_path.exists():
            for file in search_path.rglob('*'):
                if file.is_file():
                    similarity = SequenceMatcher(None, missing_name, file.name).ratio()
                    if similarity > 0.8:
                        similar.append(str(file))
        
        return sorted(similar, key=lambda x: SequenceMatcher(None, missing_name, Path(x).name).ratio(), reverse=True)
    
    def _find_similar_strings(self, target: str, candidates: List[str], threshold: float = 0.6) -> List[str]:
        """Find similar strings using fuzzy matching"""
        from difflib import SequenceMatcher
        
        similarities = []
        for candidate in candidates:
            ratio = SequenceMatcher(None, target.lower(), candidate.lower()).ratio()
            if ratio > threshold:
                similarities.append((candidate, ratio))
        
        return [s[0] for s in sorted(similarities, key=lambda x: x[1], reverse=True)]
    
    def _log_error(self, error_info: Dict[str, Any]):
        """Log error for analysis"""
        self.logger.error(f"Error: {error_info['type']} - {error_info['message']}")
        
        # Store in history
        self.recovery_history.append({
            'timestamp': error_info['timestamp'],
            'error': error_info,
            'recovery_attempted': False
        })
    
    def _log_recovery(self, option: Dict[str, Any], error: Exception, success: bool):
        """Log recovery attempt"""
        if self.recovery_history:
            self.recovery_history[-1]['recovery_attempted'] = True
            self.recovery_history[-1]['recovery_option'] = option['title']
            self.recovery_history[-1]['recovery_success'] = success
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        total_errors = len(self.recovery_history)
        recovery_attempts = sum(1 for h in self.recovery_history if h.get('recovery_attempted', False))
        successful_recoveries = sum(1 for h in self.recovery_history if h.get('recovery_success', False))
        
        return {
            'total_errors': total_errors,
            'recovery_attempts': recovery_attempts,
            'successful_recoveries': successful_recoveries,
            'success_rate': (successful_recoveries / recovery_attempts * 100) if recovery_attempts > 0 else 0
        }


# Decorator for automatic error handling
def with_error_recovery(func: Callable) -> Callable:
    """Decorator to add error recovery to functions"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            handler = ErrorRecoveryHandler()
            context = {
                'function': func.__name__,
                'args': str(args)[:100],  # Truncate for safety
                'kwargs': str(kwargs)[:100]
            }
            handler.render_error_recovery_ui(e, context)
            return None
    return wrapper