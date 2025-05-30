#!/usr/bin/env python3
"""
Edge case tests for validation modules
Tests unusual scenarios, boundary conditions, and error handling
"""

import pytest
import pandas as pd
import numpy as np
from decimal import Decimal
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'main_scripts'))

from verify_combined import CombinedWorkbookAuditor
from data_accuracy_validator import EnhancedDataValidator, ValidationError
from robust_market_mapper import RobustMarketMapper


class TestNumericEdgeCases:
    """Test edge cases for numeric validation"""
    
    def test_zero_values(self):
        """Test handling of zero values"""
        validator = EnhancedDataValidator(tolerance=0.001)
        
        source = pd.DataFrame({'value': [0.0, 0, 0.00]})
        output = pd.DataFrame({'value': [0.0, 0, 0.00]})
        
        report = validator.validate_accuracy(source, output)
        assert report['overall_accuracy'] == 100.0
    
    def test_very_small_numbers(self):
        """Test handling of very small numbers"""
        validator = EnhancedDataValidator(tolerance=0.001)
        
        source = pd.DataFrame({'value': [0.0001, 0.00001, 0.000001]})
        output = pd.DataFrame({'value': [0.0001, 0.00001, 0.000001]})
        
        report = validator.validate_accuracy(source, output)
        assert report['overall_accuracy'] == 100.0
    
    def test_very_large_numbers(self):
        """Test handling of very large numbers"""
        validator = EnhancedDataValidator(tolerance=0.001)
        
        source = pd.DataFrame({'value': [1e10, 1e15, 1e20]})
        output = pd.DataFrame({'value': [1e10, 1e15, 1e20]})
        
        report = validator.validate_accuracy(source, output)
        assert report['overall_accuracy'] == 100.0
    
    def test_floating_point_precision(self):
        """Test handling of floating point precision issues"""
        validator = EnhancedDataValidator(tolerance=0.001)
        
        # Classic floating point issue
        source = pd.DataFrame({'value': [0.1 + 0.2]})
        output = pd.DataFrame({'value': [0.3]})
        
        report = validator.validate_accuracy(source, output)
        # Should pass despite floating point representation differences
        assert report['cell_level']['cells_failed'] == 0
    
    def test_mixed_numeric_types(self):
        """Test handling of mixed int/float types"""
        validator = EnhancedDataValidator(tolerance=0.001)
        
        source = pd.DataFrame({'value': [1, 2.0, 3]})  # Mixed int/float
        output = pd.DataFrame({'value': [1.0, 2, 3.0]})  # Different types
        
        report = validator.validate_accuracy(source, output)
        assert report['overall_accuracy'] == 100.0
    
    def test_infinity_and_nan(self):
        """Test handling of infinity and NaN values"""
        validator = EnhancedDataValidator()
        
        source = pd.DataFrame({
            'value': [np.inf, -np.inf, np.nan, 1.0]
        })
        output = pd.DataFrame({
            'value': [np.inf, -np.inf, np.nan, 1.0]
        })
        
        report = validator.validate_accuracy(source, output)
        # NaN == NaN should be considered a match in this context
        assert report['cell_level']['cells_failed'] == 0


