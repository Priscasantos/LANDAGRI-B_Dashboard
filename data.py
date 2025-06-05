import pandas as pd
import json
from typing import Tuple, Dict, Any

def load_data(csv_path: str, json_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load and clean the main DataFrame and metadata."""
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
    with open(json_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
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
