"""
Agricultural Data Loader Component
=================================

Component responsible for loading and processing detailed agricultural data,
including crop data, calendars and regional coverage.

Author: Agricultural Dashboard
Date: 2025-08-07
"""

import json
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, Any, Optional


def load_agricultural_data() -> dict[str, Any]:
    """
    Load detailed agricultural data from JSON file.
    
    Returns:
        Dict with agricultural data or empty dict if error
    """
    try:
        # Determine file path (fixed: find data folder)
        current_dir = Path(__file__).resolve().parent
        # Search for data directory starting from dashboard
        data_dir = None
        for parent in current_dir.parents:
            potential_data = parent / "data" / "json"
            if potential_data.exists():
                data_dir = potential_data
                break
        
        if data_dir is None:
            st.warning("⚠️ Data/json directory not found")
            st.info(f"📂 Searching from: {current_dir}")
            return {}
            
        agricultural_file = data_dir / "agricultural_conab_mapping_data_complete.jsonc"
        
        if not agricultural_file.exists():
            st.warning(f"⚠️ Agricultural data file not found: {agricultural_file}")
            st.info(f"📂 Data directory: {data_dir}")
            # List available files
            if data_dir.exists():
                files = list(data_dir.glob("*.json*"))
                st.info(f"📋 Available files: {[f.name for f in files]}")
            return {}
        
        # Load and process JSONC file
        with open(agricultural_file, encoding='utf-8') as f:
            content = f.read()
            
        # Remove single-line comments
        lines = []
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped.startswith('//'):
                lines.append(line)
        
        # Process JSON
        clean_content = '\n'.join(lines)
        data = json.loads(clean_content)
        
        return data
        
    except json.JSONDecodeError as e:
        st.error(f"❌ Error processing agricultural JSON: {e}")
        return {}
    except Exception as e:
        st.error(f"❌ Error loading agricultural data: {e}")
        return {}


def load_agricultural_crop_calendar() -> dict[str, Any]:
    """
    Load agricultural calendar data.
    
    Returns:
        Dict with calendar data or empty dict if error
    """
    # Use the same data as the main agricultural data
    return load_agricultural_data()


