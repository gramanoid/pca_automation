# Client-Specific Mapping Rules Guide

**Created:** 2025-05-28  
**Status:** ✅ Production Ready

## Overview

The system now supports client-specific mapping rules, allowing customization of column mappings and data transformations per client without modifying the core code.

## How It Works

### 1. Configuration File

Client rules are defined in `/config/client_mapping_rules.json`:

```json
{
  "clients": {
    "sensodyne": {
      "description": "Custom mappings for Sensodyne campaigns",
      "column_overrides": {
        "SPEND_USD": "Budget",      // Map SPEND_USD to Budget
        "IMPS": "Impressions"       // Map IMPS to Impressions
      },
      "value_transformations": {
        "MARKET": {
          "Quatar": "Qatar",        // Fix typo
          "UAE": "UAE"              // Keep as-is
        }
      }
    }
  }
}
```

### 2. Using Client Rules

#### Default Client (no special rules)
```bash
python3 main_scripts/simple_llm_mapper.py \
  --input output/COMBINED.xlsx \
  --template input/OUTPUT_TEMPLATE.xlsx \
  --output output/final_mapped.xlsx
```

#### Specific Client
```bash
export CLIENT_ID=sensodyne
python3 main_scripts/simple_llm_mapper.py \
  --input output/COMBINED.xlsx \
  --template input/OUTPUT_TEMPLATE.xlsx \
  --output output/final_mapped.xlsx
```

## Configuration Structure

### Column Overrides

Maps client-specific column names to standard template columns:

```json
"column_overrides": {
  "SPEND_USD": "Budget",           // Client uses SPEND_USD instead of BUDGET_LOCAL
  "SPEND_LOCAL": "Budget",         // Another variation
  "IMPS": "Impressions",           // Client abbreviates to IMPS
  "CLICKS": "Clicks"               // Standard mapping
}
```

### Value Transformations

Fixes client-specific data values:

```json
"value_transformations": {
  "MARKET": {
    "Quatar": "Qatar",             // Common typo
    "United Arab Emirates": "UAE", // Standardize to abbreviation
    "KSA": "Saudi Arabia"          // Expand abbreviation
  },
  "PLATFORM": {
    "Facebook": "META",            // Standardize platform names
    "Instagram": "META",
    "YouTube": "DV360"
  }
}
```

### Custom Metrics (Future Enhancement)

Define client-specific calculated metrics:

```json
"custom_metrics": {
  "engagement_rate": {
    "formula": "(CLICKS + VIDEO_VIEWS) / IMPRESSIONS * 100",
    "target_column": "Engagement%"
  }
}
```

## Global Rules

Applied to all clients unless overridden:

```json
"global_rules": {
  "typo_corrections": {
    "Quatar": "Qatar",
    "Saudia Arabia": "Saudi Arabia"
  },
  "abbreviation_expansions": {
    "IMPS": "IMPRESSIONS",
    "CLKS": "CLICKS"
  },
  "platform_standardization": {
    "FB": "META",
    "YT": "DV360"
  }
}
```

## Adding a New Client

1. Edit `/config/client_mapping_rules.json`
2. Add new client block:

```json
"new_client": {
  "description": "Description of client requirements",
  "column_overrides": {
    // Add column mappings
  },
  "value_transformations": {
    // Add value fixes
  }
}
```

3. Test with sample data:
```bash
export CLIENT_ID=new_client
python3 main_scripts/simple_llm_mapper.py --input test_data.xlsx ...
```

## Priority Order

1. **Client-specific overrides** (highest priority)
2. **Global rules**
3. **Default comprehensive mappings** (lowest priority)

## Examples

### Example 1: Financial Client
```json
"finance_corp": {
  "column_overrides": {
    "TOTAL_SPEND": "Budget",
    "TOTAL_IMPRESSIONS": "Impressions",
    "CONVERSION_RATE": "CTR%"
  },
  "value_transformations": {
    "CURRENCY": {
      "USD": "$",
      "EUR": "€"
    }
  }
}
```

### Example 2: Regional Client
```json
"mena_agency": {
  "column_overrides": {
    "SPEND_AED": "Budget",
    "SPEND_SAR": "Budget"
  },
  "value_transformations": {
    "MARKET": {
      "Emirates": "UAE",
      "Kingdom": "Saudi Arabia"
    }
  }
}
```

## Testing Client Rules

1. **Check Applied Rules:**
   Look for log message: "Applied X client-specific column overrides"

2. **Verify Mappings:**
   Check the comprehensive report for correct mappings

3. **Validate Output:**
   Ensure client-specific columns appear in the output

## Troubleshooting

### Rules Not Applied
- Check CLIENT_ID is set correctly
- Verify client exists in config file
- Check for JSON syntax errors

### Incorrect Mappings
- Client overrides take precedence
- Check for conflicting rules
- Review transformation order

### Performance
- Rules are applied once at initialization
- No performance impact during mapping
- Memory efficient for large datasets

## Best Practices

1. **Document Rules:** Add clear descriptions for each client
2. **Test Thoroughly:** Verify with sample data before production
3. **Version Control:** Track changes to client rules
4. **Keep Simple:** Only add necessary overrides
5. **Standardize:** Use consistent naming conventions