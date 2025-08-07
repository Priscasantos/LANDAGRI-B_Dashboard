"""
Interactive Timeline Chart
==========================

Creates an interactive timeline visualization showing agricultural activities
across crops, states, and months.
"""

import pandas as pd
import plotly.express as px
import streamlit as st


def create_interactive_timeline(filtered_data: dict) -> None:
    """
    Create interactive timeline of agricultural activities.
    
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
        
        timeline_data = []
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        for crop, crop_states in crop_calendar.items():
            for state_entry in crop_states:
                state_name = state_entry.get('state_name', '')
                calendar_entry = state_entry.get('calendar', {})
                
                for month_full, activity in calendar_entry.items():
                    # Map full month name to abbreviated
                    month = month_mapping.get(month_full, month_full)
                    
                    if month in months and activity and activity.strip():
                        activity_types = []
                        if 'P' in activity:
                            activity_types.append('Planting')
                        if 'H' in activity:
                            activity_types.append('Harvesting')
                        
                        for act_type in activity_types:
                            timeline_data.append({
                                'Crop': crop,
                                'State': state_name,
                                'Month': month,
                                'Activity': act_type,
                                'Month_Num': months.index(month) + 1,
                                'Activity_ID': f"{crop}_{state_name}_{month}_{act_type}"
                            })

        if timeline_data:
            df_timeline = pd.DataFrame(timeline_data)
            
            # Create gantt-style chart
            fig = px.scatter(
                df_timeline,
                x='Month_Num',
                y='Crop',
                color='Activity',
                hover_data=['State', 'Month'],
                title="Interactive Agricultural Activity Timeline",
                labels={'Month_Num': 'Month'},
                color_discrete_map={
                    'Planting': '#10b981',
                    'Harvesting': '#f59e0b'
                }
            )
            
            # Customize x-axis
            fig.update_xaxes(
                tickmode='array',
                tickvals=list(range(1, 13)),
                ticktext=months
            )
            
            fig.update_layout(height=max(500, len(df_timeline['Crop'].unique()) * 40))
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error creating timeline: {e}")
