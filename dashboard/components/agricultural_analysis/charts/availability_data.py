"""
Agricultural Availability Data Loader
=====================================

Funções específicas para carregar dados de Disponibilidade de Dados Agrícolas.
Apenas informações sobre disponibilidade, qualidade e produtos de dados.

Autor: Dashboard Iniciativas LULC
Data: 2025-08-05
"""

import pandas as pd
import streamlit as st
from typing import Any
from .agricultural_loader import load_conab_detailed_data


def get_data_availability_status() -> dict[str, Any]:
    """
    Carregar status de disponibilidade dos dados CONAB.
    
    Returns:
        Dict com status de disponibilidade
    """
    conab_data = load_conab_detailed_data()
    
    if not conab_data:
        return {}
    
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        
        availability_status = {
            'data_available': bool(initiative),
            'last_update': 'N/A',
            'data_freshness': 'Unknown',
            'coverage_status': 'Unknown',
            'quality_score': 0.0,
            'completeness': 0.0
        }
        
        if initiative:
            # Verificar atualidade dos dados
            years = initiative.get('available_years', [])
            if years:
                latest_year = max(years)
                current_year = 2025
                
                availability_status['last_update'] = str(latest_year)
                
                if latest_year >= current_year - 1:
                    availability_status['data_freshness'] = 'Atual'
                elif latest_year >= current_year - 3:
                    availability_status['data_freshness'] = 'Recente'
                else:
                    availability_status['data_freshness'] = 'Desatualizado'
            
            # Status de cobertura
            detailed_coverage = initiative.get('detailed_crop_coverage', {})
            if len(detailed_coverage) >= 5:
                availability_status['coverage_status'] = 'Abrangente'
            elif len(detailed_coverage) >= 2:
                availability_status['coverage_status'] = 'Parcial'
            else:
                availability_status['coverage_status'] = 'Limitada'
            
            # Score de qualidade baseado em completude
            required_fields = [
                'coverage', 'provider', 'spatial_resolution', 'available_years',
                'methodology', 'overall_accuracy', 'detailed_crop_coverage'
            ]
            
            present_fields = sum(1 for field in required_fields if field in initiative and initiative[field])
            availability_status['completeness'] = present_fields / len(required_fields)
            availability_status['quality_score'] = availability_status['completeness'] * 100
        
        return availability_status
        
    except Exception as e:
        st.error(f"❌ Erro ao verificar disponibilidade: {e}")
        return {}


def get_data_products_catalog() -> pd.DataFrame:
    """
    Carregar catálogo de produtos de dados disponíveis.
    
    Returns:
        DataFrame com produtos de dados
    """
    conab_data = load_conab_detailed_data()
    
    if not conab_data:
        return pd.DataFrame()
    
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        data_products = initiative.get('data_products', [])
        
        if not data_products:
            # Criar produtos baseados nos dados disponíveis
            detailed_coverage = initiative.get('detailed_crop_coverage', {})
            
            products_data = []
            for crop in detailed_coverage.keys():
                products_data.append({
                    'Produto': f'Dados de {crop}',
                    'Descrição': f'Monitoramento da cultura {crop}',
                    'Resolução Temporal': 'Anual',
                    'Cobertura Espacial': 'Estados brasileiros',
                    'Formato': 'JSON',
                    'Disponibilidade': 'Disponível'
                })
            
            return pd.DataFrame(products_data)
        
        # Se existem produtos definidos
        products_data = []
        for product in data_products:
            products_data.append({
                'Produto': product.get('product_name', ''),
                'Descrição': product.get('description', ''),
                'Resolução Temporal': product.get('temporal_resolution', ''),
                'Cobertura Espacial': product.get('spatial_coverage', ''),
                'Formato': product.get('format', 'JSON'),
                'Disponibilidade': product.get('status', 'Disponível')
            })
        
        return pd.DataFrame(products_data)
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar catálogo: {e}")
        return pd.DataFrame()


