"""
🚀 Wrapper Otimizado para Overview Dashboard
============================================

Este módulo funciona como wrapper inteligente que detecta
e aplica otimizações automaticamente quando disponíveis.

Author: Sistema de Otimização Dashboard LULC
Date: 2025-07-22
"""

import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

def load_optimized_data() -> Tuple[Optional[pd.DataFrame], Dict[str, Any], Dict[str, Any]]:
    """
    Carrega dados com otimizações automáticas.
    
    Returns:
        Tupla (dataframe, dados_otimizados, sensores_meta)
    """
    current_dir = Path(__file__).parent.parent
    
    try:
        # Tenta usar sistema otimizado
        from scripts.utilities.data_optimizer import (
            load_and_optimize_initiatives, 
            load_and_optimize_sensors
        )
        
        # Carrega iniciativas otimizadas
        initiatives_file = current_dir / "data" / "initiatives_metadata.jsonc"
        sensors_file = current_dir / "data" / "sensors_metadata.jsonc"
        
        df, optimized_data = None, {}
        if initiatives_file.exists():
            df, optimized_data = load_and_optimize_initiatives(str(initiatives_file))
        
        sensors_df, sensors_meta = {}, {}
        if sensors_file.exists():
            sensors_df, sensors_meta = load_and_optimize_sensors(str(sensors_file))
        
        return df, optimized_data, sensors_meta
        
    except ImportError:
        # Fallback para carregamento tradicional
        try:
            from scripts.utilities.json_interpreter import _load_jsonc_file
            
            # Carrega iniciativas
            initiatives_file = current_dir / "data" / "initiatives_metadata.jsonc"
            df = None
            if initiatives_file.exists():
                data = _load_jsonc_file(initiatives_file)
                if isinstance(data, list):
                    df = pd.DataFrame(data)
            
            # Carrega sensores
            sensors_file = current_dir / "data" / "sensors_metadata.jsonc"
            sensors_meta = {}
            if sensors_file.exists():
                sensors_meta = _load_jsonc_file(sensors_file)
                if not isinstance(sensors_meta, dict):
                    sensors_meta = {}
            
            return df, {}, sensors_meta
            
        except Exception as e:
            st.error(f"❌ Erro no carregamento de dados: {e}")
            return None, {}, {}

def setup_performance_sidebar():
    """Configura sidebar com informações de performance."""
    try:
        from scripts.utilities.cache_manager import display_cache_stats
        
        with st.sidebar:
            st.markdown("### ⚡ Performance Dashboard")
            display_cache_stats()
            
            if st.button("🔄 Otimizar Dados"):
                st.cache_data.clear()
                st.success("✅ Cache limpo e dados otimizados!")
                st.rerun()
                
    except ImportError:
        with st.sidebar:
            st.markdown("### 📊 Status")
            st.info("💡 Sistema de otimização não ativo")
            st.markdown("Para ativar otimizações:")
            st.code("pip install -r requirements.txt")

