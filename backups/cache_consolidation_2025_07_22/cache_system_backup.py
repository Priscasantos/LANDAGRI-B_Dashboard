"""
🚀 Sistema de Cache Consolidado - Dashboard LULC
==================================================

Sistema de cache único e funcional para todos os módulos do dashboard.
Elimina duplicações e conflitos de importação.

Author: Sistema de Otimizaç    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total_operations = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_operations * 100) if total_operations > 0 else 0
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate_percent': round(hit_rate, 2),
            'cached_items': len(self.memory_cache)
        }


# Instância global do cache manager
cache_manager = SmartCacheManager()

def get_cache_manager() -> SmartCacheManager:
    """Retorna o cache manager global consolidado"""
    return cache_manager


# Funções adicionais para compatibilidade com módulos dashboard
def prepare_geographic_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Prepara dados geográficos consolidados.
    
    Args:
        df: DataFrame com dados geográficos
        
    Returns:
        Dados geográficos processados
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        return {}
    
    geo_data = {}
    
    # Procura colunas geográficas comuns
    geo_columns = ['Country', 'Region', 'Location', 'Continent', 'country', 'region']
    
    for col in geo_columns:
        if col in df.columns:
            value_counts = df[col].value_counts().head(20)
            geo_data[f'{col.lower()}_distribution'] = {
                'labels': value_counts.index.tolist(),
                'values': value_counts.values.tolist(),
                'total_unique': df[col].nunique()
            }
    
    return geo_data


def prepare_temporal_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Prepara dados temporais consolidados.
    
    Args:
        df: DataFrame com dados temporais
        
    Returns:
        Dados temporais processados
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        return {}
    
    temporal_data = {}
    
    # Procura colunas temporais comuns
    temporal_columns = [col for col in df.columns if any(word in col.lower() for word in ['date', 'year', 'time', 'ano'])]
    
    for col in temporal_columns[:3]:  # Limita a 3 colunas temporais
        if col in df.columns:
            try:
                # Tenta converter para datetime se necessário
                if not pd.api.types.is_datetime64_any_dtype(df[col]):
                    df_temp = df.copy()
                    df_temp[col] = pd.to_datetime(df_temp[col], errors='coerce')
                else:
                    df_temp = df
                
                # Extrai anos
                df_temp['year'] = df_temp[col].dt.year
                year_counts = df_temp['year'].value_counts().sort_index()
                
                temporal_data[f'{col}_timeline'] = {
                    'years': year_counts.index.tolist(),
                    'counts': year_counts.values.tolist(),
                    'range': {
                        'start': int(year_counts.index.min()),
                        'end': int(year_counts.index.max())
                    }
                }
            except Exception:
                continue
    
    return temporal_data


def prepare_detailed_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara dados detalhados consolidados.
    
    Args:
        df: DataFrame source
        
    Returns:
        DataFrame preparado para análise detalhada
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame()
    
    # Cria cópia para não modificar original
    detailed_df = df.copy()
    
    # Adiciona colunas calculadas básicas
    try:
        # Adiciona contadores básicos
        detailed_df['row_id'] = range(1, len(detailed_df) + 1)
        
        # Calcula qualidade dos dados por linha
        detailed_df['missing_fields'] = detailed_df.isnull().sum(axis=1)
        detailed_df['completeness_percent'] = ((len(detailed_df.columns) - detailed_df['missing_fields']) / len(detailed_df.columns) * 100).round(1)
        
    except Exception as e:
        print(f"⚠️ Erro ao preparar dados detalhados: {e}")
    
    return detailed_df


def display_performance_metrics():
    """Exibe métricas de performance consolidadas"""
    if STREAMLIT_AVAILABLE and st is not None:
        try:
            stats = cache_manager.get_stats()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Cache Hits", stats['cache_hits'])
            with col2:
                st.metric("Hit Rate", f"{stats['hit_rate_percent']}%")
            with col3:
                st.metric("Cached Items", stats['cached_items'])
                
        except Exception:
            pass
    else:
        stats = cache_manager.get_stats()
        print(f"📊 Performance: {stats['cache_hits']} hits, {stats['hit_rate_percent']}% hit rate")


def preload_dashboard_data() -> bool:
    """
    Pré-carrega dados do dashboard consolidado.
    
    Returns:
        True se carregamento foi bem-sucedido
    """
    try:
        metadata, df, cache_info = load_optimized_data()
        
        if df is not None and not df.empty:
            # Armazena no session state se Streamlit estiver disponível
            if STREAMLIT_AVAILABLE and st is not None:
                st.session_state.df_interpreted = df
                st.session_state.cache_stats = cache_info
                
                if metadata is not None:
                    st.session_state.sensors_meta = metadata
            
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Erro no pré-carregamento: {e}")
        return FalseULC
Date: 2025-07-22
"""

import pandas as pd
import json
import re
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

# Configuração de paths
CURRENT_DIR = Path(__file__).parent.parent
DATA_PATH = CURRENT_DIR / "data" / "initiatives_metadata.jsonc"
SENSORS_PATH = CURRENT_DIR / "data" / "sensors_metadata.jsonc"

