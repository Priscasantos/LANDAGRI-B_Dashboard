#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auxiliary Data Generation for Comparative Analysis Graphics
===========================================================

This module generates additional data structures and processing functions
to support advanced comparative analysis graphics with proper sigla integration.

Author: Dashboard Iniciativas LULC
Date: 2024
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def create_comparison_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a comparison matrix for initiatives with normalized metrics.
    
    Args:
        df: DataFrame with initiative data including Sigla column
        
    Returns:
        DataFrame with normalized comparison metrics
    """
    if df is None or df.empty or 'Sigla' not in df.columns:
        return pd.DataFrame()
    
    # Select numeric columns for comparison
    numeric_cols = ['Acurácia (%)', 'Resolução (m)', 'Classes']
    available_cols = [col for col in numeric_cols if col in df.columns]
    
    if not available_cols:
        return pd.DataFrame()
    
    # Create comparison matrix
    comparison_data = df[['Sigla', 'Nome'] + available_cols].copy()
    
    # Normalize metrics (0-1 scale)
    for col in available_cols:
        if col == 'Resolução (m)':
            # For resolution, lower is better, so invert
            comparison_data[f'{col}_normalized'] = 1 - (
                (comparison_data[col] - comparison_data[col].min()) / 
                (comparison_data[col].max() - comparison_data[col].min())
            )
        else:
            # For other metrics, higher is better
            comparison_data[f'{col}_normalized'] = (
                (comparison_data[col] - comparison_data[col].min()) / 
                (comparison_data[col].max() - comparison_data[col].min())
            )
    
    # Calculate overall score
    normalized_cols = [col for col in comparison_data.columns if col.endswith('_normalized')]
    comparison_data['Overall_Score'] = comparison_data[normalized_cols].mean(axis=1)
    
    return comparison_data

def create_temporal_analysis_data(metadata: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
    """
    Create comprehensive temporal analysis data structures.
    
    Args:
        metadata: Initiative metadata with temporal information
        df: DataFrame with initiative data including Sigla column
        
    Returns:
        Dictionary with temporal analysis data
    """
    if not metadata or df is None or df.empty or 'Sigla' not in df.columns:
        return {}
    
    # Create name to sigla mapping
    nome_to_sigla = {}
    if 'Sigla' in df.columns:
        for _, row in df.iterrows():
            nome_to_sigla[row['Nome']] = row['Sigla']
    
    temporal_data = {
        'initiatives': [],
        'timeline_matrix': {},
        'coverage_stats': {},
        'gaps_analysis': {},
        'temporal_overlap': {}
    }
    
    # Process each initiative
    all_years = set()
    for nome, meta in metadata.items():
        if 'anos_disponiveis' in meta and meta['anos_disponiveis']:
            sigla = nome_to_sigla.get(nome, nome[:10])
            anos = sorted(meta['anos_disponiveis'])
            
            initiative_data = {
                'name': nome,
                'sigla': sigla,
                'years': anos,
                'start_year': min(anos),
                'end_year': max(anos),
                'total_years': len(anos),
                'coverage_span': max(anos) - min(anos) + 1,
                'gaps': []
            }
            
            # Find gaps in temporal coverage
            for i in range(len(anos) - 1):
                if anos[i+1] - anos[i] > 1:
                    gap_start = anos[i] + 1
                    gap_end = anos[i+1] - 1
                    initiative_data['gaps'].append({
                        'start': gap_start,
                        'end': gap_end,
                        'duration': gap_end - gap_start + 1
                    })
            
            temporal_data['initiatives'].append(initiative_data)
            all_years.update(anos)
    
    # Create timeline matrix
    all_years_sorted = sorted(all_years)
    temporal_data['timeline_matrix'] = {
        'years': all_years_sorted,
        'initiatives': {}
    }
    
    for init_data in temporal_data['initiatives']:
        sigla = init_data['sigla']
        availability = [1 if year in init_data['years'] else 0 for year in all_years_sorted]
        temporal_data['timeline_matrix']['initiatives'][sigla] = {
            'availability': availability,
            'name': init_data['name']
        }
    
    # Calculate coverage statistics
    temporal_data['coverage_stats'] = {
        'total_period': {
            'start': min(all_years_sorted),
            'end': max(all_years_sorted),
            'span': max(all_years_sorted) - min(all_years_sorted) + 1
        },
        'by_initiative': {}
    }
    
    for init_data in temporal_data['initiatives']:
        sigla = init_data['sigla']
        total_span = temporal_data['coverage_stats']['total_period']['span']
        coverage_percentage = (init_data['total_years'] / total_span) * 100
        
        temporal_data['coverage_stats']['by_initiative'][sigla] = {
            'coverage_percentage': coverage_percentage,
            'total_years': init_data['total_years'],
            'span_years': init_data['coverage_span'],
            'efficiency': (init_data['total_years'] / init_data['coverage_span']) * 100 if init_data['coverage_span'] > 0 else 100
        }
    
    # Calculate temporal overlap between initiatives
    temporal_data['temporal_overlap'] = {}
    initiatives = temporal_data['initiatives']
    
    for i, init1 in enumerate(initiatives):
        for j, init2 in enumerate(initiatives[i+1:], i+1):
            sigla1, sigla2 = init1['sigla'], init2['sigla']
            years1, years2 = set(init1['years']), set(init2['years'])
            
            overlap = years1.intersection(years2)
            overlap_percentage = len(overlap) / len(years1.union(years2)) * 100 if years1.union(years2) else 0
            
            key = f"{sigla1}-{sigla2}"
            temporal_data['temporal_overlap'][key] = {
                'overlap_years': sorted(list(overlap)),
                'overlap_count': len(overlap),
                'overlap_percentage': overlap_percentage,
                'total_union_years': len(years1.union(years2))
            }
    
    return temporal_data

def create_methodology_analysis_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Create methodology analysis data with sigla integration.
    
    Args:
        df: DataFrame with initiative data including Sigla column
        
    Returns:
        Dictionary with methodology analysis data
    """
    if df is None or df.empty or 'Sigla' not in df.columns:
        return {}
    
    methodology_data = {
        'by_methodology': {},
        'methodology_performance': {},
        'methodology_trends': {},
        'cross_methodology_comparison': {}
    }
    
    # Group by methodology
    if 'Metodologia' in df.columns:
        grouped = df.groupby('Metodologia')
        
        for metodologia, group in grouped:
            siglas = group['Sigla'].tolist()
            
            methodology_data['by_methodology'][metodologia] = {
                'initiatives': siglas,
                'count': len(group),
                'siglas': siglas,
                'names': group['Nome'].tolist()
            }
            
            # Calculate performance metrics for this methodology
            if 'Acurácia (%)' in group.columns:
                accuracy_data = group['Acurácia (%)'].dropna()
                if not accuracy_data.empty:
                    methodology_data['methodology_performance'][metodologia] = {
                        'mean_accuracy': accuracy_data.mean(),
                        'std_accuracy': accuracy_data.std(),
                        'min_accuracy': accuracy_data.min(),
                        'max_accuracy': accuracy_data.max(),
                        'initiatives_with_data': len(accuracy_data)
                    }
    
    # Cross-methodology comparison
    if 'Metodologia' in df.columns and 'Acurácia (%)' in df.columns:
        methodology_comparison = df.groupby('Metodologia')['Acurácia (%)'].agg([
            'mean', 'std', 'count', 'min', 'max'
        ]).round(2)
        
        methodology_data['cross_methodology_comparison'] = methodology_comparison.to_dict('index')
    
    return methodology_data