class TestStringEdgeCases:
    """Test edge cases for string validation"""
    
    def test_empty_strings(self):
        """Test handling of empty strings"""
        auditor = CombinedWorkbookAuditor()
        
        planned = pd.DataFrame({
            'CAMPAIGN': ['', 'Campaign A', '   '],  # Empty and whitespace
            'MARKET': ['UAE', '', 'QAT']
        })
        delivered = pd.DataFrame({
            'CAMPAIGN': ['', 'Campaign A', '   '],
            'MARKET': ['UAE', '', 'QAT']
        })
        combined = planned.copy()
        
        result = auditor.audit_combined(planned, delivered, combined)
        assert result['valid'] == True
    
    def test_unicode_characters(self):
        """Test handling of unicode characters"""
        mapper = RobustMarketMapper()
        
        planned = pd.DataFrame({
            'CAMPAIGN': ['Campaign 中文', 'Campaña Ñ', 'مملكة'],
            'MARKET': ['UAE', 'QAT', 'OMN'],
            'PLATFORM': ['DV360', 'META', 'TIKTOK']
        })
        delivered = planned.copy()
        
        result = mapper.map_campaigns(planned, delivered)
        assert len(result) == 3
        assert all(result['match_status'] == 'matched')
    
    def test_special_characters(self):
        """Test handling of special characters in strings"""
        validator = EnhancedDataValidator()
        
        source = pd.DataFrame({
            'campaign': ['Test & Co.', 'Campaign (2024)', '#1 Best!']
        })
        output = source.copy()
        
        report = validator.validate_accuracy(source, output)
        assert report['overall_accuracy'] == 100.0
    
    def test_case_sensitivity(self):
        """Test case sensitivity in string matching"""
        auditor = CombinedWorkbookAuditor()
        
        # Exact case match required
        planned = pd.DataFrame({'CAMPAIGN': ['Campaign ABC']})
        delivered = pd.DataFrame({'CAMPAIGN': ['Campaign ABC']})
        combined = pd.DataFrame({'CAMPAIGN': ['Campaign abc']})  # Different case
        
        result = auditor.audit_combined(planned, delivered, combined)
        # Should fail due to case mismatch
        assert result['valid'] == False


class TestDataTypeEdgeCases:
    """Test edge cases for different data types"""
    
    def test_date_handling(self):
        """Test handling of date values"""
        auditor = CombinedWorkbookAuditor()
        
        planned = pd.DataFrame({
            'START_DATE': pd.to_datetime(['2024-01-01', '2024-02-01']),
            'END_DATE': pd.to_datetime(['2024-01-31', '2024-02-29'])
        })
        delivered = pd.DataFrame()
        combined = planned.copy()
        
        result = auditor.audit_combined(planned, delivered, combined)
        assert result['valid'] == True
    
    def test_boolean_values(self):
        """Test handling of boolean values"""
        validator = EnhancedDataValidator()
        
        source = pd.DataFrame({
            'is_active': [True, False, True],
            'has_data': [False, True, False]
        })
        output = source.copy()
        
        report = validator.validate_accuracy(source, output)
        assert report['overall_accuracy'] == 100.0
    
    def test_mixed_data_types(self):
        """Test handling of mixed data types in same column"""
        mapper = RobustMarketMapper()
        
        # This is generally bad practice but should not crash
        planned = pd.DataFrame({
            'CAMPAIGN': ['Campaign 1', 'Campaign 2'],
            'MIXED': [123, 'ABC']  # Mixed types
        })
        delivered = pd.DataFrame({
            'CAMPAIGN': ['Campaign 1'],
            'MIXED': ['123']  # String representation of number
        })
        
        # Should handle without crashing
        result = mapper.map_campaigns(planned, delivered)
        assert len(result) >= 1


class TestMissingDataEdgeCases:
    """Test edge cases for missing data"""
    
    def test_all_nan_column(self):
        """Test handling of columns with all NaN values"""
        validator = EnhancedDataValidator()
        
        source = pd.DataFrame({
            'value': [1, 2, 3],
            'all_nan': [np.nan, np.nan, np.nan]
        })
        output = source.copy()
        
        report = validator.validate_accuracy(source, output)
        assert report['overall_accuracy'] == 100.0
    
    def test_sparse_data(self):
        """Test handling of sparse data (mostly NaN)"""
        auditor = CombinedWorkbookAuditor()
        
        planned = pd.DataFrame({
            'CAMPAIGN': ['A', 'B', 'C'],
            'BUDGET': [1000, np.nan, np.nan],
            'MARKET': ['UAE', np.nan, 'QAT']
        })
        delivered = pd.DataFrame({
            'CAMPAIGN': ['A', 'B'],
            'SPEND': [950, np.nan]
        })
        combined = pd.DataFrame({
            'CAMPAIGN': ['A', 'B', 'C'],
            'BUDGET': [1000, np.nan, np.nan],
            'SPEND': [950, np.nan, np.nan]
        })
        
        result = auditor.audit_combined(planned, delivered, combined)
        # Should handle NaN values appropriately
        assert isinstance(result['accuracy_pct'], float)
    
    def test_empty_dataframes(self):
        """Test handling of empty dataframes"""
        mapper = RobustMarketMapper()
        
        # Empty with columns
        planned = pd.DataFrame(columns=['CAMPAIGN', 'MARKET', 'BUDGET'])
        delivered = pd.DataFrame(columns=['CAMPAIGN', 'MARKET', 'SPEND'])
        
        result = mapper.map_campaigns(planned, delivered)
        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)


