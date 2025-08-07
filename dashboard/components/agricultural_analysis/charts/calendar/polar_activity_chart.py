"""
Polar Activity Chart
===================

Creates a polar visualization of agricultural activities throughout the year,
showing planting and harvesting patterns in a circular format.
"""

import plotly.graph_objects as go
import streamlit as st


def create_polar_activity_chart(filtered_data: dict) -> None:
    """
    Create polar chart showing activity distribution throughout the year.
    
    Parameters:
    -----------
    filtered_data : dict
        Dictionary containing filtered crop calendar data
        
    Returns:
    --------
    None
        Displays the chart directly in Streamlit
    """
    try:
        crop_calendar = filtered_data.get('crop_calendar', {})
        
        # Month mapping from full to abbreviated names
        month_mapping = {
            'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr',
            'May': 'May', 'June': 'Jun', 'July': 'Jul', 'August': 'Aug',
            'September': 'Sep', 'October': 'Oct', 'November': 'Nov', 'December': 'Dec'
        }
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        monthly_counts = {month: {'Planting': 0, 'Harvesting': 0} for month in months}
        
        for _crop, crop_states in crop_calendar.items():
            for state_entry in crop_states:
                calendar_entry = state_entry.get('calendar', {})
                
                for month_full, activity in calendar_entry.items():
                    # Map full month name to abbreviated
                    month = month_mapping.get(month_full, month_full)
                    
                    if month in months and activity and activity.strip():
                        if 'P' in activity:
                            monthly_counts[month]['Planting'] += 1
                        if 'H' in activity:
                            monthly_counts[month]['Harvesting'] += 1

        # Prepare data for polar chart
        planting_values = [monthly_counts[month]['Planting'] for month in months] + [monthly_counts[months[0]]['Planting']]
        harvesting_values = [monthly_counts[month]['Harvesting'] for month in months] + [monthly_counts[months[0]]['Harvesting']]

        # Use angles in degrees (0-360) for better control
        angles = list(range(0, 360, 30)) + [0]  # 12 months + return to start

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=planting_values,
            theta=angles,
            fill='toself',
            name='Planting Activities',
            line_color='#10b981',
            fillcolor='rgba(16, 185, 129, 0.2)'
        ))

        fig.add_trace(go.Scatterpolar(
            r=harvesting_values,
            theta=angles,
            fill='toself',
            name='Harvesting Activities',
            line_color='#f59e0b',
            fillcolor='rgba(245, 158, 11, 0.2)'
        ))

        max_value = max(planting_values + harvesting_values) if planting_values + harvesting_values else 10

        fig.update_layout(
            polar={
                "radialaxis": {"visible": True, "range": [0, max_value]},
                "angularaxis": {
                    "direction": "clockwise",
                    "period": 360,
                    "tickmode": "array",
                    "tickvals": list(range(0, 360, 30)),
                    "ticktext": months
                }
            },
            title="🌙 Polar Activity Distribution",
            height=400,
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating polar chart: {e}")
