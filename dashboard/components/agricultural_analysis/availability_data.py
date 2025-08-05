"""
Availability Data Component
==========================

Componente responsável por gerenciar dados de disponibilidade 
e qualidade do sistema de monitoramento agrícola.

Author: Dashboard Iniciativas LULC
Date: 2025-08-05
"""

from pathlib import Path
from typing import Any, Dict

import pandas as pd
import streamlit as st

from .agricultural_loader import load_conab_detailed_data


def get_data_availability_status() -> Dict[str, Any]:
    """
    Obter status de disponibilidade dos dados.
    
    Returns:
        Dict com informações de disponibilidade dos dados
    """
    data = load_conab_detailed_data()
    
    if not data:
        return {
            'status': 'unavailable',
            'message': 'Dados não disponíveis',
            'coverage': 0,
            'last_update': 'N/A'
        }
    
    # Calcular estatísticas de disponibilidade
    initiatives = data.get('initiatives', [])
    total_initiatives = len(initiatives)
    
    # Verificar cobertura temporal
    temporal_coverage = 0
    if initiatives:
        for initiative in initiatives:
            if initiative.get('period_covered', {}).get('end_date'):
                temporal_coverage += 1
    
    coverage_percent = (temporal_coverage / total_initiatives * 100) if total_initiatives > 0 else 0
    
    return {
        'status': 'available' if total_initiatives > 0 else 'unavailable',
        'total_initiatives': total_initiatives,
        'coverage_percent': round(coverage_percent, 1),
        'temporal_coverage': temporal_coverage,
        'last_update': '2024-12-01',  # Data fictícia - pode ser dinâmica
        'message': f'{total_initiatives} iniciativas disponíveis'
    }


def get_data_quality_metrics() -> Dict[str, Any]:
    """
    Obter métricas de qualidade dos dados.
    
    Returns:
        Dict com métricas de qualidade
    """
    data = load_conab_detailed_data()
    
    if not data:
        return {
            'overall_quality': 0,
            'completeness': 0,
            'accuracy': 0,
            'consistency': 0,
            'timeliness': 0
        }
    
    initiatives = data.get('initiatives', [])
    
    # Calcular métricas de qualidade (simuladas)
    quality_scores = []
    
    for initiative in initiatives:
        score = 0
        
        # Completeness: verifica se tem dados essenciais
        if initiative.get('crops_monitored'):
            score += 25
        if initiative.get('states_covered'):
            score += 25
        if initiative.get('period_covered'):
            score += 25
        if initiative.get('methodology'):
            score += 25
            
        quality_scores.append(score)
    
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    return {
        'overall_quality': round(avg_quality, 1),
        'completeness': round(avg_quality * 0.9, 1),  # Simulado
        'accuracy': round(avg_quality * 0.85, 1),     # Simulado
        'consistency': round(avg_quality * 0.95, 1),  # Simulado
        'timeliness': round(avg_quality * 0.8, 1)     # Simulado
    }


def get_spatial_coverage_status() -> pd.DataFrame:
    """
    Obter status de cobertura espacial.
    
    Returns:
        DataFrame com informações de cobertura por estado/região
    """
    data = load_conab_detailed_data()
    
    if not data:
        return pd.DataFrame(columns=['Estado', 'Cobertura', 'Iniciativas', 'Status'])
    
    # Processar cobertura espacial
    spatial_data = []
    initiatives = data.get('initiatives', [])
    
    # Coletar todos os estados mencionados
    all_states = set()
    for initiative in initiatives:
        states = initiative.get('states_covered', [])
        if isinstance(states, list):
            all_states.update(states)
        elif isinstance(states, str):
            all_states.add(states)
    
    # Calcular cobertura por estado
    for state in sorted(all_states):
        count = 0
        for initiative in initiatives:
            states = initiative.get('states_covered', [])
            if isinstance(states, list) and state in states:
                count += 1
            elif isinstance(states, str) and state == states:
                count += 1
        
        coverage = (count / len(initiatives) * 100) if initiatives else 0
        status = 'Completa' if coverage >= 80 else 'Parcial' if coverage >= 40 else 'Limitada'
        
        spatial_data.append({
            'Estado': state,
            'Cobertura': f"{coverage:.1f}%",
            'Iniciativas': count,
            'Status': status
        })
    
    return pd.DataFrame(spatial_data)


def get_temporal_coverage_analysis() -> Dict[str, Any]:
    """
    Analisar cobertura temporal dos dados.
    
    Returns:
        Dict com análise de cobertura temporal
    """
    data = load_conab_detailed_data()
    
    if not data:
        return {
            'period_start': 'N/A',
            'period_end': 'N/A',
            'total_years': 0,
            'gaps': [],
            'coverage_score': 0
        }
    
    initiatives = data.get('initiatives', [])
    
    # Analisar períodos cobertos
    start_years = []
    end_years = []
    
    for initiative in initiatives:
        period = initiative.get('period_covered', {})
        if period.get('start_date'):
            try:
                start_year = int(period['start_date'][:4])
                start_years.append(start_year)
            except (ValueError, TypeError):
                pass
                
        if period.get('end_date'):
            try:
                end_year = int(period['end_date'][:4])
                end_years.append(end_year)
            except (ValueError, TypeError):
                pass
    
    if start_years and end_years:
        min_year = min(start_years)
        max_year = max(end_years)
        total_years = max_year - min_year + 1
        coverage_score = min(100, (len(initiatives) / total_years) * 50)
    else:
        min_year = max_year = total_years = coverage_score = 0
    
    return {
        'period_start': str(min_year) if min_year > 0 else 'N/A',
        'period_end': str(max_year) if max_year > 0 else 'N/A',
        'total_years': total_years,
        'initiatives_count': len(initiatives),
        'coverage_score': round(coverage_score, 1)
    }


def get_data_access_information() -> Dict[str, Any]:
    """
    Obter informações sobre acesso aos dados.
    
    Returns:
        Dict com informações de acesso
    """
    return {
        'provider': 'CONAB - Companhia Nacional de Abastecimento',
        'access_level': 'Público',
        'update_frequency': 'Anual',
        'data_format': 'JSON, CSV, Shapefile',
        'api_available': False,
        'download_available': True,
        'license': 'Dados Abertos',
        'contact': 'dados@conab.gov.br',
        'documentation_url': 'https://www.conab.gov.br/info-agro',
        'last_updated': '2024-12-01'
    }
