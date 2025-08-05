#!/usr/bin/env python3
"""
Test script to verify CONAB data loading functionality.
"""

import sys
from pathlib import Path
import pandas as pd

# Add dashboard to path
sys.path.insert(0, str(Path(__file__).parent / "dashboard"))

def test_conab_loading():
    """Test CONAB data loading."""
    try:
        from agricultural_analysis import _load_conab_data
        
        print("🔄 Loading CONAB data...")
        df = _load_conab_data()
        
        print(f"✅ Success! Loaded {len(df)} records")
        print(f"📊 Columns: {list(df.columns)}")
        
        if 'State' in df.columns:
            states = df['State'].unique()
            print(f"🇧🇷 States: {sorted(states)}")
        
        if 'Crop' in df.columns:
            crops = df['Crop'].unique()
            print(f"🌾 Crops: {sorted(crops)}")
        
        if 'Region' in df.columns:
            regions = df['Region'].unique()
            print(f"🗺️ Regions: {sorted(regions)}")
        
        print("\n📋 Sample data:")
        print(df.head(3).to_string())
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_conab_loading()
    sys.exit(0 if success else 1)
