# Excel Template Protection Guide

## Overview

This guide explains how to protect the Excel template (`OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx`) to prevent accidental modifications while maintaining usability for the automation script.

## What Can Be Protected in Excel via Python

### 1. **Sheet-Level Protection**
Using openpyxl's `SheetProtection` class, we can control:
- **Cell editing** - Prevent users from modifying cell values
- **Cell selection** - Allow/prevent selecting locked cells (for copying)
- **Formatting** - Prevent changes to cell/column/row formatting
- **Structure changes** - Prevent inserting/deleting rows/columns
- **Sorting & filtering** - Lock sort and filter functionality
- **Objects & scenarios** - Protect embedded objects and scenarios

### 2. **Cell-Level Protection**
Individual cells can be:
- **Locked** - Cannot be edited when sheet is protected
- **Unlocked** - Can be edited even when sheet is protected
- **Hidden** - Formula is hidden from formula bar (but result still visible)

### 3. **Workbook Protection**
- **Structure** - Prevent adding/deleting/renaming sheets
- **Windows** - Prevent moving/resizing workbook windows

## Our Template Protection Strategy

For the automation template, we implement:

### ✅ **What Users CAN Do:**
1. **Select any cell** - Click on any cell to see its value
2. **Copy cell contents** - Ctrl+C works on all cells
3. **View formulas** - See formulas in formula bar
4. **Navigate freely** - Use arrow keys, scroll, etc.
5. **Edit Census TA and TA Population** - Only these cells remain unlocked

### ❌ **What Users CANNOT Do:**
1. **Edit locked cells** - Cannot change values in protected cells
2. **Delete content** - Cannot clear cell contents
3. **Change formatting** - Cannot modify fonts, colors, borders
4. **Insert/delete rows or columns** - Structure is locked
5. **Modify sheet structure** - Cannot rename, add, or delete sheets

## Protection Implementation

### Default Protection (Script Mode)

The template is protected with only specific cells unlocked:

**Unlocked Cells (Editable):**
- **DV360**: C16 (Census TA), C17 (TA Population)
- **META**: C54 (Census TA), C55 (TA Population)  
- **TIKTOK**: C92 (Census TA), C93 (TA Population)

### How to Protect the Template

```bash
# Basic protection for script use (recommended)
python main_scripts/protect_excel_template.py \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
    --mode script

# With password protection
python main_scripts/protect_excel_template.py \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
    --mode script \
    --password "YourSecurePassword"

# With additional manual entry cells
python main_scripts/protect_excel_template.py \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
    --mode script \
    --manual-cells A1 A2 B3 B4
```

## Technical Details

### Protection Settings Applied

```python
protection = SheetProtection()

# Core settings
protection.sheet = True              # Enable protection
protection.selectLockedCells = False # Allow selecting locked cells (for copying)
protection.selectUnlockedCells = False # Allow selecting unlocked cells

# Prevent modifications
protection.formatCells = True        # No formatting changes
protection.formatColumns = True      # No column formatting
protection.formatRows = True         # No row formatting
protection.insertColumns = True      # No inserting columns
protection.insertRows = True         # No inserting rows
protection.deleteColumns = True      # No deleting columns
protection.deleteRows = True         # No deleting rows
protection.sort = True              # No sorting
protection.autoFilter = True        # No filter changes
```

### Why These Settings?

1. **`selectLockedCells = False`** - Counterintuitively, setting this to False ALLOWS users to select locked cells. This enables copying.

2. **All format/structure options = True** - Setting these to True PREVENTS the action, maintaining template integrity.

3. **Cell-level locking** - By default, all cells are locked, then we selectively unlock only Census TA and TA Population cells.

## Use Cases

### For Template Distribution
```bash
# Protect template before sharing with users
python main_scripts/protect_excel_template.py \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
    --mode script \
    --password "CompanyPassword2025"
```

### For Development/Testing
```bash
# Create unprotected copy for development
# (Simply use the original unprotected template)
```

### For Training
```bash
# Protect with simple password for training sessions
python main_scripts/protect_excel_template.py \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
    --mode script \
    --password "training"
```

## Important Notes

1. **Password Protection**: If you set a password, users will need it to unprotect the sheet. Store passwords securely!

2. **Merged Cells**: The Census TA and TA Population cells are merged (C:D). The protection handles this automatically.

3. **Automation Compatibility**: The protected template works perfectly with the automation scripts - they can still write to all cells programmatically.

4. **Copy Protection**: While users can copy cell contents, they cannot paste into locked cells.

5. **Visual Indicators**: In Excel, locked cells typically show a lock icon when you try to edit them.

## Troubleshooting

### "Cannot edit cell" error
- This is expected for locked cells
- Check if you need to edit Census TA or TA Population fields (these should be unlocked)

### Need to modify the template
1. Open in Excel
2. Go to Review → Unprotect Sheet
3. Enter password if one was set
4. Make changes
5. Re-protect using the script

### Lost password
- Unfortunately, Excel protection passwords cannot be recovered
- Keep the original unprotected template as backup
- Document passwords in a secure password manager

## Best Practices

1. **Always keep an unprotected master copy** - Store safely for future modifications

2. **Use meaningful passwords** - But not too complex for internal use

3. **Document protection status** - Add "_PROTECTED" to filename

4. **Test before distribution** - Ensure Census TA and TA Population are editable

5. **Train users** - Explain what can and cannot be edited

## Summary

The template protection provides the perfect balance:
- ✅ Template structure is protected from accidents
- ✅ Users can view and copy any data
- ✅ Manual entry is allowed only where needed
- ✅ Automation scripts work without modification
- ✅ Professional and secure distribution