# R&F Data Handling Guide

**Date Created:** 2025-05-28  
**Purpose:** Complete guide for handling Reach & Frequency (R&F) data  
**Scope:** Understanding, extracting, and mapping R&F data correctly

## 🎯 Overview

R&F (Reach & Frequency) data has a unique structure that differs from standard media data. This guide documents the complete solution for handling R&F data correctly.

## 📊 R&F Data Structure

### Key Differences from Media Data

1. **PLATFORM Column Contains Metrics**
   - Unlike media data where PLATFORM = "DV360", "META", etc.
   - R&F data has PLATFORM = metric names like "Campaign Reach (Absl)"
   
2. **Source Sheet Identifies Platform**
   - Each sheet in the DELIVERED file corresponds to a platform
   - DV360 sheet → DV360 R&F data
   - META sheet → META R&F data
   - TIKTOK sheet → TIKTOK R&F data

3. **Data Location in Template**
   - Campaign Level (rows 16-23): Only shows R&F actuals (no planned values)
   - Section Level (rows 25-38): Shows both planned and actuals

### R&F Metrics

The following metrics appear in the PLATFORM column for R&F data:

```
Campaign Reach (Absl)     → Total Reach
Campaign Reach (%)        → Reach percentage
Campaign Frequency        → Avg. Frequency
Campaign EffReach 1+      → Effective reach 1+
Campaign EffReach 2+      → Effective reach 2+
Campaign EffReach 3+      → Effective reach 3+
```

## 🔧 Implementation Details

### 1. Data Extraction Enhancement

The `excel_data_extractor.py` now tags R&F data with special Source_Sheet values:

```python
# For R&F data, add suffix to Source_Sheet
if file_format == 'delivered' and 'PLATFORM' in df_region_data.columns:
    rf_mask = df_region_data['PLATFORM'].astype(str).str.contains(r'(Reach|Freq)', na=False, regex=True)
    df_region_data['Source_Sheet'] = normalized_name
    df_region_data.loc[rf_mask, 'Source_Sheet'] = f"{normalized_name}_RF"
    df_region_data.loc[~rf_mask, 'Source_Sheet'] = f"{normalized_name}_MEDIA"
```

This creates Source_Sheet values like:
- `DV360_RF` for R&F data from DV360 sheet
- `DV360_MEDIA` for media data from DV360 sheet

### 2. Template Mapping Logic

The `simple_llm_mapper.py` handles R&F data specially:

```python
def _calculate_metrics_for_market(self, platform, market, planned_data, actuals_data, actuals_rf_data):
    # For Campaign Level rows 16-23, we only put actuals from R&F
    if actuals_rf_data is not None and not actuals_rf_data.empty:
        # Look for Campaign Reach (Absl) in the PLATFORM column
        campaign_reach_mask = actuals_rf_data['PLATFORM'] == 'Campaign Reach (Absl)'
        if campaign_reach_mask.any() and 'UNIQUES_REACH' in actuals_rf_data.columns:
            actuals_reach = actuals_rf_data.loc[campaign_reach_mask, 'UNIQUES_REACH'].sum()
```

### 3. Campaign Level vs Section Level

**Campaign Level (rows 16-23):**
- Markets are merged cells spanning 2 columns
- Only R&F actuals are shown (planned column left empty)
- Data comes exclusively from R&F sheets

**Section Level (rows 25-38):**
- Markets are split into Planned/Actuals columns
- Both planned and actuals values shown
- Data comes from both MEDIA and R&F sources

## 📋 Validation Checks

The production error handler validates R&F data:

1. **Structure Validation**
   - Checks for required columns: PLATFORM, MARKET, UNIQUES_REACH
   - Verifies PLATFORM contains expected metric names
   - Validates numeric data integrity

2. **Data Completeness**
   - Ensures sufficient R&F data coverage
   - Warns about missing metrics
   - Tracks completeness percentage

## 🚨 Common Issues and Solutions

### Issue 1: R&F Data Shows 0 Values
**Cause:** Looking for platform name in PLATFORM column  
**Solution:** Check for metric names instead

### Issue 2: Missing R&F Data in Output
**Cause:** Source_Sheet not properly tagged  
**Solution:** Ensure excel_data_extractor adds _RF suffix

### Issue 3: Wrong Row Placement
**Cause:** Not distinguishing Campaign vs Section level  
**Solution:** Use different logic for rows 16-23 vs 25-38

## 📊 Example Data Flow

```
DELIVERED Excel File:
├── DV360 Sheet
│   ├── Media Data (PLATFORM = "DV360")
│   └── R&F Data (PLATFORM = "Campaign Reach (Absl)")
│
└── META Sheet
    ├── Media Data (PLATFORM = "META")
    └── R&F Data (PLATFORM = "Campaign Frequency")
    
↓ After Extraction ↓

Combined DataFrame:
├── DV360_MEDIA rows
├── DV360_RF rows (tagged with Source_Sheet = "DV360_RF")
├── META_MEDIA rows
└── META_RF rows (tagged with Source_Sheet = "META_RF")

↓ After Mapping ↓

Output Template:
├── Campaign Level (16-23): R&F actuals only
└── Section Level (25-38): Both planned and actuals
```

## 🔍 Debugging R&F Issues

To debug R&F data issues:

1. **Check Source_Sheet Tagging**
   ```python
   # In combined Excel, filter for _RF suffix
   rf_data = df[df['Source_Sheet'].str.contains('_RF')]
   print(rf_data['Source_Sheet'].unique())
   ```

2. **Verify PLATFORM Values**
   ```python
   # Should see metric names, not platform names
   print(rf_data['PLATFORM'].unique())
   ```

3. **Check Data Values**
   ```python
   # UNIQUES_REACH should have numeric values
   print(rf_data.groupby('PLATFORM')['UNIQUES_REACH'].sum())
   ```

## 📚 Configuration

R&F handling can be customized in `template_mapping_config.json`:

```json
{
  "rf_metrics": {
    "Campaign Reach (Absl)": "Total Reach",
    "Campaign Reach (%)": "Reach %",
    "Campaign Frequency": "Avg. Frequency"
  },
  "rf_data_source": "DELIVERED R&F",
  "campaign_level_rows": [16, 17, 18, 19, 20, 21, 22, 23]
}
```

## ✅ Best Practices

1. **Always validate R&F data structure** before processing
2. **Use Source_Sheet tagging** to identify R&F vs media data
3. **Handle missing R&F data gracefully** - use 0 or dash
4. **Test with multiple client datasets** to ensure robustness
5. **Monitor R&F extraction completeness** in logs

## 🛠️ Troubleshooting Commands

```bash
# Check R&F data extraction
grep "R&F" main_scripts/logs/excel_processor.log

# Validate R&F structure
python -c "import pandas as pd; df=pd.read_excel('output/COMBINED*.xlsx'); print(df[df['Source_Sheet'].str.contains('_RF')]['PLATFORM'].unique())"

# Test R&F mapping
python main_scripts/simple_llm_mapper.py --input output/COMBINED*.xlsx --template input/OUTPUT_TEMPLATE*.xlsx --output test_rf_output.xlsx
```

---

This guide will be updated as we encounter new R&F data patterns or requirements.