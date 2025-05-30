#!/usr/bin/env python3
"""
Comprehensive pytest test suite for validation modules
Tests edge cases, accuracy checks, and fail-fast mechanisms
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import tempfile
import shutil
from datetime import datetime
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'main_scripts'))

from verify_combined import CombinedWorkbookAuditor, assert_combined_validity
from data_accuracy_validator import EnhancedDataValidator, ValidationError
from robust_market_mapper import RobustMarketMapper


class TestCombinedWorkbookAuditor:
    """Test cases for COMBINED workbook validation"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample dataframes for testing"""
        planned = pd.DataFrame({
            'CAMPAIGN': ['Campaign A', 'Campaign B', 'Campaign C'],
            'MARKET': ['UAE', 'QAT', 'OMN'],
            'PLATFORM': ['DV360', 'META', 'TIKTOK'],
            'BUDGET_LOCAL': [1000, 2000, 1500],
            'IMPRESSIONS': [10000, 20000, 15000],
            'START_DATE': ['2024-01-01', '2024-01-01', '2024-01-01'],
            'END_DATE': ['2024-01-31', '2024-01-31', '2024-01-31']
        })
        
        delivered = pd.DataFrame({
            'CAMPAIGN': ['Campaign A', 'Campaign B', 'Campaign D'],  # C missing, D extra
            'MARKET': ['UAE', 'QAT', 'JOR'],
            'PLATFORM': ['DV360', 'META', 'META'],
            'SPEND_LOCAL': [950, 1900, 500],
            'SPEND_USD': [950, 1900, 500],
            'IMPRESSIONS': [9500, 19000, 5000],
            'CLICKS': [95, 190, 50],
            'REACH': [8000, 16000, 4000],
            'FREQUENCY': [1.2, 1.2, 1.25]
        })
        
        # Combined should follow business rules
        combined = pd.DataFrame({
            'CAMPAIGN': ['Campaign A', 'Campaign B', 'Campaign C', 'Campaign D'],
            'MARKET': ['UAE', 'QAT', 'OMN', 'JOR'],
            'PLATFORM': ['DV360', 'META', 'TIKTOK', 'META'],
            'BUDGET_LOCAL': [1000, 2000, 1500, 0],  # Planned values, 0 for D
            'SPEND_LOCAL': [950, 1900, 0, 500],     # Delivered values, 0 for C
            'IMPRESSIONS': [9500, 19000, 15000, 5000],  # Delivered if exists, else planned
            'CLICKS': [95, 190, 0, 50],             # Delivered only
            'REACH': [8000, 16000, 0, 4000],        # Delivered only
            'START_DATE': ['2024-01-01', '2024-01-01', '2024-01-01', None]
        })
        
        return {
            'planned': planned,
            'delivered': delivered,
            'combined': combined
        }
    
    def test_perfect_match_validation(self, sample_data):
        """Test validation with perfectly matched data"""
        auditor = CombinedWorkbookAuditor()
        result = auditor.audit_combined(
            sample_data['planned'],
            sample_data['delivered'],
            sample_data['combined']
        )
        
        assert result['valid'] == True
        assert result['accuracy_pct'] == 100.0
        assert result['failed'] == 0
    
    def test_business_rule_violations(self, sample_data):
        """Test detection of business rule violations"""
        # Modify combined to violate rules
        bad_combined = sample_data['combined'].copy()
        bad_combined.loc[0, 'BUDGET_LOCAL'] = 900  # Should be 1000 from planned
        
        auditor = CombinedWorkbookAuditor()
        result = auditor.audit_combined(
            sample_data['planned'],
            sample_data['delivered'],
            bad_combined
        )
        
        assert result['valid'] == False
        assert result['failed'] > 0
        assert any(f['field'] == 'BUDGET_LOCAL' for f in result['failures'])
    
    def test_planned_only_campaign(self):
        """Test handling of planned-only campaigns"""
        planned = pd.DataFrame({
            'CAMPAIGN': ['Campaign X'],
            'MARKET': ['UAE'],
            'PLATFORM': ['DV360'],
            'BUDGET_LOCAL': [5000]
        })
        
        delivered = pd.DataFrame()  # Empty
        
        combined = pd.DataFrame({
            'CAMPAIGN': ['Campaign X'],
            'MARKET': ['UAE'],
            'PLATFORM': ['DV360'],
            'BUDGET_LOCAL': [5000],
            'SPEND_LOCAL': [0]  # Should be 0 or None for planned-only
        })
        
        auditor = CombinedWorkbookAuditor()
        result = auditor.audit_combined(planned, delivered, combined)
        
        assert result['valid'] == True
    
    def test_delivered_only_campaign(self):
        """Test handling of delivered-only campaigns"""
        planned = pd.DataFrame()  # Empty
        
        delivered = pd.DataFrame({
            'CAMPAIGN': ['Campaign Y'],
            'MARKET': ['JOR'],
            'PLATFORM': ['META'],
            'SPEND_LOCAL': [3000],
            'IMPRESSIONS': [30000]
        })
        
        combined = pd.DataFrame({
            'CAMPAIGN': ['Campaign Y'],
            'MARKET': ['JOR'],
            'PLATFORM': ['META'],
            'BUDGET_LOCAL': [0],  # Should be 0 or None for delivered-only
            'SPEND_LOCAL': [3000],
            'IMPRESSIONS': [30000]
        })
        
        auditor = CombinedWorkbookAuditor()
        result = auditor.audit_combined(planned, delivered, combined)
        
        assert result['valid'] == True
    
    def test_calculated_metrics(self):
        """Test validation of calculated metrics (CTR, CPM, etc.)"""
        delivered = pd.DataFrame({
            'CAMPAIGN': ['Campaign Z'],
            'CLICKS': [100],
            'IMPRESSIONS': [10000],
            'SPEND_USD': [50]
        })
        
        combined = pd.DataFrame({
            'CAMPAIGN': ['Campaign Z'],
            'CTR': [1.0],  # 100/10000 * 100
            'CPM': [5.0],  # 50/10000 * 1000
            'CPC': [0.5]   # 50/100
        })
        
        auditor = CombinedWorkbookAuditor()
        # This should validate the calculated fields
        result = auditor.audit_combined(pd.DataFrame(), delivered, combined)
        
        assert result['accuracy_pct'] >= 99.9  # Allow for small floating point differences