def create_geographic_analysis_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Create geographic scope analysis data with sigla integration.
    
    Args:
        df: DataFrame with initiative data including Sigla column
        
    Returns:
        Dictionary with geographic analysis data
    """
    if df is None or df.empty or 'Sigla' not in df.columns:
        return {}
    
    geographic_data = {
        'by_scope': {},
        'scope_performance': {},
        'resolution_by_scope': {},
        'scope_comparison': {}
    }
    
    # Determine scope column
    scope_col = None
    for col in ['Tipo', 'Escopo', 'Scope']:
        if col in df.columns:
            scope_col = col
            break
    
    if scope_col:
        grouped = df.groupby(scope_col)
        
        for scope, group in grouped:
            siglas = group['Sigla'].tolist()
            
            geographic_data['by_scope'][scope] = {
                'initiatives': siglas,
                'count': len(group),
                'siglas': siglas,
                'names': group['Nome'].tolist()
            }
            
            # Performance by scope
            if 'Acurácia (%)' in group.columns:
                accuracy_data = group['Acurácia (%)'].dropna()
                if not accuracy_data.empty:
                    geographic_data['scope_performance'][scope] = {
                        'mean_accuracy': accuracy_data.mean(),
                        'std_accuracy': accuracy_data.std(),
                        'initiatives_count': len(accuracy_data)
                    }
            
            # Resolution by scope
            if 'Resolução (m)' in group.columns:
                resolution_data = group['Resolução (m)'].dropna()
                if not resolution_data.empty:
                    geographic_data['resolution_by_scope'][scope] = {
                        'mean_resolution': resolution_data.mean(),
                        'min_resolution': resolution_data.min(),
                        'max_resolution': resolution_data.max(),
                        'initiatives_count': len(resolution_data)
                    }
    
    return geographic_data

def create_class_analysis_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Create land cover class analysis data with sigla integration.
    
    Args:
        df: DataFrame with initiative data including Sigla column
        
    Returns:
        Dictionary with class analysis data
    """
    if df is None or df.empty or 'Sigla' not in df.columns:
        return {}
    
    class_data = {
        'class_distribution': {},
        'class_ranges': {},
        'class_performance_correlation': {},
        'initiatives_by_class_count': {}
    }
    
    if 'Classes' in df.columns:
        classes_data = df[['Sigla', 'Nome', 'Classes']].dropna()
        
        # Class distribution
        class_counts = classes_data['Classes'].value_counts().sort_index()
        class_data['class_distribution'] = class_counts.to_dict()
        
        # Class ranges analysis
        class_data['class_ranges'] = {
            'min_classes': classes_data['Classes'].min(),
            'max_classes': classes_data['Classes'].max(),
            'mean_classes': classes_data['Classes'].mean(),
            'std_classes': classes_data['Classes'].std()
        }
        
        # Group initiatives by class count ranges
        class_ranges = {
            'Low (2-10)': (2, 10),
            'Medium (11-20)': (11, 20),
            'High (21+)': (21, float('inf'))
        }
        
        for range_name, (min_val, max_val) in class_ranges.items():
            mask = (classes_data['Classes'] >= min_val) & (classes_data['Classes'] <= max_val)
            initiatives_in_range = classes_data[mask]
            
            class_data['initiatives_by_class_count'][range_name] = {
                'siglas': initiatives_in_range['Sigla'].tolist(),
                'names': initiatives_in_range['Nome'].tolist(),
                'count': len(initiatives_in_range),
                'class_values': initiatives_in_range['Classes'].tolist()
            }
        
        # Correlation with performance metrics
        if 'Acurácia (%)' in df.columns:
            correlation_data = df[['Classes', 'Acurácia (%)']].dropna()
            if len(correlation_data) > 1:
                correlation = correlation_data['Classes'].corr(correlation_data['Acurácia (%)'])
                class_data['class_performance_correlation'] = {
                    'correlation_with_accuracy': correlation,
                    'sample_size': len(correlation_data)
                }
    
    return class_data

