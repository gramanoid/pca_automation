"""
Production Error Handler for Media Plan to Raw Data Automation
Handles edge cases, validates data integrity, and provides detailed logging
"""

import logging
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import traceback
import json
import os

class ProductionErrorHandler:
    """Comprehensive error handling for production deployment"""
    
    def __init__(self, log_level: str = "INFO"):
        """Initialize error handler with logging configuration"""
        self.setup_logging(log_level)
        self.error_log = []
        self.warning_log = []
        self.validation_results = {}
        
    def setup_logging(self, log_level: str):
        """Configure production-grade logging"""
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        simple_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # File handler for all logs
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f'production_{datetime.now().strftime("%Y%m%d")}.log')
        )
        file_handler.setFormatter(detailed_formatter)
        
        # Error file handler
        error_handler = logging.FileHandler(
            os.path.join(log_dir, f'errors_{datetime.now().strftime("%Y%m%d")}.log')
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(simple_formatter)
        
        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_level))
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)
        
    def validate_rf_data_structure(self, df: pd.DataFrame, source_type: str) -> Dict[str, Any]:
        """Validate R&F data structure and integrity"""
        validation_report = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        try:
            # Check if this is R&F data
            if 'DELIVERED R&F' in source_type or '_RF' in str(df.get('Source_Sheet', pd.Series()).iloc[0] if not df.empty else ''):
                self.logger.info("Validating R&F data structure...")
                
                # Required columns for R&F data
                required_rf_columns = ['PLATFORM', 'MARKET', 'UNIQUES_REACH']
                missing_columns = [col for col in required_rf_columns if col not in df.columns]
                
                if missing_columns:
                    validation_report['is_valid'] = False
                    validation_report['errors'].append(f"Missing required R&F columns: {missing_columns}")
                    return validation_report
                
                # Check if PLATFORM column contains metric names
                rf_metrics = ['Campaign Reach (Absl)', 'Campaign Reach (%)', 'Campaign Frequency', 
                            'Campaign EffReach 1+', 'Campaign EffReach 2+', 'Campaign EffReach 3+']
                
                platform_values = df['PLATFORM'].unique()
                found_metrics = [m for m in rf_metrics if m in platform_values]
                
                if not found_metrics:
                    validation_report['warnings'].append(
                        f"Expected R&F metrics in PLATFORM column but found: {list(platform_values)[:5]}"
                    )
                
                # Validate numeric data
                if 'UNIQUES_REACH' in df.columns:
                    numeric_df = pd.to_numeric(df['UNIQUES_REACH'], errors='coerce')
                    null_count = numeric_df.isna().sum()
                    if null_count > 0:
                        validation_report['warnings'].append(
                            f"Found {null_count} non-numeric values in UNIQUES_REACH"
                        )
                    
                    # Check for negative values
                    negative_count = (numeric_df < 0).sum()
                    if negative_count > 0:
                        validation_report['errors'].append(
                            f"Found {negative_count} negative values in UNIQUES_REACH"
                        )
                        validation_report['is_valid'] = False
                
                # Check market consistency
                if 'MARKET' in df.columns:
                    markets = df['MARKET'].dropna().unique()
                    validation_report['metrics']['unique_markets'] = len(markets)
                    validation_report['metrics']['markets'] = list(markets)
                
                # Data completeness check
                total_rows = len(df)
                complete_rows = len(df.dropna(subset=['PLATFORM', 'MARKET', 'UNIQUES_REACH']))
                completeness = (complete_rows / total_rows * 100) if total_rows > 0 else 0
                
                validation_report['metrics']['total_rows'] = total_rows
                validation_report['metrics']['complete_rows'] = complete_rows
                validation_report['metrics']['completeness_pct'] = completeness
                
                if completeness < 80:
                    validation_report['warnings'].append(
                        f"Low data completeness: {completeness:.1f}% ({complete_rows}/{total_rows} complete rows)"
                    )
                
        except Exception as e:
            validation_report['is_valid'] = False
            validation_report['errors'].append(f"Validation error: {str(e)}")
            self.logger.error(f"R&F validation failed: {e}", exc_info=True)
            
        return validation_report
        
    def validate_platform_data(self, df: pd.DataFrame, platform: str) -> Dict[str, Any]:
        """Validate platform-specific data integrity"""
        validation_report = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        try:
            # Filter data for this platform
            platform_data = self._filter_platform_data(df, platform)
            
            if platform_data.empty:
                validation_report['warnings'].append(f"No data found for platform: {platform}")
                return validation_report
                
            # Check required columns
            media_required = ['IMPRESSIONS', 'CLICKS_ACTIONS', 'BUDGET_LOCAL']
            missing = [col for col in media_required if col not in platform_data.columns]
            
            if missing:
                validation_report['warnings'].append(f"Missing columns for {platform}: {missing}")
                
            # Validate numeric consistency
            for col in ['IMPRESSIONS', 'CLICKS_ACTIONS']:
                if col in platform_data.columns:
                    numeric_col = pd.to_numeric(platform_data[col], errors='coerce')
                    if numeric_col.min() < 0:
                        validation_report['errors'].append(f"Negative values found in {col}")
                        validation_report['is_valid'] = False
                        
            # CTR validation
            if 'CTR' in platform_data.columns and 'IMPRESSIONS' in platform_data.columns:
                ctr_issues = self._validate_ctr(platform_data)
                if ctr_issues:
                    validation_report['warnings'].extend(ctr_issues)
                    
            # Budget validation
            if 'BUDGET_LOCAL' in platform_data.columns:
                budget_sum = pd.to_numeric(platform_data['BUDGET_LOCAL'], errors='coerce').sum()
                validation_report['metrics']['total_budget'] = budget_sum
                
                if budget_sum <= 0:
                    validation_report['warnings'].append(f"Zero or negative total budget for {platform}")
                    
        except Exception as e:
            validation_report['errors'].append(f"Platform validation error: {str(e)}")
            self.logger.error(f"Platform validation failed for {platform}: {e}", exc_info=True)
            
        return validation_report
        
    def _filter_platform_data(self, df: pd.DataFrame, platform: str) -> pd.DataFrame:
        """Filter data for specific platform with alias handling"""
        platform_aliases = {
            'DV360': ['DV360', 'YOUTUBE', 'DISPLAY & VIDEO 360', 'GOOGLE DV360', 'DV 360'],
            'META': ['META', 'FACEBOOK', 'FB', 'INSTAGRAM', 'IG', 'FACEBOOK/INSTAGRAM'],
            'TIKTOK': ['TIKTOK', 'TIK TOK', 'TIKTOK ADS', 'TT']
        }
        
        # Get all aliases for this platform
        aliases = platform_aliases.get(platform, [platform])
        
        # Filter by Source_Sheet first
        if 'Source_Sheet' in df.columns:
            platform_mask = df['Source_Sheet'].str.upper().isin([a.upper() for a in aliases])
            # Also check for _MEDIA suffix
            media_mask = df['Source_Sheet'].str.upper().isin([f"{a.upper()}_MEDIA" for a in aliases])
            return df[platform_mask | media_mask]
            
        return pd.DataFrame()
        
    def _validate_ctr(self, df: pd.DataFrame) -> List[str]:
        """Validate CTR calculations"""
        issues = []
        
        try:
            ctr = pd.to_numeric(df['CTR'], errors='coerce')
            impressions = pd.to_numeric(df['IMPRESSIONS'], errors='coerce')
            clicks = pd.to_numeric(df.get('CLICKS_ACTIONS', 0), errors='coerce')
            
            # Check if CTR is in percentage (0-100) or decimal (0-1)
            if ctr.max() > 1:
                # Likely percentage
                calculated_ctr = (clicks / impressions * 100).fillna(0)
            else:
                # Likely decimal
                calculated_ctr = (clicks / impressions).fillna(0)
                
            # Allow 5% tolerance for rounding
            diff = abs(ctr - calculated_ctr)
            tolerance = calculated_ctr * 0.05
            
            discrepancies = diff > tolerance
            if discrepancies.any():
                count = discrepancies.sum()
                issues.append(f"Found {count} CTR calculation discrepancies (>5% difference)")
                
        except Exception as e:
            issues.append(f"CTR validation error: {str(e)}")
            
        return issues
        
    def handle_missing_data(self, df: pd.DataFrame, context: Dict[str, Any]) -> pd.DataFrame:
        """Handle missing data with appropriate defaults"""
        try:
            # Define default values by column type
            defaults = {
                'numeric': 0,
                'percentage': 0,
                'text': '-',
                'date': None
            }
            
            # Column type mapping
            numeric_cols = ['IMPRESSIONS', 'CLICKS_ACTIONS', 'VIDEO_VIEWS', 'UNIQUES_REACH',
                           'BUDGET_LOCAL', 'PLATFORM_BUDGET_LOCAL', 'PLATFORM_FEE_LOCAL']
            percentage_cols = ['CTR', 'VTR']
            
            # Apply defaults
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    
            for col in percentage_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    
            # Log missing data summary
            missing_summary = df.isnull().sum()
            if missing_summary.any():
                self.logger.info(f"Missing data handled: {missing_summary[missing_summary > 0].to_dict()}")
                
        except Exception as e:
            self.logger.error(f"Error handling missing data: {e}", exc_info=True)
            
        return df
        
    def create_validation_report(self, results: Dict[str, Any]) -> str:
        """Create comprehensive validation report"""
        report_lines = [
            "=" * 70,
            "PRODUCTION VALIDATION REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 70,
            ""
        ]
        
        # Overall status
        all_valid = all(r.get('is_valid', False) for r in results.values() if isinstance(r, dict))
        report_lines.append(f"Overall Status: {'✅ PASS' if all_valid else '❌ FAIL'}")
        report_lines.append("")
        
        # Detailed results
        for component, result in results.items():
            if isinstance(result, dict):
                report_lines.append(f"\n{component.upper()}")
                report_lines.append("-" * 40)
                
                # Status
                is_valid = result.get('is_valid', False)
                report_lines.append(f"Status: {'✅ Valid' if is_valid else '❌ Invalid'}")
                
                # Errors
                if result.get('errors'):
                    report_lines.append("\nErrors:")
                    for error in result['errors']:
                        report_lines.append(f"  ❌ {error}")
                        
                # Warnings
                if result.get('warnings'):
                    report_lines.append("\nWarnings:")
                    for warning in result['warnings']:
                        report_lines.append(f"  ⚠️ {warning}")
                        
                # Metrics
                if result.get('metrics'):
                    report_lines.append("\nMetrics:")
                    for key, value in result['metrics'].items():
                        report_lines.append(f"  • {key}: {value}")
                        
        # Summary
        report_lines.extend([
            "",
            "=" * 70,
            "SUMMARY",
            "=" * 70
        ])
        
        error_count = sum(len(r.get('errors', [])) for r in results.values() if isinstance(r, dict))
        warning_count = sum(len(r.get('warnings', [])) for r in results.values() if isinstance(r, dict))
        
        report_lines.append(f"Total Errors: {error_count}")
        report_lines.append(f"Total Warnings: {warning_count}")
        report_lines.append(f"Recommendation: {'Ready for production' if all_valid else 'Address errors before deployment'}")
        
        return "\n".join(report_lines)
        
    def log_performance_metrics(self, operation: str, start_time: datetime, 
                               records_processed: int, additional_metrics: Dict = None):
        """Log performance metrics for monitoring"""
        duration = (datetime.now() - start_time).total_seconds()
        
        metrics = {
            'operation': operation,
            'duration_seconds': duration,
            'records_processed': records_processed,
            'records_per_second': records_processed / duration if duration > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        if additional_metrics:
            metrics.update(additional_metrics)
            
        self.logger.info(f"Performance: {operation} - {duration:.2f}s for {records_processed} records")
        
        # Save to metrics file for monitoring
        metrics_file = os.path.join(os.path.dirname(__file__), 'logs', 'performance_metrics.jsonl')
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(metrics) + '\n')
            
        return metrics


