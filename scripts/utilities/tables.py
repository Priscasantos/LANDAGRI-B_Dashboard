import pandas as pd
import json
import os
from typing import Dict, Any

def load_processed_data():
    """Carrega dados processados do diretório data/processed"""
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Corrected path to go up two levels to workspace root, then to data/processed
        data_path = os.path.join(base_path, '..', '..', 'data', 'processed')
        
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
    if filtered_df is not None and not filtered_df.empty and 'Name' in filtered_df.columns:  # Changed 'Nome' to 'Name'
        nomes_filtrados = filtered_df['Name'].tolist() # Changed 'Nome' to 'Name'
    else:
        nomes_filtrados = list(processed_metadata.keys())
    
    for nome in nomes_filtrados:
        if nome in processed_metadata:
            meta_info = processed_metadata[nome]
            
            gap_data.append({
                'Name': nome, # Changed 'Nome' to 'Name'
                'First Year': meta_info.get('first_year'), # Changed 'primeiro_ano' to 'first_year'
                'Last Year': meta_info.get('last_year'), # Changed 'ultimo_ano' to 'last_year'
                'Number of years with temporal gap': meta_info.get('years_with_gap', 0), # Changed 'anos_com_lacuna' to 'years_with_gap'
                'Largest temporal gap': meta_info.get('largest_gap', 0), # Changed 'maior_lacuna' to 'largest_gap'
                'Type': meta_info.get('type', 'Unknown') # Changed 'tipo' to 'type' and 'Desconhecido' to 'Unknown'
            })
    
    gap_df = pd.DataFrame(gap_data)
    
    # Retornar apenas iniciativas com dados temporais válidos
    return gap_df[gap_df['First Year'].notna()].copy() # Changed 'Primeiro Ano' to 'First Year'

def safe_dataframe_display(df: pd.DataFrame) -> str:
    """Convert DataFrame to HTML table for Streamlit display."""
    return df.to_html(classes='streamlit-table', escape=False, index=False)
