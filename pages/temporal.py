import streamlit as st
import pandas as pd
import plotly.express as px
from utils import safe_download_image
from config import get_initiative_color_map

def run():
    st.header("⏳ Análise Temporal Interativa por Ano")
    if 'metadata' not in st.session_state:
        st.warning("⚠️ Metadados não encontrados. Execute a página principal (app.py) primeiro.")
        st.stop()
    meta_geral = st.session_state.metadata
    all_years = sorted({ano for meta_data_item in meta_geral.values() for ano in meta_data_item.get('anos_disponiveis', []) if isinstance(ano, (int, float)) and pd.notna(ano)})
    if not all_years:
        st.warning("Não há dados anuais numéricos disponíveis nas iniciativas para esta análise.")
        st.stop()
    selected_year_slider = st.slider(
        "Selecione o ano para visualizar a cobertura das iniciativas:", 
        min_value=int(min(all_years)), 
        max_value=int(max(all_years)), 
        value=int(min(all_years)), 
        step=1,
        key="analise_temporal_year_slider"
    )
    inits_with_year = [
        nome for nome, meta_data_item in meta_geral.items() 
        if meta_data_item.get('anos_disponiveis') and selected_year_slider in meta_data_item['anos_disponiveis']
    ]
    if inits_with_year:
        bar_df_temporal = pd.DataFrame({'Iniciativa': inits_with_year, 'Disponível': [1]*len(inits_with_year)})
        initiative_color_map = get_initiative_color_map(bar_df_temporal['Iniciativa'].tolist())
        fig_bar_temporal = px.bar(bar_df_temporal, x='Iniciativa', y='Disponível', color='Iniciativa',
            color_discrete_map=initiative_color_map,
            title=f'Iniciativas com dados disponíveis em {selected_year_slider}', height=400)
        fig_bar_temporal.update_layout(showlegend=False, yaxis=dict(showticklabels=False, title=''))
        st.plotly_chart(fig_bar_temporal, use_container_width=True)
        safe_download_image(fig_bar_temporal, f"iniciativas_disponiveis_{selected_year_slider}.png", f"⬇️ Baixar Gráfico {selected_year_slider} (PNG)")
    else:
        st.info(f"Nenhuma iniciativa encontrada com dados para o ano {selected_year_slider}.")
