"""
CONAB Data Loader Component
==========================

Componente responsável por carregar e processar dados detalhados da iniciativa CONAB,
incluindo dados de culturas, calendários e cobertura regional.

Autor: Dashboard Iniciativas LULC
Data: 2025-08-01
"""

import json
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, Any, Optional


def load_conab_detailed_data() -> Dict[str, Any]:
    """
    Carregar dados detalhados da iniciativa CONAB do arquivo JSON.
    
    Returns:
        Dict com dados da iniciativa CONAB ou dict vazio se erro
    """
    try:
        # Determinar caminho do arquivo
        current_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        conab_file = current_dir / "data" / "json" / "conab_detailed_initiative.jsonc"
        
        if not conab_file.exists():
            st.warning(f"⚠️ Arquivo CONAB não encontrado: {conab_file}")
            return {}
        
        # Carregar e processar arquivo JSONC
        with open(conab_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Remover comentários de linha simples
        lines = []
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped.startswith('//'):
                lines.append(line)
        
        # Processar JSON
        clean_content = '\n'.join(lines)
        data = json.loads(clean_content)
        
        return data
        
    except json.JSONDecodeError as e:
        st.error(f"❌ Erro ao processar JSON do CONAB: {e}")
        return {}
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados CONAB: {e}")
        return {}


def load_conab_crop_calendar() -> Dict[str, Any]:
    """
    Carregar dados do calendário agrícola CONAB.
    
    Returns:
        Dict com dados do calendário ou dict vazio se erro
    """
    try:
        # Determinar caminho do arquivo
        current_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        calendar_files = [
            current_dir / "data" / "json" / "conab_crop_calendar.jsonc",
            current_dir / "data" / "json" / "conab_crop_calendar_complete.jsonc"
        ]
        
        calendar_data = {}
        
        for calendar_file in calendar_files:
            if calendar_file.exists():
                with open(calendar_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remover comentários
                lines = []
                for line in content.splitlines():
                    stripped = line.strip()
                    if not stripped.startswith('//'):
                        lines.append(line)
                
                # Processar JSON
                clean_content = '\n'.join(lines)
                data = json.loads(clean_content)
                
                # Merge data
                calendar_data.update(data)
        
        return calendar_data
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar calendário CONAB: {e}")
        return {}


def get_conab_crop_stats(conab_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrair estatísticas principais dos dados CONAB.
    
    Args:
        conab_data: Dados brutos do CONAB
        
    Returns:
        Dict com estatísticas processadas
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
        
        # Contar culturas detalhadas
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        stats['total_crops'] = len(detailed_coverage)
        
        # Contar estados únicos cobertos
        all_states = set()
        for crop_data in detailed_coverage.values():
            regions = crop_data.get('regions', [])
            all_states.update(regions)
        stats['states_covered'] = len(all_states)
        
        # Cobertura regional
        regional_coverage = initiative.get('regional_coverage', [])
        stats['regions_covered'] = len(regional_coverage)
        
        # Span temporal
        years = initiative.get('available_years', [])
        if years:
            stats['temporal_span'] = max(years) - min(years) + 1
        
        # Resolução espacial
        resolution = initiative.get('spatial_resolution')
        if resolution:
            stats['resolution'] = f"{resolution}m"
        
        # Precisão geral
        accuracy = initiative.get('overall_accuracy')
        if accuracy:
            stats['accuracy'] = accuracy
        
        # Área de cobertura
        coverage = initiative.get('coverage', 'N/A')
        stats['coverage_area'] = coverage
        
    except Exception as e:
        st.error(f"❌ Erro ao processar estatísticas CONAB: {e}")
    
    return stats


def get_crop_regional_distribution(conab_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Extrair distribuição regional das culturas dos dados CONAB.
    
    Args:
        conab_data: Dados brutos do CONAB
        
    Returns:
        DataFrame com distribuição regional
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
                # Contar anos de dados disponíveis
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
        st.error(f"❌ Erro ao processar distribuição regional: {e}")
        return pd.DataFrame()


def get_temporal_coverage_evolution(conab_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Extrair evolução da cobertura temporal das culturas.
    
    Args:
        conab_data: Dados brutos do CONAB
        
    Returns:
        DataFrame com evolução temporal
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        available_years = initiative.get('available_years', [])
        
        # Criar matriz de cobertura por ano e cultura
        evolution_data = []
        
        for year in available_years:
            year_crops = 0
            year_regions = set()
            
            for crop, crop_data in detailed_coverage.items():
                first_crop_years = crop_data.get('first_crop_years', {})
                second_crop_years = crop_data.get('second_crop_years', {})
                
                # Verificar se a cultura tem dados neste ano
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
        st.error(f"❌ Erro ao processar evolução temporal: {e}")
        return pd.DataFrame()


def get_crop_seasons_analysis(conab_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Analisar padrões de safras das culturas (primeira e segunda safra).
    
    Args:
        conab_data: Dados brutos do CONAB
        
    Returns:
        DataFrame com análise de safras
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        seasons_data = []
        
        for crop, crop_data in detailed_coverage.items():
            first_crop_years = crop_data.get('first_crop_years', {})
            second_crop_years = crop_data.get('second_crop_years', {})
            
            # Contar regiões com primeira safra
            first_regions = len([r for r, years in first_crop_years.items() if years])
            
            # Contar regiões com segunda safra
            second_regions = len([r for r, years in second_crop_years.items() if years])
            
            # Total de regiões
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
        st.error(f"❌ Erro ao processar análise de safras: {e}")
        return pd.DataFrame()


def get_conab_data_products(conab_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Extrair informações sobre produtos de dados do CONAB.
    
    Args:
        conab_data: Dados brutos do CONAB
        
    Returns:
        DataFrame com produtos de dados
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
        st.error(f"❌ Erro ao processar produtos de dados: {e}")
        return pd.DataFrame()


def validate_conab_data_quality(conab_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validar qualidade e completude dos dados CONAB.
    
    Args:
        conab_data: Dados brutos do CONAB
        
    Returns:
        Dict com métricas de qualidade
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
        
        # Campos obrigatórios
        required_fields = [
            'coverage', 'provider', 'spatial_resolution', 'available_years',
            'methodology', 'overall_accuracy', 'detailed_crop_coverage'
        ]
        
        # Verificar completude
        present_fields = 0
        for field in required_fields:
            if field in initiative and initiative[field]:
                present_fields += 1
            else:
                quality_metrics['missing_fields'].append(field)
        
        quality_metrics['completeness_score'] = present_fields / len(required_fields)
        
        # Verificar atualidade dos dados
        years = initiative.get('available_years', [])
        if years:
            latest_year = max(years)
            current_year = 2025  # Ano atual
            if latest_year >= current_year - 1:
                quality_metrics['data_freshness'] = 'Current'
            elif latest_year >= current_year - 3:
                quality_metrics['data_freshness'] = 'Recent'
            else:
                quality_metrics['data_freshness'] = 'Outdated'
        
        # Verificar cobertura de dados
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
