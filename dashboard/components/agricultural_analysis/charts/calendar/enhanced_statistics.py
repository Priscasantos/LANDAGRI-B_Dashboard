"""
Enhanced Statistics Display
===========================

Creates enhanced statistical displays for agricultural calendar data
with advanced metrics and visualizations.
"""

import streamlit as st


def create_enhanced_statistics(filtered_data: dict, selected_crops: list[str], selected_states: list[str]) -> None:
    """
    Create enhanced statistics display for calendar data.
    
    Parameters:
    -----------
    filtered_data : dict
        Dictionary containing filtered crop calendar data
    selected_crops : list[str]
        List of selected crop names
    selected_states : list[str]
        List of selected state names
        
    Returns:
    --------
    None
        Displays the statistics directly in Streamlit
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        # Calculate advanced statistics
        total_combinations = len(selected_crops) * len(selected_states)
        available_combinations = sum(len(crop_states) for crop_states in crop_calendar.values())
        coverage_rate = (available_combinations / total_combinations) * 100 if total_combinations > 0 else 0
        
        # Calculate temporal diversity
        all_activities = []
        seasonal_spread = []
        
        for crop_states in crop_calendar.values():
            for state_entry in crop_states:
                calendar_entry = state_entry.get('calendar', {})
                active_months = sum(1 for activity in calendar_entry.values() if activity and activity.strip())
                all_activities.append(active_months)
                
                # Calculate seasonal spread (number of consecutive months)
                month_indices = []
                for month, activity in calendar_entry.items():
                    if activity and activity.strip():
                        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                        if month in months:
                            month_indices.append(months.index(month))
                
                if month_indices:
                    spread = max(month_indices) - min(month_indices) + 1
                    seasonal_spread.append(spread)
        
        avg_active_months = sum(all_activities) / len(all_activities) if all_activities else 0
        avg_seasonal_spread = sum(seasonal_spread) / len(seasonal_spread) if seasonal_spread else 0
        
        # Calculate concentration index
        concentration_index = (12 - avg_active_months) / 11 * 100 if avg_active_months > 0 else 0
        
        # Display advanced metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Coverage Rate",
                f"{coverage_rate:.1f}%",
                help="Percentage of crop-state combinations with available data"
            )
        
        with col2:
            st.metric(
                "Avg Active Months",
                f"{avg_active_months:.1f}",
                help="Average number of months with agricultural activity"
            )
        
        with col3:
            st.metric(
                "Seasonal Spread",
                f"{avg_seasonal_spread:.1f}",
                help="Average seasonal span in months"
            )
        
        with col4:
            st.metric(
                "Concentration Index",
                f"{concentration_index:.1f}%",
                help="Degree of seasonal activity concentration"
            )
        
        with col5:
            st.metric(
                "Data Points",
                available_combinations,
                help="Total number of crop-state combinations available"
            )
            
    except Exception as e:
        st.error(f"Error creating enhanced statistics: {e}")
