import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import sys
from pathlib import Path

# Import English translations
from scripts.utilities.english_translations import (
    UI_TRANSLATIONS, METRICS_TRANSLATIONS, CHART_TRANSLATIONS
)

def run():
    st.header("🔍 Detailed Analysis - Custom Comparisons")
    st.markdown("Select two or more initiatives for detailed comparative analysis.")
    
    # Adicionar scripts ao path
    current_dir = Path(__file__).parent.parent.parent
    scripts_path = str(current_dir / "scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
        
    # Importar módulos localmente
    try:
        from scripts.data_generation.data_processing import load_data
        from scripts.utilities.utils import safe_download_image
    except ImportError as e:
        st.error(f"Erro ao importar módulos: {e}")
        return
    
    if 'df_geral' not in st.session_state or st.session_state.df_geral.empty:
        # Tentar carregar dados processados diretamente
        df_loaded, metadata_loaded = load_data(
            "data/processed/initiatives_processed.csv",
            "data/processed/metadata_processed.json"
        )
        if df_loaded is not None and not df_loaded.empty:
            st.session_state.df_geral = df_loaded
            st.session_state.metadata = metadata_loaded
        else:
            st.warning("⚠️ Data not found. Run the main page (app.py) first.")
            st.stop()
    df_geral = st.session_state.df_geral
    
    # Create name to sigla mapping from DataFrame
    nome_to_sigla = {}
    if 'Sigla' in df_geral.columns:
        for _, row in df_geral.iterrows():
            nome_to_sigla[row['Nome']] = row['Sigla']
    
    # Add Display_Name column for consistent sigla usage
    df_geral = df_geral.copy()
    df_geral['Display_Name'] = df_geral.apply(
        lambda row: nome_to_sigla.get(row['Nome'], row['Nome'][:10]), axis=1
    )
    
    # Initiative selection for comparison
    selected_initiatives = st.multiselect(
        "🎯 Select initiatives to compare:",
        options=df_geral["Nome"].tolist(),
        default=df_geral["Nome"].tolist()[:min(3, len(df_geral))],
        help="Choose 2 or more initiatives for detailed comparative analysis"
    )
    
    if len(selected_initiatives) < 2:
        st.info("👈 Select at least two initiatives in the menu above to start analysis.")
        return
    
    # Filter data for selected initiatives
    df_filtered = df_geral[df_geral["Nome"].isin(selected_initiatives)].copy()

    # Standardized tabs with English translations
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dual Bars",
        "🎯 Radar",
        "🔥 Heatmap", 
        "📈 Table",
        "📅 Annual Coverage"
    ])

    with tab1:
        # Dual Bars using siglas
        df_filtered['resolucao_norm'] = (1 / df_filtered['Resolução (m)']) / (1 / df_filtered['Resolução (m)']).max()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_filtered['Display_Name'],  # Use siglas
            x=df_filtered['Acurácia (%)'],
            name='Accuracy (%)',
            orientation='h',
            marker_color='royalblue'
        ))
        fig.add_trace(go.Bar(
            y=df_filtered['Display_Name'],  # Use siglas
            x=df_filtered['resolucao_norm'] * 100,
            name='Resolution (normalized)',
            orientation='h',
            marker_color='orange'
        ))
        fig.update_layout(
            barmode='group', 
            xaxis_title='Value (%)', 
            yaxis_title='Initiative',
            title='Comparison: Accuracy vs Resolution',
            height=max(400, len(df_filtered) * 25)
        )
        st.plotly_chart(fig, use_container_width=True)
        safe_download_image(fig, "dual_bars_detailed.png", "⬇️ Download Chart")

    with tab2:
        # Radar using siglas
        radar_columns = ['Acurácia (%)', 'Resolução (m)', 'Classes']
        available_radar_cols = [col for col in radar_columns if col in df_filtered.columns]
        if len(available_radar_cols) >= 2:
            radar_df = df_filtered[['Display_Name'] + available_radar_cols].copy()
            for col in available_radar_cols:
                min_val, max_val = radar_df[col].min(), radar_df[col].max()
                if max_val - min_val > 0:
                    if col == 'Resolução (m)':
                        radar_df[col] = 1 - (radar_df[col] - min_val) / (max_val - min_val)
                    else:
                        radar_df[col] = (radar_df[col] - min_val) / (max_val - min_val)
                else:
                    radar_df[col] = 0.5
            fig_radar = go.Figure()
            colors = px.colors.qualitative.Set1
            for i, (idx, row) in enumerate(radar_df.iterrows()):
                values = row[available_radar_cols].tolist()
                values_closed = values + [values[0]]
                theta_closed = available_radar_cols + [available_radar_cols[0]]
                fig_radar.add_trace(go.Scatterpolar(
                    r=values_closed,
                    theta=theta_closed,
                    fill='toself',
                    name=row['Display_Name'],  # Use siglas
                    line_color=colors[i % len(colors)]
                ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                title='Multi-dimensional Comparison (Radar)',
                height=600
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            safe_download_image(fig_radar, "radar_chart_detailed.png", "⬇️ Download Chart")
        else:
            st.warning("Insufficient data for radar chart.")

    with tab3:
        # Heatmap using siglas
        if len(available_radar_cols) >= 2:
            heatmap_df = radar_df.set_index('Display_Name')[available_radar_cols]  # Use siglas
            fig_heatmap = px.imshow(
                heatmap_df.values,
                x=heatmap_df.columns,
                y=heatmap_df.index,
                color_continuous_scale='viridis',
                aspect='auto',
                title='Performance Heatmap (normalized values)',
                labels=dict(x='Metric', y='Initiative', color='Normalized Value')
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
            safe_download_image(fig_heatmap, "heatmap_detailed.png", "⬇️ Download Chart")
        else:
            st.warning("Insufficient data for heatmap.")

    with tab4:
        # Table
        st.dataframe(df_filtered, use_container_width=True)   
        
    with tab5:
        st.subheader("Annual Coverage by Initiative (Multiple Selection)")
        meta = st.session_state.get('metadata', {})
        
        if not selected_initiatives:
            st.info("Select at least one initiative to view annual coverage.")
        else:            
            try:
                from scripts.plotting.generate_graphics import plot_annual_coverage_multiselect
                fig_annual = plot_annual_coverage_multiselect(meta, df_filtered, selected_initiatives)
                st.plotly_chart(fig_annual, use_container_width=True)
                safe_download_image(fig_annual, "annual_coverage_detailed.png", "⬇️ Download Coverage (PNG)")
            except ImportError:
                st.error("Annual coverage function not available")
