#!/usr/bin/env python3
"""
Robust Market Mapping Module
Handles all edge cases: planned-only, delivered-only, and unmatched campaigns
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

class RobustMarketMapper:
    """Ensures every campaign gets mapped with proper fallbacks."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize with configuration."""
        self.config = self._load_config(config_path)
        self.em_dash = "—"  # Standard em-dash for missing values
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration with edge case handling rules."""
        try:
            import json
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            # Default configuration if file not found
            return {
                "mapping_config": {
                    "edge_case_handling": {
                        "planned_only": {
                            "actuals_display": "—",
                            "include_in_output": True
                        },
                        "delivered_only": {
                            "planned_display": "—",
                            "include_in_output": True
                        },
                        "unmatched": {
                            "display_value": "—",
                            "log_warning": True
                        }
                    }
                }
            }
    
    def _is_rf_data(self, df: pd.DataFrame) -> pd.Series:
        """Identify R&F data rows that should be preserved as-is."""
        if df.empty or 'PLATFORM' not in df.columns:
            return pd.Series([], dtype=bool)
        return df['PLATFORM'].astype(str).str.contains(r'(Reach|Freq)', na=False, regex=True)
    
    def _clean_string_dashes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert string '-' values to NaN in numeric columns."""
        if df.empty:
            return df
            
        df = df.copy()
        numeric_columns = [
            'BUDGET_LOCAL', 'PLATFORM_BUDGET_LOCAL', 'PLATFORM_FEE_LOCAL',
            'IMPRESSIONS', 'CLICKS_ACTIONS', 'VIDEO_VIEWS', 'UNIQUES_REACH',
            'FREQUENCY', 'PERCENT_UNIQUES', 'CPM_LOCAL', 'CPC_LOCAL', 'CPV_LOCAL',
            'CTR_PERCENT', 'VTR_PERCENT', 'TA_SIZE', 'WEEKS'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                # Replace string '-' with NaN, but preserve actual numeric values
                df[col] = df[col].replace('-', np.nan)
                # Try to convert to numeric, keeping NaN for non-convertible values
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def map_campaigns(self, planned_df: pd.DataFrame, delivered_df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform robust market mapping ensuring every campaign is included.
        R&F data is preserved as-is without matching.
        
        Args:
            planned_df: DataFrame with planned campaign data
            delivered_df: DataFrame with delivered campaign data
            
        Returns:
            DataFrame with all campaigns mapped, including edge cases
        """
        logger.info(f"Starting robust market mapping: {len(planned_df)} planned, {len(delivered_df)} delivered")
        
        # Clean up string "-" values to NaN before processing
        if not delivered_df.empty:
            delivered_df = self._clean_string_dashes(delivered_df)
        if not planned_df.empty:
            planned_df = self._clean_string_dashes(planned_df)
        
        # Separate R&F data from delivered data for special handling
        rf_data = pd.DataFrame()
        delivered_media = delivered_df.copy() if not delivered_df.empty else pd.DataFrame()
        
        if not delivered_df.empty:
            rf_mask = self._is_rf_data(delivered_df)
            if rf_mask.any():
                rf_data = delivered_df[rf_mask].copy()
                delivered_media = delivered_df[~rf_mask].copy()
                logger.info(f"Separated {len(rf_data)} R&F rows from {len(delivered_media)} media rows")
        
        # Create composite keys for matching (excluding R&F data)
        if not planned_df.empty:
            planned_df = planned_df.copy()
            planned_df['mapping_key'] = (
                planned_df['CAMPAIGN'].astype(str) + '|' + 
                planned_df['MARKET'].astype(str) + '|' + 
                planned_df['PLATFORM'].astype(str)
            )
        
        if not delivered_media.empty:
            delivered_media['mapping_key'] = (
                delivered_media['CAMPAIGN'].astype(str) + '|' + 
                delivered_media['MARKET'].astype(str) + '|' + 
                delivered_media['PLATFORM'].astype(str)
            )
        
        # Perform full outer join (excluding R&F data)
        if not planned_df.empty and not delivered_media.empty:
            combined_df = pd.merge(
                planned_df,
                delivered_media,
                on='mapping_key',
                how='outer',
                suffixes=('_planned', '_delivered'),
                indicator=True
            )
        elif not planned_df.empty:
            # Only planned data
            combined_df = planned_df.copy()
            combined_df['_merge'] = 'left_only'
        elif not delivered_media.empty:
            # Only delivered media data
            combined_df = delivered_media.copy()
            combined_df['_merge'] = 'right_only'
        else:
            # Both empty (only R&F data case)
            combined_df = pd.DataFrame()
        
        # Handle missing values based on merge indicator
        if not combined_df.empty:
            combined_df = self._handle_edge_cases(combined_df)
            combined_df = self._prepare_output(combined_df)
        
        # Add R&F data back (preserved as-is)
        if not rf_data.empty:
            logger.info(f"Adding {len(rf_data)} R&F rows back to combined data")
            if combined_df.empty:
                combined_df = rf_data.copy()
            else:
                # Ensure both DataFrames have the same columns
                combined_cols = set(combined_df.columns)
                rf_cols = set(rf_data.columns)
                
                # Add missing columns to R&F data
                for col in combined_cols - rf_cols:
                    rf_data[col] = np.nan
                
                # Add missing columns to combined data
                for col in rf_cols - combined_cols:
                    combined_df[col] = np.nan
                
                # Concatenate
                combined_df = pd.concat([combined_df, rf_data], ignore_index=True)
        
        # Log summary
        self._log_mapping_summary(combined_df)
        
        return combined_df
    
    def _handle_edge_cases(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle planned-only, delivered-only, and unmatched campaigns."""
        edge_config = self.config.get('mapping_config', {}).get('edge_case_handling', {})
        
        # Process based on merge indicator
        if '_merge' in df.columns:
            # Left only (planned only)
            planned_only_mask = df['_merge'] == 'left_only'
            if planned_only_mask.any():
                logger.info(f"Found {planned_only_mask.sum()} planned-only campaigns")
                if edge_config.get('planned_only', {}).get('include_in_output', True):
                    # Set delivered columns to em-dash
                    delivered_cols = [col for col in df.columns if col.endswith('_delivered')]
                    for col in delivered_cols:
                        df.loc[planned_only_mask, col] = self.em_dash
            
            # Right only (delivered only)
            delivered_only_mask = df['_merge'] == 'right_only'
            if delivered_only_mask.any():
                logger.info(f"Found {delivered_only_mask.sum()} delivered-only campaigns")
                if edge_config.get('delivered_only', {}).get('include_in_output', True):
                    # Set planned columns to em-dash
                    planned_cols = [col for col in df.columns if col.endswith('_planned')]
                    for col in planned_cols:
                        df.loc[delivered_only_mask, col] = self.em_dash
            
            # Both (matched)
            matched_mask = df['_merge'] == 'both'
            logger.info(f"Found {matched_mask.sum()} matched campaigns")
        
        return df
    
    def _prepare_output(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare final output with consolidated columns."""
        # Key columns to consolidate
        key_columns = ['CAMPAIGN', 'MARKET', 'PLATFORM']
        
        # Consolidate key columns (take non-null value)
        for col in key_columns:
            planned_col = f'{col}_planned'
            delivered_col = f'{col}_delivered'
            
            if planned_col in df.columns and delivered_col in df.columns:
                df[col] = df[planned_col].fillna(df[delivered_col])
            elif planned_col in df.columns:
                df[col] = df[planned_col]
            elif delivered_col in df.columns:
                df[col] = df[delivered_col]
        
        # Handle numeric columns with proper display
        numeric_columns = [
            'BUDGET_LOCAL', 'PLATFORM_BUDGET_LOCAL', 'PLATFORM_FEE_LOCAL',
            'IMPRESSIONS', 'CLICKS_ACTIONS', 'VIDEO_VIEWS', 'UNIQUES_REACH',
            'FREQUENCY', 'PERCENT_UNIQUES', 'CPM_LOCAL', 'CPC_LOCAL', 'CPV_LOCAL',
            'CTR_PERCENT', 'VTR_PERCENT', 'TA_SIZE', 'WEEKS'
        ]
        
        for base_col in numeric_columns:
            # Create consolidated columns with planned/delivered suffixes
            planned_col = f'{base_col}_planned'
            delivered_col = f'{base_col}_delivered'
            
            # Ensure columns exist with proper values
            if planned_col in df.columns:
                # Convert em-dash back to NaN for calculations
                df[planned_col] = df[planned_col].replace(self.em_dash, np.nan)
            
            if delivered_col in df.columns:
                # Convert em-dash back to NaN for calculations
                df[delivered_col] = df[delivered_col].replace(self.em_dash, np.nan)
        
        # Add match status column
        if '_merge' in df.columns:
            df['match_status'] = df['_merge'].map({
                'left_only': 'planned_only',
                'right_only': 'delivered_only',
                'both': 'matched'
            })
        
        # Drop temporary columns
        columns_to_drop = ['mapping_key', '_merge']
        df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
        
        return df
    
    def _log_mapping_summary(self, df: pd.DataFrame):
        """Log summary of mapping results."""
        if 'match_status' in df.columns:
            status_counts = df['match_status'].value_counts()
            logger.info("\n=== Market Mapping Summary ===")
            logger.info(f"Total campaigns: {len(df)}")
            for status, count in status_counts.items():
                logger.info(f"  {status}: {count} ({count/len(df)*100:.1f}%)")
            logger.info("==============================\n")


def test_robust_mapping():
    """Test the robust market mapping with edge cases."""
    mapper = RobustMarketMapper()
    
    # Test Case 1: Planned-only campaign
    print("\nTest 1: Planned-only campaign")
    planned = pd.DataFrame({
        'CAMPAIGN': ['Campaign A'],
        'MARKET': ['UAE'],
        'PLATFORM': ['DV360'],
        'BUDGET': [1000]
    })
    delivered = pd.DataFrame()  # Empty
    
    result = mapper.map_campaigns(planned, delivered)
    print(f"Result shape: {result.shape}")
    print(f"Match status: {result.get('match_status', ['N/A'])[0] if len(result) > 0 else 'No data'}")
    assert len(result) == 1, "Should have 1 row"
    
    # Test Case 2: Delivered-only campaign
    print("\nTest 2: Delivered-only campaign")
    planned = pd.DataFrame()  # Empty
    delivered = pd.DataFrame({
        'CAMPAIGN': ['Campaign B'],
        'MARKET': ['JOR'],
        'PLATFORM': ['META'],
        'SPEND_USD': [500]
    })
    
    result = mapper.map_campaigns(planned, delivered)
    print(f"Result shape: {result.shape}")
    print(f"Match status: {result.get('match_status', ['N/A'])[0] if len(result) > 0 else 'No data'}")
    assert len(result) == 1, "Should have 1 row"
    
    # Test Case 3: Mismatched markets
    print("\nTest 3: Mismatched markets (different campaigns)")
    planned = pd.DataFrame({
        'CAMPAIGN': ['Campaign C'],
        'MARKET': ['UAE'],
        'PLATFORM': ['DV360'],
        'BUDGET': [1000]
    })
    delivered = pd.DataFrame({
        'CAMPAIGN': ['Campaign C'],
        'MARKET': ['OMN'],
        'PLATFORM': ['DV360'],
        'SPEND_USD': [500]
    })
    
    result = mapper.map_campaigns(planned, delivered)
    print(f"Result shape: {result.shape}")
    print(f"Unique match statuses: {result['match_status'].unique() if 'match_status' in result else 'No status'}")
    assert len(result) == 2, "Should have 2 rows (one for each market)"
    
    # Test Case 4: Perfect match
    print("\nTest 4: Perfect match")
    planned = pd.DataFrame({
        'CAMPAIGN': ['Campaign D'],
        'MARKET': ['QAT'],
        'PLATFORM': ['TIKTOK'],
        'BUDGET': [2000]
    })
    delivered = pd.DataFrame({
        'CAMPAIGN': ['Campaign D'],
        'MARKET': ['QAT'],
        'PLATFORM': ['TIKTOK'],
        'SPEND_USD': [1800]
    })
    
    result = mapper.map_campaigns(planned, delivered)
    print(f"Result shape: {result.shape}")
    print(f"Match status: {result.get('match_status', ['N/A'])[0] if len(result) > 0 else 'No data'}")
    assert len(result) == 1, "Should have 1 row"
    assert result['match_status'][0] == 'matched', "Should be matched"
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    # Run tests
    test_robust_mapping()