def get_conab_crop_stats(conab_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract main statistics from CONAB data.
    
    Args:
        conab_data: Raw CONAB data
        
    Returns:
        Dict with processed statistics
    """
    stats = {
        'total_crops': 0,
        'states_covered': 0,
        'regions_covered': 0,
        'temporal_span': 0,
        'resolution': 'N/A',
        'accuracy': 0.0,
        'coverage_area': 'N/A'
    }
    
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        
        if not initiative:
            return stats
        
        # Count detailed crops
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        stats['total_crops'] = len(detailed_coverage)
        
        # Count unique covered states
        all_states = set()
        for crop_data in detailed_coverage.values():
            regions = crop_data.get('regions', [])
            all_states.update(regions)
        stats['states_covered'] = len(all_states)
        
        # Regional coverage
        regional_coverage = initiative.get('regional_coverage', [])
        stats['regions_covered'] = len(regional_coverage)
        
        # Temporal span
        years = initiative.get('available_years', [])
        if years:
            stats['temporal_span'] = max(years) - min(years) + 1
        
        # Spatial resolution
        resolution = initiative.get('spatial_resolution')
        if resolution:
            stats['resolution'] = f"{resolution}m"
        
        # Overall accuracy
        accuracy = initiative.get('overall_accuracy')
        if accuracy:
            stats['accuracy'] = accuracy
        
        # Coverage area
        coverage = initiative.get('coverage', 'N/A')
        stats['coverage_area'] = coverage
        
    except Exception as e:
        st.error(f"❌ Error processing CONAB statistics: {e}")
    
    return stats


def get_crop_regional_distribution(conab_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Extract regional distribution of crops from CONAB data.
    
    Args:
        conab_data: Raw CONAB data
        
    Returns:
        DataFrame with regional distribution
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        distribution_data = []
        
        for crop, crop_data in detailed_coverage.items():
            regions = crop_data.get('regions', [])
            first_crop_years = crop_data.get('first_crop_years', {})
            second_crop_years = crop_data.get('second_crop_years', {})
            
            for region in regions:
                # Count years of available data
                first_years = len(first_crop_years.get(region, []))
                second_years = len(second_crop_years.get(region, []))
                total_years = first_years + second_years
                
                distribution_data.append({
                    'crop': crop,
                    'region': region,
                    'first_crop_years': first_years,
                    'second_crop_years': second_years,
                    'total_years': total_years,
                    'has_second_crop': second_years > 0
                })
        
        return pd.DataFrame(distribution_data)
        
    except Exception as e:
        st.error(f"❌ Error processing regional distribution: {e}")
        return pd.DataFrame()


def get_temporal_coverage_evolution(conab_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Extract temporal coverage evolution of crops.
    
    Args:
        conab_data: Raw CONAB data
        
    Returns:
        DataFrame with temporal evolution
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        available_years = initiative.get('available_years', [])
        
        # Create coverage matrix by year and crop
        evolution_data = []
        
        for year in available_years:
            year_crops = 0
            year_regions = set()
            
            for crop, crop_data in detailed_coverage.items():
                first_crop_years = crop_data.get('first_crop_years', {})
                second_crop_years = crop_data.get('second_crop_years', {})
                
                # Check if crop has data for this year
                has_data = False
                for region, years_list in first_crop_years.items():
                    if any(str(year) in year_str for year_str in years_list):
                        has_data = True
                        year_regions.add(region)
                        break
                
                if not has_data:
                    for region, years_list in second_crop_years.items():
                        if any(str(year) in year_str for year_str in years_list):
                            has_data = True
                            year_regions.add(region)
                            break
                
                if has_data:
                    year_crops += 1
            
            evolution_data.append({
                'year': year,
                'crops_covered': year_crops,
                'regions_covered': len(year_regions)
            })
        
        return pd.DataFrame(evolution_data)
        
    except Exception as e:
        st.error(f"❌ Error processing temporal evolution: {e}")
        return pd.DataFrame()


def get_crop_seasons_analysis(conab_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Analyze crop season patterns (first and second harvest).
    
    Args:
        conab_data: Raw CONAB data
        
    Returns:
        DataFrame with season analysis
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        seasons_data = []
        
        for crop, crop_data in detailed_coverage.items():
            first_crop_years = crop_data.get('first_crop_years', {})
            second_crop_years = crop_data.get('second_crop_years', {})
            
            # Count regions with first harvest
            first_regions = len([r for r, years in first_crop_years.items() if years])
            
            # Count regions with second harvest
            second_regions = len([r for r, years in second_crop_years.items() if years])
            
            # Total regions
            all_regions = set(first_crop_years.keys()) | set(second_crop_years.keys())
            total_regions = len(all_regions)
            
            seasons_data.append({
                'crop': crop,
                'first_crop_regions': first_regions,
                'second_crop_regions': second_regions,
                'total_regions': total_regions,
                'double_crop_ratio': second_regions / total_regions if total_regions > 0 else 0,
                'has_double_cropping': second_regions > 0
            })
        
        return pd.DataFrame(seasons_data)
        
    except Exception as e:
        st.error(f"❌ Error processing season analysis: {e}")
        return pd.DataFrame()


def get_conab_data_products(conab_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Extract information about CONAB data products.
    
    Args:
        conab_data: Raw CONAB data
        
    Returns:
        DataFrame with data products
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        data_products = initiative.get('data_products', [])
        
        if not data_products:
            return pd.DataFrame()
        
        products_data = []
        for product in data_products:
            products_data.append({
                'product_name': product.get('product_name', ''),
                'description': product.get('description', ''),
                'temporal_resolution': product.get('temporal_resolution', ''),
                'spatial_coverage': product.get('spatial_coverage', '')
            })
        
        return pd.DataFrame(products_data)
        
    except Exception as e:
        st.error(f"❌ Error processing data products: {e}")
        return pd.DataFrame()


def validate_conab_data_quality(conab_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate CONAB data quality and completeness.
    
    Args:
        conab_data: Raw CONAB data
        
    Returns:
        Dict with quality metrics
    """
    quality_metrics = {
        'completeness_score': 0.0,
        'data_freshness': 'Unknown',
        'missing_fields': [],
        'data_coverage': 'Unknown',
        'validation_errors': []
    }
    
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        
        if not initiative:
            quality_metrics['validation_errors'].append("No CONAB initiative data found")
            return quality_metrics
        
        # Required fields
        required_fields = [
            'coverage', 'provider', 'spatial_resolution', 'available_years',
            'methodology', 'overall_accuracy', 'detailed_crop_coverage'
        ]
        
        # Check completeness
        present_fields = 0
        for field in required_fields:
            if field in initiative and initiative[field]:
                present_fields += 1
            else:
                quality_metrics['missing_fields'].append(field)
        
        quality_metrics['completeness_score'] = present_fields / len(required_fields)
        
        # Check data freshness
        years = initiative.get('available_years', [])
        if years:
            latest_year = max(years)
            current_year = 2025  # Current year
            if latest_year >= current_year - 1:
                quality_metrics['data_freshness'] = 'Current'
            elif latest_year >= current_year - 3:
                quality_metrics['data_freshness'] = 'Recent'
            else:
                quality_metrics['data_freshness'] = 'Outdated'
        
        # Check data coverage
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        if len(detailed_coverage) >= 5:
            quality_metrics['data_coverage'] = 'Comprehensive'
        elif len(detailed_coverage) >= 2:
            quality_metrics['data_coverage'] = 'Partial'
        else:
            quality_metrics['data_coverage'] = 'Limited'
        
    except Exception as e:
        quality_metrics['validation_errors'].append(f"Error validating data: {e}")
    
    return quality_metrics


def safe_get_data(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get data from dictionary with nested key support.
    
    Args:
        data: Dictionary to search
        key: Key to search for (supports dot notation)
        default: Default value if key not found
        
    Returns:
        Retrieved value or default
    """
    try:
        if '.' in key:
            keys = key.split('.')
            current = data
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return default
            return current
        else:
            return data.get(key, default) if isinstance(data, dict) else default
    except Exception:
        return default


def validate_data_structure(data: Any, expected_type: type = dict) -> bool:
    """
    Validate if data has expected structure.
    
    Args:
        data: Data to validate
        expected_type: Expected type
        
    Returns:
        True if valid, False otherwise
    """
    try:
        if not isinstance(data, expected_type):
            return False
        
        if expected_type == dict:
            return len(data) > 0
        elif expected_type == list:
            return len(data) > 0
        
        return True
    except Exception:
        return False
