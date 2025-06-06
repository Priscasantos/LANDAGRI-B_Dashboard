"""
Funções atualizadas para tools/tables.py usando dados processados
"""
import pandas as pd
import json
import sys
import os

def load_processed_data():
    """Carrega dados processados do diretório initiative_data"""
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_path, '..', 'initiative_data')
        
        # Carregar CSV processado
        csv_path = os.path.join(data_path, 'initiatives_processed.csv')
        df = pd.read_csv(csv_path)
        
        # Carregar metadados processados  
        meta_path = os.path.join(data_path, 'metadata_processed.json')
        with open(meta_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        return df, metadata
    except Exception as e:
        print(f"Erro ao carregar dados processados: {e}")
        return None, None

def gap_analysis_updated(metadata_dummy=None, filtered_df_dummy=None) -> pd.DataFrame:
    """
    Versão atualizada da gap_analysis usando dados processados
    Mantém a mesma assinatura para compatibilidade
    """
    df, metadata = load_processed_data()
    
    if df is None or metadata is None:
        return pd.DataFrame()
    
    # Preparar dados para análise de lacunas seguindo a estrutura solicitada
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
    
    # Retornar apenas iniciativas com dados temporais válidos
    return gap_df[gap_df['Primeiro Ano'].notna()].copy()

def safe_dataframe_display(df: pd.DataFrame) -> str:
    """Convert DataFrame to HTML table for Streamlit display."""
    return df.to_html(classes='streamlit-table', escape=False, index=False)

# Teste das funções
if __name__ == "__main__":
    print("=== Teste das Funções Atualizadas para tools/tables.py ===")
    
    # Testar gap_analysis_updated
    gap_df = gap_analysis_updated()
    print(f"📊 Gap Analysis: {len(gap_df)} registros")
    
    if len(gap_df) > 0:
        print("\nColunas:", gap_df.columns.tolist())
        print("\nPrimeiros registros:")
        print(gap_df.head())
        
        # Verificar se há lacunas
        com_lacunas = gap_df[gap_df['Maior lacuna temporal'] > 1]
        print(f"\n🔍 Iniciativas com lacunas > 1: {len(com_lacunas)}")
        if len(com_lacunas) > 0:
            print(com_lacunas[['Nome', 'Maior lacuna temporal', 'Número de anos com lacuna temporal']])
    else:
        print("❌ Nenhum dado retornado")
