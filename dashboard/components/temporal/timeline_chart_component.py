"""
Timeline Chart Component
-----------------------
Exibe o gráfico de timeline das iniciativas LULC.
"""
import streamlit as st
import pandas as pd
from plotly import graph_objects as go
from plotly import express as px

try:
    from scripts.plotting.charts.temporal_charts import plot_timeline_chart
except ImportError:
    plot_timeline_chart = None

def render_timeline_chart(df_for_analysis, raw_initiatives_metadata):
    """Renderiza o gráfico de timeline e métricas relacionadas."""
    # ... Função migrada de show_timeline_chart ...
    fig_timeline = None
    if plot_timeline_chart:
        fig_timeline = plot_timeline_chart(raw_initiatives_metadata, df_for_analysis)

    if fig_timeline is None:
        fig_timeline = create_basic_timeline_chart(raw_initiatives_metadata, df_for_analysis)

    if fig_timeline is None:
        st.info("No data to display for the timeline chart.")
        return

    st.plotly_chart(fig_timeline, use_container_width=True)

    # Métricas
    nome_to_sigla = {}
    if (
        df_for_analysis is not None
        and "Acronym" in df_for_analysis.columns
        and "Name" in df_for_analysis.columns
    ):
        for _, row in df_for_analysis.iterrows():
            if pd.notna(row["Name"]) and pd.notna(row["Acronym"]):
                nome_to_sigla[row["Name"]] = row["Acronym"]

    temporal_data = []
    for nome, details in raw_initiatives_metadata.items():
        if isinstance(details, dict) and "available_years" in details:
            anos_lista = (
                details["available_years"]
                if isinstance(details["available_years"], list)
                else []
            )
            if anos_lista:
                temporal_data.append(
                    {
                        "Nome": nome,
                        "Display_Name": nome_to_sigla.get(nome, nome[:15]),
                        "Anos_Lista": anos_lista,
                        "Primeiro_Ano": min(anos_lista),
                        "Ultimo_Ano": max(anos_lista),
                    }
                )
    temporal_df = pd.DataFrame(temporal_data)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Initiatives", len(temporal_df))
    with col2:
        if (
            not temporal_df.empty
            and "Primeiro_Ano" in temporal_df.columns
            and "Ultimo_Ano" in temporal_df.columns
        ):
            periodo_total = f"{temporal_df['Primeiro_Ano'].min()}-{temporal_df['Ultimo_Ano'].max()}"
        else:
            periodo_total = "N/A"
        st.metric("Total Period Covered", periodo_total)
    with col3:
        if not temporal_df.empty:
            total_anos_disponiveis = sum(len(anos) for anos in temporal_df["Anos_Lista"])
            st.metric("Total Years Available", total_anos_disponiveis)
        else:
            st.metric("Total Years Available", "N/A")

def create_basic_timeline_chart(metadata, df_for_analysis):
    """Create a basic timeline chart as fallback (cópia da função original)."""
    try:
        nome_to_sigla = {}
        if (
            df_for_analysis is not None
            and "Acronym" in df_for_analysis.columns
            and "Name" in df_for_analysis.columns
        ):
            for _, row in df_for_analysis.iterrows():
                if pd.notna(row["Name"]) and pd.notna(row["Acronym"]):
                    nome_to_sigla[row["Name"]] = row["Acronym"]
        fig = go.Figure()
        y_pos = 0
        colors = px.colors.qualitative.Plotly
        for i, (nome, details) in enumerate(metadata.items()):
            if isinstance(details, dict) and "available_years" in details:
                years = (
                    details["available_years"]
                    if isinstance(details["available_years"], list)
                    else []
                )
                if years:
                    display_name = nome_to_sigla.get(nome, nome[:15])
                    fig.add_trace(
                        go.Scatter(
                            x=years,
                            y=[y_pos] * len(years),
                            mode="markers",
                            name=display_name,
                            marker={
                                "size": 10,
                                "color": colors[i % len(colors)],
                                "symbol": "square",
                            },
                            hovertemplate=f"<b>{display_name}</b><br>Year: %{{x}}<extra></extra>",
                        )
                    )
                    y_pos += 1
        fig.update_layout(
            title="LULC Initiatives Timeline",
            xaxis_title="Year",
            yaxis_title="Initiative",
            height=600,
            showlegend=True,
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis={
                "title_font": {"family": "Arial Black"},
                "showgrid": True,
                "gridcolor": "rgba(128,128,128,0.2)",
            },
            yaxis={
                "title_font": {"family": "Arial Black"},
                "showgrid": True,
                "gridcolor": "rgba(128,128,128,0.2)",
            },
        )
        return fig
    except Exception as e:
        st.error(f"Error creating basic timeline chart: {e}")
        return None