def integrate_error_handler(mapper_instance):
    """Integrate error handler with existing mapper"""
    error_handler = ProductionErrorHandler()
    
    # Monkey patch the mapper with enhanced error handling
    original_calculate = mapper_instance._calculate_metrics_for_market
    
    def enhanced_calculate(platform, market, planned_data, actuals_data, actuals_rf_data):
        try:
            # Validate inputs
            if actuals_rf_data is not None and not actuals_rf_data.empty:
                validation = error_handler.validate_rf_data_structure(
                    actuals_rf_data, 'DELIVERED R&F'
                )
                if not validation['is_valid']:
                    error_handler.logger.error(f"R&F validation failed: {validation['errors']}")
                    # Continue with empty R&F data rather than crash
                    actuals_rf_data = pd.DataFrame()
                    
            # Call original function
            result = original_calculate(platform, market, planned_data, actuals_data, actuals_rf_data)
            
            # Validate output
            for metric, values in result.items():
                if isinstance(values, dict):
                    for key, value in values.items():
                        if pd.isna(value) or value < 0:
                            error_handler.logger.warning(
                                f"Invalid value for {metric}.{key}: {value} - Setting to 0"
                            )
                            values[key] = 0
                            
            return result
            
        except Exception as e:
            error_handler.logger.error(
                f"Error calculating metrics for {platform}/{market}: {e}", 
                exc_info=True
            )
            # Return safe defaults
            return {
                'Total Reach': {'planned': 0, 'actuals': 0},
                'Total Impressions': {'planned': 0, 'actuals': 0},
                'Total Spend': {'planned': 0, 'actuals': 0},
                'Avg. Frequency': {'planned': 0, 'actuals': 0},
                'Clicks': {'planned': 0, 'actuals': 0},
                'Video Views': {'planned': 0, 'actuals': 0},
                'CTR': {'planned': 0, 'actuals': 0},
                'VTR': {'planned': 0, 'actuals': 0}
            }
    
    mapper_instance._calculate_metrics_for_market = enhanced_calculate
    mapper_instance.error_handler = error_handler
    
    return mapper_instance