def get_data_quality_metrics() -> pd.DataFrame:
    """
    Carregar métricas de qualidade dos dados.
    
    Returns:
        DataFrame com métricas de qualidade por cultura
    """
    conab_data = load_conab_detailed_data()
    
    if not conab_data:
        return pd.DataFrame()
    
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        overall_accuracy = initiative.get('overall_accuracy', 0)
        
        quality_data = []
        
        for crop, crop_data in detailed_coverage.items():
            regions = crop_data.get('regions', [])
            first_crop_years = crop_data.get('first_crop_years', {})
            second_crop_years = crop_data.get('second_crop_years', {})
            
            # Calcular completude dos dados
            total_possible_entries = len(regions) * 10  # Assumindo 10 anos de dados possíveis
            actual_entries = sum(len(years) for years in first_crop_years.values())
            actual_entries += sum(len(years) for years in second_crop_years.values())
            
            completeness = (actual_entries / total_possible_entries * 100) if total_possible_entries > 0 else 0
            
            # Calcular consistência (baseado na distribuição regional)
            consistency = (len(regions) / 27 * 100) if len(regions) > 0 else 0  # 27 estados do Brasil
            
            quality_data.append({
                'Cultura': crop,
                'Estados Cobertos': len(regions),
                'Completude (%)': round(completeness, 1),
                'Consistência Regional (%)': round(consistency, 1),
                'Precisão Geral (%)': round(overall_accuracy * 100, 1) if overall_accuracy else 0,
                'Score Qualidade': round((completeness + consistency + (overall_accuracy * 100 if overall_accuracy else 0)) / 3, 1),
                'Status': 'Boa' if completeness > 70 else 'Regular' if completeness > 40 else 'Limitada'
            })
        
        return pd.DataFrame(quality_data)
        
    except Exception as e:
        st.error(f"❌ Erro ao calcular qualidade: {e}")
        return pd.DataFrame()


def get_data_coverage_summary() -> dict[str, Any]:
    """
    Carregar resumo de cobertura dos dados.
    
    Returns:
        Dict com resumo de cobertura
    """
    conab_data = load_conab_detailed_data()
    
    if not conab_data:
        return {}
    
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        # Calcular estatísticas de cobertura
        all_states = set()
        total_data_points = 0
        crops_with_double_crop = 0
        
        for crop_data in detailed_coverage.values():
            regions = crop_data.get('regions', [])
            all_states.update(regions)
            
            first_crop_years = crop_data.get('first_crop_years', {})
            second_crop_years = crop_data.get('second_crop_years', {})
            
            for years in first_crop_years.values():
                total_data_points += len(years)
            
            for years in second_crop_years.values():
                total_data_points += len(years)
            
            if any(len(years) > 0 for years in second_crop_years.values()):
                crops_with_double_crop += 1
        
        coverage_summary = {
            'total_crops': len(detailed_coverage),
            'states_covered': len(all_states),
            'total_data_points': total_data_points,
            'crops_with_double_crop': crops_with_double_crop,
            'double_crop_percentage': (crops_with_double_crop / len(detailed_coverage) * 100) if detailed_coverage else 0,
            'spatial_resolution': initiative.get('spatial_resolution', 'N/A'),
            'provider': initiative.get('provider', 'N/A'),
            'methodology': initiative.get('methodology', 'N/A'),
            'coverage_area': initiative.get('coverage', 'N/A')
        }
        
        return coverage_summary
        
    except Exception as e:
        st.error(f"❌ Erro ao calcular cobertura: {e}")
        return {}


def get_access_information() -> dict[str, Any]:
    """
    Carregar informações de acesso aos dados.
    
    Returns:
        Dict com informações de acesso
    """
    conab_data = load_conab_detailed_data()
    
    if not conab_data:
        return {}
    
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        
        access_info = {
            'provider': initiative.get('provider', 'CONAB'),
            'access_level': 'Público',
            'license': 'Creative Commons',
            'update_frequency': 'Anual',
            'format': 'JSON/JSONC',
            'api_available': False,
            'download_available': True,
            'documentation_available': True,
            'contact_email': 'dados@conab.gov.br',
            'website': 'https://www.conab.gov.br/',
            'terms_of_use': 'Dados públicos para uso científico e educacional'
        }
        
        return access_info
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar informações de acesso: {e}")
        return {}
