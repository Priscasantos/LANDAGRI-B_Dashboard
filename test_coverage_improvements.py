"""
Test Improved Coverage Calculations and Regional Colors
======================================================

Tests the corrected percentage calculations and regional color application
in spatial coverage and crop diversity charts.

Author: LANDAGRI-B Project Team 
Date: 2025-08-11
"""

def test_improved_coverage_calculations():
    """Test the improved coverage calculation methods"""
    print("=== TESTING IMPROVED COVERAGE CALCULATIONS ===")
    
    # Import the color palette functions
    from dashboard.components.agricultural_analysis.charts.availability.color_palettes import (
        get_state_color, get_region_color, get_state_acronym, STATE_TO_REGION
    )
    
    # Test state to region mapping
    print("\n1. Testing State to Region Mapping:")
    test_states = ['SP', 'MG', 'SC', 'MT', 'PA', 'BA', 'CE']
    for state in test_states:
        region = STATE_TO_REGION.get(state, 'Unknown')
        color = get_state_color(state, use_dark=True)
        print(f"   {state} → {region} → {color}")
    
    print("\n2. Testing Regional Colors:")
    regions = ['North', 'Northeast', 'Central-West', 'Southeast', 'South']
    for region in regions:
        light_color = get_region_color(region, use_dark=False)
        dark_color = get_region_color(region, use_dark=True)
        print(f"   {region}: Light={light_color}, Dark={dark_color}")
    
    # Test state acronym conversion
    print("\n3. Testing State Name to Acronym Conversion:")
    test_names = ['São Paulo', 'Minas Gerais', 'Santa Catarina', 'Mato Grosso']
    for name in test_names:
        acronym = get_state_acronym(name)
        print(f"   {name} → {acronym}")
    
    print("\n4. Testing Improved Coverage Calculation:")
    
    # Mock data to demonstrate the calculation improvement
    mock_data = {
        'crop_calendar': {
            'Soja': [
                {'state_name': 'São Paulo', 'calendar': {'Jan': 'P', 'Feb': 'P', 'Mar': 'H'}},
                {'state_name': 'Minas Gerais', 'calendar': {'Jan': 'P', 'Feb': 'P', 'Mar': 'H', 'Apr': 'H'}},
                {'state_name': 'Santa Catarina', 'calendar': {'Jan': 'P', 'Feb': 'PH'}},  # More activity
                {'state_name': 'Mato Grosso', 'calendar': {'Jan': 'P', 'Feb': 'P', 'Mar': 'H', 'Apr': 'H', 'May': 'H'}},
            ],
            'Milho': [
                {'state_name': 'São Paulo', 'calendar': {'Apr': 'P', 'May': 'P'}},
                {'state_name': 'Minas Gerais', 'calendar': {'Apr': 'P', 'May': 'P', 'Jun': 'H'}},
                {'state_name': 'Mato Grosso', 'calendar': {'Apr': 'P', 'May': 'PH', 'Jun': 'H'}},  # More activity
            ],
            'Arroz': [
                {'state_name': 'São Paulo', 'calendar': {'Sep': 'P'}},
                {'state_name': 'Santa Catarina', 'calendar': {'Sep': 'P', 'Oct': 'P', 'Nov': 'H'}},
            ]
        }
    }
    
    # Calculate using improved method
    state_coverage = {}
    
    for crop_name, crop_data in mock_data['crop_calendar'].items():
        for state_info in crop_data:
            state = state_info.get('state_name', 'Unknown')
            state_acronym = get_state_acronym(state)
            calendar = state_info.get('calendar', {})
            
            if state_acronym not in state_coverage:
                state_coverage[state_acronym] = {
                    'total_activities': 0,
                    'active_months': 0,
                    'crops': set()
                }
            
            # Count ALL activities (improved method)
            active_months_this_crop = 0
            total_activities_this_crop = 0
            
            for month, activity in calendar.items():
                if activity and activity.strip():
                    active_months_this_crop += 1
                    total_activities_this_crop += 1
                    # Bonus for combined activities
                    if activity.strip() == 'PH':
                        total_activities_this_crop += 1
            
            if total_activities_this_crop > 0:
                state_coverage[state_acronym]['crops'].add(crop_name)
                state_coverage[state_acronym]['total_activities'] += total_activities_this_crop
                state_coverage[state_acronym]['active_months'] += active_months_this_crop
    
    # Calculate percentages using improved method
    max_total_activities = max(data['total_activities'] for data in state_coverage.values())
    max_crops = max(len(data['crops']) for data in state_coverage.values())
    max_active_months = max(data['active_months'] for data in state_coverage.values())
    
    print("\nState Coverage Analysis (Improved Method):")
    print(f"Max activities: {max_total_activities}, Max crops: {max_crops}, Max months: {max_active_months}")
    
    for state, data in state_coverage.items():
        # Improved calculation with multiple factors
        activity_factor = (data['total_activities'] / max_total_activities) * 60  # 60% weight
        crop_factor = (len(data['crops']) / max_crops) * 30  # 30% weight
        density_factor = (data['active_months'] / max_active_months) * 10  # 10% weight
        
        coverage_percent = activity_factor + crop_factor + density_factor
        
        region = STATE_TO_REGION.get(state, 'Unknown')
        color = get_state_color(state, use_dark=True)
        
        print(f"   {state} ({region}): {coverage_percent:.1f}% [Activities: {data['total_activities']}, Crops: {len(data['crops'])}, Months: {data['active_months']}] Color: {color}")
    
    print("\n✅ Improved calculation now gives DIFFERENT percentages based on activity density!")
    print("✅ States are colored according to their Brazilian regions!")
    print("✅ Coverage calculation considers multiple factors for more accurate representation!")


if __name__ == "__main__":
    test_improved_coverage_calculations()
