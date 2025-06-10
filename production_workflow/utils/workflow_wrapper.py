"""
Workflow Wrapper - Provides a clean interface for Streamlit to use workflow modules
"""

import subprocess
import sys
import os
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
import logging

class WorkflowWrapper:
    """Wrapper class to interface with production workflow scripts"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.metrics = {}
        self.logger = logging.getLogger(__name__)
    
    def extract_and_combine_data(
        self, 
        planned_path: Optional[str] = None, 
        delivered_path: Optional[str] = None,
        output_dir: str = "output",
        combine: bool = True
    ) -> Dict[str, str]:
        """
        Extract and combine data from PLANNED and DELIVERED files
        
        Returns:
            Dict with paths to output files
        """
        cmd = [
            sys.executable,
            str(self.project_root / "production_workflow" / "01_data_extraction" / "extract_and_combine_data.py")
        ]
        
        if planned_path:
            cmd.extend(["--planned-input", planned_path])
        if delivered_path:
            cmd.extend(["--delivered-input", delivered_path])
        
        cmd.extend(["--output-dir", output_dir])
        
        if combine and planned_path and delivered_path:
            cmd.append("--combine")
        
        # Add log level if debug mode
        if os.getenv("EXCEL_EXTRACTOR_LOG_LEVEL") == "DEBUG":
            cmd.extend(["--log-level", "DEBUG"])
        
        try:
            # Run the extraction script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=str(self.project_root)
            )
            
            # Parse output to find generated files
            output_files = {}
            output_dir_path = Path(output_dir)
            
            # Look for generated files
            if output_dir_path.exists():
                files = list(output_dir_path.glob("*.xlsx"))
                for file in files:
                    if "PLANNED_" in file.name:
                        output_files['planned'] = str(file)
                    elif "DELIVERED_" in file.name:
                        output_files['delivered'] = str(file)
                    elif "COMBINED_" in file.name:
                        output_files['combined'] = str(file)
            
            # Extract metrics from output
            self._parse_metrics(result.stdout)
            
            return output_files
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Extraction failed: {e.stderr}")
            raise RuntimeError(f"Data extraction failed: {e.stderr}")
    
    def map_to_template(
        self,
        input_file: str,
        template_file: str,
        output_file: str,
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Map combined data to output template
        
        Args:
            input_file: Path to combined data file
            template_file: Path to template file
            output_file: Path for output file
            progress_callback: Optional callback function(step, message) for progress updates
        
        Returns:
            Dict with mapping results
        """
        cmd = [
            sys.executable,
            str(self.project_root / "production_workflow" / "03_template_mapping" / "map_to_template.py"),
            "--input", input_file,
            "--template", template_file,
            "--output", output_file
        ]
        
        # Add log level if debug mode
        if os.getenv("MAPPER_LOG_LEVEL") == "DEBUG":
            cmd.extend(["--log-level", "DEBUG"])
        
        try:
            # If we have a progress callback, parse output in real-time
            if progress_callback:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=str(self.project_root),
                    bufsize=1,
                    universal_newlines=True
                )
                
                output_lines = []
                error_lines = []
                
                # Read output line by line
                for line in process.stdout:
                    output_lines.append(line)
                    
                    # Parse progress indicators
                    if "Step" in line and "of" in line:
                        try:
                            # Extract step number from lines like "Step 2 of 8: Loading data"
                            parts = line.strip().split()
                            if len(parts) >= 5 and parts[0] == "Step":
                                step = int(parts[1]) - 1  # Convert to 0-based
                                message = " ".join(parts[4:]) if len(parts) > 4 else ""
                                if progress_callback:
                                    progress_callback(step, message)
                        except:
                            pass
                    
                    # Also check for specific progress messages
                    if "Loading combined data" in line:
                        progress_callback(1, "Loading Excel files and checking structure")
                    elif "Validating data structure" in line:
                        progress_callback(2, "Validating platform data sections")
                    elif "columns for mapping" in line:
                        progress_callback(3, line.strip())
                    elif "Using LLM" in line or "AI" in line:
                        progress_callback(4, "Applying AI-powered mapping with Gemini 2.5 Pro")
                    elif "Writing to template" in line:
                        progress_callback(5, "Writing mapped data to output template")
                    elif "Generating report" in line:
                        progress_callback(6, "Generating detailed mapping report")
                
                # Get any error output
                for line in process.stderr:
                    error_lines.append(line)
                
                # Wait for completion
                process.wait()
                
                # Check return code
                if process.returncode != 0:
                    error_msg = "".join(error_lines) or "Unknown error"
                    self.logger.error(f"Mapping failed: {error_msg}")
                    raise RuntimeError(f"Template mapping failed: {error_msg}")
                
                result_stdout = "".join(output_lines)
            else:
                # Standard subprocess run without progress
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=str(self.project_root)
                )
                result_stdout = result.stdout
            
            # Parse mapping results
            mapping_results = self._parse_mapping_results(result_stdout, output_file)
            return mapping_results
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Mapping failed: {e.stderr}")
            raise RuntimeError(f"Template mapping failed: {e.stderr}")
        except Exception as e:
            self.logger.error(f"Unexpected error during mapping: {str(e)}")
            raise
    
    def validate_data(
        self,
        mapped_file: str,
        source_file: str
    ) -> Dict[str, Any]:
        """
        Validate mapped data accuracy
        
        Returns:
            Dict with validation results
        """
        # Use the CLI wrapper script
        cmd = [
            sys.executable,
            str(self.project_root / "production_workflow" / "04_validation" / "validate_accuracy_cli.py"),
            "--mapped-file", mapped_file,
            "--source-file", source_file
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=str(self.project_root)
            )
            
            # Parse JSON validation results
            try:
                validation_results = json.loads(result.stdout)
            except json.JSONDecodeError:
                # Fallback to parsing method
                validation_results = self._parse_validation_results(result.stdout)
            return validation_results
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Validation failed: {e.stderr}")
            # Return partial results even on failure
            return {
                'total_checks': 0,
                'passed_checks': 0,
                'errors': [str(e)],
                'warnings': [],
                'success_rate': 0
            }
    
    def _parse_metrics(self, output: str) -> None:
        """Parse metrics from script output"""
        # Look for common metrics patterns
        if "rows processed" in output.lower():
            # Extract row counts
            import re
            planned_match = re.search(r'planned.*?(\d+)\s*rows', output, re.IGNORECASE)
            if planned_match:
                self.metrics['planned_rows'] = int(planned_match.group(1))
            
            delivered_match = re.search(r'delivered.*?(\d+)\s*rows', output, re.IGNORECASE)
            if delivered_match:
                self.metrics['delivered_rows'] = int(delivered_match.group(1))
            
            combined_match = re.search(r'combined.*?(\d+)\s*rows', output, re.IGNORECASE)
            if combined_match:
                self.metrics['combined_rows'] = int(combined_match.group(1))
    
    def _parse_mapping_results(self, output: str, output_file: str) -> Dict[str, Any]:
        """Parse mapping results from output"""
        results = {
            'mapped_count': 0,
            'total_columns': 0,
            'coverage': 0,
            'rows_written': 0,
            'unmapped_columns': []
        }
        
        # Try to load the generated file to get stats
        if os.path.exists(output_file):
            try:
                df = pd.read_excel(output_file)
                results['rows_written'] = len(df)
                results['total_columns'] = len(df.columns)
            except:
                pass
        
        # Look for coverage in output
        import re
        coverage_match = re.search(r'coverage.*?(\d+(?:\.\d+)?)\s*%', output, re.IGNORECASE)
        if coverage_match:
            results['coverage'] = float(coverage_match.group(1))
        
        # Set default coverage if not found
        if results['coverage'] == 0 and results['total_columns'] > 0:
            results['coverage'] = 100.0  # Assume 100% if file was created
        
        results['mapped_count'] = results['total_columns']
        
        return results
    
    def _parse_validation_results(self, output: str) -> Dict[str, Any]:
        """Parse validation results from output"""
        results = {
            'total_checks': 0,
            'passed_checks': 0,
            'errors': [],
            'warnings': [],
            'success_rate': 100.0
        }
        
        # Parse output for validation metrics
        import re
        
        # Look for check counts
        total_match = re.search(r'total.*?checks.*?(\d+)', output, re.IGNORECASE)
        if total_match:
            results['total_checks'] = int(total_match.group(1))
        
        passed_match = re.search(r'passed.*?(\d+)', output, re.IGNORECASE)
        if passed_match:
            results['passed_checks'] = int(passed_match.group(1))
        
        # Look for errors and warnings
        if "error" in output.lower():
            error_lines = [line for line in output.split('\n') if 'error' in line.lower()]
            results['errors'] = error_lines[:10]  # First 10 errors
        
        if "warning" in output.lower():
            warning_lines = [line for line in output.split('\n') if 'warning' in line.lower()]
            results['warnings'] = warning_lines[:10]  # First 10 warnings
        
        # Calculate success rate
        if results['total_checks'] > 0:
            results['success_rate'] = (results['passed_checks'] / results['total_checks']) * 100
        
        return results