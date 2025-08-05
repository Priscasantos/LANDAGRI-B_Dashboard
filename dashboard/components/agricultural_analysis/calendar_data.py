"""
Agricultural Calendar Data Loader
=================================

Funções específicas para carregar dados do Calendário Agrícola.
Apenas dados de calendário de safras e períodos de plantio/colheita.

Autor: Dashboard Iniciativas LULC
Data: 2025-08-05
"""

import pandas as pd
import streamlit as st
from typing import Any
from .agricultural_loader import load_conab_crop_calendar


def get_calendar_heatmap_data() -> pd.DataFrame:
    """
    Carregar dados do calendário para heatmap de safras.
    
    Returns:
        DataFrame formatado para visualização de calendário
    """
    calendar_data = load_conab_crop_calendar()
    
    if not calendar_data:
        return pd.DataFrame()
    
    try:
        # Extrair dados do calendário
        crops_calendar = calendar_data.get('CONAB Crop Calendar', {})
        
        calendar_matrix = []
        months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        for crop, crop_info in crops_calendar.items():
            if isinstance(crop_info, dict):
                regions = crop_info.get('regions', {})
                
                for region, region_info in regions.items():
                    planting_period = region_info.get('planting_period', [])
                    harvest_period = region_info.get('harvest_period', [])
                    
                    # Criar linha para o calendário
                    row = {
                        'Cultura': crop,
                        'Região': region,
                        'Tipo': 'Plantio'
                    }
                    
                    # Marcar meses de plantio
                    for month in months:
                        row[month] = 1 if month in planting_period else 0
                    
                    calendar_matrix.append(row.copy())
                    
                    # Linha para colheita
                    row['Tipo'] = 'Colheita'
                    for month in months:
                        row[month] = 1 if month in harvest_period else 0
                    
                    calendar_matrix.append(row.copy())
        
        return pd.DataFrame(calendar_matrix)
        
    except Exception as e:
        st.error(f"❌ Erro ao processar calendário: {e}")
        return pd.DataFrame()


def get_crop_seasons_calendar() -> dict[str, Any]:
    """
    Carregar informações de safras para cada cultura.
    
    Returns:
        Dict com informações de safras por cultura
    """
    calendar_data = load_conab_crop_calendar()
    
    if not calendar_data:
        return {}
    
    try:
        crops_calendar = calendar_data.get('CONAB Crop Calendar', {})
        seasons_info = {}
        
        for crop, crop_info in crops_calendar.items():
            if isinstance(crop_info, dict):
                regions = crop_info.get('regions', {})
                
                # Agregar informações de safras
                total_regions = len(regions)
                regions_with_double_crop = 0
                main_planting_months = set()
                main_harvest_months = set()
                
                for region_info in regions.values():
                    planting_period = region_info.get('planting_period', [])
                    harvest_period = region_info.get('harvest_period', [])
                    second_crop = region_info.get('second_crop', False)
                    
                    if second_crop:
                        regions_with_double_crop += 1
                    
                    main_planting_months.update(planting_period)
                    main_harvest_months.update(harvest_period)
                
                seasons_info[crop] = {
                    'total_regions': total_regions,
                    'double_crop_regions': regions_with_double_crop,
                    'double_crop_percentage': (regions_with_double_crop / total_regions * 100) if total_regions > 0 else 0,
                    'main_planting_months': sorted(list(main_planting_months)),
                    'main_harvest_months': sorted(list(main_harvest_months)),
                    'crop_duration_months': len(main_planting_months) + len(main_harvest_months)
                }
        
        return seasons_info
        
    except Exception as e:
        st.error(f"❌ Erro ao processar safras: {e}")
        return {}


