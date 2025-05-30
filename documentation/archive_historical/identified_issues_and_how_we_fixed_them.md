# Identified Issues and How We Fixed Them

## 🧭 **CENTRAL GUIDE NAVIGATION**
| **File** | **Use For** | **Status** |
|----------|-------------|------------|
| [`current_status.md`](current_status.md) | Current priorities & immediate context | 🔴 **ACTIVE DEBUGGING** |
| **→ THIS FILE** | **Debug history & proven solutions** | 🔍 **REFERENCE** |
| [`q_and_a_output_template_mapping.md`](q_and_a_output_template_mapping.md) | Final phase specs & requirements | 📋 **BLOCKED** |
| [`rules.md`](rules.md) | Implementation protocols & procedures | ⚡ Active |

## 🔗 **CURRENT DEBUGGING CONTEXT**
**Active Issue:** Campaign Reach (Absl) and Campaign Freq. missing from output  
**Status:** 🔍 **DEBUGGING** - Region 0 R&F normalization issue  
**Related Historical Issues:** Issues #3 (R&F Processing), #4 (Market Column Detection)  
**Next Phase Dependency:** [Template Population Requirements](q_and_a_output_template_mapping.md#critical-urgent-issue-identified)

## ✅ **RECENTLY RESOLVED ISSUES (2025-05-27)**

### Issue #9: False-Positive R&F Assertions on PLANNED Sheets
**Status:** ✅ **RESOLVED**  
**Symptom:** AssertionError for Campaign Reach/Freq on "PLANNED" data sheets  
**Root Cause:** Unconditional assertions expecting R&F metrics on all sheets  
**Solution Applied:**
1. Added `_rf_expected_for_sheet()` helper function
2. Wrapped assertions in conditional check
3. Only assert R&F metrics when legitimately expected (DELIVERED files with R&F indicators)

### Issue #10: Script Abortion on Single Sheet Errors
**Status:** ✅ **RESOLVED**  
**Symptom:** Entire script fails if one sheet encounters an error  
**Root Cause:** No error isolation between sheet processing  
**Solution Applied:**
1. Added try/except block around sheet processing loop
2. Errors logged per sheet with context
3. Script continues processing other sheets

### Issue #11: Uninitialized Variable Errors
**Status:** ✅ **RESOLVED**  
**Symptom:** Potential NameError for `combined_df` and `final_df_for_output`  
**Root Cause:** Variables used before initialization in some code paths  
**Solution Applied:**
1. Explicitly initialized both variables as None at function start
2. Added guard clause to check `combined_df` before use
3. Graceful exit when no data collected

## 🚧 **CURRENT ACTIVE ISSUE (2025-05-26)**

### Issue #8: Campaign Metrics Missing from R&F Normalization
**Status:** 🔴 **ACTIVE DEBUGGING**  
**Symptom:** Campaign Reach (Absl) and Campaign Freq. missing from `COMBINED_*.xlsx` output  
**Source Confirmed:** ✅ Present in DV360 sheet rows 3-4 with valid data  
**Root Cause:** Region 0 containing campaign metrics not being R&F normalized  
**Processing Evidence:** DV360 shows 2 regions found, 2 processed, **only 1 R&F normalized**  

**Debug History:**
- ✅ **Phase 1:** Fixed main R&F detection logic (46 rows now detected vs 0)
- ✅ **Phase 2:** Confirmed funnel metrics working (Awareness, Consideration, Purchase)
- 🔴 **Phase 3:** **CURRENT** - Region 0 R&F normalization investigation

**Solution Strategy:** 
1. [Sequential thinking analysis](rules.md#sequential-thinking) of Region 0 processing
2. Investigate `normalize_rf_table` function for Region 0 inclusion
3. Review `validate_marker_alignment` function for Region 0 boundaries
4. Add enhanced logging to track Region 0 processing decisions

**Related Historical Patterns:**
- **Similar to Issue #3:** R&F table processing challenges
- **Similar to Issue #4:** Region boundary detection problems
- **Key Difference:** This affects campaign-level aggregation, not individual market data

**Template Impact:** [BLOCKS all template population development](q_and_a_output_template_mapping.md#dependency-blocker-status)

---

## 📚 **SOLUTION PATTERNS & DEBUG WISDOM**

### **R&F Processing Issues (Issues #3, #8)**
**Pattern:** R&F table detection and normalization problems  
**Common Causes:** Region boundary detection, keyword matching, processing criteria  
**Proven Approaches:** 
- Investigate region detection logic first
- Add comprehensive logging for processing decisions
- Validate source data presence before assuming processing failure
- Use sequential thinking for persistent issues ([Rule #6](rules.md))

### **Region Detection Issues (Issues #4, #8)**  
**Pattern:** Table regions not properly identified or processed  
**Common Causes:** Marker alignment, header detection, boundary definition  
**Proven Approaches:**
- Check both marker-based and identifier-based detection
- Validate region boundaries include all necessary data
- Review processing criteria for edge cases

### **Data Mapping Issues (Issues #2, #4)**
**Pattern:** Data present in source but missing in output  
**Common Causes:** Column mapping, region exclusion, transformation errors  
**Proven Approaches:**
- Confirm data presence in source files
- Trace data flow through processing pipeline
- Add validation checkpoints at each processing stage

## Initial Challenge: Processing PCA/Delivered Files & Identifier-Based Region Finding

**Problem:** The script initially struggled with PCA/Delivered (non-marker-based) Excel formats. This was due to the original design heavily relying on START/END markers for table detection. Processing these files required:
1.  A robust mechanism to identify tables based on keyword identifiers in header rows (the `_find_regions_with_identifiers` function).
2.  Handling of multiple tables per sheet, common in PCA reports.
3.  Logic for header uniquification to prevent errors when concatenating data with duplicate column names.

**Solution:**
*   Developed and integrated the `_find_regions_with_identifiers` function to detect tables based on keywords in potential header rows, crucial for PCA/Delivered files.
*   Enhanced table detection logic (originally `validate_marker_alignment`, later combined with identifier logic) to correctly identify multiple distinct table regions per sheet.
*   Implemented header uniquification by appending suffixes (e.g., `_1`, `_2`) to duplicate column names during data extraction.
*   Added filename-based heuristics to help differentiate between PLANNED (marker-reliant) and DELIVERED/PCA (identifier-reliant) formats, guiding the appropriate detection strategy.

**Status:** Resolved. The script now effectively processes both PLANNED and DELIVERED/PCA formats, utilizing a combination of marker-based and identifier-based table detection with header uniquification.

## Issue 3: Special Handling for Reach & Frequency Tables in PCA Format

**Problem:** PCA format files often contain Reach & Frequency (R&F) tables in a wide format (metrics as rows, markets as columns). These need to be transformed (unpivoted/melted) into a long format (one row per metric-market combination) to align with the standard data structure and allow for proper analysis and combination with other data types.

**Solution:** 
*   A dedicated function, `normalize_rf_table` (later refined and integrated into `process_rf_table`), was developed to specifically detect and process these R&F tables.
*   This function identifies likely R&F tables based on keywords in the first column (e.g., "METRICS/ MARKET") and the structure of subsequent columns (market names).
*   It then transforms these tables from wide to long format, creating appropriate `MARKET`, `RAW_METRIC_NAME`, and `VALUE` columns, which are then mapped to standard output columns like `UNIQUES_REACH`, `FREQUENCY`, `BUDGET_LOCAL`, etc.
*   A `Source_Type` of "DELIVERED R&F" is assigned to this data.

**Status:** Resolved. R&F tables are now correctly identified, processed, and integrated into the output.

## Issue 4: MARKET Column Empty for DELIVERED MEDIA Rows

**Error Message/Symptom:** The `MARKET` column in the output file was blank for rows with `Source_Type` = "DELIVERED MEDIA", although market information was present in the input DELIVERED Excel file, often in a "Metrics / Market" style column.

**Root Cause:** The table detection logic sometimes defined a region that excluded the actual "Metrics / Market" column, especially if it was immediately to the left of the main data block. The R&F table processing correctly identified markets, but standard media tables did not.

**Solution:**
1.  Modified `extract_data_to_dataframe`.
2.  After initial header extraction, if 'MARKET' is not among the mapped headers and the region's starting column is not the first column of the sheet:
    *   The script checks the cell immediately to the left of the detected region's top-left data cell (i.e., `sheet.cell(header_row_idx + 1, data_start_col_idx).value`).
    *   If this cell's value contains "MARKET", "METRICS/ MARKET", or "METRICS / MARKET" (case-insensitive), the script assumes the true market column was missed.
    *   The `data_start_col_idx` and `region['start_col']` are decremented by 1 (shifting the region one column to the left).
    *   `raw_headers` are re-extracted using the adjusted column range.
This ensures that if a "Metrics / Market" type column is just outside the initially detected region for standard media tables, it's correctly included.

**Status:** Fixed. Verified by checking the output where DELIVERED MEDIA rows now correctly show market names.

## Issue 5: Date Formatting Incorrect (DD/MM/YYYY HH:MM:SS instead of DD/MM/YY)

**Error Message/Symptom:** `START_DATE` and `END_DATE` columns in the output Excel file were displayed with full datetime objects (e.g., "20/04/2025 00:00:00") instead of the desired "DD/MM/YY" text format.

**Root Cause:** Pandas DataFrames were written to Excel, and Excel's default behavior was to interpret date-like strings or datetime objects as full datetime values.

**Solution:**
1.  In `process_workbook`, before writing the `final_df_for_output` to Excel, a new formatting step was added for "START_DATE" and "END_DATE" columns.
2.  A helper function `_fmt_date` is applied to each value in these columns:
    *   If the value is a pandas `Timestamp` or Python `datetime` object, it's formatted to `'%d/%m/%y'` and prepended with an apostrophe (e.g., `'20/04/25'`). The apostrophe forces Excel to treat it as text.
    *   If the value is already a string and contains "00:00:00" or "-", it attempts to parse it as a date, format it to `'%d/%m/%y'`, and prepend an apostrophe.
    *   Other string values are returned as is (unless they are successfully parsed as dates by the above rule).
    *   Non-string, non-datetime values are returned as is.
This ensures that Excel displays the dates as plain text in the "DD/MM/YY" format and does not auto-convert them.

**Status:** Fixed. Verified by inspecting the output Excel file; date columns now show as text in the desired format.

## Issue 6: Numerical Columns Lack Excel Formatting (Thousand Separators, Decimals)

**Error Message/Symptom:** Numeric columns like `IMPRESSIONS`, `BUDGET_LOCAL`, etc., in the output Excel file were displayed as raw numbers without thousand separators or a consistent number of decimal places.

**Root Cause:** When writing a pandas DataFrame to Excel, standard number formatting is not automatically applied by `to_excel()`.

**Solution:**
1.  After `final_df_for_output.to_excel(...)` is called in `process_workbook`:
    *   The script re-opens the just-saved Excel file using `openpyxl.load_workbook()`.
    *   It iterates through the columns defined in the `NUMERIC_COLUMNS` list.
    *   For each cell in these numeric columns (excluding the header row), if the cell contains a numeric value (int or float), its `number_format` property is set to `'#,##0.00'`.
    *   The workbook is then saved again, overwriting the previous version with the newly applied formatting.

**Status:** Fixed. Verified by inspecting the output Excel file; numeric columns are now formatted with thousand separators and two decimal places.

## Issue 7: Handling of `excel_data_extractor_v0_6.py` and Output Directory Problems

**Error Message/Symptom:** Script runs were failing or producing no output. Errors included `FileNotFoundError` for `excel_data_extractor_v0_6.py` and empty output directories.

**Root Cause:** 
1.  The `excel_data_extractor_v0_6.py` script, which was a wrapper for optimizations, was accidentally deleted or not consistently present, leading to `FileNotFoundError`.
2.  There were some initial misconfigurations or misunderstandings regarding the default output directory (now resolved with standard `output/` directory).

**Solution:**
1.  The core optimization logic from `excel_data_extractor_v0_6.py` (specifically the `_determine_effective_bounds` function) was permanently integrated into the main `excel_data_extractor.py` script.
2.  The `excel_data_extractor_v0_6.py` file was confirmed to be deletable after this integration.
3.  The default output directory in `excel_data_extractor.py` (in `parse_arguments`) was confirmed/set to `output/`. The script runs were then explicitly directed to use `--output-dir output` during testing to ensure clarity.
4.  It was clarified that the primary cause of no output after some changes was the temporary absence of the `v0_6.py` file before its logic was fully merged into the main script and the user restored it.

**Status:** Resolved. The system now uses a single `excel_data_extractor.py` with integrated optimizations, and output directory settings are clear. The `v0_6.py` file is no longer needed. 