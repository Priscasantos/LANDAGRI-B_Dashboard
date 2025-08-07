"""
Agricultural Overview Data Loader
=================================

Funções específicas para carregar dados do Overview Agrícola.
Apenas dados de visão geral e estatísticas principais.

Autor: Dashboard Iniciativas LULC
Data: 2025-08-05
"""

import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, Any
from ..agricultural_loader import load_conab_detailed_data


def get_agricultural_overview_stats() -> Dict[str, Any]:
    """
    Carregar apenas estatísticas de overview agrícola.
    
    Returns:
        Dict com estatísticas principais para overview
    """
    conab_data = load_conab_detailed_data()
    
    if not conab_data:
        return {}
    
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        
        # Estatísticas principais para overview
        overview_stats = {
            'total_crops': 0,
            'states_covered': 0,
            'total_area_monitored': 'N/A',
            'resolution': 'N/A',
            'accuracy': 0.0,
            'provider': 'N/A',
            'methodology': 'N/A'
        }
        
        # Dados básicos
        overview_stats['provider'] = initiative.get('provider', 'N/A')
        overview_stats['methodology'] = initiative.get('methodology', 'N/A')
        
        # Contagem de culturas
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        overview_stats['total_crops'] = len(detailed_coverage)
        
        # Estados cobertos
        all_states = set()
        for crop_data in detailed_coverage.values():
            states = crop_data.get('regions', [])  # Nome inconsistente na fonte - contém estados
            all_states.update(states)
        overview_stats['states_covered'] = len(all_states)
        
        # Resolução espacial
        resolution = initiative.get('spatial_resolution')
        if resolution:
            overview_stats['resolution'] = f"{resolution}m"
        
        # Precisão geral
        accuracy = initiative.get('overall_accuracy')
        if accuracy:
            overview_stats['accuracy'] = accuracy
        
        # Área de cobertura
        coverage = initiative.get('coverage', 'N/A')
        overview_stats['total_area_monitored'] = coverage
        
        return overview_stats
        
    except Exception as e:
        st.error(f"❌ Erro ao processar overview: {e}")
        return {}


def get_crops_overview_data() -> pd.DataFrame:
    """
    Carregar dados das culturas para overview.
    
    Returns:
        DataFrame com informações básicas das culturas
    """
    conab_data = load_conab_detailed_data()
    
    if not conab_data:
        return pd.DataFrame()
    
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        crops_data = []
        
        for crop, crop_data in detailed_coverage.items():
            states = crop_data.get('regions', [])  # Nome inconsistente na fonte - contém estados
            first_crop_years = crop_data.get('first_crop_years', {})
            second_crop_years = crop_data.get('second_crop_years', {})
            
            # Contar total de anos de dados
            total_data_points = 0
            for region_years in first_crop_years.values():
                total_data_points += len(region_years)
            for region_years in second_crop_years.values():
                total_data_points += len(region_years)
            
            # Verificar se tem dupla safra
            has_double_crop = any(len(years) > 0 for years in second_crop_years.values())
            
            crops_data.append({
                'Cultura': crop,
                'Estados': len(states),
                'Dupla Safra': has_double_crop,
                'Total Dados': total_data_points,
                'Estados Lista': ', '.join(states[:3]) + ('...' if len(states) > 3 else '')
            })
        
        return pd.DataFrame(crops_data)
        
    except Exception as e:
        st.error(f"❌ Erro ao processar dados de culturas: {e}")
        return pd.DataFrame()


def get_states_summary() -> pd.DataFrame:
    """
    Carregar resumo por estados para overview.
    
    Returns:
        DataFrame com resumo por estado brasileiro
    """
    conab_data = load_conab_detailed_data()
    
    if not conab_data:
        return pd.DataFrame()
    
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        # Agregar por estado
        states_summary = {}
        
        for crop, crop_data in detailed_coverage.items():
            states = crop_data.get('regions', [])  # Nome inconsistente na fonte - contém estados
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
                
                # Contar anos de dados
                first_years = len(first_crop_years.get(state, []))
                second_years = len(second_crop_years.get(state, []))
                states_summary[state]['total_years'] += first_years + second_years
                
                # Verificar dupla safra
                if second_years > 0:
                    states_summary[state]['has_double_crop'] = True
        
        # Converter para DataFrame
        summary_data = []
        for state_data in states_summary.values():
            summary_data.append({
                'Estado': state_data['state'],
                'Culturas': state_data['crops_count'],
                'Total Anos': state_data['total_years'],
                'Dupla Safra': state_data['has_double_crop']
            })
        
        return pd.DataFrame(summary_data)
        
    except Exception as e:
        st.error(f"❌ Erro ao processar resumo por estados: {e}")
        return pd.DataFrame()
