"""
Summary Tables Module
=====================

Module for creating enhanced summary tables for agricultural data analysis.
"""

import pandas as pd
import streamlit as st
from typing import Dict, Any, Optional


def create_crop_summary_table(calendar_data: dict, crop: str) -> pd.DataFrame | None:
    """
    Create a summary table for a specific crop.
    
    Parameters:
    -----------
    calendar_data : dict
        Agricultural calendar data
    crop : str
        Crop name to analyze
        
    Returns:
    --------
    pd.DataFrame | None
        Summary table or None if no data
    """
    if not calendar_data or crop not in calendar_data:
        return None
    
    try:
        crop_info = calendar_data[crop]
        summary_data = []
        
        if isinstance(crop_info, dict):
            # Dict format: crop -> state -> activities
            for state, activities in crop_info.items():
                if isinstance(activities, dict):
                    total_activities = sum(len(months) if isinstance(months, list) else 0 
                                         for months in activities.values())
                    planting_months = activities.get('plantio', [])
                    harvest_months = activities.get('colheita', [])
                    
                    summary_data.append({
                        'State/Region': state,
                        'Total Activities': total_activities,
                        'Planting Months': len(planting_months) if isinstance(planting_months, list) else 0,
                        'Harvest Months': len(harvest_months) if isinstance(harvest_months, list) else 0,
                        'Activity Period': f"{min(planting_months) if planting_months else 'N/A'} - {max(harvest_months) if harvest_months else 'N/A'}"
                    })
        elif isinstance(crop_info, list):
            # List format: crop -> [state_entries]
            for entry in crop_info:
                if isinstance(entry, dict):
                    state = entry.get('estado', 'N/A')
                    activities = entry.get('atividades', {})
                    
                    total_activities = sum(len(months) if isinstance(months, list) else 0 
                                         for months in activities.values())
                    planting_months = activities.get('plantio', [])
                    harvest_months = activities.get('colheita', [])
                    
                    summary_data.append({
                        'State/Region': state,
                        'Total Activities': total_activities,
                        'Planting Months': len(planting_months) if isinstance(planting_months, list) else 0,
                        'Harvest Months': len(harvest_months) if isinstance(harvest_months, list) else 0,
                        'Activity Period': f"{min(planting_months) if planting_months else 'N/A'} - {max(harvest_months) if harvest_months else 'N/A'}"
                    })
        
        if summary_data:
            return pd.DataFrame(summary_data)
        return None
        
    except Exception as e:
        st.error(f"Error creating crop summary table: {e}")
        return None


def create_regional_summary_table(calendar_data: dict, selected_regions: list) -> pd.DataFrame | None:
    """
    Create a summary table for regional comparison.
    
    Parameters:
    -----------
    calendar_data : dict
        Agricultural calendar data
    selected_regions : list
        List of regions to compare
        
    Returns:
    --------
    pd.DataFrame | None
        Regional summary table or None if no data
    """
    if not calendar_data or not selected_regions:
        return None
    
    try:
        summary_data = []
        
        for region in selected_regions:
            region_crops = 0
            total_activities = 0
            
            for crop, crop_info in calendar_data.items():
                if isinstance(crop_info, str):
                    continue
                    
                has_region_data = False
                
                if isinstance(crop_info, dict):
                    if region in crop_info:
                        has_region_data = True
                        activities = crop_info[region]
                        if isinstance(activities, dict):
                            total_activities += sum(len(months) if isinstance(months, list) else 0 
                                                  for months in activities.values())
                elif isinstance(crop_info, list):
                    for entry in crop_info:
                        if isinstance(entry, dict) and entry.get('estado') == region:
                            has_region_data = True
                            activities = entry.get('atividades', {})
                            total_activities += sum(len(months) if isinstance(months, list) else 0 
                                                  for months in activities.values())
                
                if has_region_data:
                    region_crops += 1
            
            summary_data.append({
                'Region': region,
                'Total Crops': region_crops,
                'Total Activities': total_activities,
                'Avg Activities per Crop': round(total_activities / region_crops, 2) if region_crops > 0 else 0
            })
        
        if summary_data:
            return pd.DataFrame(summary_data)
        return None
        
    except Exception as e:
        st.error(f"Error creating regional summary table: {e}")
        return None


def create_activities_summary_table(calendar_data: dict) -> pd.DataFrame | None:
    """
    Create a summary table of activities across all crops.
    
    Parameters:
    -----------
    calendar_data : dict
        Agricultural calendar data
        
    Returns:
    --------
    pd.DataFrame | None
        Activities summary table or None if no data
    """
    if not calendar_data:
        return None
    
    try:
        activity_counts = {}
        month_activity_counts = {month: 0 for month in range(1, 13)}
        
        for crop, crop_info in calendar_data.items():
            if isinstance(crop_info, str):
                continue
                
            if isinstance(crop_info, dict):
                # Dict format: crop -> state -> activities
                for state, activities in crop_info.items():
                    if isinstance(activities, dict):
                        for activity, months in activities.items():
                            if isinstance(months, list):
                                activity_counts[activity] = activity_counts.get(activity, 0) + len(months)
                                for month in months:
                                    if 1 <= month <= 12:
                                        month_activity_counts[month] += 1
            elif isinstance(crop_info, list):
                # List format: crop -> [state_entries]
                for entry in crop_info:
                    if isinstance(entry, dict):
                        activities = entry.get('atividades', {})
                        if isinstance(activities, dict):
                            for activity, months in activities.items():
                                if isinstance(months, list):
                                    activity_counts[activity] = activity_counts.get(activity, 0) + len(months)
                                    for month in months:
                                        if 1 <= month <= 12:
                                            month_activity_counts[month] += 1
        
        # Convert to summary format
        summary_data = []
        for activity, count in activity_counts.items():
            summary_data.append({
                'Activity Type': activity.title(),
                'Total Occurrences': count,
                'Percentage': round((count / sum(activity_counts.values())) * 100, 2) if activity_counts else 0
            })
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            return df.sort_values('Total Occurrences', ascending=False)
        return None
        
    except Exception as e:
        st.error(f"Error creating activities summary table: {e}")
        return None


def format_dataframe_display(df: pd.DataFrame, title: str = "", use_container_width: bool = True) -> None:
    """
    Display a DataFrame with enhanced formatting.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to display
    title : str, optional
        Title for the table
    use_container_width : bool, optional
        Whether to use container width
    """
    if df is None or df.empty:
        st.warning("⚠️ No data available for table")
        return
    
    if title:
        st.markdown(f"##### {title}")
    
    # Enhanced styling
    st.dataframe(
        df,
        use_container_width=use_container_width,
        hide_index=True,
        column_config={
            col: st.column_config.NumberColumn(
                format="%.2f" if df[col].dtype in ['float64', 'float32'] else None
            ) if df[col].dtype in ['int64', 'int32', 'float64', 'float32'] else None
            for col in df.columns
        }
    )
    
    # Add download button
    csv_data = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name=f"{title.lower().replace(' ', '_')}_summary.csv" if title else "summary.csv",
        mime="text/csv",
        use_container_width=True
    )
