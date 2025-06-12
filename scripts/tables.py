import pandas as pd
import json
import os
from typing import Dict, Any, List

def load_processed_data():
    """Carrega dados processados do diretório initiative_data"""
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_path, '..', 'initiative_data')
        
        # Carregar metadados processados  
        meta_path = os.path.join(data_path, 'metadata_processed.json')
        with open(meta_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        return metadata
    except Exception as e:
        print(f"Erro ao carregar dados processados: {e}")
        return None

def gap_analysis(metadata: Dict[str, Any], filtered_df: pd.DataFrame) -> pd.DataFrame:
    """
    Análise de lacunas temporais usando dados processados
    """
    # Carregar dados processados
    processed_metadata = load_processed_data()
    
    if processed_metadata is None:
        return pd.DataFrame()
    
    # Preparar dados para análise de lacunas seguindo a estrutura solicitada
    gap_data = []
    
    # Usar nomes das iniciativas do filtered_df se disponível, senão usar todos
    if filtered_df is not None and not filtered_df.empty and 'Nome' in filtered_df.columns:
        nomes_filtrados = filtered_df['Nome'].tolist()
    else:
        nomes_filtrados = list(processed_metadata.keys())
    
    for nome in nomes_filtrados:
        if nome in processed_metadata:
            meta_info = processed_metadata[nome]
            
            gap_data.append({
                'Nome': nome,
                'Primeiro Ano': meta_info.get('primeiro_ano'),
                'Último Ano': meta_info.get('ultimo_ano'), 
                'Número de anos com lacuna temporal': meta_info.get('anos_com_lacuna', 0),
                'Maior lacuna temporal': meta_info.get('maior_lacuna', 0),
                'Tipo': meta_info.get('tipo', 'Desconhecido')
            })
    
    gap_df = pd.DataFrame(gap_data)
    
    # Retornar apenas iniciativas com dados temporais válidos
    return gap_df[gap_df['Primeiro Ano'].notna()].copy()

def safe_dataframe_display(df: pd.DataFrame) -> str:
    """Convert DataFrame to HTML table for Streamlit display."""
    return df.to_html(classes='streamlit-table', escape=False, index=False)