class TestPerformanceEdgeCases:
    """Test edge cases for performance and scalability"""
    
    def test_large_dataset(self):
        """Test handling of large datasets"""
        validator = EnhancedDataValidator()
        
        # Create large dataset
        n_rows = 10000
        source = pd.DataFrame({
            'id': range(n_rows),
            'value1': np.random.rand(n_rows),
            'value2': np.random.rand(n_rows),
            'category': np.random.choice(['A', 'B', 'C'], n_rows)
        })
        output = source.copy()
        
        # Should complete without memory issues
        report = validator.validate_accuracy(source, output)
        assert report['overall_accuracy'] == 100.0
    
    def test_many_columns(self):
        """Test handling of wide datasets (many columns)"""
        validator = EnhancedDataValidator()
        
        # Create wide dataset
        n_cols = 100
        data = {f'col_{i}': [1, 2, 3] for i in range(n_cols)}
        source = pd.DataFrame(data)
        output = source.copy()
        
        report = validator.validate_accuracy(source, output)
        assert report['overall_accuracy'] == 100.0


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_mismatched_column_count(self):
        """Test handling of different column counts"""
        validator = EnhancedDataValidator()
        
        source = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        output = pd.DataFrame({'A': [1, 2]})  # Missing column B
        
        # Should handle gracefully
        report = validator.validate_accuracy(source, output)
        assert 'cell_level' in report
    
    def test_mismatched_row_count(self):
        """Test handling of different row counts"""
        validator = EnhancedDataValidator()
        
        source = pd.DataFrame({'value': [1, 2, 3]})
        output = pd.DataFrame({'value': [1, 2]})  # Missing row
        
        report = validator.validate_accuracy(source, output)
        # Should validate only the overlapping rows
        assert report['row_level']['total_rows'] == 2
    
    def test_corrupt_data_handling(self):
        """Test handling of corrupt or unusual data"""
        mapper = RobustMarketMapper()
        
        # Create data with potential issues
        planned = pd.DataFrame({
            'CAMPAIGN': [None, '', 'Valid Campaign'],
            'MARKET': ['UAE', None, 'QAT'],
            'BUDGET': ['not_a_number', 1000, 2000]
        })
        delivered = pd.DataFrame({
            'CAMPAIGN': ['', 'Valid Campaign', None],
            'MARKET': ['UAE', 'QAT', 'OMN'],
            'SPEND': [500, 1800, 'invalid']
        })
        
        # Should handle without crashing
        result = mapper.map_campaigns(planned, delivered)
        assert isinstance(result, pd.DataFrame)


class TestConfigurationEdgeCases:
    """Test edge cases for configuration and settings"""
    
    def test_extreme_tolerance_values(self):
        """Test extreme tolerance values"""
        # Zero tolerance
        validator_zero = EnhancedDataValidator(tolerance=0.0)
        source = pd.DataFrame({'value': [1.0]})
        output = pd.DataFrame({'value': [1.0000001]})
        
        report = validator_zero.validate_accuracy(source, output)
        assert report['cell_level']['cells_failed'] > 0
        
        # Very high tolerance
        validator_high = EnhancedDataValidator(tolerance=0.5)  # 50%
        source = pd.DataFrame({'value': [100]})
        output = pd.DataFrame({'value': [140]})  # 40% difference
        
        report = validator_high.validate_accuracy(source, output)
        assert report['cell_level']['cells_failed'] == 0
    
    def test_custom_business_rules(self):
        """Test custom business rules configuration"""
        # Create auditor with custom rules
        auditor = CombinedWorkbookAuditor()
        auditor.business_rules['CUSTOM_FIELD'] = 'use_planned'
        
        planned = pd.DataFrame({'CUSTOM_FIELD': ['Custom Value']})
        delivered = pd.DataFrame({'CUSTOM_FIELD': ['Different Value']})
        combined = pd.DataFrame({'CUSTOM_FIELD': ['Custom Value']})
        
        result = auditor.audit_combined(planned, delivered, combined)
        assert result['valid'] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])