import pandas as pd
import json
from typing import Tuple, Dict, Any

def load_data(csv_path: str = None, json_path: str = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load and clean the main DataFrame and metadata using processed files."""
    
    # Se os caminhos não forem fornecidos, usar os arquivos processados
    if csv_path is None:
        csv_path = 'initiative_data/initiatives_processed.csv'
    if json_path is None:
        json_path = 'initiative_data/initiative_meta.json'
    
    # Verificar se existe o arquivo processado e usar ele prioritariamente
    try:
        processed_csv = 'initiative_data/initiatives_processed.csv'
        df = pd.read_csv(processed_csv)
        print(f"✅ Usando arquivo processado: {processed_csv}")
    except FileNotFoundError:
        # Fallback para o arquivo original se existir
        try:
            dtype_dict = {
                'Nome': 'str',
                'Tipo': 'str',
                'Resolução (m)': 'float64',
                'Acurácia (%)': 'float64',
                'Classes': 'float64',
                'Metodologia': 'str',
                'Frequência Temporal': 'str',
                'Anos Disponíveis': 'str',
                'Escopo': 'str',
                'Score Resolução': 'float64',
                'Score Geral': 'float64',
                'Categoria Acurácia': 'str',
                'Categoria Resolução': 'str'
            }
            df = pd.read_csv(csv_path, dtype=dtype_dict)
            print(f"⚠️ Usando arquivo original: {csv_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Nenhum arquivo de dados encontrado. Verifique se existe {processed_csv} ou {csv_path}")
    
    # Carregar metadados
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"✅ Metadados carregados: {json_path}")
    except FileNotFoundError:
        # Fallback para metadados processados
        try:
            processed_meta = 'initiative_data/metadata_processed.json'
            with open(processed_meta, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"⚠️ Usando metadados processados: {processed_meta}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Nenhum arquivo de metadados encontrado. Verifique se existe {json_path} ou metadata_processed.json")
    
    return df, metadata

def prepare_plot_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare DataFrame for plotting by converting to native Python types."""
    plot_data = {}
    for col in df.columns:
        if df[col].dtype == 'object':
            plot_data[col] = df[col].astype(str).fillna('N/A').tolist()
        elif df[col].dtype in ['float64', 'int64']:
            plot_data[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).tolist()
        else:
            plot_data[col] = df[col].astype(str).tolist()
    return pd.DataFrame(plot_data)