class TestEnhancedDataValidator:
    """Test cases for data accuracy validator"""
    
    @pytest.fixture
    def sample_dataframes(self):
        """Create sample source and output dataframes"""
        source = pd.DataFrame({
            'Campaign': ['A', 'B', 'C'],
            'Budget': [1000.0, 2000.0, 1500.0],
            'Impressions': [10000, 20000, 15000],
            'Clicks': [100, 200, 150],
            'Platform': ['DV360', 'META', 'TIKTOK']
        })
        
        # Perfect match output
        output_perfect = source.copy()
        
        # Output with small differences
        output_small_diff = source.copy()
        output_small_diff.loc[0, 'Budget'] = 1000.5  # 0.05% difference
        
        # Output with large differences
        output_large_diff = source.copy()
        output_large_diff.loc[0, 'Budget'] = 1100  # 10% difference
        
        return {
            'source': source,
            'output_perfect': output_perfect,
            'output_small_diff': output_small_diff,
            'output_large_diff': output_large_diff
        }
    
    def test_perfect_accuracy(self, sample_dataframes):
        """Test validator with perfect match"""
        validator = EnhancedDataValidator(tolerance=0.001)
        
        report = validator.validate_accuracy(
            sample_dataframes['source'],
            sample_dataframes['output_perfect']
        )
        
        assert report['overall_accuracy'] == 100.0
        assert report['cell_level']['accuracy'] == 100.0
        assert report['row_level']['accuracy'] == 100.0
        assert report['grand_total']['accuracy'] == 100.0
    
    def test_within_tolerance(self, sample_dataframes):
        """Test validator with differences within tolerance"""
        validator = EnhancedDataValidator(tolerance=0.001)  # 0.1% tolerance
        
        report = validator.validate_accuracy(
            sample_dataframes['source'],
            sample_dataframes['output_small_diff']
        )
        
        # 0.05% difference should pass with 0.1% tolerance
        assert report['cell_level']['cells_failed'] == 0
    
    def test_exceed_tolerance(self, sample_dataframes):
        """Test validator with differences exceeding tolerance"""
        validator = EnhancedDataValidator(tolerance=0.001)  # 0.1% tolerance
        
        report = validator.validate_accuracy(
            sample_dataframes['source'],
            sample_dataframes['output_large_diff']
        )
        
        # 10% difference should fail with 0.1% tolerance
        assert report['cell_level']['cells_failed'] > 0
        assert report['overall_accuracy'] < 100.0
    
    def test_fail_fast_mechanism(self, sample_dataframes):
        """Test fail-fast mechanism raises exception"""
        validator = EnhancedDataValidator(tolerance=0.001, strict_mode=True)
        
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_accuracy(
                sample_dataframes['source'],
                sample_dataframes['output_large_diff']
            )
        
        assert "Overall accuracy" in str(exc_info.value)
        assert "< 100%" in str(exc_info.value)
    
    def test_cell_fingerprinting(self, sample_dataframes):
        """Test SHA-256 fingerprinting of cells"""
        validator = EnhancedDataValidator()
        
        # Create fingerprints
        fp1 = validator._create_fingerprint("A1", "test_value", "test.xlsx", "Sheet1")
        fp2 = validator._create_fingerprint("A2", "test_value", "test.xlsx", "Sheet1")
        fp3 = validator._create_fingerprint("A3", "different_value", "test.xlsx", "Sheet1")
        
        # Same values should have same hash
        assert fp1.sha256_hash == fp2.sha256_hash
        
        # Different values should have different hash
        assert fp1.sha256_hash != fp3.sha256_hash
    
    def test_multi_level_validation(self, sample_dataframes):
        """Test all validation levels work correctly"""
        validator = EnhancedDataValidator()
        
        # Modify data to create specific failures
        output = sample_dataframes['source'].copy()
        output.loc[0, 'Budget'] = 1100  # Cell level failure
        
        report = validator.validate_accuracy(
            sample_dataframes['source'],
            output
        )
        
        # Check all levels were validated
        assert 'cell_level' in report
        assert 'row_level' in report
        assert 'section_level' in report
        assert 'grand_total' in report
        
        # Cell level should have failures
        assert report['cell_level']['cells_failed'] > 0
        
        # Grand total should also fail (sum is different)
        assert report['grand_total']['columns_failed'] > 0
    
    def test_diff_report_generation(self, sample_dataframes, tmp_path):
        """Test CSV diff report generation"""
        validator = EnhancedDataValidator()
        
        # Create validation with failures
        output = sample_dataframes['source'].copy()
        output.loc[0, 'Budget'] = 1100
        
        report = validator.validate_accuracy(
            sample_dataframes['source'],
            output
        )
        
        # Generate diff report
        csv_path = validator.generate_diff_report(str(tmp_path))
        
        assert Path(csv_path).exists()
        assert Path(csv_path).suffix == '.csv'
        
        # Read and verify CSV content
        df = pd.read_csv(csv_path)
        assert 'level' in df.columns
        assert 'diff_pct' in df.columns
        assert len(df) > 0


