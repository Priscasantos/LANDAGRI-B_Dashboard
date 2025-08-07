#!/usr/bin/env python3
"""
Import Test Script for Agricultural Analysis Components
======================================================

Quick test to verify all components can be imported successfully.
"""

import sys
from pathlib import Path

# Add the dashboard path
dashboard_path = Path(__file__).parent / "dashboard"
sys.path.insert(0, str(dashboard_path))

def test_agricultural_components():
    """Test importing all agricultural analysis components."""
    
    print("🧪 Testing Agricultural Analysis Component Imports...")
    print("=" * 60)
    
    # Test 1: Agricultural Loader
    try:
        from components.agricultural_analysis.agricultural_loader import (
            load_conab_detailed_data,
            load_conab_crop_calendar,
            validate_conab_data_quality
        )
        print("✅ Agricultural Loader: SUCCESS")
    except ImportError as e:
        print(f"❌ Agricultural Loader: FAILED - {e}")
    
    # Test 2: Agricultural Overview
    try:
        from components.agricultural_analysis.overview.agricultural_overview import render_agricultural_overview
        print("✅ Agricultural Overview: SUCCESS")
    except ImportError as e:
        print(f"❌ Agricultural Overview: FAILED - {e}")
    
    # Test 3: Crop Availability
    try:
        from components.agricultural_analysis.crop_availability import render_crop_availability
        print("✅ Crop Availability: SUCCESS")
    except ImportError as e:
        print(f"❌ Crop Availability: FAILED - {e}")
    
    # Test 4: Agricultural Calendar
    try:
        from components.agricultural_analysis.agricultural_calendar import run as run_calendar
        print("✅ Agricultural Calendar: SUCCESS")
    except ImportError as e:
        print(f"❌ Agricultural Calendar: FAILED - {e}")
    
    # Test 5: CONAB Analysis
    try:
        from components.agricultural_analysis.conab_analysis import run as run_conab
        print("✅ CONAB Analysis: SUCCESS")
    except ImportError as e:
        print(f"❌ CONAB Analysis: FAILED - {e}")
    
    # Test 6: Main Agricultural Analysis (the one that was failing)
    try:
        from components.agricultural_analysis import (
            render_agricultural_overview,
            render_crop_availability,
            render_agricultural_calendar,
            render_conab_analysis
        )
        print("✅ Main Agricultural Analysis Module: SUCCESS")
    except ImportError as e:
        print(f"❌ Main Agricultural Analysis Module: FAILED - {e}")
    
    print("=" * 60)
    print("🎉 Import testing completed!")

if __name__ == "__main__":
    test_agricultural_components()
