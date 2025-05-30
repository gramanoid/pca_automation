#!/usr/bin/env python3
"""
Enhanced Data Accuracy Validator with Multi-Level Checks
Performs forensic-grade validation with SHA-256 fingerprinting and detailed reporting
"""

import pandas as pd
import numpy as np
import hashlib
import json
import csv
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import argparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CellFingerprint:
    """Forensic fingerprint for each cell"""
    location: str  # e.g., "A1", "B2"
    value: Any
    value_type: str
    sha256_hash: str
    source_file: str
    source_sheet: str
    timestamp: str


@dataclass
class ValidationResult:
    """Result of a validation check"""
    level: str  # 'cell', 'row', 'section', 'grand_total'
    location: str
    expected: Any
    actual: Any
    diff_pct: float
    passed: bool
    message: str


class ValidationError(Exception):
    """Custom exception for validation failures"""
    pass


class EnhancedDataValidator:
    """Multi-level data accuracy validator with forensic capabilities"""
    
    def __init__(self, tolerance: float = 0.001, strict_mode: bool = True):
        """
        Initialize validator with configurable tolerance.
        
        Args:
            tolerance: Maximum allowed difference (0.001 = 0.1%)
            strict_mode: If True, fail on any mismatch
        """
        self.tolerance = tolerance
        self.strict_mode = strict_mode
        self.cell_registry: Dict[str, CellFingerprint] = {}
        self.validation_results: List[ValidationResult] = []
        self.accuracy_summary = {
            'cell': {'total': 0, 'passed': 0, 'failed': 0},
            'row': {'total': 0, 'passed': 0, 'failed': 0},
            'section': {'total': 0, 'passed': 0, 'failed': 0},
            'grand_total': {'total': 0, 'passed': 0, 'failed': 0}
        }
    
    def validate_accuracy(self, source_df: pd.DataFrame, output_df: pd.DataFrame, 
                         mapping_info: Dict = None) -> Dict:
        """
        Perform comprehensive multi-level validation.
        
        Args:
            source_df: Original source data
            output_df: Mapped output data
            mapping_info: Column mapping information
            
        Returns:
            Dict with validation results and accuracy metrics
        """
        logger.info("Starting multi-level data accuracy validation...")
        
        # Reset results
        self.validation_results = []
        self.cell_registry = {}
        
        # Level 1: Cell-level validation
        cell_results = self._validate_cells(source_df, output_df, mapping_info)
        
        # Level 2: Row-level validation
        row_results = self._validate_rows(source_df, output_df)
        
        # Level 3: Section-level validation
        section_results = self._validate_sections(source_df, output_df)
        
        # Level 4: Grand total validation
        total_results = self._validate_totals(source_df, output_df)
        
        # Calculate overall accuracy
        overall_accuracy = self._calculate_overall_accuracy()
        
        # Generate comprehensive report
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_accuracy': overall_accuracy,
            'accuracy_by_level': self.accuracy_summary,
            'cell_level': cell_results,
            'row_level': row_results,
            'section_level': section_results,
            'grand_total': total_results,
            'validation_results': self.validation_results,
            'cell_fingerprints': len(self.cell_registry),
            'tolerance_used': self.tolerance,
            'strict_mode': self.strict_mode
        }
        
        # Fail-fast check if strict mode
        if self.strict_mode and overall_accuracy < 100.0:
            raise ValidationError(
                f"Validation failed: Overall accuracy {overall_accuracy:.2f}% < 100%"
            )
        
        return report
    
    def _validate_cells(self, source_df: pd.DataFrame, output_df: pd.DataFrame, 
                       mapping_info: Dict = None) -> Dict:
        """Perform cell-by-cell validation with SHA-256 fingerprinting."""
        logger.info("Performing cell-level validation...")
        
        mismatches = []
        total_cells = 0
        cells_passed = 0
        
        # Get column mappings
        if mapping_info:
            column_map = mapping_info
        else:
            # Auto-detect mappings based on column names
            column_map = self._auto_detect_mappings(source_df, output_df)
        
        # Validate each mapped column
        for source_col, output_col in column_map.items():
            if source_col not in source_df.columns or output_col not in output_df.columns:
                continue
                
            for idx in range(min(len(source_df), len(output_df))):
                total_cells += 1
                location = f"{output_col}{idx+2}"  # Excel-style reference
                
                source_val = source_df.iloc[idx][source_col]
                output_val = output_df.iloc[idx][output_col]
                
                # Create cell fingerprints
                source_fp = self._create_fingerprint(
                    f"{source_col}{idx+2}", source_val, "source", "source"
                )
                output_fp = self._create_fingerprint(
                    location, output_val, "output", "output"
                )
                
                self.cell_registry[f"source_{source_col}_{idx}"] = source_fp
                self.cell_registry[f"output_{output_col}_{idx}"] = output_fp
                
                # Compare values
                match, diff_pct = self._compare_values(source_val, output_val)
                
                if match:
                    cells_passed += 1
                else:
                    mismatches.append({
                        'location': location,
                        'source_column': source_col,
                        'output_column': output_col,
                        'row': idx,
                        'expected': source_val,
                        'actual': output_val,
                        'diff_pct': diff_pct,
                        'source_hash': source_fp.sha256_hash,
                        'output_hash': output_fp.sha256_hash
                    })
                    
                    self.validation_results.append(ValidationResult(
                        level='cell',
                        location=location,
                        expected=source_val,
                        actual=output_val,
                        diff_pct=diff_pct,
                        passed=False,
                        message=f"Cell mismatch: {source_col} -> {output_col}"
                    ))
        
        # Update summary
        self.accuracy_summary['cell']['total'] = total_cells
        self.accuracy_summary['cell']['passed'] = cells_passed
        self.accuracy_summary['cell']['failed'] = len(mismatches)
        
        accuracy = (cells_passed / total_cells * 100) if total_cells > 0 else 0
        
        return {
            'accuracy': accuracy,
            'total_cells': total_cells,
            'cells_passed': cells_passed,
            'cells_failed': len(mismatches),
            'mismatches': mismatches[:100]  # Limit to first 100 for readability
        }
    
    def _validate_rows(self, source_df: pd.DataFrame, output_df: pd.DataFrame) -> Dict:
        """Validate data integrity at row level."""
        logger.info("Performing row-level validation...")
        
        row_mismatches = []
        total_rows = min(len(source_df), len(output_df))
        rows_passed = 0
        
        numeric_columns = source_df.select_dtypes(include=[np.number]).columns
        
        for idx in range(total_rows):
            row_valid = True
            row_errors = []
            
            # Check row sums for numeric columns
            for col in numeric_columns:
                if col in output_df.columns:
                    source_sum = source_df.iloc[idx][numeric_columns].sum()
                    output_sum = output_df.iloc[idx][numeric_columns].sum()
                    
                    match, diff_pct = self._compare_values(source_sum, output_sum)
                    if not match:
                        row_valid = False
                        row_errors.append({
                            'metric': 'row_sum',
                            'expected': source_sum,
                            'actual': output_sum,
                            'diff_pct': diff_pct
                        })
            
            if row_valid:
                rows_passed += 1
            else:
                row_mismatches.append({
                    'row': idx,
                    'errors': row_errors
                })
                
                self.validation_results.append(ValidationResult(
                    level='row',
                    location=f"Row {idx+2}",
                    expected=None,
                    actual=None,
                    diff_pct=0,
                    passed=False,
                    message=f"Row validation failed with {len(row_errors)} errors"
                ))
        
        # Update summary
        self.accuracy_summary['row']['total'] = total_rows
        self.accuracy_summary['row']['passed'] = rows_passed
        self.accuracy_summary['row']['failed'] = len(row_mismatches)
        
        accuracy = (rows_passed / total_rows * 100) if total_rows > 0 else 0
        
        return {
            'accuracy': accuracy,
            'total_rows': total_rows,
            'rows_passed': rows_passed,
            'rows_failed': len(row_mismatches),
            'mismatches': row_mismatches[:50]
        }
    
    def _validate_sections(self, source_df: pd.DataFrame, output_df: pd.DataFrame) -> Dict:
        """Validate data by logical sections (platforms, markets, etc.)."""
        logger.info("Performing section-level validation...")
        
        section_results = {}
        total_sections = 0
        sections_passed = 0
        
        # Validate by platform if column exists
        if 'PLATFORM' in source_df.columns and 'PLATFORM' in output_df.columns:
            platforms = source_df['PLATFORM'].unique()
            
            for platform in platforms:
                total_sections += 1
                source_platform = source_df[source_df['PLATFORM'] == platform]
                output_platform = output_df[output_df['PLATFORM'] == platform]
                
                if len(output_platform) == 0:
                    section_results[f"platform_{platform}"] = {
                        'passed': False,
                        'message': f"Platform {platform} missing in output"
                    }
                    continue
                
                # Check platform totals
                numeric_cols = source_platform.select_dtypes(include=[np.number]).columns
                all_match = True
                
                for col in numeric_cols:
                    if col in output_platform.columns:
                        source_total = source_platform[col].sum()
                        output_total = output_platform[col].sum()
                        
                        match, diff_pct = self._compare_values(source_total, output_total)
                        if not match:
                            all_match = False
                            self.validation_results.append(ValidationResult(
                                level='section',
                                location=f"Platform_{platform}_{col}",
                                expected=source_total,
                                actual=output_total,
                                diff_pct=diff_pct,
                                passed=False,
                                message=f"Platform {platform} total mismatch for {col}"
                            ))
                
                if all_match:
                    sections_passed += 1
                    section_results[f"platform_{platform}"] = {'passed': True}
                else:
                    section_results[f"platform_{platform}"] = {'passed': False}
        
        # Update summary
        self.accuracy_summary['section']['total'] = total_sections
        self.accuracy_summary['section']['passed'] = sections_passed
        self.accuracy_summary['section']['failed'] = total_sections - sections_passed
        
        accuracy = (sections_passed / total_sections * 100) if total_sections > 0 else 100
        
        return {
            'accuracy': accuracy,
            'total_sections': total_sections,
            'sections_passed': sections_passed,
            'sections_failed': total_sections - sections_passed,
            'section_details': section_results
        }
    
    def _validate_totals(self, source_df: pd.DataFrame, output_df: pd.DataFrame) -> Dict:
        """Validate grand totals for all numeric columns."""
        logger.info("Performing grand total validation...")
        
        total_mismatches = []
        numeric_columns = source_df.select_dtypes(include=[np.number]).columns
        total_columns = 0
        columns_passed = 0
        
        for col in numeric_columns:
            if col in output_df.columns:
                total_columns += 1
                source_total = source_df[col].sum()
                output_total = output_df[col].sum()
                
                match, diff_pct = self._compare_values(source_total, output_total)
                
                if match:
                    columns_passed += 1
                else:
                    total_mismatches.append({
                        'column': col,
                        'expected': source_total,
                        'actual': output_total,
                        'diff_pct': diff_pct
                    })
                    
                    self.validation_results.append(ValidationResult(
                        level='grand_total',
                        location=f"Total_{col}",
                        expected=source_total,
                        actual=output_total,
                        diff_pct=diff_pct,
                        passed=False,
                        message=f"Grand total mismatch for {col}"
                    ))
        
        # Update summary
        self.accuracy_summary['grand_total']['total'] = total_columns
        self.accuracy_summary['grand_total']['passed'] = columns_passed
        self.accuracy_summary['grand_total']['failed'] = len(total_mismatches)
        
        accuracy = (columns_passed / total_columns * 100) if total_columns > 0 else 100
        
        return {
            'accuracy': accuracy,
            'total_columns': total_columns,
            'columns_passed': columns_passed,
            'columns_failed': len(total_mismatches),
            'mismatches': total_mismatches
        }
    
    def _compare_values(self, val1: Any, val2: Any) -> Tuple[bool, float]:
        """
        Compare two values with appropriate tolerance.
        
        Returns:
            Tuple of (match: bool, diff_pct: float)
        """
        # Handle None/NaN cases
        if pd.isna(val1) and pd.isna(val2):
            return True, 0.0
        if pd.isna(val1) or pd.isna(val2):
            return False, 100.0
        
        # Handle string values
        if isinstance(val1, str) or isinstance(val2, str):
            return str(val1).strip() == str(val2).strip(), 0.0 if val1 == val2 else 100.0
        
        # Handle numeric values
        try:
            num1 = float(val1)
            num2 = float(val2)
            
            # Use Decimal for precise comparison
            dec1 = Decimal(str(num1))
            dec2 = Decimal(str(num2))
            
            if dec1 == 0 and dec2 == 0:
                return True, 0.0
            
            # Calculate percentage difference
            if dec1 == 0:
                diff_pct = float(abs(dec2) * 100)
            else:
                diff_pct = float(abs(dec2 - dec1) / abs(dec1) * 100)
            
            # Check against tolerance
            return diff_pct <= (self.tolerance * 100), diff_pct
            
        except (ValueError, TypeError):
            return val1 == val2, 0.0 if val1 == val2 else 100.0
    
    def _create_fingerprint(self, location: str, value: Any, 
                           source_file: str, source_sheet: str) -> CellFingerprint:
        """Create SHA-256 fingerprint for a cell value."""
        # Convert value to string for hashing
        value_str = str(value) if not pd.isna(value) else "NULL"
        value_bytes = value_str.encode('utf-8')
        
        # Create SHA-256 hash
        sha256_hash = hashlib.sha256(value_bytes).hexdigest()
        
        # Determine value type
        if pd.isna(value):
            value_type = "null"
        elif isinstance(value, (int, float)):
            value_type = "numeric"
        elif isinstance(value, str):
            value_type = "string"
        elif isinstance(value, datetime):
            value_type = "datetime"
        else:
            value_type = "other"
        
        return CellFingerprint(
            location=location,
            value=value,
            value_type=value_type,
            sha256_hash=sha256_hash,
            source_file=source_file,
            source_sheet=source_sheet,
            timestamp=datetime.now().isoformat()
        )
    
    def _auto_detect_mappings(self, source_df: pd.DataFrame, 
                             output_df: pd.DataFrame) -> Dict[str, str]:
        """Auto-detect column mappings based on column names and data patterns."""
        mappings = {}
        
        # First try exact matches
        for col in source_df.columns:
            if col in output_df.columns:
                mappings[col] = col
        
        # Then try common variations
        variations = {
            'BUDGET': ['Budget', 'BUDGET_LOCAL', 'BUDGET_USD'],
            'SPEND': ['Spend', 'SPEND_LOCAL', 'SPEND_USD', 'Actual Spend'],
            'IMPRESSIONS': ['Impressions', 'Imps', 'IMPRESSIONS'],
            'CLICKS': ['Clicks', 'CLICKS'],
            'CTR': ['CTR', 'CTR%', 'Click Rate'],
            'CPM': ['CPM', 'Cost per Mille'],
            'CPC': ['CPC', 'Cost per Click']
        }
        
        for source_col in source_df.columns:
            if source_col not in mappings:
                for base, variants in variations.items():
                    if source_col in variants:
                        for output_col in output_df.columns:
                            if output_col in variants:
                                mappings[source_col] = output_col
                                break
        
        return mappings
    
    def _calculate_overall_accuracy(self) -> float:
        """Calculate weighted overall accuracy across all levels."""
        weights = {
            'cell': 0.4,
            'row': 0.2,
            'section': 0.2,
            'grand_total': 0.2
        }
        
        total_accuracy = 0.0
        for level, weight in weights.items():
            level_data = self.accuracy_summary[level]
            if level_data['total'] > 0:
                level_accuracy = level_data['passed'] / level_data['total'] * 100
                total_accuracy += level_accuracy * weight
        
        return total_accuracy
    
    def generate_diff_report(self, output_path: str, max_rows: int = 1000):
        """Generate detailed CSV diff report."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_path = Path(output_path) / f"validation_diff_report_{timestamp}.csv"
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'level', 'location', 'expected', 'actual', 'diff_pct', 
                'passed', 'message', 'timestamp'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write all validation results (up to max_rows)
            for i, result in enumerate(self.validation_results[:max_rows]):
                writer.writerow({
                    'level': result.level,
                    'location': result.location,
                    'expected': result.expected,
                    'actual': result.actual,
                    'diff_pct': f"{result.diff_pct:.2f}%",
                    'passed': result.passed,
                    'message': result.message,
                    'timestamp': datetime.now().isoformat()
                })
        
        logger.info(f"Diff report saved to: {csv_path}")
        return csv_path
    
    def generate_summary_report(self, report: Dict, output_path: str):
        """Generate human-readable summary report."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = Path(output_path) / f"validation_summary_{timestamp}.txt"
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("DATA ACCURACY VALIDATION REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Generated: {report['timestamp']}\n")
            f.write(f"Overall Accuracy: {report['overall_accuracy']:.2f}%\n")
            f.write(f"Tolerance: {report['tolerance_used']*100:.1f}%\n")
            f.write(f"Strict Mode: {report['strict_mode']}\n\n")
            
            # Level summaries
            f.write("ACCURACY BY LEVEL\n")
            f.write("-" * 40 + "\n")
            for level, data in report['accuracy_by_level'].items():
                accuracy = (data['passed'] / data['total'] * 100) if data['total'] > 0 else 0
                f.write(f"{level.upper():15} {accuracy:6.2f}% ({data['passed']:,}/{data['total']:,})\n")
            
            f.write("\n")
            
            # Cell level details
            if report['cell_level']['cells_failed'] > 0:
                f.write(f"\nCELL LEVEL MISMATCHES (Top 10 of {report['cell_level']['cells_failed']})\n")
                f.write("-" * 40 + "\n")
                for i, mismatch in enumerate(report['cell_level']['mismatches'][:10]):
                    f.write(f"{i+1}. {mismatch['location']} ({mismatch['source_column']} -> {mismatch['output_column']})\n")
                    f.write(f"   Expected: {mismatch['expected']}\n")
                    f.write(f"   Actual: {mismatch['actual']}\n")
                    f.write(f"   Diff: {mismatch['diff_pct']:.2f}%\n\n")
            
            # Grand total details
            if report['grand_total']['columns_failed'] > 0:
                f.write(f"\nGRAND TOTAL MISMATCHES ({report['grand_total']['columns_failed']} columns)\n")
                f.write("-" * 40 + "\n")
                for mismatch in report['grand_total']['mismatches']:
                    f.write(f"Column: {mismatch['column']}\n")
                    f.write(f"  Expected Total: {mismatch['expected']:,.2f}\n")
                    f.write(f"  Actual Total: {mismatch['actual']:,.2f}\n")
                    f.write(f"  Difference: {mismatch['diff_pct']:.2f}%\n\n")
        
        logger.info(f"Summary report saved to: {report_path}")
        return report_path