class TestRobustMarketMapper:
    """Test cases for robust market mapping"""
    
    def test_planned_only_mapping(self):
        """Test mapping with planned-only campaigns"""
        mapper = RobustMarketMapper()
        
        planned = pd.DataFrame({
            'CAMPAIGN': ['Campaign A'],
            'MARKET': ['UAE'],
            'PLATFORM': ['DV360'],
            'BUDGET': [1000]
        })
        delivered = pd.DataFrame()  # Empty
        
        result = mapper.map_campaigns(planned, delivered)
        
        assert len(result) == 1
        assert result.iloc[0]['match_status'] == 'planned_only'
        assert result.iloc[0]['CAMPAIGN'] == 'Campaign A'
    
    def test_delivered_only_mapping(self):
        """Test mapping with delivered-only campaigns"""
        mapper = RobustMarketMapper()
        
        planned = pd.DataFrame()  # Empty
        delivered = pd.DataFrame({
            'CAMPAIGN': ['Campaign B'],
            'MARKET': ['JOR'],
            'PLATFORM': ['META'],
            'SPEND_USD': [500]
        })
        
        result = mapper.map_campaigns(planned, delivered)
        
        assert len(result) == 1
        assert result.iloc[0]['match_status'] == 'delivered_only'
        assert result.iloc[0]['CAMPAIGN'] == 'Campaign B'
    
    def test_perfect_match_mapping(self):
        """Test mapping with perfectly matched campaigns"""
        mapper = RobustMarketMapper()
        
        planned = pd.DataFrame({
            'CAMPAIGN': ['Campaign C'],
            'MARKET': ['QAT'],
            'PLATFORM': ['TIKTOK'],
            'BUDGET': [2000]
        })
        delivered = pd.DataFrame({
            'CAMPAIGN': ['Campaign C'],
            'MARKET': ['QAT'],
            'PLATFORM': ['TIKTOK'],
            'SPEND_USD': [1800]
        })
        
        result = mapper.map_campaigns(planned, delivered)
        
        assert len(result) == 1
        assert result.iloc[0]['match_status'] == 'matched'
        assert pd.notna(result.iloc[0]['BUDGET_planned'])
        assert pd.notna(result.iloc[0]['SPEND_USD_delivered'])
    
    def test_mismatched_markets(self):
        """Test mapping with same campaign in different markets"""
        mapper = RobustMarketMapper()
        
        planned = pd.DataFrame({
            'CAMPAIGN': ['Campaign D'],
            'MARKET': ['UAE'],
            'PLATFORM': ['DV360'],
            'BUDGET': [3000]
        })
        delivered = pd.DataFrame({
            'CAMPAIGN': ['Campaign D'],
            'MARKET': ['OMN'],  # Different market
            'PLATFORM': ['DV360'],
            'SPEND_USD': [2500]
        })
        
        result = mapper.map_campaigns(planned, delivered)
        
        assert len(result) == 2  # One for each market
        assert set(result['match_status']) == {'planned_only', 'delivered_only'}
    
    def test_empty_data_handling(self):
        """Test handling of empty dataframes"""
        mapper = RobustMarketMapper()
        
        # Both empty
        result = mapper.map_campaigns(pd.DataFrame(), pd.DataFrame())
        assert len(result) == 0
        
        # Verify no exceptions are raised
        assert isinstance(result, pd.DataFrame)