def get_monthly_activity_summary() -> pd.DataFrame:
    """
    Carregar resumo de atividades agrícolas por mês.
    
    Returns:
        DataFrame com atividades por mês
    """
    calendar_data = load_conab_crop_calendar()
    
    if not calendar_data:
        return pd.DataFrame()
    
    try:
        crops_calendar = calendar_data.get('CONAB Crop Calendar', {})
        
        monthly_activity = {
            'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                   'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
            'Plantios': [0] * 12,
            'Colheitas': [0] * 12,
            'Culturas_Ativas': [0] * 12
        }
        
        month_to_index = {month: i for i, month in enumerate(monthly_activity['Mês'])}
        
        for crop, crop_info in crops_calendar.items():
            if isinstance(crop_info, dict):
                regions = crop_info.get('regions', {})
                
                for region_info in regions.values():
                    planting_period = region_info.get('planting_period', [])
                    harvest_period = region_info.get('harvest_period', [])
                    
                    # Contar plantios por mês
                    for month in planting_period:
                        if month in month_to_index:
                            monthly_activity['Plantios'][month_to_index[month]] += 1
                    
                    # Contar colheitas por mês
                    for month in harvest_period:
                        if month in month_to_index:
                            monthly_activity['Colheitas'][month_to_index[month]] += 1
                    
                    # Estimar culturas ativas (entre plantio e colheita)
                    if planting_period and harvest_period:
                        start_month = month_to_index.get(planting_period[0], 0)
                        end_month = month_to_index.get(harvest_period[-1], 11)
                        
                        # Se passa do ano (ex: planta em Nov, colhe em Mar)
                        if start_month > end_month:
                            for i in range(start_month, 12):
                                monthly_activity['Culturas_Ativas'][i] += 1
                            for i in range(0, end_month + 1):
                                monthly_activity['Culturas_Ativas'][i] += 1
                        else:
                            for i in range(start_month, end_month + 1):
                                monthly_activity['Culturas_Ativas'][i] += 1
        
        return pd.DataFrame(monthly_activity)
        
    except Exception as e:
        st.error(f"❌ Erro ao processar atividades mensais: {e}")
        return pd.DataFrame()


def get_regional_calendar_patterns() -> pd.DataFrame:
    """
    Carregar padrões de calendário por região.
    
    Returns:
        DataFrame com padrões regionais
    """
    calendar_data = load_conab_crop_calendar()
    
    if not calendar_data:
        return pd.DataFrame()
    
    try:
        crops_calendar = calendar_data.get('CONAB Crop Calendar', {})
        
        regional_patterns = {}
        
        for crop, crop_info in crops_calendar.items():
            if isinstance(crop_info, dict):
                regions = crop_info.get('regions', {})
                
                for region, region_info in regions.items():
                    if region not in regional_patterns:
                        regional_patterns[region] = {
                            'region': region,
                            'total_crops': 0,
                            'double_crop_count': 0,
                            'main_planting_season': [],
                            'main_harvest_season': []
                        }
                    
                    regional_patterns[region]['total_crops'] += 1
                    
                    if region_info.get('second_crop', False):
                        regional_patterns[region]['double_crop_count'] += 1
                    
                    planting_period = region_info.get('planting_period', [])
                    harvest_period = region_info.get('harvest_period', [])
                    
                    regional_patterns[region]['main_planting_season'].extend(planting_period)
                    regional_patterns[region]['main_harvest_season'].extend(harvest_period)
        
        # Converter para DataFrame
        patterns_data = []
        for region_data in regional_patterns.values():
            # Encontrar meses mais comuns
            planting_months = list(set(region_data['main_planting_season']))
            harvest_months = list(set(region_data['main_harvest_season']))
            
            patterns_data.append({
                'Região': region_data['region'],
                'Total_Culturas': region_data['total_crops'],
                'Dupla_Safra': region_data['double_crop_count'],
                'Perc_Dupla_Safra': (region_data['double_crop_count'] / region_data['total_crops'] * 100) if region_data['total_crops'] > 0 else 0,
                'Principais_Meses_Plantio': ', '.join(planting_months[:3]),
                'Principais_Meses_Colheita': ', '.join(harvest_months[:3])
            })
        
        return pd.DataFrame(patterns_data)
        
    except Exception as e:
        st.error(f"❌ Erro ao processar padrões regionais: {e}")
        return pd.DataFrame()
