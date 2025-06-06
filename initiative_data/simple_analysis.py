"""
Versão simplificada das funções de análise usando dados processados
"""
import pandas as pd
import json
from typing import Dict, Any, List

def load_simple_data():
    """Carrega dados processados simples"""
    try:
        # Carregar CSV processado
        df = pd.read_csv('initiative_data/initiatives_processed.csv')
        
        # Carregar metadados processados
        with open('initiative_data/metadata_processed.json', 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        # Carregar configuração
        with open('initiative_data/config_simple.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        return df, metadata, config
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return None, None, None

def gap_analysis_simple() -> pd.DataFrame:
    """Análise de lacunas temporais usando dados processados"""
    df, metadata, config = load_simple_data()
    
    if df is None:
        return pd.DataFrame()
    
    # Preparar dados para análise de lacunas
    gap_data = []
    
    for _, row in df.iterrows():
        nome = row['Nome']
        
        # Buscar dados nos metadados processados
        if nome in metadata:
            meta_info = metadata[nome]
            
            gap_data.append({
                'Nome': nome,
                'Primeiro Ano': meta_info.get('primeiro_ano'),
                'Último Ano': meta_info.get('ultimo_ano'), 
                'Número de anos com lacuna temporal': meta_info.get('anos_com_lacuna', 0),
                'Maior lacuna temporal': meta_info.get('maior_lacuna', 0),
                'Tipo': meta_info.get('tipo', 'Desconhecido')
            })
    
    gap_df = pd.DataFrame(gap_data)
    
    # Filtrar apenas iniciativas com lacunas > 0 ou múltiplos anos
    gap_df_filtered = gap_df[
        (gap_df['Maior lacuna temporal'] > 1) | 
        (gap_df['Número de anos com lacuna temporal'] > 0)
    ].copy()
    
    return gap_df_filtered

def get_summary_stats() -> Dict[str, Any]:
    """Estatísticas resumidas dos dados"""
    df, metadata, config = load_simple_data()
    
    if df is None:
        return {}
    
    stats = {
        'total_iniciativas': len(df),
        'tipos_distribuicao': df['Tipo'].value_counts().to_dict(),
        'metodologias_distribuicao': df['Metodologia'].value_counts().to_dict(),
        'resolucao_media': df['Resolução (m)'].mean(),
        'acuracia_media': df['Acurácia (%)'].mean(),
        'classes_media': df['Classes'].mean(),
        'anos_cobertura': {
            'minimo': df['Primeiro Ano'].min(),
            'maximo': df['Último Ano'].max(),
            'media_duracao': df['Número de Anos'].mean()
        },
        'lacunas_temporais': {
            'iniciativas_com_lacunas': len(df[df['Anos com Lacuna'] > 0]),
            'maior_lacuna_geral': df['Maior Lacuna (anos)'].max(),
            'media_lacunas': df[df['Anos com Lacuna'] > 0]['Maior Lacuna (anos)'].mean()
        }
    }
    
    return stats

def get_initiatives_by_filter(tipo=None, metodologia=None, min_acuracia=None, max_resolucao=None) -> pd.DataFrame:
    """Filtrar iniciativas com critérios específicos"""
    df, metadata, config = load_simple_data()
    
    if df is None:
        return pd.DataFrame()
    
    filtered_df = df.copy()
    
    if tipo:
        filtered_df = filtered_df[filtered_df['Tipo'] == tipo]
    
    if metodologia:
        filtered_df = filtered_df[filtered_df['Metodologia'] == metodologia]
        
    if min_acuracia:
        filtered_df = filtered_df[filtered_df['Acurácia (%)'] >= min_acuracia]
        
    if max_resolucao:
        filtered_df = filtered_df[filtered_df['Resolução (m)'] <= max_resolucao]
    
    return filtered_df

def get_temporal_coverage_summary() -> pd.DataFrame:
    """Resumo da cobertura temporal por iniciativa"""
    df, metadata, config = load_simple_data()
    
    if df is None:
        return pd.DataFrame()
    
    temporal_data = []
    
    for nome in df['Nome']:
        if nome in metadata:
            meta_info = metadata[nome]
            anos = meta_info.get('anos_disponiveis', [])
            
            temporal_data.append({
                'Nome': nome,
                'Primeiro Ano': meta_info.get('primeiro_ano'),
                'Último Ano': meta_info.get('ultimo_ano'),
                'Total de Anos': len(anos),
                'Anos Disponíveis': ', '.join(map(str, anos[:10])) + ('...' if len(anos) > 10 else ''),
                'Tipo': meta_info.get('tipo'),
                'Continuidade': 'Contínua' if meta_info.get('maior_lacuna', 0) <= 1 else 'Com Lacunas'
            })
    
    return pd.DataFrame(temporal_data)

if __name__ == "__main__":
    # Teste das funções
    print("=== Teste das Funções Simplificadas ===")
    
    # Testar carregamento
    df, metadata, config = load_simple_data()
    if df is not None:
        print(f"✅ Dados carregados: {len(df)} iniciativas")
        print(f"✅ Metadados: {len(metadata)} registros") 
        print(f"✅ Configuração carregada")
    else:
        print("❌ Erro no carregamento")
        exit(1)
    
    # Testar análise de lacunas
    gap_df = gap_analysis_simple()
    print(f"\n📊 Análise de lacunas: {len(gap_df)} iniciativas com lacunas")
    if len(gap_df) > 0:
        print(gap_df[['Nome', 'Maior lacuna temporal', 'Número de anos com lacuna temporal']].head())
    
    # Testar estatísticas
    stats = get_summary_stats()
    print(f"\n📈 Estatísticas:")
    print(f"  - Total: {stats.get('total_iniciativas', 0)} iniciativas")
    print(f"  - Acurácia média: {stats.get('acuracia_media', 0):.1f}%")
    print(f"  - Resolução média: {stats.get('resolucao_media', 0):.0f}m")
    
    # Testar filtros
    globais = get_initiatives_by_filter(tipo='Global')
    print(f"\n🌍 Iniciativas globais: {len(globais)}")
    
    # Testar cobertura temporal
    temporal = get_temporal_coverage_summary()
    print(f"\n⏱️ Resumo temporal: {len(temporal)} registros")
