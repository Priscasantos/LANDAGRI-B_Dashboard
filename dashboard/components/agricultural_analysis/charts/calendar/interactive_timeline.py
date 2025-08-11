"""
Interactive Timeline Chart
==========================

Creates an interactive timeline visualization showing agricultural activities
across crops, states, and months with connected lines and enhanced visual design.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import streamlit as st
import numpy as np


def create_interactive_timeline(filtered_data: dict) -> None:
    """
    Create interactive timeline of agricultural activities with connected lines and enhanced visuals.
    
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
        
        # Enhanced activity detection
        def detect_activities(activity_code):
            """
            Detect planting and harvesting activities from various code formats.
            
            Args:
                activity_code: String containing activity codes
                
            Returns:
                list: List of detected activities
            """
            if not activity_code or not activity_code.strip():
                return []
            
            activity_code = activity_code.upper().strip()
            activities = []
            
            # Check for combined planting/harvesting first (PH, P/H, etc.)
            if ('PH' in activity_code or 'P/H' in activity_code or 
                'H/P' in activity_code or 'P AND H' in activity_code or
                'H AND P' in activity_code):
                return ['Planting', 'Harvesting']
            
            # Check for planting indicators
            if any(indicator in activity_code for indicator in ['P', 'PLANT', 'SOWING', 'SEED']):
                activities.append('Planting')
            
            # Check for harvesting indicators  
            if any(indicator in activity_code for indicator in ['H', 'HARVEST', 'COLHEITA', 'COLLECT']):
                activities.append('Harvesting')
            
            return activities
        
        for crop, crop_states in crop_calendar.items():
            for state_entry in crop_states:
                state_name = state_entry.get('state_name', '')
                calendar_entry = state_entry.get('calendar', {})
                
                for month_full, activity in calendar_entry.items():
                    # Map full month name to abbreviated
                    month = month_mapping.get(month_full, month_full)
                    
                    if month in months and activity and activity.strip():
                        activity_types = detect_activities(activity)
                        
                        for act_type in activity_types:
                            timeline_data.append({
                                'Crop': crop,
                                'State': state_name,
                                'Month': month,
                                'Activity': act_type,
                                'Month_Num': months.index(month) + 1,
                                'Activity_ID': f"{crop}_{state_name}_{month}_{act_type}",
                                'Original_Code': activity
                            })

        if timeline_data:
            df_timeline = pd.DataFrame(timeline_data)
            
            # Create enhanced visualization with subplots
            fig = make_subplots(
                rows=1, cols=1,
                subplot_titles=["Interactive Agricultural Activity Timeline"],
                specs=[[{"secondary_y": False}]]
            )
            
            # Color schemes for activities
            activity_colors = {
                'Planting': '#10b981',    # Green
                'Harvesting': '#f59e0b'   # Orange/Yellow
            }
            
            # Group data by activity type for simplified legend
            activity_groups = {}
            for activity in ['Planting', 'Harvesting']:
                activity_data = df_timeline[df_timeline['Activity'] == activity]
                if len(activity_data) > 0:
                    activity_groups[activity] = activity_data
            
            # Create traces for each activity type (simplified legend)
            for activity, activity_data in activity_groups.items():
                # Group by crop-state combination for line connections
                combinations = activity_data.groupby(['Crop', 'State'])
                
                for (crop, state), subset in combinations:
                    # Sort by month for proper line connection
                    subset = subset.sort_values('Month_Num')
                    
                    # Create y-position based on crop index with slight offset for state
                    crops = df_timeline['Crop'].unique()
                    base_y = list(crops).index(crop)
                    
                    # Add slight vertical offset for different states of same crop
                    states_for_crop = df_timeline[df_timeline['Crop'] == crop]['State'].unique()
                    state_offset = list(states_for_crop).index(state) * 0.1 - (len(states_for_crop) - 1) * 0.05
                    y_pos = base_y + state_offset
                    
                    # Determine if this should show in legend (only first trace per activity)
                    show_legend = (crop == crops[0] and state == states_for_crop[0] and 
                                 activity in activity_groups and 
                                 (crop, state) == list(combinations.groups.keys())[0])
                    
                    # Add connected line trace
                    fig.add_trace(
                        go.Scatter(
                            x=subset['Month_Num'],
                            y=[y_pos] * len(subset),
                            mode='lines+markers',
                            name=f"{activity}",  # Simplified name for legend
                            legendgroup=activity,  # Group by activity type
                            line=dict(
                                color=activity_colors[activity],
                                width=2.5,
                                dash='solid' if activity == 'Planting' else 'dot'
                            ),
                            marker=dict(
                                size=10,
                                color=activity_colors[activity],
                                symbol='circle' if activity == 'Planting' else 'diamond',
                                line=dict(width=2, color='white')
                            ),
                            hovertemplate=(
                                f"<b>{crop}</b><br>"
                                f"State: {state}<br>"
                                f"Activity: {activity}<br>"
                                f"Month: %{{customdata[0]}}<br>"
                                f"Code: %{{customdata[1]}}<extra></extra>"
                            ),
                            customdata=list(zip(subset['Month'], subset['Original_Code'])),
                            showlegend=show_legend  # Only show legend for representative traces
                        )
                    )
            
            # Customize layout
            fig.update_layout(
                title={
                    'text': "Interactive Agricultural Activity Timeline",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'color': '#2c3e50'}
                },
                xaxis=dict(
                    title="Month",
                    tickmode='array',
                    tickvals=list(range(1, 13)),
                    ticktext=months,
                    showgrid=True,
                    gridcolor='lightgray',
                    gridwidth=1,
                    range=[0.5, 12.5]
                ),
                yaxis=dict(
                    title="Crops",
                    tickmode='array',
                    tickvals=list(range(len(df_timeline['Crop'].unique()))),
                    ticktext=list(df_timeline['Crop'].unique()),
                    showgrid=True,
                    gridcolor='lightgray',
                    gridwidth=1
                ),
                height=max(600, len(df_timeline['Crop'].unique()) * 60),
                hovermode='closest',
                legend=dict(
                    orientation="h",  # Horizontal legend
                    yanchor="top",
                    y=-0.1,  # Position below the chart
                    xanchor="center",
                    x=0.5,
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor="gray",
                    borderwidth=1,
                    font=dict(size=12)
                ),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            # Add annotations for activity types
            fig.add_annotation(
                text="Legend: 🌱 Planting (Green solid lines, circles) | 🌾 Harvesting (Orange dotted lines, diamonds)",
                xref="paper", yref="paper",
                x=0.5, y=-0.15,
                xanchor="center",
                showarrow=False,
                font=dict(size=11, color="#2c3e50"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="lightgray",
                borderwidth=1
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display summary statistics
            st.markdown("### Activity Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_activities = len(df_timeline)
                st.metric("Total Activities", total_activities)
            
            with col2:
                planting_count = len(df_timeline[df_timeline['Activity'] == 'Planting'])
                st.metric("Planting Activities", planting_count)
            
            with col3:
                harvesting_count = len(df_timeline[df_timeline['Activity'] == 'Harvesting'])
                st.metric("Harvesting Activities", harvesting_count)
                
        else:
            st.warning("No timeline data available for the selected filters.")
            
    except Exception as e:
        st.error(f"Error creating timeline: {e}")
        st.exception(e)  # Show detailed error for debugging
