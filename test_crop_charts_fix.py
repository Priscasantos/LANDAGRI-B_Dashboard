#!/usr/bin/env python3
"""
Test Crop Distribution Charts with State Acronyms and English Regions
====================================================================
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Test the utility functions
from dashboard.components.agricultural_analysis.charts.calendar.crop_distribution_charts import (
    get_state_acronym, 
    get_brazilian_region,
    create_crop_type_distribution_chart,
    create_crop_diversity_by_region_chart,
    create_number_of_crops_per_region_chart
)

def test_state_acronym_mapping():
    """Test state name to acronym conversion"""
    print("🧪 Testing State Acronym Mapping")
    
    test_states = {
        'São Paulo': 'SP',
        'Minas Gerais': 'MG', 
        'Santa Catarina': 'SC',
        'Rio Grande do Sul': 'RS',
        'Paraná': 'PR',
        'Mato Grosso': 'MT',
        'Bahia': 'BA'
    }
    
    for state_name, expected_acronym in test_states.items():
        result = get_state_acronym(state_name)
        status = "✅" if result == expected_acronym else "❌"
        print(f"  {status} {state_name} → {result} (expected: {expected_acronym})")
    
    print()

def test_region_mapping():
    """Test acronym to region conversion"""
    print("🌍 Testing Region Mapping")
    
    test_regions = {
        'SP': 'Southeast',
        'MG': 'Southeast', 
        'SC': 'South',
        'RS': 'South',
        'PR': 'South',
        'MT': 'Central-West',
        'BA': 'Northeast',
        'AM': 'North',
        'PA': 'North'
    }
    
    for acronym, expected_region in test_regions.items():
        result = get_brazilian_region(acronym)
        status = "✅" if result == expected_region else "❌"
        print(f"  {status} {acronym} → {result} (expected: {expected_region})")
    
    print()

def test_mock_data_processing():
    """Test chart functions with mock data"""
    print("📊 Testing Chart Functions with Mock Data")
    
    # Mock calendar data structure
    mock_data = {
        'crop_calendar': {
            'Soja': {
                'São Paulo': {
                    'planting_months': ['September', 'October'],
                    'harvesting_months': ['February', 'March']
                },
                'Minas Gerais': {
                    'planting_months': ['October', 'November'],
                    'harvesting_months': ['March', 'April']
                },
                'Santa Catarina': {
                    'planting_months': ['September'],
                    'harvesting_months': ['January', 'February']
                }
            },
            'Milho': {
                'Mato Grosso': {
                    'planting_months': ['January', 'February'],
                    'harvesting_months': ['June', 'July']
                },
                'Bahia': {
                    'planting_months': ['March'],
                    'harvesting_months': ['August']
                }
            }
        }
    }
    
    try:
        # Test crop type distribution chart
        fig1 = create_crop_type_distribution_chart(mock_data)
        if fig1:
            print("  ✅ Crop type distribution chart created successfully")
        else:
            print("  ❌ Failed to create crop type distribution chart")
        
        # Test crop diversity by region chart
        fig2 = create_crop_diversity_by_region_chart(mock_data)
        if fig2:
            print("  ✅ Crop diversity by region chart created successfully")
        else:
            print("  ❌ Failed to create crop diversity by region chart")
        
        # Test number of crops per region chart
        fig3 = create_number_of_crops_per_region_chart(mock_data)
        if fig3:
            print("  ✅ Number of crops per region chart created successfully")
        else:
            print("  ❌ Failed to create number of crops per region chart")
            
    except Exception as e:
        print(f"  ❌ Error in chart functions: {e}")
    
    print()

def main():
    """Run all tests"""
    print("🧪 Testing Crop Distribution Charts - State Acronyms & English Regions")
    print("=" * 75)
    
    test_state_acronym_mapping()
    test_region_mapping()
    test_mock_data_processing()
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
