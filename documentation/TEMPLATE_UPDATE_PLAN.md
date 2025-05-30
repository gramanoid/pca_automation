# Template Update Development Plan

## Overview
This document outlines the comprehensive development plan for updating the Media Plan automation system to match the new Excel template structure provided on May 29, 2025.

## Key Changes in New Template

### 1. Row Number Updates
All platform sections have been shifted to new row positions:

#### DV360 (Rows 15-42)
- **Header Row**: 15 (previously 15 - no change)
- **Campaign Level**: Rows 16-23 (previously 16-23 - no change) 
- **Section Headers**: Row 24 (previously 24 - no change)
- **Awareness**: Rows 25-30 (previously 25-30 - no change)
- **Consideration**: Rows 31-36 (previously 31-36 - no change)
- **Purchase**: Rows 37-42 (previously 37-41 - EXPANDED by 1 row)

#### META (Rows 53-80)
- **Header Row**: 53 (previously 52 - shifted down by 1)
- **Campaign Level**: Rows 54-61 (previously 53-60 - shifted down by 1)
- **Section Headers**: Row 62 (previously 61 - shifted down by 1)
- **Awareness**: Rows 63-68 (previously 62-67 - shifted down by 1)
- **Consideration**: Rows 69-74 (previously 68-73 - shifted down by 1)
- **Purchase**: Rows 75-80 (previously 74-78 - shifted down by 1, EXPANDED by 1 row)

#### TIKTOK (Rows 91-118)
- **Header Row**: 91 (previously 92 - shifted UP by 1)
- **Campaign Level**: Rows 92-99 (previously 93-100 - shifted UP by 1)
- **Section Headers**: Row 100 (previously 101 - shifted UP by 1)
- **Awareness**: Rows 101-106 (previously 102-107 - shifted UP by 1)
- **Consideration**: Rows 107-112 (previously 108-113 - shifted UP by 1)
- **Purchase**: Rows 113-118 (previously 114-118 - shifted UP by 1, no size change)

### 2. Purchase Section Structure Change
The Purchase section now includes 6 metrics instead of 5:
1. Clicks
2. Impressions
3. CTR%
4. CPC
5. **Reach abs** (NEW)
6. Budget

### 3. New Market Addition
Jordan (JOR) has been added as the 6th market in columns O and P.

### 4. Merged Cell Structure
Campaign Level rows have specific merged cell requirements:
- Census TA (row 16/54/92): C & D columns are MERGED
- TA Population (row 17/55/93): C & D columns are MERGED
- Other Campaign Level metrics: C (PLANNED) and D (ACTUALS) are separate

## Implementation Status

### ✅ Completed Tasks

1. **Platform Structure Update** (simple_llm_mapper.py)
   - Updated all row numbers for DV360, META, and TIKTOK sections
   - Adjusted end_row values to accommodate 6-metric Purchase sections
   - Updated all metric row references

2. **Purchase Section Metrics**
   - Added "Reach abs" as the 5th metric in Purchase sections
   - Updated metric_offsets dictionary to include 6 metrics for Purchase
   - Maintained consistency across all platforms

3. **Consideration Section Verification**
   - Confirmed "Reach abs" remains at row 5 of 6 metrics
   - No extra rows added

4. **Jordan Market Support**
   - Added 'JOR' and 'JORDAN' to valid_markets list
   - Updated market processing to handle up to 6 markets
   - Extended column mapping to include O:P columns

5. **Merged Cell Handling**
   - Updated comments to reflect merged cell structure
   - Existing code already handles merged cells correctly

6. **Template Protection Script**
   - Created protect_excel_template.py
   - Supports full protection and selective protection modes
   - Allows specifying editable ranges for data entry

### 🔄 Pending Tasks

7. **Testing**
   - Run full end-to-end test with sample data
   - Verify all cells are written to correct positions
   - Confirm Jordan market appears in columns O:P
   - Test template protection functionality

8. **Documentation Updates**
   - Update CLAUDE.md with new row structure
   - Update README.md if needed
   - Create user guide for template protection

## Development Plan

### Phase 1: Code Updates (COMPLETED)
- [x] Update platform_structure dictionary
- [x] Fix Purchase section to include "Reach abs"
- [x] Add Jordan to market handling
- [x] Update market loops to handle 6 markets
- [x] Create template protection script

### Phase 2: Testing & Validation
- [ ] Create test data including Jordan market
- [ ] Run extraction and mapping process
- [ ] Verify output matches new template structure
- [ ] Test template protection with password
- [ ] Test selective protection with editable cells

### Phase 3: Documentation & Deployment
- [ ] Update all documentation files
- [ ] Create migration guide for existing users
- [ ] Test deployment package
- [ ] Create backup of old configuration

## Template Protection Usage

### Full Protection (Lock Everything)
```bash
python main_scripts/protect_excel_template.py \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
    --password "SecurePassword123" \
    --mode full
```

### Selective Protection (Allow Data Entry)
```bash
python main_scripts/protect_excel_template.py \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
    --password "SecurePassword123" \
    --mode selective
```

### Protection Without Password
```bash
python main_scripts/protect_excel_template.py \
    --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
    --mode full \
    --allow-formatting
```

## Testing Checklist

- [ ] DV360 data appears in rows 15-42
- [ ] META data appears in rows 53-80  
- [ ] TIKTOK data appears in rows 91-118
- [ ] Purchase sections have 6 rows each
- [ ] Jordan market appears in columns O:P
- [ ] Campaign Level merged cells are preserved
- [ ] All numeric formatting is correct
- [ ] Template protection prevents accidental changes

## Risk Mitigation

1. **Backward Compatibility**
   - Keep backup of old platform_structure
   - Allow configuration override via environment variable
   - Document migration path

2. **Data Validation**
   - Add row number validation before writing
   - Log all cell write operations
   - Create detailed error reports

3. **Template Changes**
   - Protected template prevents accidental modifications
   - Version control for template files
   - Clear documentation of expected structure

## Next Steps

1. Complete testing phase with real data
2. Update production documentation
3. Deploy updated system
4. Train users on template protection
5. Monitor for any issues

## Contact for Questions

For any questions about this update plan, please refer to:
- CLAUDE.md for technical details
- README.md for general project information
- This document for specific template changes