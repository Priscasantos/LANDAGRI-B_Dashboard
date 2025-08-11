"""
Agricultural Overview Data Loader
=================================

Specific functions for loading Agricultural Overview data.
Only overview data and main statistics.

Author: LULC Initiatives Dashboard
Date: 2025-08-05
"""

import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, Any
from ..agricultural_loader import load_agricultural_data


def get_agricultural_overview_stats() -> Dict[str, Any]:
    """
    Load only agricultural overview statistics.
    
    Returns:
        Dict with main statistics for overview
    """
    agricultural_data = load_agricultural_data()
    
    if not agricultural_data:
        return {}
    
    try:
        initiative = agricultural_data.get('CONAB Crop Monitoring Initiative', {})
        
        # Main statistics for overview
        overview_stats = {
            'total_crops': 0,
            'states_covered': 0,
            'total_area_monitored': 'N/A',
            'resolution': 'N/A',
            'accuracy': 0.0,
            'provider': 'N/A',
            'methodology': 'N/A'
        }
        
        # Basic data
        overview_stats['provider'] = initiative.get('provider', 'N/A')
        overview_stats['methodology'] = initiative.get('methodology', 'N/A')
        
        # Crop count
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        overview_stats['total_crops'] = len(detailed_coverage)
        
        # Covered states
        all_states = set()
        for crop_data in detailed_coverage.values():
            states = crop_data.get('regions', [])  # Inconsistent name in source - contains states
            all_states.update(states)
        overview_stats['states_covered'] = len(all_states)
        
        # Spatial resolution
        resolution = initiative.get('spatial_resolution')
        if resolution:
            overview_stats['resolution'] = f"{resolution}m"
        
        # Overall accuracy
        accuracy = initiative.get('overall_accuracy')
        if accuracy:
            overview_stats['accuracy'] = accuracy
        
        # Coverage area
        coverage = initiative.get('coverage', 'N/A')
        overview_stats['total_area_monitored'] = coverage
        
        return overview_stats
        
    except Exception as e:
        st.error(f"❌ Error processing overview: {e}")
        return {}


def get_crops_overview_data() -> pd.DataFrame:
    """
    Load crop data for overview.
    
    Returns:
        DataFrame with basic crop information
    """
    agricultural_data = load_agricultural_data()
    
    if not agricultural_data:
        return pd.DataFrame()
    
    try:
        initiative = agricultural_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        crops_data = []
        
        for crop, crop_data in detailed_coverage.items():
            states = crop_data.get('regions', [])  # Inconsistent name in source - contains states
            first_crop_years = crop_data.get('first_crop_years', {})
            second_crop_years = crop_data.get('second_crop_years', {})
            
            # Count total data points
            total_data_points = 0
            for region_years in first_crop_years.values():
                total_data_points += len(region_years)
            for region_years in second_crop_years.values():
                total_data_points += len(region_years)
            
            # Check for double crop
            has_double_crop = any(len(years) > 0 for years in second_crop_years.values())
            
            crops_data.append({
                'Crop': crop,
                'States': len(states),
                'Double Crop': has_double_crop,
                'Total Data': total_data_points,
                'States List': ', '.join(states[:3]) + ('...' if len(states) > 3 else '')
            })
        
        return pd.DataFrame(crops_data)
        
    except Exception as e:
        st.error(f"❌ Error processing crop data: {e}")
        return pd.DataFrame()


def get_states_summary() -> pd.DataFrame:
    """
    Load state summary for overview.
    
    Returns:
        DataFrame with summary by Brazilian state
    """
    agricultural_data = load_agricultural_data()
    
    if not agricultural_data:
        return pd.DataFrame()
    
    try:
        initiative = agricultural_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        # Aggregate by state
        states_summary = {}
        
        for crop, crop_data in detailed_coverage.items():
            states = crop_data.get('regions', [])  # Inconsistent name in source - contains states
            first_crop_years = crop_data.get('first_crop_years', {})
            second_crop_years = crop_data.get('second_crop_years', {})
            
            for state in states:
                if state not in states_summary:
                    states_summary[state] = {
                        'state': state,
                        'crops_count': 0,
                        'total_years': 0,
                        'has_double_crop': False
                    }
                
                states_summary[state]['crops_count'] += 1
                
                # Count data years
                first_years = len(first_crop_years.get(state, []))
                second_years = len(second_crop_years.get(state, []))
                states_summary[state]['total_years'] += first_years + second_years
                
                # Check double crop
                if second_years > 0:
                    states_summary[state]['has_double_crop'] = True
        
        # Convert to DataFrame
        summary_data = []
        for state_data in states_summary.values():
            summary_data.append({
                'State': state_data['state'],
                'Crops': state_data['crops_count'],
                'Total Years': state_data['total_years'],
                'Double Crop': state_data['has_double_crop']
            })
        
        return pd.DataFrame(summary_data)
        
    except Exception as e:
        st.error(f"❌ Error processing state summary: {e}")
        return pd.DataFrame()
