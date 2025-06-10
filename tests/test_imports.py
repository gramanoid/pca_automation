#!/usr/bin/env python3
"""Test script to verify imports work correctly."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import modules directly to avoid numeric path issues
import production_workflow
sys.path.append(str(Path(__file__).parent.parent / 'production_workflow' / '04_validation'))
sys.path.append(str(Path(__file__).parent.parent / 'production_workflow' / '02_data_processing'))

try:
    from validate_accuracy import EnhancedDataValidator, ValidationError
    print("✓ Successfully imported EnhancedDataValidator and ValidationError")
except ImportError as e:
    print(f"✗ Failed to import from validate_accuracy: {e}")

try:
    from market_mapper import RobustMarketMapper
    print("✓ Successfully imported RobustMarketMapper")
except ImportError as e:
    print(f"✗ Failed to import from market_mapper: {e}")

# Test instantiation
try:
    validator = EnhancedDataValidator()
    print("✓ Successfully created EnhancedDataValidator instance")
except Exception as e:
    print(f"✗ Failed to create EnhancedDataValidator: {e}")

try:
    mapper = RobustMarketMapper()
    print("✓ Successfully created RobustMarketMapper instance")
except Exception as e:
    print(f"✗ Failed to create RobustMarketMapper: {e}")

print("\nImport test complete!")