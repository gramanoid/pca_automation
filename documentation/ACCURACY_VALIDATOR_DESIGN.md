# Data Accuracy Validator - Technical Design

## Executive Summary
A forensic validator that assumes every mapped value is wrong until cryptographically proven correct.

---

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Input Files    │────▶│   Validator      │────▶│  Audit Report   │
│ (PLANNED/DELIV) │     │   Core Engine    │     │  + Confidence   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │ Cell Registry │
                        │  (SHA-256)    │
                        └──────────────┘
```

## Plan of Attack

### Phase 1: Data Fingerprinting
1. **Cell Registry Construction**
   - Hash every input cell: `SHA256(sheet|row|col|value|type)`
   - Build bidirectional lookup: input_cell ↔ output_cell
   - Track transformation rules applied

2. **Type Preservation**
   - Capture native Excel types (not Python interpretations)
   - Store as: `{type: 'currency', precision: 2, raw: 1234.56}`
   - Flag any implicit conversions

### Phase 2: Mapping Verification
1. **Deterministic Path Tracing**
   ```python
   trace = {
       'output_cell': 'Sheet1!E15',
       'input_cells': ['PLANNED!C10', 'DELIVERED!D20'],
       'transformations': ['sum', 'round(2)'],
       'confidence': 0.0  # Start at zero
   }
   ```

2. **Reverse Engineering**
   - For each output value, compute expected inputs
   - Verify forward and backward calculations match

### Phase 3: Reconciliation Engine
1. **Exact Match Testing**
   ```python
   def verify_cell(output_ref, expected_sources):
       output_val = get_cell_value(output_ref)
       
       # Method 1: Direct comparison
       for source in expected_sources:
           source_val = get_cell_value(source)
           if not exact_match(output_val, source_val):
               return False, f"Type mismatch: {type(output_val)} != {type(source_val)}"
       
       # Method 2: Reverse calculation
       computed = apply_transformations(expected_sources)
       if not exact_match(output_val, computed):
           return False, f"Computation mismatch: {output_val} != {computed}"
       
       # Method 3: Bit-level comparison for floats
       if isinstance(output_val, float):
           if not compare_binary_representation(output_val, computed):
               return False, "Float precision loss detected"
       
       return True, "Verified"
   ```

2. **Multi-dimensional Validation**
   - Row totals must equal sum of cells
   - Column totals must match platform aggregates
   - Cross-sheet references must resolve

## Core Algorithm (Pseudocode)

```python
class AccuracyValidator:
    def __init__(self):
        self.cell_registry = {}
        self.audit_log = []
        self.confidence = 0.0
        
    def validate(self, input_files, output_file, mapping_rules):
        # Step 1: Fingerprint all inputs
        for file in input_files:
            self._fingerprint_cells(file)
        
        # Step 2: Parse mapping rules
        expected_mappings = self._parse_rules(mapping_rules)
        
        # Step 3: Validate each output cell
        total_cells = 0
        valid_cells = 0
        
        for sheet in output_file.sheets:
            for row in sheet.rows:
                for cell in row.cells:
                    total_cells += 1
                    result = self._validate_cell(cell, expected_mappings)
                    
                    if result.is_valid:
                        valid_cells += 1
                    else:
                        self._log_failure(cell, result)
        
        # Step 4: Cross-validation
        structural_valid = self._validate_structure(output_file)
        
        # Step 5: Compute confidence
        self.confidence = self._calculate_confidence(
            valid_cells, total_cells, structural_valid
        )
        
        return self.confidence == 1.0
    
    def _validate_cell(self, cell, mappings):
        # Get expected source
        source = mappings.get(cell.reference)
        if not source:
            return ValidationResult(False, "No mapping defined")
        
        # Verify type consistency
        if cell.type != source.expected_type:
            return ValidationResult(False, f"Type mismatch: {cell.type} != {source.expected_type}")
        
        # Verify value
        if source.is_formula:
            computed = self._evaluate_formula(source.formula, cell.sheet)
            if not self._exact_compare(cell.value, computed):
                return ValidationResult(False, f"Formula mismatch: {cell.value} != {computed}")
        else:
            source_value = self._get_source_value(source.reference)
            if not self._exact_compare(cell.value, source_value):
                return ValidationResult(False, f"Value mismatch: {cell.value} != {source_value}")
        
        return ValidationResult(True, "Valid")
    
    def _exact_compare(self, val1, val2):
        # Handle different types
        if type(val1) != type(val2):
            return False
        
        # String comparison
        if isinstance(val1, str):
            return val1 == val2
        
        # Numeric comparison with Decimal precision
        if isinstance(val1, (int, float)):
            # Convert to Decimal for exact comparison
            d1 = Decimal(str(val1))
            d2 = Decimal(str(val2))
            return d1 == d2
        
        # Date comparison
        if isinstance(val1, datetime):
            return val1 == val2
        
        return val1 == val2
