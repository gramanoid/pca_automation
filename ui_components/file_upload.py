"""
File Upload Component for PCA Automation
Handles file upload, validation, and preview functionality
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import os

class FileUploadComponent:
    """Component for handling file uploads with validation and preview"""
    
    def __init__(self):
        self.file_type_configs = {
            'PLANNED': {
                'title': '📋 PLANNED File',
                'help_text': 'Media plan template (e.g., PLANNED_INPUT_TEMPLATE_*.xlsx)',
                'required_sheets': ['DV360', 'META', 'TIKTOK'],
                'validation_type': 'planned'
            },
            'DELIVERED': {
                'title': '📈 DELIVERED File',
                'help_text': 'Platform data exports (e.g., DELIVERED_INPUT_TEMPLATE_*.xlsx)',
                'sheet_patterns': ['DV360', 'META', 'TIKTOK'],
                'validation_type': 'delivered'
            },
            'TEMPLATE': {
                'title': '📄 OUTPUT TEMPLATE',
                'help_text': 'Empty template to fill (e.g., OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx)',
                'validation_type': 'template'
            }
        }
    
    def validate_uploaded_file(self, file, file_type: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        Validate uploaded file format and structure
        
        Returns:
            Tuple of (is_valid, message, preview_df)
        """
        try:
            # Try to read the Excel file
            df_first_sheet = pd.read_excel(file, sheet_name=0, nrows=10)
            
            # Reset file pointer for further processing
            file.seek(0)
            
            # Type-specific validation
            if file_type == "PLANNED":
                # Check for required sheets
                xl_file = pd.ExcelFile(file)
                required_sheets = self.file_type_configs['PLANNED']['required_sheets']
                missing_sheets = [sheet for sheet in required_sheets if sheet not in xl_file.sheet_names]
                
                if missing_sheets:
                    return False, f"❌ Missing required sheets: {', '.join(missing_sheets)}", None
                
                file.seek(0)
                return True, f"✅ Valid PLANNED file with {len(xl_file.sheet_names)} sheets", df_first_sheet
                
            elif file_type == "DELIVERED":
                # Check for platform data
                xl_file = pd.ExcelFile(file)
                platform_sheets = [s for s in xl_file.sheet_names 
                                 if any(p in s.upper() for p in self.file_type_configs['DELIVERED']['sheet_patterns'])]
                
                if not platform_sheets:
                    return False, "❌ No platform sheets found (DV360, META, or TIKTOK)", None
                    
                file.seek(0)
                return True, f"✅ Valid DELIVERED file with {len(platform_sheets)} platform sheets", df_first_sheet
                
            elif file_type == "TEMPLATE":
                # For templates, we need to check the actual structure
                try:
                    xl_file = pd.ExcelFile(file)
                    sheet_names = xl_file.sheet_names
                    
                    # Basic validation - just check if it's a valid Excel file with at least one sheet
                    if len(sheet_names) == 0:
                        return False, "❌ No sheets found in template", None
                    
                    file.seek(0)
                    return True, f"✅ Valid OUTPUT TEMPLATE file with {len(sheet_names)} sheet(s)", df_first_sheet
                except Exception as e:
                    return False, f"❌ Error validating template: {str(e)}", None
                
            else:
                file.seek(0)
                return True, "✅ File loaded successfully", df_first_sheet
                
        except Exception as e:
            return False, f"❌ Error reading file: {str(e)}", None
    
    def save_uploaded_file(self, uploaded_file, file_type: str, temp_dir: str) -> Optional[Path]:
        """Save uploaded file to temporary directory"""
        if uploaded_file is not None:
            file_path = Path(temp_dir) / f"{file_type}_{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.uploaded_files[file_type] = file_path
            return file_path
        return None
    
    def render_file_upload(self, file_type: str, column) -> Dict[str, Any]:
        """
        Render file upload widget with validation and preview
        
        Returns:
            Dict with upload status and file information
        """
        config = self.file_type_configs[file_type]
        
        with column:
            st.subheader(config['title'])
            
            # File uploader
            uploaded_file = st.file_uploader(
                f"Upload {file_type} Excel file",
                type=['xlsx', 'xls'],
                key=f"{file_type.lower()}_uploader",
                help=config['help_text']
            )
            
            result = {
                'uploaded': False,
                'valid': False,
                'file_path': None,
                'message': None
            }
            
            if uploaded_file:
                # Validate file
                is_valid, message, preview_df = self.validate_uploaded_file(uploaded_file, file_type)
                st.session_state.file_validation[file_type] = is_valid
                
                if is_valid:
                    st.success(message)
                    file_path = self.save_uploaded_file(
                        uploaded_file, 
                        file_type, 
                        st.session_state.temp_dir
                    )
                    
                    result['uploaded'] = True
                    result['valid'] = True
                    result['file_path'] = file_path
                    result['message'] = message
                    
                    # Show preview
                    with st.expander("📊 Preview uploaded data"):
                        st.dataframe(preview_df, use_container_width=True)
                        st.caption(f"Showing first 10 rows")
                else:
                    st.error(message)
                    result['uploaded'] = True
                    result['valid'] = False
                    result['message'] = message
            
            return result
    
    def render_upload_summary(self, upload_results: Dict[str, Dict[str, Any]]) -> Tuple[bool, bool]:
        """
        Render upload summary and check if all files are ready
        
        Returns:
            Tuple of (all_uploaded, all_valid)
        """
        all_uploaded = all(result['uploaded'] for result in upload_results.values())
        all_valid = all(result['valid'] for result in upload_results.values() if result['uploaded'])
        
        if all_uploaded and all_valid:
            st.markdown(
                '<div class="success-message">✅ All required files uploaded and validated! '
                'Proceeding to marker validation...</div>', 
                unsafe_allow_html=True
            )
        elif all_uploaded and not all_valid:
            invalid_files = [
                file_type for file_type, result in upload_results.items() 
                if result['uploaded'] and not result['valid']
            ]
            st.error(f"⚠️ Please fix validation errors for: {', '.join(invalid_files)}")
        else:
            missing_files = [
                file_type for file_type, result in upload_results.items() 
                if not result['uploaded']
            ]
            if missing_files:
                st.warning(f"⚠️ Please upload all required files. Missing: {', '.join(missing_files)}")
        
        return all_uploaded, all_valid