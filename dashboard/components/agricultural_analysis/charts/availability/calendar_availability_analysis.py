"""
Calendar Availability Analysis
=============================

Module for availability analysis based on agricultural calendar data.
Generates availability score charts by state and crop using CONAB data as priority.
"""

import pandas as pd
import plotly.express as px
import streamlit as st
import json
import os

# Import safe access functions
from ...agricultural_loader import (
    load_agricultural_data, 
    safe_get_data, 
    validate_data_structure
)


def render_calendar_availability_analysis(calendar_data: dict) -> None:
    """
    Render calendar availability analysis with CONAB data priority.
    
    Parameters:
    -----------
    calendar_data : dict
        Agricultural calendar data containing planting and harvest information
        
    Returns:
    --------
    None
        Renders directly in Streamlit
    """
    try:
        # Priority 1: Try to load agricultural data
        agricultural_data = load_agricultural_data()
        
        if agricultural_data and validate_data_structure(agricultural_data):
            st.info("📊 Using agricultural data as primary source for availability analysis")
            # Use agricultural data directly 
            calendar_data = agricultural_data
        
        # Safe access to calendar data
        crop_calendar = safe_get_data(calendar_data, 'crop_calendar') or {}
        states_info = safe_get_data(calendar_data, 'states') or {}
        
        if not crop_calendar:
            st.info("📊 No calendar data available for availability analysis")
            return

        # Prepare availability data
        availability_data = []
        
        for crop, crop_states in crop_calendar.items():
            # Handle different data structures
            if isinstance(crop_states, list):
                # CONAB format: list of state entries
                for state_entry in crop_states:
                    if isinstance(state_entry, dict):
                        state_code = safe_get_data(state_entry, 'state_code') or ''
                        state_name = safe_get_data(state_entry, 'state_name') or state_code
                        calendar_entry = safe_get_data(state_entry, 'calendar') or {}
                        
                        # Count months with activity
                        active_months = sum(1 for activity in calendar_entry.values() if activity and activity.strip())
                        planting_months = sum(1 for activity in calendar_entry.values() if activity and 'P' in activity)
                        harvest_months = sum(1 for activity in calendar_entry.values() if activity and 'H' in activity)
                        
                        availability_data.append({
                            'crop': crop,
                            'state': state_name,
                            'state_code': state_code,
                            'active_months': active_months,
                            'planting_months': planting_months,
                            'harvest_months': harvest_months,
                            'availability_score': active_months / 12.0  # Normalize to 0-1
                        })
            
            elif isinstance(crop_states, dict):
                # Legacy format: dictionary of states
                for state_key, state_data in crop_states.items():
                    if isinstance(state_data, dict):
                        calendar_entry = safe_get_data(state_data, 'calendar') or state_data
                        
                        # Count months with activity
                        active_months = sum(1 for activity in calendar_entry.values() if activity and str(activity).strip())
                        planting_months = sum(1 for activity in calendar_entry.values() if activity and 'P' in str(activity))
                        harvest_months = sum(1 for activity in calendar_entry.values() if activity and 'H' in str(activity))
                        
                        availability_data.append({
                            'crop': crop,
                            'state': state_key,
                            'state_code': state_key,
                            'active_months': active_months,
                            'planting_months': planting_months,
                            'harvest_months': harvest_months,
                            'availability_score': active_months / 12.0  # Normalize to 0-1
                        })

        if availability_data:
            df_availability = pd.DataFrame(availability_data)
            
            # Convert score to more intuitive percentage
            df_availability['availability_percentage'] = df_availability['availability_score'] * 100
            
            # Availability charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Average availability by state
                state_avg = df_availability.groupby('state')['availability_percentage'].mean().reset_index()
                state_avg = state_avg.sort_values('availability_percentage', ascending=False)
                
                fig_state = px.bar(
                    state_avg.head(15),
                    x='availability_percentage',
                    y='state',
                    orientation='h',
                    title="📊 Availability by State (%)",
                    labels={'availability_percentage': 'Availability (%)', 'state': 'State'}
                )
                fig_state.update_layout(xaxis=dict(range=[0, 100]))
                st.plotly_chart(fig_state, use_container_width=True, key="calendar_availability_by_state_tab")
            
            with col2:
                # Availability by crop
                crop_avg = df_availability.groupby('crop')['availability_percentage'].mean().reset_index()
                crop_avg = crop_avg.sort_values('availability_percentage', ascending=False)
                
                fig_crop = px.bar(
                    crop_avg,
                    x='crop',
                    y='availability_percentage',
                    title="🌾 Availability by Crop (%)",
                    labels={'availability_percentage': 'Availability (%)', 'crop': 'Crop'}
                )
                fig_crop.update_layout(xaxis_tickangle=45, yaxis=dict(range=[0, 100]))
                st.plotly_chart(fig_crop, use_container_width=True, key="calendar_availability_by_crop")

            # Summary table
            st.markdown("##### 📋 Availability Summary")
            summary_stats = df_availability.groupby('crop').agg({
                'state': 'count',
                'active_months': 'mean',
                'availability_score': 'mean'
            }).round(2)
            summary_stats.columns = ['States Covered', 'Active Months (Average)', 'Availability Score']
            st.dataframe(summary_stats, use_container_width=True)

    except Exception as e:
        st.error(f"Error in calendar availability analysis: {e}")