```

## Test Matrix

### Minimal Reproducible Dataset

```python
test_cases = {
    "happy_path": {
        "input": {"A1": 100, "B1": 200},
        "output": {"C1": 300},  # A1 + B1
        "expected": "PASS"
    },
    
    "type_mismatch": {
        "input": {"A1": "100", "B1": 200},
        "output": {"C1": 300},
        "expected": "FAIL: Type coercion detected"
    },
    
    "precision_loss": {
        "input": {"A1": 0.1, "B1": 0.2},
        "output": {"C1": 0.30000000000000004},  # Float precision issue
        "expected": "FAIL: Precision loss"
    },
    
    "missing_data": {
        "input": {"A1": 100, "B1": None},
        "output": {"C1": 100},
        "expected": "FAIL: Null handling inconsistent"
    },
    
    "duplicate_keys": {
        "input": {"Platform": ["DV360", "DV360"], "Value": [100, 200]},
        "output": {"DV360_Total": 300},
        "expected": "PASS with warning: Duplicate key aggregation"
    },
    
    "rounding_scenarios": {
        "input": {"A1": 10.126, "B1": 20.874},
        "output": {"C1": 31.00},  # Rounded to 2 decimals
        "expected": "PASS if rounding rule documented"
    },
    
    "currency_formatting": {
        "input": {"A1": 1234.56},
        "output": {"B1": "£1,234.56"},
        "expected": "PASS if format transformation tracked"
    },
    
    "percentage_handling": {
        "input": {"A1": 0.1523},
        "output": {"B1": "15.23%"},
        "expected": "PASS if percentage rule applied"
    }
}
```

## Risk Mitigation Strategies

### 1. Preventing False Positives

**Problem**: Previous validator reported 100% when it wasn't.

**Solution**: Multi-layer verification
```python
def prevent_false_positives(self):
    # Never trust single validation
    checks = [
        self._validate_data_integrity(),
        self._validate_structural_integrity(),
        self._validate_cross_references(),
        self._validate_aggregates(),
        self._validate_formulas()
    ]
    
    # Require ALL checks to pass
    return all(checks) and len(checks) >= 5
```

### 2. Self-Audit Mechanism

```python
class ValidatorAuditor:
    def audit_validator(self, validator_instance):
        # Test with known-bad data
        bad_result = validator_instance.validate(KNOWN_BAD_DATA)
        if bad_result == True:
            raise Exception("Validator failed to catch known errors")
        
        # Test with known-good data
        good_result = validator_instance.validate(KNOWN_GOOD_DATA)
        if good_result == False:
            raise Exception("Validator produced false negative")
        
        # Inject single-bit errors
        for i in range(100):
            mutated = self._inject_bit_error(KNOWN_GOOD_DATA, i)
            if validator_instance.validate(mutated) == True:
                raise Exception(f"Failed to catch bit error at position {i}")
        
        return True
```

### 3. Confidence Scoring

```python
def calculate_confidence(self):
    # Start pessimistic
    confidence = 0.0
    
    # Data coverage (25%)
    coverage_score = self.validated_cells / self.total_cells
    confidence += coverage_score * 0.25
    
    # Type consistency (25%)
    type_score = self.correct_types / self.total_cells
    confidence += type_score * 0.25
    
    # Structural integrity (25%)
    structure_score = self.valid_aggregates / self.total_aggregates
    confidence += structure_score * 0.25
    
    # Cross-validation (25%)
    cross_score = self.valid_references / self.total_references
    confidence += cross_score * 0.25
    
    # Apply penalties
    if self.errors > 0:
        confidence *= (1 - self.errors / self.total_cells)
    
    # Never round up
    return math.floor(confidence * 10000) / 10000
```

## Implementation Checklist

- [ ] Cell-level hashing with SHA-256
- [ ] Bidirectional mapping registry
- [ ] Type preservation layer
- [ ] Decimal arithmetic for all numerics
- [ ] Formula parser and evaluator
- [ ] Cross-sheet reference resolver
- [ ] Aggregate validation (row/column totals)
- [ ] Bit-level float comparison
- [ ] Audit trail with timestamps
- [ ] Self-test suite with mutation testing
- [ ] Performance profiling (<30s requirement)
- [ ] Memory-mapped Excel reading for large files

## Dependencies

```python
# requirements.txt
openpyxl==3.1.2       # Excel handling
python-decimal==1.70   # Exact numeric operations
xxhash==3.4.1         # Fast hashing
pytest==8.1.1         # Testing framework
hypothesis==6.99.0    # Property-based testing
memory-profiler==0.61 # Performance monitoring
```

## Performance Optimizations

1. **Lazy Loading**: Only load cells being validated
2. **Parallel Validation**: Use multiprocessing for independent sheets
3. **Caching**: Cache computed formulas and lookups
4. **Early Exit**: Stop on first critical error if requested

## Failure Modes to Test

1. Excel stores 0.1 + 0.2 differently than Python
2. Currency symbols affect numeric comparison
3. Hidden columns/rows in Excel
4. Merged cells spanning multiple references
5. Circular references in formulas
6. External workbook references
7. Named ranges vs cell references
8. Array formulas
9. Conditional formatting affecting values
10. Regional settings (comma vs dot decimals)

---

## Next Steps

1. Build proof-of-concept with test matrix
2. Stress test with production data
3. Add mutation testing to verify validator catches errors
4. Performance profile with 50k-row dataset
5. Create CI/CD pipeline for validator regression tests