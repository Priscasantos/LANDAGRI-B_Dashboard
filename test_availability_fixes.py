#!/usr/bin/env python3
"""
Test Availability Chart Fixes - State vs Region Data
===================================================
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def test_availability_chart_fixes():
    """Test if the availability charts show correct data for states vs regions"""
    print("🧪 Testing Availability Chart Fixes")
    print("=" * 50)
    
    # Mock data structure that mimics crop calendar format
    mock_data = {
        'crop_calendar': {
            'Soja': [
                {
                    'state_name': 'São Paulo',
                    'region': 'Southeast',
                    'calendar': {
                        'January': '', 'February': 'H', 'March': 'H', 'April': '',
                        'May': '', 'June': '', 'July': '', 'August': '',
                        'September': 'P', 'October': 'P', 'November': '', 'December': ''
                    }
                },
                {
                    'state_name': 'Minas Gerais',
                    'region': 'Southeast', 
                    'calendar': {
                        'January': '', 'February': 'H', 'March': 'H', 'April': '',
                        'May': '', 'June': '', 'July': '', 'August': '',
                        'September': 'P', 'October': 'P', 'November': 'P', 'December': ''
                    }
                },
                {
                    'state_name': 'Santa Catarina',
                    'region': 'South',
                    'calendar': {
                        'January': 'H', 'February': 'H', 'March': '', 'April': '',
                        'May': '', 'June': '', 'July': '', 'August': '',
                        'September': 'P', 'October': 'P', 'November': '', 'December': ''
                    }
                }
            ],
            'Milho': [
                {
                    'state_name': 'Mato Grosso',
                    'region': 'Central-West',
                    'calendar': {
                        'January': 'P', 'February': 'P', 'March': '', 'April': '',
                        'May': '', 'June': 'H', 'July': 'H', 'August': '',
                        'September': '', 'October': '', 'November': '', 'December': ''
                    }
                }
            ]
        }
    }
    
    try:
        # Test spatial coverage functions
        from dashboard.components.agricultural_analysis.charts.availability.spatial_coverage import (
            plot_conab_spatial_coverage_by_state, 
            plot_conab_spatial_coverage_by_region,
            get_state_acronym
        )
        
        print("📍 Testing State Mapping:")
        test_states = ['São Paulo', 'Minas Gerais', 'Santa Catarina', 'Mato Grosso']
        for state in test_states:
            acronym = get_state_acronym(state)
            print(f"  {state} → {acronym}")
        print()
        
        print("📊 Testing Spatial Coverage Charts:")
        
        # Test state function
        fig_state = plot_conab_spatial_coverage_by_state(mock_data)
        if fig_state and fig_state.data:
            print("  ✅ State spatial coverage chart created successfully")
            # Check if chart uses state acronyms
            y_data = fig_state.data[0].y if fig_state.data else []
            print(f"    States shown: {list(y_data) if y_data else 'None'}")
        else:
            print("  ❌ State spatial coverage chart failed")
        
        # Test region function  
        fig_region = plot_conab_spatial_coverage_by_region(mock_data)
        if fig_region and fig_region.data:
            print("  ✅ Region spatial coverage chart created successfully")
            # Check if chart uses English regions
            y_data = fig_region.data[0].y if fig_region.data else []
            print(f"    Regions shown: {list(y_data) if y_data else 'None'}")
        else:
            print("  ❌ Region spatial coverage chart failed")
        
        print()
        
        # Test crop diversity functions
        from dashboard.components.agricultural_analysis.charts.availability.crop_diversity import (
            plot_conab_crop_diversity_by_state,
            plot_conab_crop_diversity_by_region
        )
        
        print("🌱 Testing Crop Diversity Charts:")
        
        # Test state function
        fig_crop_state = plot_conab_crop_diversity_by_state(mock_data)
        if fig_crop_state and fig_crop_state.data:
            print("  ✅ State crop diversity chart created successfully") 
            # Check data
            y_data = fig_crop_state.data[0].y if fig_crop_state.data else []
            print(f"    States shown: {list(y_data) if y_data else 'None'}")
        else:
            print("  ❌ State crop diversity chart failed")
        
        # Test region function
        fig_crop_region = plot_conab_crop_diversity_by_region(mock_data)
        if fig_crop_region and fig_crop_region.data:
            print("  ✅ Region crop diversity chart created successfully")
            # Check data
            y_data = fig_crop_region.data[0].y if fig_crop_region.data else []
            print(f"    Regions shown: {list(y_data) if y_data else 'None'}")
        else:
            print("  ❌ Region crop diversity chart failed")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("✅ Availability chart fix testing completed!")

if __name__ == "__main__":
    test_availability_chart_fixes()