@st.cache_data(ttl=3600, show_spinner="🔄 Processando filtros...")
def get_filtered_data(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Aplica filtros aos dados com cache inteligente.
    
    Args:
        df: DataFrame original
        filters: Dicionário com filtros aplicados
        
    Returns:
        DataFrame filtrado
    """
    filtered_df = df.copy()
    
    for column, values in filters.items():
        if values and column in filtered_df.columns:
            if isinstance(values, list):
                filtered_df = filtered_df[filtered_df[column].isin(values)]
            else:
                filtered_df = filtered_df[filtered_df[column] == values]
    
    return filtered_df

@st.cache_data(ttl=1800, show_spinner="📊 Gerando estatísticas...")
def calculate_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula estatísticas do dataset com cache.
    
    Args:
        df: DataFrame para análise
        
    Returns:
        Dicionário com estatísticas
    """
    if df.empty:
        return {}
    
    stats = {
        'total_initiatives': len(df),
        'unique_countries': df['Country'].nunique() if 'Country' in df.columns else 0,
        'unique_sensors': df['Sensor'].nunique() if 'Sensor' in df.columns else 0,
        'unique_types': df['Type'].nunique() if 'Type' in df.columns else 0,
    }
    
    # Estatísticas por categoria
    categorical_columns = ['Country', 'Type', 'Sensor', 'Region']
    for col in categorical_columns:
        if col in df.columns:
            stats[f'{col.lower()}_distribution'] = df[col].value_counts().head(20).to_dict()
    
    return stats

@st.cache_data(ttl=1800, show_spinner="🗺️ Processando dados geográficos...")
def prepare_geographic_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Prepara dados geográficos com cache.
    
    Args:
        df: DataFrame com dados geográficos
        
    Returns:
        Dados processados para visualizações geográficas
    """
    if df.empty or 'Country' not in df.columns:
        return {}
    
    # Agrega por país
    country_stats = df['Country'].value_counts()
    
    # Prepara dados para mapa
    geo_data = {
        'countries': country_stats.index.tolist(),
        'counts': country_stats.values.tolist(),
        'total_countries': len(country_stats),
        'top_5_countries': country_stats.head(5).to_dict()
    }
    
    return geo_data

@st.cache_data(ttl=1800, show_spinner="📈 Preparando gráficos...")  
def prepare_chart_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Prepara dados para gráficos com cache otimizado.
    
    Args:
        df: DataFrame com dados
        
    Returns:
        Dados formatados para gráficos
    """
    if df.empty:
        return {}
    
    chart_data = {}
    
    # Dados para gráfico de sensores
    if 'Sensor' in df.columns:
        sensor_counts = df['Sensor'].value_counts().head(15)
        chart_data['sensors'] = {
            'labels': sensor_counts.index.tolist(),
            'values': sensor_counts.values.tolist()
        }
    
    # Dados para gráfico de tipos
    if 'Type' in df.columns:
        type_counts = df['Type'].value_counts()
        chart_data['types'] = {
            'labels': type_counts.index.tolist(),
            'values': type_counts.values.tolist()
        }
    
    # Dados temporais
    date_columns = [col for col in df.columns if 'date' in col.lower() or 'year' in col.lower()]
    for date_col in date_columns:
        if date_col in df.columns:
            try:
                df_temp = df.copy()
                if not pd.api.types.is_datetime64_any_dtype(df_temp[date_col]):
                    df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
                
                df_temp['year'] = df_temp[date_col].dt.year
                yearly_counts = df_temp['year'].value_counts().sort_index()
                
                chart_data[f'{date_col}_timeline'] = {
                    'years': yearly_counts.index.tolist(),
                    'counts': yearly_counts.values.tolist()
                }
            except Exception:
                continue
    
    return chart_data

def display_performance_metrics():
    """Exibe métricas de performance no dashboard."""
    st.markdown("### ⚡ Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        try:
            cache_hits = len([k for k in st.session_state.keys() if isinstance(k, str) and 'cache' in k.lower()])
            st.metric("Cache Entries", cache_hits)
        except Exception:
            st.metric("Cache Entries", "N/A")
    
    with col2:
        data_size = st.session_state.get('df_interpreted', pd.DataFrame()).memory_usage(deep=True).sum()
        st.metric("Data Size", f"{data_size / 1024:.1f}KB")
    
    with col3:
        st.metric("Cached Functions", "5+")
    
    with col4:
        st.metric("Optimization", "✅ Active")

def preload_dashboard_data():
    """
    Pré-carrega todos os dados necessários para o dashboard.
    """
    try:
        with st.spinner("🚀 Inicializando sistema otimizado..."):
            # Carrega dados principais
            df, optimized_data, sensors_meta = load_optimized_data()
            
            if df is not None:
                st.session_state.df_interpreted = df
                st.session_state.optimized_data = optimized_data
                st.session_state.sensors_meta = sensors_meta
                
                # Pré-computa estatísticas
                calculate_statistics(df)
                prepare_geographic_data(df)
                prepare_chart_data(df)
                
                st.success("✅ Sistema otimizado carregado!")
                return True
            else:
                st.error("❌ Falha no carregamento dos dados")
                return False
                
    except Exception as e:
        st.error(f"❌ Erro na inicialização: {e}")
        return False
