"""
Enhanced Calendar Heatmap Chart
===============================

Creates an enhanced heatmap visualization of agricultural calendar data
with activity differentiation and detailed annotations.
"""

import pandas as pd
import plotly.express as px
import streamlit as st


def create_enhanced_calendar_heatmap(filtered_data: dict) -> None:
    """
    Create enhanced heatmap of agricultural calendar with activity details.
    
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
        
        if not crop_calendar:
            st.info("No calendar data for enhanced heatmap")
            return

        # Month mapping from full to abbreviated names
        month_mapping = {
            'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr',
            'May': 'May', 'June': 'Jun', 'July': 'Jul', 'August': 'Aug',
            'September': 'Sep', 'October': 'Oct', 'November': 'Nov', 'December': 'Dec'
        }

        # Prepare heatmap data with differentiated activities
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        heatmap_data = []
        
        for crop, crop_states in crop_calendar.items():
            crop_activities = {month: {'planting': 0, 'harvesting': 0, 'both': 0} for month in months}
            
            for state_entry in crop_states:
                calendar_entry = state_entry.get('calendar', {})
                
                for month_full, activity in calendar_entry.items():
                    # Map full month name to abbreviated
                    month = month_mapping.get(month_full, month_full)
                    
                    if month in months and activity and activity.strip():
                        # Categorize activities
                        if 'P' in activity and 'H' in activity:
                            crop_activities[month]['both'] += 1
                        elif 'P' in activity:
                            crop_activities[month]['planting'] += 1
                        elif 'H' in activity:
                            crop_activities[month]['harvesting'] += 1
            
            # Calculate total activity score
            for month in months:
                total_score = (crop_activities[month]['planting'] +
                             crop_activities[month]['harvesting'] +
                             crop_activities[month]['both'] * 2)
                
                heatmap_data.append({
                    'Crop': crop,
                    'Month': month,
                    'Activity_Score': total_score,
                    'Planting': crop_activities[month]['planting'],
                    'Harvesting': crop_activities[month]['harvesting'],
                    'Both': crop_activities[month]['both']
                })

        if heatmap_data:
            df_heatmap = pd.DataFrame(heatmap_data)
            pivot_heatmap = df_heatmap.pivot(index='Crop', columns='Month', values='Activity_Score')
            pivot_heatmap = pivot_heatmap.fillna(0)
            
            # Reorder columns in correct month order
            pivot_heatmap = pivot_heatmap.reindex(columns=months, fill_value=0)

            fig = px.imshow(
                pivot_heatmap.values,
                x=pivot_heatmap.columns,
                y=pivot_heatmap.index,
                color_continuous_scale='Viridis',
                title="Enhanced Crop Calendar Activity Heatmap",
                labels={'x': 'Month', 'y': 'Crop', 'color': 'Activity Score'},
                aspect='auto'
            )
            
            # Add detailed annotations
            for i, _crop in enumerate(pivot_heatmap.index):
                for j, _month in enumerate(pivot_heatmap.columns):
                    value = pivot_heatmap.iloc[i, j]
                    if value > 0:
                        fig.add_annotation(
                            x=j, y=i,
                            text=str(int(value)),
                            showarrow=False,
                            font={"color": "white" if value > pivot_heatmap.values.max()/2 else "black"}
                        )
            
            fig.update_layout(height=max(500, len(pivot_heatmap.index) * 35))
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating enhanced heatmap: {e}")
