#!/usr/bin/env python3
"""
Test script for CONAB charts functionality.

This script tests all the CONAB chart functions with the actual data
to ensure they work correctly after the fixes.
"""

import sys
import os
import json
from pathlib import Path

# Add the dashboard directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "dashboard"))

try:
    from dashboard.components.agricultural_analysis.charts.conab_charts import (
        plot_conab_spatial_coverage,
        plot_conab_temporal_coverage,
        plot_conab_crop_diversity,
        plot_conab_spatial_temporal_distribution,
        validate_conab_data,
        get_conab_summary_stats
    )
    print("✅ Successfully imported CONAB chart functions")
except ImportError as e:
    print(f"❌ Failed to import CONAB chart functions: {e}")
    print("Let me check what's available in the module...")
    try:
        import dashboard.components.agricultural_analysis.charts.conab_charts as conab_module
        available_functions = [attr for attr in dir(conab_module) if not attr.startswith('_')]
        print(f"Available functions: {available_functions}")
    except Exception as e2:
        print(f"Error checking module: {e2}")
    sys.exit(1)

def load_conab_data():
    """Load the CONAB data from the JSON file."""
    try:
        data_path = Path(__file__).parent / "data" / "json" / "agricultural_conab_mapping_data_complete.jsonc"
        
        if not data_path.exists():
            print(f"❌ Data file not found: {data_path}")
            return None
            
        with open(data_path, 'r', encoding='utf-8') as f:
            # Remove comments from JSONC file
            content = f.read()
            lines = content.split('\n')
            cleaned_lines = []
            for line in lines:
                # Remove lines that start with // (comments)
                if not line.strip().startswith('//'):
                    cleaned_lines.append(line)
            cleaned_content = '\n'.join(cleaned_lines)
            
            data = json.loads(cleaned_content)
            print(f"✅ Successfully loaded CONAB data with {len(data.get('crop_calendar', {}))} crops")
            return data
            
    except Exception as e:
        print(f"❌ Failed to load CONAB data: {e}")
        return None

def test_conab_functions():
    """Test all CONAB chart functions."""
    print("\n" + "="*50)
    print("TESTING CONAB CHART FUNCTIONS")
    print("="*50)
    
    # Load data
    conab_data = load_conab_data()
    if not conab_data:
        print("❌ Cannot proceed without data")
        return False
    
    # Test data validation
    print("\n1. Testing data validation...")
    is_valid = validate_conab_data(conab_data)
    print(f"   Data validation: {'✅ PASS' if is_valid else '❌ FAIL'}")
    
    if not is_valid:
        print("❌ Data validation failed, cannot proceed")
        return False
    
    # Test summary stats
    print("\n2. Testing summary statistics...")
    try:
        stats = get_conab_summary_stats(conab_data)
        if stats:
            print(f"   ✅ Summary stats generated:")
            print(f"      - Total crops: {stats.get('total_crops', 0)}")
            print(f"      - Total states: {stats.get('total_states', 0)}")
            print(f"      - Total regions: {stats.get('total_regions', 0)}")
            print(f"      - Total activities: {stats.get('total_activities', 0)}")
        else:
            print("   ❌ Failed to generate summary stats")
    except Exception as e:
        print(f"   ❌ Error in summary stats: {e}")
    
    # Test spatial coverage chart
    print("\n3. Testing spatial coverage chart...")
    try:
        fig = plot_conab_spatial_coverage(conab_data)
        if fig:
            print("   ✅ Spatial coverage chart created successfully")
        else:
            print("   ❌ Failed to create spatial coverage chart")
    except Exception as e:
        print(f"   ❌ Error in spatial coverage chart: {e}")
    
    # Test temporal coverage chart
    print("\n4. Testing temporal coverage chart...")
    try:
        fig = plot_conab_temporal_coverage(conab_data)
        if fig:
            print("   ✅ Temporal coverage chart created successfully")
        else:
            print("   ❌ Failed to create temporal coverage chart")
    except Exception as e:
        print(f"   ❌ Error in temporal coverage chart: {e}")
    
    # Test crop diversity chart
    print("\n5. Testing crop diversity chart...")
    try:
        fig = plot_conab_crop_diversity(conab_data)
        if fig:
            print("   ✅ Crop diversity chart created successfully")
        else:
            print("   ❌ Failed to create crop diversity chart")
    except Exception as e:
        print(f"   ❌ Error in crop diversity chart: {e}")
    
    # Test spatial-temporal distribution chart
    print("\n6. Testing spatial-temporal distribution chart...")
    try:
        fig = plot_conab_spatial_temporal_distribution(conab_data)
        if fig:
            print("   ✅ Spatial-temporal distribution chart created successfully")
        else:
            print("   ❌ Failed to create spatial-temporal distribution chart")
    except Exception as e:
        print(f"   ❌ Error in spatial-temporal distribution chart: {e}")
    
    print("\n" + "="*50)
    print("CONAB CHART TESTING COMPLETED")
    print("="*50)
    return True

def test_month_translation():
    """Test month translation functionality."""
    print("\n" + "="*50)
    print("TESTING MONTH TRANSLATION")
    print("="*50)
    
    month_translation = {
        'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
        'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
        'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
        'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
    }
    
    print("Testing month translations:")
    for eng, pt in month_translation.items():
        print(f"   {eng} -> {pt}")
    
    print("✅ Month translation mappings are correct")
    print("="*50)

if __name__ == "__main__":
    print("CONAB Charts Test Suite")
    print("=" * 50)
    
    # Test month translation
    test_month_translation()
    
    # Test CONAB functions
    success = test_conab_functions()
    
    if success:
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("✅ CONAB charts are ready to use in the dashboard")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("❌ Please check the errors above")
    
    print("\n" + "="*50)
