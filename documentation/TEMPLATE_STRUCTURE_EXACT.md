# Exact Template Structure Documentation

## Overview
This document contains the EXACT cell positions and structure for the output template, as confirmed by the user.

## General Structure
- **DV360**: Rows 15-41 (A15:N41)
- **META**: Rows 52-81 (A52:N81)  
- **TIKTOK**: Rows 92-119 (A92:N119)
- All platforms follow the EXACT same pattern, just starting at different rows

## Market Column Mapping
Markets can appear in any order and not all markets will be present in every campaign. The template supports up to 5 markets:
- **Market 1**: E:F (e.g., E15:F15 for DV360 header)
- **Market 2**: G:H (e.g., G15:H15 for DV360 header)
- **Market 3**: I:J (e.g., I15:J15 for DV360 header)
- **Market 4**: K:L (e.g., K15:L15 for DV360 header)
- **Market 5**: M:N (e.g., M15:N15 for DV360 header)

Default template order: UAE, OMN (Oman), LEB (Lebanon), KWT (Kuwait), QAT (Qatar)
But actual order should be based on campaign data (can sort by budget from highest to lowest).

## DV360 Section (Rows 15-41)

### Header Structure
- **Row 15**: Platform header
  - B15: Empty
  - C15:D15 (merged): "DV360 TOTAL"
  - E15:F15 (merged): Market 1 name
  - G15:H15 (merged): Market 2 name
  - Pattern continues for each market

### Campaign Level Section (Rows 16-23)
CRITICAL DISTINCTION:
- **Rows 16-17**: ONLY C:D are merged. Markets have merged cells (E16:F16, G16:H16, etc.)
- **Rows 18-23**: ALL columns split into Planned/Actuals (C=Planned, D=Actuals for Total)

| Row | Column B Label | Total | Markets |
|-----|---------------|-------|---------|
| 16  | Census TA     | C16:D16 merged | E16:F16 merged, G16:H16 merged, etc. |
| 17  | TA Population | C17:D17 merged | E17:F17 merged, G17:H17 merged, etc. |
| 18  | Total Reach   | C18=Planned, D18=Actuals | E18=Planned, F18=Actuals, etc. |
| 19  | Total Reach%  | C19=Planned, D19=Actuals | E19=Planned, F19=Actuals, etc. |
| 20  | Total Frequency| C20=Planned, D20=Actuals | E20=Planned, F20=Actuals, etc. |
| 21  | CPM           | C21=Planned, D21=Actuals | E21=Planned, F21=Actuals, etc. |
| 22  | Impressions   | C22=Planned, D22=Actuals | E22=Planned, F22=Actuals, etc. |
| 23  | Budget        | C23=Planned, D23=Actuals | E23=Planned, F23=Actuals, etc. |

### Section Headers (Row 24)
- B24: "Campaign Level" label
- C24: "Planned", D24: "Actuals" 
- E24: "Planned", F24: "Actuals" (for Market 1)
- G24: "Planned", H24: "Actuals" (for Market 2)
- Pattern continues for each market

### Awareness Section (Rows 25-30)
| Row | Column B Label | Data follows Planned/Actuals split from row 24 |
|-----|---------------|------------------------------------------------|
| 25  | Reach         | C25=Planned, D25=Actuals, E25=Planned, F25=Actuals, etc. |
| 26  | Reach%        | Same pattern |
| 27  | Frequency     | Same pattern |
| 28  | Impressions   | Same pattern |
| 29  | CPM           | Same pattern |
| 30  | Budget        | Same pattern |

### Consideration Section (Rows 31-36)
| Row | Column B Label | Data follows Planned/Actuals split |
|-----|---------------|-----------------------------------|
| 31  | Views         | Same pattern as Awareness |
| 32  | Impressions   | Same pattern |
| 33  | VTR%          | Same pattern |
| 34  | CPV           | Same pattern |
| 35  | Reach abs     | Same pattern |
| 36  | Budget        | Same pattern |

### Purchase Section (Rows 37-41)
| Row | Column B Label | Data follows Planned/Actuals split |
|-----|---------------|-----------------------------------|
| 37  | Clicks        | Same pattern as above |
| 38  | Impressions   | Same pattern |
| 39  | CTR%          | Same pattern |
| 40  | CPC           | Same pattern |
| 41  | Budget        | Same pattern (Note: only 5 rows for Purchase) |

## META Section (Rows 52-81)
Follows EXACT same pattern as DV360, but:
- Platform header at row 52 (C52:D52 merged for "META TOTAL")
- Census TA at row 53
- TA Population at row 54
- And so on...

## TIKTOK Section (Rows 92-119)
Follows EXACT same pattern as DV360, but:
- Platform header at row 92 (C92:D92 merged for "TIKTOK TOTAL")
- Census TA at row 93
- TA Population at row 94
- And so on...

## Data Source Mapping (from Q&A document)

### Campaign Level Formulas
- **Census TA**: Manual input (leave ALL cells empty - both TOTAL and market columns)
- **TA Population**: Manual input (leave ALL cells empty - both TOTAL and market columns)
- **Total Reach**: Sum of Awareness Reach + Consideration Reach Abs + Purchase Reach Abs
- **Total Reach%**: Total Reach ÷ TA Population (will show "-" if TA Population is empty)
- **Total Frequency**: Sum of all impressions ÷ Total Reach
- **CPM**: Budget ÷ (Sum of impressions ÷ 1000)
- **Impressions**: Sum of Awareness + Consideration + Purchase impressions
- **Budget**: Sum of Awareness + Consideration + Purchase budgets

### Data Filtering
- **PLANNED data**: Filter by `Source_Type == 'PLANNED'`
- **ACTUALS data**: Filter by `Source_Type == 'DELIVERED MEDIA'` or `Source_Type == 'DELIVERED R&F'`
- **Platform**: Filter by `PLATFORM` column ('DV360', 'Meta', 'TikTok')
- **Objective**: Filter by `CEJ_OBJECTIVES` column ('Awareness', 'Consideration', 'Purchase')
- **Market**: Filter by `MARKET` column

## Key Implementation Points
1. **Merged Cells**: Only rows 16-17 have merged cells in Campaign Level
2. **Dynamic Markets**: Number and order of markets varies by campaign
3. **Column Pattern**: C:D for Total, then E:F, G:H, I:J, K:L, M:N for up to 5 markets
4. **Planned/Actuals Split**: Starts from row 18 for Campaign Level, row 24 header onwards for sections
5. **Empty Data**: Leave cells empty if no data available (no N/A unless specified)