def main():
    """Command line interface for data accuracy validator"""
    parser = argparse.ArgumentParser(
        description='Validate data accuracy with multi-level checks'
    )
    parser.add_argument(
        '--source',
        required=True,
        help='Path to source data file'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Path to output/mapped data file'
    )
    parser.add_argument(
        '--tolerance',
        type=float,
        default=0.001,
        help='Tolerance for numeric comparisons (default: 0.001 = 0.1%)'
    )
    parser.add_argument(
        '--fail-fast',
        action='store_true',
        help='Exit with code 1 if accuracy < 100%'
    )
    parser.add_argument(
        '--report-dir',
        default='.',
        help='Directory for saving reports (default: current directory)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load data
        source_df = pd.read_excel(args.source)
        output_df = pd.read_excel(args.output)
        
        # Initialize validator
        validator = EnhancedDataValidator(
            tolerance=args.tolerance,
            strict_mode=args.fail_fast
        )
        
        # Run validation
        report = validator.validate_accuracy(source_df, output_df)
        
        # Generate reports
        report_dir = Path(args.report_dir)
        report_dir.mkdir(exist_ok=True)
        
        diff_path = validator.generate_diff_report(str(report_dir))
        summary_path = validator.generate_summary_report(report, str(report_dir))
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"VALIDATION COMPLETE")
        print(f"{'='*60}")
        print(f"Overall Accuracy: {report['overall_accuracy']:.2f}%")
        print(f"Status: {'✅ PASSED' if report['overall_accuracy'] >= 100 else '❌ FAILED'}")
        print(f"\nReports saved:")
        print(f"  - Diff Report: {diff_path}")
        print(f"  - Summary: {summary_path}")
        
        # Exit code based on result
        if args.fail_fast and report['overall_accuracy'] < 100:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        print(f"\n❌ VALIDATION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()