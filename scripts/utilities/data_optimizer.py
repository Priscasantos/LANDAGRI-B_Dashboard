"""
⚡ Sistema de Otimização de Dados para Dashboard LULC
====================================================

Este módulo implementa otimizações avançadas para processamento
de dados fixos, eliminando recomputações desnecessárias.

Features:
- Pré-processamento inteligente
- Dados agregados otimizados
- Índices pré-computados
- Transformações em lote
- Compressão automática

Author: Sistema de Otimização Dashboard LULC
Date: 2025-07-22
"""

import pandas as pd
from typing import Dict, Any, Tuple, Optional
import streamlit as st
from pathlib import Path
import json
from .cache_manager import cached, get_cache_manager

class DataOptimizer:
    """
    🚀 Otimizador de Dados para Performance Máxima
    
    Pré-processa e otimiza dados fixos para eliminar
    recomputações em tempo de execução.
    """
    
    def __init__(self):
        """Inicializa o otimizador."""
        self.cache_manager = get_cache_manager()
        self._optimized_data: Dict[str, Any] = {}
        
    @cached(ttl_seconds=7200, persist=True, key_prefix="optimized_")
    def optimize_initiatives_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        🎯 Otimiza dados de iniciativas com agregações pré-computadas.
        
        Args:
            df: DataFrame com dados das iniciativas
            
        Returns:
            Dicionário com dados otimizados e agregações
        """
        optimized = {}
        
        # ===== AGREGAÇÕES BÁSICAS =====
        optimized['total_initiatives'] = len(df)
        optimized['unique_sensors'] = df['Sensor'].nunique() if 'Sensor' in df.columns else 0
        optimized['unique_countries'] = df['Country'].nunique() if 'Country' in df.columns else 0
        
        # ===== DADOS CATEGÓRICOS OTIMIZADOS =====
        if 'Sensor' in df.columns:
            sensor_counts = df['Sensor'].value_counts().to_dict()
            optimized['sensor_distribution'] = sensor_counts
            optimized['top_sensors'] = list(sensor_counts.keys())[:10]
        
        if 'Type' in df.columns:
            type_counts = df['Type'].value_counts().to_dict()
            optimized['type_distribution'] = type_counts
        
        if 'Country' in df.columns:
            country_counts = df['Country'].value_counts().to_dict()
            optimized['country_distribution'] = country_counts
            optimized['top_countries'] = list(country_counts.keys())[:15]
        
        # ===== ANÁLISES TEMPORAIS PRÉ-COMPUTADAS =====
        date_columns = [col for col in df.columns if 'date' in col.lower() or 'year' in col.lower()]
        
        for date_col in date_columns:
            if date_col in df.columns:
                try:
                    # Converte para datetime se necessário
                    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
                        df_temp = df.copy()
                        df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
                    else:
                        df_temp = df
                    
                    # Extrai ano para análises
                    df_temp['year'] = df_temp[date_col].dt.year
                    year_counts = df_temp['year'].value_counts().sort_index().to_dict()
                    optimized[f'{date_col}_yearly'] = year_counts
                    
                    # Estatísticas temporais
                    optimized[f'{date_col}_range'] = {
                        'min': df_temp[date_col].min().isoformat() if pd.notna(df_temp[date_col].min()) else None,
                        'max': df_temp[date_col].max().isoformat() if pd.notna(df_temp[date_col].max()) else None
                    }
                except Exception:
                    continue
        
        # ===== ANÁLISES GEOGRÁFICAS =====
        geo_columns = ['Country', 'Region', 'Location', 'Continent']
        for geo_col in geo_columns:
            if geo_col in df.columns:
                optimized[f'{geo_col.lower()}_stats'] = {
                    'unique_count': df[geo_col].nunique(),
                    'top_5': df[geo_col].value_counts().head(5).to_dict()
                }
        
        # ===== DADOS PARA FILTROS OTIMIZADOS =====
        optimized['filter_options'] = {}
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_columns:
            if col in df.columns and df[col].nunique() < 100:  # Evita colunas com muitos valores únicos
                unique_values = sorted(df[col].dropna().unique().tolist())
                optimized['filter_options'][col] = unique_values
        
        # ===== MÉTRICAS DE QUALIDADE DOS DADOS =====
        optimized['data_quality'] = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_data_percent': (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100),
            'columns_with_missing': df.isnull().any().sum(),
            'duplicate_rows': df.duplicated().sum()
        }
        
        # ===== DADOS PARA TABELAS PAGINADAS =====
        optimized['paginated_data'] = self._create_paginated_chunks(df)
        
        return optimized
    
    def _create_paginated_chunks(self, df: pd.DataFrame, chunk_size: int = 50) -> Dict[int, pd.DataFrame]:
        """Cria chunks paginados dos dados."""
        chunks = {}
        total_pages = (len(df) + chunk_size - 1) // chunk_size
        
        for page in range(total_pages):
            start_idx = page * chunk_size
            end_idx = min((page + 1) * chunk_size, len(df))
            chunks[page] = df.iloc[start_idx:end_idx].copy()
        
        return chunks
    
    @cached(ttl_seconds=7200, persist=True, key_prefix="charts_")
    def optimize_chart_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        📊 Pré-computa dados para gráficos otimizados.
        
        Args:
            df: DataFrame com dados das iniciativas
            
        Returns:
            Dados otimizados para gráficos
        """
        chart_data = {}
        
        # ===== DADOS PARA GRÁFICO DE BARRAS (SENSORES) =====
        if 'Sensor' in df.columns:
            sensor_data = df['Sensor'].value_counts().head(15)
            chart_data['sensor_bar_chart'] = {
                'labels': sensor_data.index.tolist(),
                'values': sensor_data.values.tolist(),
                'total': sensor_data.sum()
            }
        
        # ===== DADOS PARA GRÁFICO DE PIZZA (TIPOS) =====
        if 'Type' in df.columns:
            type_data = df['Type'].value_counts()
            chart_data['type_pie_chart'] = {
                'labels': type_data.index.tolist(),
                'values': type_data.values.tolist()
            }
        
        # ===== DADOS PARA GRÁFICO TEMPORAL =====
        date_columns = [col for col in df.columns if 'date' in col.lower() or 'year' in col.lower()]
        
        for date_col in date_columns:
            if date_col in df.columns:
                try:
                    df_temp = df.copy()
                    if not pd.api.types.is_datetime64_any_dtype(df_temp[date_col]):
                        df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
                    
                    df_temp['year'] = df_temp[date_col].dt.year
                    yearly_data = df_temp['year'].value_counts().sort_index()
                    
                    chart_data[f'{date_col}_timeline'] = {
                        'years': yearly_data.index.tolist(),
                        'counts': yearly_data.values.tolist()
                    }
                except Exception:
                    continue
        
        # ===== DADOS PARA GRÁFICO GEOGRÁFICO =====
        if 'Country' in df.columns:
            country_data = df['Country'].value_counts().head(20)
            chart_data['geographic_chart'] = {
                'countries': country_data.index.tolist(),
                'counts': country_data.values.tolist()
            }
        
        return chart_data
    
    @cached(ttl_seconds=3600, persist=True, key_prefix="search_")
    def optimize_search_indices(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        🔍 Cria índices otimizados para busca e filtros.
        
        Args:
            df: DataFrame com dados das iniciativas
            
        Returns:
            Índices otimizados para busca
        """
        indices = {}
        
        # ===== ÍNDICE DE TEXTO COMPLETO =====
        text_columns = ['Name', 'Description', 'Organization', 'Country']
        searchable_text = []
        
        for idx, row in df.iterrows():
            text_parts = []
            for col in text_columns:
                if col in df.columns and pd.notna(row[col]):
                    text_parts.append(str(row[col]).lower())
            
            searchable_text.append(' '.join(text_parts))
        
        indices['searchable_text'] = searchable_text
        indices['row_indices'] = df.index.tolist()
        
        # ===== ÍNDICES CATEGÓRICOS =====
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_columns:
            if col in df.columns:
                # Cria mapeamento de valor -> lista de índices
                value_to_indices = {}
                for idx, value in enumerate(df[col]):
                    if pd.notna(value):
                        value_str = str(value).lower()
                        if value_str not in value_to_indices:
                            value_to_indices[value_str] = []
                        value_to_indices[value_str].append(idx)
                
                indices[f'{col}_index'] = value_to_indices
        
        return indices
    
    def get_optimized_data(self, key: str) -> Any:
        """Recupera dados otimizados do cache."""
        return self.cache_manager.get(f"optimized_{key}")
    
    def invalidate_optimization(self, pattern: Optional[str] = None):
        """Invalida otimizações baseado em padrão."""
        if pattern:
            self.cache_manager.invalidate(f"optimized_{pattern}")
        else:
            self.cache_manager.invalidate("optimized_")

# Instância global do otimizador
_data_optimizer = None

def get_data_optimizer() -> DataOptimizer:
    """Retorna instância singleton do otimizador."""
    global _data_optimizer
    if _data_optimizer is None:
        _data_optimizer = DataOptimizer()
    return _data_optimizer

@cached(ttl_seconds=3600, persist=True, key_prefix="processed_")
def load_and_optimize_initiatives(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    🚀 Carrega e otimiza dados de iniciativas em uma operação.
    
    Args:
        file_path: Caminho para o arquivo de dados
        
    Returns:
        Tupla com DataFrame e dados otimizados
    """
    # Carrega dados
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # Otimiza dados
    optimizer = get_data_optimizer()
    optimized_data = optimizer.optimize_initiatives_data(df)
    chart_data = optimizer.optimize_chart_data(df)
    search_indices = optimizer.optimize_search_indices(df)
    
    # Combina todas as otimizações
    full_optimization = {
        'basic_stats': optimized_data,
        'chart_data': chart_data,
        'search_indices': search_indices
    }
    
    return df, full_optimization

@cached(ttl_seconds=1800, persist=True, key_prefix="sensors_")
def load_and_optimize_sensors(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    📡 Carrega e otimiza dados de sensores.
    
    Args:
        file_path: Caminho para o arquivo de sensores
        
    Returns:
        Tupla com DataFrame e dados otimizados
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # Otimizações específicas para sensores
    optimizations = {
        'total_sensors': len(df),
        'sensor_types': df['type'].value_counts().to_dict() if 'type' in df.columns else {},
        'resolution_stats': df['resolution'].value_counts().to_dict() if 'resolution' in df.columns else {},
        'unique_platforms': df['platform'].nunique() if 'platform' in df.columns else 0
    }
    
    return df, optimizations

def preload_all_data():
    """
    🎯 Pré-carrega todos os dados otimizados na inicialização.
    
    Esta função deve ser chamada uma vez na inicialização do app
    para garantir que todos os dados estejam otimizados e em cache.
    """
    try:
        # Caminhos dos arquivos
        initiatives_file = "data/initiatives_metadata.jsonc"
        sensors_file = "data/sensors_metadata.jsonc"
        
        if Path(initiatives_file).exists():
            st.info("🚀 Pré-carregando dados de iniciativas...")
            load_and_optimize_initiatives(initiatives_file)
            
        if Path(sensors_file).exists():
            st.info("📡 Pré-carregando dados de sensores...")
            load_and_optimize_sensors(sensors_file)
            
        # Mostra estatísticas do cache
        cache_stats = get_cache_manager().get_stats()
        st.success(f"✅ Dados otimizados carregados! Hit Rate: {cache_stats['hit_rate_percent']}%")
        
    except Exception as e:
        st.error(f"❌ Erro no pré-carregamento: {e}")

def display_optimization_stats():
    """Exibe estatísticas de otimização no Streamlit."""
    st.subheader("⚡ Estatísticas de Otimização")
    
    optimizer = get_data_optimizer()
    cache_manager = get_cache_manager()
    
    # Estatísticas do cache
    stats = cache_manager.get_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Cache Hit Rate", f"{stats['hit_rate_percent']}%")
        st.metric("Entradas em Memória", stats['memory_entries'])
    
    with col2:
        st.metric("Uso de Memória", f"{stats['memory_usage_mb']:.1f}MB")
        st.metric("Entradas em Disco", stats['disk_entries'])
    
    with col3:
        st.metric("Compressões", stats['compressions'])
        st.metric("Evictions", stats['evictions'])
    
    # Gráfico de performance
    if stats['hits'] + stats['misses'] > 0:
        cache_data = pd.DataFrame({
            'Tipo': ['Cache Hits', 'Cache Misses'],
            'Quantidade': [stats['hits'], stats['misses']]
        })
        
        st.bar_chart(cache_data.set_index('Tipo'))
    
    # Botões de controle
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Recarregar Otimizações"):
            optimizer.invalidate_optimization()
            preload_all_data()
            st.rerun()
    
    with col2:
        if st.button("🗑️ Limpar Cache Completo"):
            cache_manager.invalidate()
            st.success("Cache limpo!")
            st.rerun()
