import pandas as pd
from typing import Dict, Any, List

def gap_analysis(metadata: Dict[str, Any], filtered_df: pd.DataFrame) -> pd.DataFrame:
    gap_data = []
    for nome, meta in metadata.items():
        if 'anos_disponiveis' in meta:
            anos = sorted(meta['anos_disponiveis'])
            tipo = filtered_df[filtered_df['Nome'] == nome]['Tipo'].iloc[0] if nome in filtered_df['Nome'].values else None
            if not tipo or len(anos) < 2:
                continue
            gaps = [anos[i+1] - anos[i] for i in range(len(anos)-1)]
            max_gap = max(gaps) if gaps else 0
            gap_data.append({'Nome': nome, 'Maior Lacuna (anos)': max_gap, 'Tipo': tipo})
    return pd.DataFrame(gap_data)

def safe_dataframe_display(df: pd.DataFrame) -> str:
    """Convert DataFrame to HTML table for Streamlit display."""
    return df.to_html(classes='streamlit-table', escape=False, index=False)