def create_comprehensive_ranking_data(df: pd.DataFrame, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create comprehensive ranking data for initiatives with multiple criteria.
    
    Args:
        df: DataFrame with initiative data including Sigla column
        metadata: Initiative metadata
        
    Returns:
        Dictionary with ranking data
    """
    if df is None or df.empty or 'Sigla' not in df.columns:
        return {}
    
    ranking_data = {
        'overall_ranking': [],
        'accuracy_ranking': [],
        'resolution_ranking': [],
        'temporal_coverage_ranking': [],
        'composite_scores': {}
    }
    
    # Create name to sigla mapping for temporal data
    nome_to_sigla = {}
    for _, row in df.iterrows():
        nome_to_sigla[row['Nome']] = row['Sigla']
    
    # Prepare ranking DataFrame
    ranking_df = df[['Sigla', 'Nome']].copy()
    
    # Add normalized metrics
    metrics = ['Acurácia (%)', 'Resolução (m)', 'Classes']
    for metric in metrics:
        if metric in df.columns:
            if metric == 'Resolução (m)':
                # Lower resolution is better, so invert
                ranking_df[f'{metric}_score'] = 1 - (
                    (df[metric] - df[metric].min()) / (df[metric].max() - df[metric].min())
                )
            else:
                # Higher values are better
                ranking_df[f'{metric}_score'] = (
                    (df[metric] - df[metric].min()) / (df[metric].max() - df[metric].min())
                )
    
    # Add temporal coverage score
    if metadata:
        temporal_scores = []
        for _, row in ranking_df.iterrows():
            nome = row['Nome']
            if nome in metadata and 'anos_disponiveis' in metadata[nome]:
                years_count = len(metadata[nome]['anos_disponiveis'])
                temporal_scores.append(years_count)
            else:
                temporal_scores.append(0)
        
        if temporal_scores and max(temporal_scores) > 0:
            ranking_df['Temporal_score'] = [
                score / max(temporal_scores) for score in temporal_scores
            ]
    
    # Calculate composite score
    score_columns = [col for col in ranking_df.columns if col.endswith('_score')]
    if score_columns:
        ranking_df['Composite_Score'] = ranking_df[score_columns].mean(axis=1)
        
        # Create rankings
        ranking_data['overall_ranking'] = ranking_df.nlargest(len(ranking_df), 'Composite_Score')[
            ['Sigla', 'Nome', 'Composite_Score']
        ].to_dict('records')
    
    # Individual metric rankings
    if 'Acurácia (%)' in df.columns:
        accuracy_ranking = df.nlargest(len(df), 'Acurácia (%)')[
            ['Sigla', 'Nome', 'Acurácia (%)']
        ].to_dict('records')
        ranking_data['accuracy_ranking'] = accuracy_ranking
    
    if 'Resolução (m)' in df.columns:
        resolution_ranking = df.nsmallest(len(df), 'Resolução (m)')[
            ['Sigla', 'Nome', 'Resolução (m)']
        ].to_dict('records')
        ranking_data['resolution_ranking'] = resolution_ranking
    
    # Store composite scores for reference
    if 'Composite_Score' in ranking_df.columns:
        for _, row in ranking_df.iterrows():
            ranking_data['composite_scores'][row['Sigla']] = {
                'overall_score': row['Composite_Score'],
                'individual_scores': {
                    col.replace('_score', ''): row[col] 
                    for col in score_columns if col in row
                }
            }
    
    return ranking_data

def generate_all_auxiliary_data(df: pd.DataFrame, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate all auxiliary data structures for comparative analysis.
    
    Args:
        df: DataFrame with initiative data including Sigla column
        metadata: Initiative metadata
        
    Returns:
        Dictionary containing all auxiliary data structures
    """
    print("🔄 Generating auxiliary data for comparative analysis...")
    
    auxiliary_data = {
        'comparison_matrix': create_comparison_matrix(df),
        'temporal_analysis': create_temporal_analysis_data(metadata, df),
        'methodology_analysis': create_methodology_analysis_data(df),
        'geographic_analysis': create_geographic_analysis_data(df),
        'class_analysis': create_class_analysis_data(df),
        'ranking_data': create_comprehensive_ranking_data(df, metadata),
        'generation_timestamp': datetime.now().isoformat(),
        'data_summary': {
            'total_initiatives': len(df) if df is not None else 0,
            'initiatives_with_temporal_data': len([
                nome for nome, meta in metadata.items() 
                if 'anos_disponiveis' in meta and meta['anos_disponiveis']
            ]) if metadata else 0,
            'available_metrics': list(df.columns) if df is not None else []
        }
    }
    
    print(f"✅ Generated auxiliary data for {auxiliary_data['data_summary']['total_initiatives']} initiatives")
    print(f"📊 Created {len(auxiliary_data)} data structure categories")
    
    return auxiliary_data

def save_auxiliary_data(auxiliary_data: Dict[str, Any], filepath: str = None) -> bool:
    """
    Save auxiliary data to JSON file.
    
    Args:
        auxiliary_data: Generated auxiliary data
        filepath: Optional custom filepath
        
    Returns:
        True if saved successfully, False otherwise
    """
    if filepath is None:
        filepath = "data/processed/auxiliary_data.json"
    
    try:
        # Convert DataFrame to dict if present
        data_to_save = auxiliary_data.copy()
        if 'comparison_matrix' in data_to_save and hasattr(data_to_save['comparison_matrix'], 'to_dict'):
            data_to_save['comparison_matrix'] = data_to_save['comparison_matrix'].to_dict('records')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 Auxiliary data saved to {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error saving auxiliary data: {e}")
        return False

def load_auxiliary_data(filepath: str = None) -> Dict[str, Any]:
    """
    Load auxiliary data from JSON file.
    
    Args:
        filepath: Optional custom filepath
        
    Returns:
        Loaded auxiliary data or empty dict if failed
    """
    if filepath is None:
        filepath = "data/processed/auxiliary_data.json"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            auxiliary_data = json.load(f)
        
        print(f"📂 Auxiliary data loaded from {filepath}")
        return auxiliary_data
    except Exception as e:
        print(f"❌ Error loading auxiliary data: {e}")
        return {}

# Example usage function for testing
def test_auxiliary_data_generation():
    """Test function to validate auxiliary data generation."""
    print("🧪 Testing auxiliary data generation...")
    
    try:
        from data_processing import load_data_from_jsonc
        
        # Load data
        df, metadata = load_data_from_jsonc()
        
        if df is None or df.empty:
            print("❌ No data loaded for testing")
            return False
        
        # Generate auxiliary data
        auxiliary_data = generate_all_auxiliary_data(df, metadata)
        
        # Validate generated data
        required_keys = [
            'comparison_matrix', 'temporal_analysis', 'methodology_analysis',
            'geographic_analysis', 'class_analysis', 'ranking_data'
        ]
        
        all_present = all(key in auxiliary_data for key in required_keys)
        
        if all_present:
            print("✅ All auxiliary data structures generated successfully")
            
            # Show summary
            summary = auxiliary_data['data_summary']
            print(f"📊 Summary: {summary['total_initiatives']} initiatives, {summary['initiatives_with_temporal_data']} with temporal data")
            
            return True
        else:
            missing = [key for key in required_keys if key not in auxiliary_data]
            print(f"❌ Missing data structures: {missing}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing auxiliary data generation: {e}")
        return False

if __name__ == "__main__":
    test_auxiliary_data_generation()
