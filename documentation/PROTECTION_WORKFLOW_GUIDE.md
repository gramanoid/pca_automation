# Excel Protection in the Workflow

## Overview

The Excel protection is applied to the **empty template** BEFORE the automation workflow begins. This ensures template integrity throughout the entire process.

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ INITIAL SETUP (One-time)                                        │
├─────────────────────────────────────────────────────────────────┤
│ 1. Original Template (OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx)     │
│    ↓                                                            │
│ 2. Apply Protection Script                                      │
│    ↓                                                            │
│ 3. Protected Template (OUTPUT_TEMPLATE_FILE_EMPTY_FILE_         │
│    PROTECTED_FOR_SCRIPT.xlsx)                                   │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│ REGULAR WORKFLOW (Every time)                                   │
├─────────────────────────────────────────────────────────────────┤
│ 1. Input Files:                                                 │
│    - PLANNED Excel files                                        │
│    - DELIVERED Excel files                                      │
│    - Protected Template ←── USES PROTECTED VERSION             │
│                                                                 │
│ 2. Excel Data Extractor                                         │
│    ↓                                                            │
│ 3. COMBINED.xlsx (intermediate file)                           │
│    ↓                                                            │
│ 4. Simple LLM Mapper                                            │
│    - Reads Protected Template                                   │
│    - Writes data programmatically (bypasses protection)        │
│    ↓                                                            │
│ 5. Final Output (final_mapped.xlsx)                             │
│    - Contains all mapped data                                   │
│    - NOT protected (ready for use)                              │
└─────────────────────────────────────────────────────────────────┘
```

## Step-by-Step Process

### 1. Initial Setup (Do Once)

```bash
# Protect the empty template
python3 main_scripts/protect_excel_template.py \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
    --mode script \
    --password "SecurePassword123"

# This creates: OUTPUT_TEMPLATE_FILE_EMPTY_FILE_PROTECTED_FOR_SCRIPT.xlsx
```

### 2. Update Your Commands (Use Protected Template)

```bash
# Old command (using unprotected template)
python3 main_scripts/simple_llm_mapper.py \
    --input output/COMBINED_*.xlsx \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
    --output output/final_mapped.xlsx

# New command (using protected template)
python3 main_scripts/simple_llm_mapper.py \
    --input output/COMBINED_*.xlsx \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE_PROTECTED_FOR_SCRIPT.xlsx \
    --output output/final_mapped.xlsx
```

## Key Points

### Where Protection Happens

1. **BEFORE the workflow** - Template is protected once during setup
2. **NOT during mapping** - The mapper reads the protected template
3. **NOT on output** - The final output is not protected

### Why This Works

1. **Python can write to protected cells** - When openpyxl opens a protected Excel file, it can still modify cells programmatically
2. **Protection is for human users** - Prevents accidental manual edits
3. **Template structure preserved** - Ensures consistent mapping

### Benefits

1. **Template Integrity** 
   - Column headers can't be accidentally changed
   - Row structure remains intact
   - Metric names stay consistent

2. **Automation Reliability**
   - Script always finds expected structure
   - No surprises from manual edits
   - Consistent output every time

3. **User Safety**
   - Can't accidentally break the template
   - Can still enter Census TA and TA Population
   - Can copy any data needed

## Common Scenarios

### Scenario 1: New User Setup
```bash
# Admin protects template once
python3 main_scripts/protect_excel_template.py \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
    --mode script

# Share protected template with users
# Users run normal workflow with protected template
```

### Scenario 2: Template Update Needed
```bash
# 1. Unprotect in Excel (Review → Unprotect Sheet)
# 2. Make changes
# 3. Re-protect with script
python3 main_scripts/protect_excel_template.py \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
    --mode script
```

### Scenario 3: Different Protection Levels
```bash
# For automation team (minimal protection)
python3 main_scripts/protect_excel_template.py \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
    --mode script

# For end users (full protection, no manual entry)
python3 main_scripts/protect_excel_template.py \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
    --mode full \
    --password "ViewOnly"
```

## Best Practices

1. **Keep Both Versions**
   - `OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx` (original, unprotected)
   - `OUTPUT_TEMPLATE_FILE_EMPTY_FILE_PROTECTED_FOR_SCRIPT.xlsx` (for daily use)

2. **Document Protection Status**
   - Add README note about which template to use
   - Include password in secure documentation

3. **Test Before Deployment**
   ```bash
   # Test that automation still works
   python3 main_scripts/simple_llm_mapper.py \
       --input output/COMBINED_*.xlsx \
       --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE_PROTECTED_FOR_SCRIPT.xlsx \
       --output output/test_protected_output.xlsx
   ```

4. **Version Control**
   - Keep unprotected template in version control
   - Protected version can be generated as needed

## FAQ

**Q: Will protection slow down the automation?**
A: No, Python handles protected files just as fast as unprotected ones.

**Q: Can users still manually enter Census TA and TA Population?**
A: Yes, these cells (C16, C17, C54, C55, C92, C93) remain editable.

**Q: What if someone needs to edit other cells?**
A: They would need to unprotect the sheet with the password first.

**Q: Is the final output protected?**
A: No, the final output (final_mapped.xlsx) is not protected and fully editable.

**Q: Can I protect the final output too?**
A: Yes, but that's a separate step after mapping:
```bash
python3 main_scripts/protect_excel_template.py \
    --template output/final_mapped.xlsx \
    --mode full \
    --password "ReadOnly"
```

## Summary

The protection workflow is simple:
1. **Protect the empty template once** (before any automation)
2. **Use the protected template** in all automation runs
3. **Final output remains unprotected** for user flexibility

This ensures template integrity while maintaining full automation functionality!