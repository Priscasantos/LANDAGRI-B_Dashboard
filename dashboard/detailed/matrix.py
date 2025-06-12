import streamlit as st
import pandas as pd
import sys
from pathlib import Path

def run():
    # Adicionar scripts ao path
    current_dir = Path(__file__).parent.parent.parent
    scripts_path = str(current_dir / "scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    
    # Importar módulos localmente
    try:
        from utils import safe_download_image
        from generate_graphics import plot_heatmap_tecnico
    except ImportError as e:
        st.error(f"Erro ao importar módulos: {e}")
        return
    
    if 'filtered_df' not in st.session_state or st.session_state.filtered_df.empty:
        st.warning("⚠️ Nenhuma iniciativa corresponde aos filtros selecionados na página principal. Ajuste os filtros para visualizar os dados.")
        st.stop()
    df_filt = st.session_state.filtered_df
    fig_heatmap_tech = plot_heatmap_tecnico(df_filt)
    st.plotly_chart(fig_heatmap_tech, use_container_width=True)
    safe_download_image(fig_heatmap_tech, "heatmap_comparacao_tecnica.png", "⬇️ Baixar Heatmap (PNG)")
    potential_heatmap_cols = ['Nome', 'Acurácia (%)', 'Resolução (m)', 'Classes']
    if 'Frequência Numerica' in df_filt.columns:
        potential_heatmap_cols.append('Frequência Numerica')
    heatmap_data_cols_to_export = [col for col in potential_heatmap_cols if col in df_filt.columns]
    if len(heatmap_data_cols_to_export) > 1:
        st.download_button(
            "⬇️ Baixar Dados Base do Heatmap (CSV)", 
            data=df_filt[heatmap_data_cols_to_export].to_csv(index=False).encode('utf-8'), 
            file_name="dados_base_heatmap_tecnico.csv", 
            mime="text/csv",
            help="Baixa os dados das colunas principais usadas para gerar o heatmap, antes de qualquer normalização interna da plotagem."
        )
    else:
        st.markdown("*Download da tabela de dados base do heatmap não disponível (colunas relevantes não encontradas).*")
