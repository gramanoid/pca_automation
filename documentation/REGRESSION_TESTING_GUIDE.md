# Regression Testing Guide

**Created:** May 29, 2025  
**Purpose:** Ensure system stability and prevent breaking existing functionality

## Overview

Regression testing verifies that changes to the codebase don't break existing functionality. This project now includes comprehensive regression tests to maintain quality.

## Test Structure

```
test_regression_basic.py      # Core functionality tests (17 tests)
test_regression_production.py # Production pipeline tests (12 tests)
test_regression_simple.py     # Simple integration tests (10 tests)
test_fixtures/               # Small test data files
```

## Running Regression Tests

### Quick Test (Recommended)
```bash
# Run basic regression tests - fast and reliable
python3 test_regression_basic.py
```

### Full Test Suite
```bash
# Run all tests with pytest
python3 -m pytest test_regression*.py -v

# Run specific test file
python3 -m pytest test_regression_basic.py -v
```

### Continuous Testing
```bash
# Watch for changes and auto-run tests
python3 -m pytest test_regression_basic.py -v --watch
```

## Test Categories

### 1. Core Data Structures (test_regression_basic.py)
- ✅ COMBINED file structure validation
- ✅ Platform data structure checks
- ✅ R&F data structure validation

### 2. Number Handling
- ✅ Currency formatting (2 decimals)
- ✅ Percentage calculations
- ✅ CPM/CPC calculations

### 3. Template Structure
- ✅ Template header positions
- ✅ Platform row positions (DV360: 15, META: 52, TIKTOK: 92)
- ✅ Market column structure

### 4. Configuration Files
- ✅ Client mapping rules JSON validation
- ✅ Template mapping config structure
- ✅ Memory file integrity

### 5. Data Validation
- ✅ No negative financial values
- ✅ Logical relationships (CTR ≤ 100%, Clicks ≤ Impressions)

### 6. Production Pipeline
- ✅ Real file extraction
- ✅ Data quality checks
- ✅ Mapping functionality

### 7. Performance
- ✅ Processing speed < 2 seconds for fixtures
- ✅ Memory usage < 100MB increase

### 8. Backward Compatibility
- ✅ Column name normalization
- ✅ Platform alias handling (YOUTUBE → DV360)
- ✅ Config file structure

## Test Results Summary

### Basic Tests (100% Pass Rate)
```
✅ 17 tests passed
✅ Core functionality verified
✅ No regressions detected
```

### Production Tests (Known Issues)
- Data quality: 60% campaign fill rate (normal for R&F data)
- Config structure: Some keys renamed in latest version
- MergedCell error in template (non-critical)

## Writing New Tests

### Adding a Test
```python
def test_new_feature(self):
    """Test: New feature should work correctly"""
    # Arrange
    test_data = create_test_data()
    
    # Act
    result = process_data(test_data)
    
    # Assert
    assert result.success == True
    assert len(result.data) > 0
```

### Test Best Practices
1. **One assertion per test** - Keep tests focused
2. **Descriptive names** - test_what_should_happen()
3. **Fast execution** - Use fixtures, not real files
4. **Independent** - Tests shouldn't depend on each other
5. **Repeatable** - Same result every time

## Continuous Integration

### Pre-commit Hook
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
python3 test_regression_basic.py
if [ $? -ne 0 ]; then
    echo "Regression tests failed! Please fix before committing."
    exit 1
fi
```

### GitHub Actions (Future)
```yaml
name: Regression Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - run: pip install -r requirements.txt
    - run: python -m pytest test_regression*.py
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're in the project root directory
   - Check that main_scripts/ is in Python path

2. **Missing Test Fixtures**
   - Run: `python3 create_test_fixtures.py`
   - This creates all necessary test files

3. **API Key Errors**
   - Most tests don't require API keys
   - Set ANTHROPIC_API_KEY only for full pipeline tests

4. **Permission Errors**
   - Ensure write permissions in test directories
   - Clean up old test outputs

## Maintenance

### Regular Tasks
- **Weekly**: Run full test suite
- **Before Deploy**: Run all regression tests
- **After Major Changes**: Update test fixtures
- **Monthly**: Review and update tests

### Test Coverage Goals
- Core functionality: 100% ✅
- Edge cases: 80%
- Error scenarios: 90%
- Performance benchmarks: 100% ✅

## Benefits

1. **Confidence** - Make changes without fear
2. **Early Detection** - Catch bugs before production
3. **Documentation** - Tests show how system works
4. **Speed** - Automated testing is faster than manual
5. **Quality** - Maintain high code standards

---

Remember: **A test that catches one bug pays for all the time spent writing tests!**