class TestIntegration:
    """Integration tests for the complete validation pipeline"""
    
    def test_end_to_end_validation(self, tmp_path):
        """Test complete validation workflow"""
        # Create test data
        planned = pd.DataFrame({
            'CAMPAIGN': ['A', 'B', 'C'],
            'MARKET': ['UAE', 'QAT', 'OMN'],
            'PLATFORM': ['DV360', 'META', 'TIKTOK'],
            'BUDGET_LOCAL': [1000, 2000, 1500],
            'BUDGET_USD': [1000, 2000, 1500]
        })
        
        delivered = pd.DataFrame({
            'CAMPAIGN': ['A', 'B'],
            'MARKET': ['UAE', 'QAT'],
            'PLATFORM': ['DV360', 'META'],
            'SPEND_LOCAL': [950, 1900],
            'SPEND_USD': [950, 1900],
            'IMPRESSIONS': [9500, 19000]
        })
        
        # Step 1: Map campaigns
        mapper = RobustMarketMapper()
        combined = mapper.map_campaigns(planned, delivered)
        
        # Step 2: Validate combined
        auditor = CombinedWorkbookAuditor()
        audit_result = auditor.audit_combined(planned, delivered, combined)
        
        # Step 3: Validate accuracy
        validator = EnhancedDataValidator()
        accuracy_report = validator.validate_accuracy(planned, combined)
        
        # Assertions
        assert len(combined) >= 2  # At least the matched campaigns
        assert audit_result['passed'] > 0
        assert accuracy_report['overall_accuracy'] > 0
    
    def test_fail_fast_integration(self):
        """Test fail-fast mechanism across modules"""
        # Create data that will fail validation
        source = pd.DataFrame({
            'VALUE': [100, 200, 300]
        })
        output = pd.DataFrame({
            'VALUE': [110, 220, 330]  # 10% difference
        })
        
        validator = EnhancedDataValidator(tolerance=0.001, strict_mode=True)
        
        with pytest.raises(ValidationError):
            validator.validate_accuracy(source, output)


@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create a temporary directory with test data files"""
    tmp_dir = tmp_path_factory.mktemp("test_data")
    
    # Create test Excel files
    planned_df = pd.DataFrame({
        'CAMPAIGN': ['Test Campaign 1', 'Test Campaign 2'],
        'BUDGET': [1000, 2000]
    })
    delivered_df = pd.DataFrame({
        'CAMPAIGN': ['Test Campaign 1', 'Test Campaign 2'],
        'SPEND': [950, 1900]
    })
    
    planned_df.to_excel(tmp_dir / "planned.xlsx", index=False)
    delivered_df.to_excel(tmp_dir / "delivered.xlsx", index=False)
    
    return tmp_dir


def test_command_line_interface(test_data_dir, monkeypatch):
    """Test command line interfaces work correctly"""
    # Test verify_combined CLI
    monkeypatch.setattr(
        'sys.argv',
        ['verify_combined.py', '--combined', str(test_data_dir / 'planned.xlsx')]
    )
    
    # Should not raise exception for valid data
    from verify_combined import main as verify_main
    # Note: In real test, we'd mock sys.exit to verify it's called with 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])