def load_optimized_data() -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Dict[str, Any]]:
    """
    Carrega dados das iniciativas LULC com sistema de cache otimizado.
    
    Returns:
        Tupla (metadata_df, initiatives_df, cache_info)
    """
    cache_info = {
        'cache_hits': 0, 
        'cache_misses': 1, 
        'status': 'loading',
        'source': 'consolidated_cache'
    }
    
    try:
        # Carrega dados das iniciativas
        initiatives_df = None
        if DATA_PATH.exists():
            content = _load_jsonc_file(DATA_PATH)
            if content:
                if isinstance(content, dict):
                    initiatives_df = pd.DataFrame([content])
                elif isinstance(content, list):
                    initiatives_df = pd.DataFrame(content)
                else:
                    initiatives_df = pd.DataFrame()
        
        # Carrega metadados dos sensores
        sensors_df = None
        if SENSORS_PATH.exists():
            sensors_content = _load_jsonc_file(SENSORS_PATH)
            if sensors_content and isinstance(sensors_content, dict):
                sensors_df = pd.DataFrame([sensors_content])
        
        # Atualiza informações de cache
        if initiatives_df is not None and not initiatives_df.empty:
            cache_info.update({
                'status': 'success',
                'rows': len(initiatives_df),
                'columns': len(initiatives_df.columns),
                'data_loaded': True
            })
            
            if STREAMLIT_AVAILABLE and st is not None:
                try:
                    st.sidebar.success(f"✅ Dados carregados: {len(initiatives_df)} iniciativas")
                except Exception:
                    pass
        else:
            cache_info.update({
                'status': 'empty_data',
                'data_loaded': False
            })
            
            if STREAMLIT_AVAILABLE and st is not None:
                try:
                    st.sidebar.warning("⚠️ Nenhum dado carregado")
                except Exception:
                    pass
        
        return sensors_df, initiatives_df, cache_info
        
    except Exception as e:
        cache_info.update({
            'status': 'error',
            'error': str(e),
            'data_loaded': False
        })
        
        if STREAMLIT_AVAILABLE and st is not None:
            try:
                st.sidebar.error(f"❌ Erro no carregamento: {str(e)[:50]}...")
            except Exception:
                pass
        else:
            print(f"❌ Erro no carregamento: {e}")
        
        return None, pd.DataFrame(), cache_info


def _load_jsonc_file(file_path: Path) -> Any:
    """
    Carrega arquivo JSONC removendo comentários.
    
    Args:
        file_path: Caminho para o arquivo JSONC
        
    Returns:
        Dados parseados do JSON
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove comentários JSONC
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        return json.loads(content)
    except Exception as e:
        print(f"❌ Erro ao carregar {file_path}: {e}")
        return None

def setup_performance_sidebar():
    """
    Configura sidebar de performance consolidada.
    """
    if STREAMLIT_AVAILABLE and st is not None:
        try:
            st.sidebar.markdown("### 📊 Performance")
            st.sidebar.info("🚀 Sistema consolidado ativo")
                
            # Mostra informações básicas do cache
            if hasattr(st.session_state, 'cache_stats'):
                stats = st.session_state.cache_stats
                st.sidebar.metric("Cache Hits", stats.get('cache_hits', 0))
                st.sidebar.metric("Cache Status", stats.get('status', 'unknown'))
        except Exception:
            pass
    else:
        print("📊 Performance sidebar configurada (modo debug)")


def get_filtered_data(df: pd.DataFrame, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Filtra dados de forma consolidada.
    
    Args:
        df: DataFrame para filtrar
        filters: Dicionário com filtros a aplicar
        
    Returns:
        DataFrame filtrado
    """
    if filters and isinstance(df, pd.DataFrame) and not df.empty:
        filtered_df = df.copy()
        
        for column, value in filters.items():
            if column in filtered_df.columns and value is not None:
                if isinstance(value, (list, tuple)):
                    filtered_df = filtered_df[filtered_df[column].isin(value)]
                else:
                    filtered_df = filtered_df[filtered_df[column] == value]
        
        return filtered_df
    
    return df


def calculate_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula estatísticas consolidadas.
    
    Args:
        df: DataFrame para analisar
        
    Returns:
        Dicionário com estatísticas
    """
    if isinstance(df, pd.DataFrame) and not df.empty:
        stats = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
            'missing_data_percent': (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
        }
        
        # Estatísticas por coluna categórica
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols[:5]:  # Limita a 5 colunas
            stats[f'{col}_unique_count'] = df[col].nunique()
            
        return stats
    
    return {}


def prepare_chart_data(df: pd.DataFrame, chart_type: str = 'basic') -> Dict[str, Any]:
    """
    Prepara dados para gráficos consolidados.
    
    Args:
        df: DataFrame source
        chart_type: Tipo de gráfico
        
    Returns:
        Dados preparados para gráficos
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        return {}
    
    chart_data = {'chart_type': chart_type}
    
    # Dados básicos para gráficos
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    
    for col in categorical_cols[:3]:  # Primeiras 3 colunas categóricas
        if col in df.columns:
            value_counts = df[col].value_counts().head(10)
            chart_data[f'{col}_data'] = {
                'labels': value_counts.index.tolist(),
                'values': value_counts.values.tolist()
            }
    
    return chart_data


# Cache manager consolidado
class SmartCacheManager:
    """Cache manager consolidado e funcional"""
    
    def __init__(self):
        self.memory_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get(self, key):
        if key in self.memory_cache:
            self.cache_hits += 1
            print(f"⚡ Memory cache HIT: {key[:30]}...")
            return self.memory_cache[key]
        else:
            self.cache_misses += 1
            return None
    
    def set(self, key, value):
        self.memory_cache[key] = value
        print(f"💾 Cache SET: {key[:30]}...")
    
    def get_stats(self):
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_size': len(self.memory_cache)
        }

# Instância global
cache_manager = SmartCacheManager()

def get_cache_manager():
    """Retorna o cache manager global"""
    return cache_manager
