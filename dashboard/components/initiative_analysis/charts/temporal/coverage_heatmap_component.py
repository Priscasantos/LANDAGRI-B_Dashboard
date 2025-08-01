"""
Componente modular para heatmap de cobertura temporal das iniciativas LULC.
Visualiza a disponibilidade de dados ao longo do tempo em formato de heatmap.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_coverage_heatmap(temporal_df: pd.DataFrame) -> None:
    """
    Renderiza o heatmap de cobertura temporal com controles interativos.

    Args:
        temporal_df: DataFrame com dados temporais das iniciativas
    """
    st.markdown("### 🔥 Coverage Heatmap")
    st.markdown("*Visualizing data availability across time and initiatives*")

    if temporal_df.empty:
        st.warning("❌ No temporal data available for coverage heatmap.")
        return

    # Controles de visualização
    col1, col2, col3 = st.columns(3)

    with col1:
        start_year = st.selectbox(
            "Start Year",
            options=list(range(1985, 2025)),
            index=list(range(1985, 2025)).index(1990),
            key="heatmap_start_year"
        )

    with col2:
        end_year = st.selectbox(
            "End Year",
            options=list(range(1985, 2025)),
            index=list(range(1985, 2025)).index(2023),
            key="heatmap_end_year"
        )

    with col3:
        sort_by = st.selectbox(
            "Sort initiatives by",
            ["Name", "First Year", "Last Year", "Coverage"],
            index=2,
            key="heatmap_sort"
        )

    # Validar intervalo de anos
    if start_year >= end_year:
        st.error("Start year must be less than end year.")
        return

    # Gerar e exibir o heatmap
    fig = plot_coverage_heatmap_chart(temporal_df, start_year, end_year, sort_by)
    st.plotly_chart(fig, use_container_width=True)

    # Estatísticas de cobertura
    with st.expander("📊 Coverage Statistics"):
        display_coverage_statistics(temporal_df, start_year, end_year)


def plot_coverage_heatmap_chart(
    temporal_data: pd.DataFrame,
    start_year: int = 1990,
    end_year: int = 2023,
    sort_by: str = "Last Year"
) -> go.Figure:
    """
    Gera heatmap da cobertura temporal das iniciativas.

    Args:
            text="No temporal data available for coverage heatmap",
        start_year: Ano inicial para visualização
        end_year: Ano final para visualização
        sort_by: Critério de ordenação das iniciativas

    Returns:
        go.Figure: Figura Plotly com heatmap de cobertura
    """
    if temporal_data.empty or ('Years_List' not in temporal_data.columns and 'Anos_Lista' not in temporal_data.columns):
        fig = go.Figure()
        fig.add_annotation(
            text="No temporal data available for coverage heatmap",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font={"size": 14, "color": "gray"}
        )
        fig.update_layout(
            title="Coverage Heatmap - No Data",
            xaxis={"title": "Year"},
            yaxis={"title": "Initiatives"}
        )
        return fig

    # Criar matriz de cobertura
    years_range = list(range(start_year, end_year + 1))
    initiatives_data = []
    for _, row in temporal_data.iterrows():
        years_list = row['Years_List'] if 'Years_List' in row else row.get('Anos_Lista')
        if isinstance(years_list, list):
            coverage_array = [1 if year in years_list else 0 for year in years_range]
            initiatives_data.append({
                'initiative': row['Display_Name'],
                'full_name': row['Name'],
                'coverage': coverage_array,
                'first_year': min(years_list) if years_list else start_year,
                'last_year': max(years_list) if years_list else start_year,
                'total_coverage': sum(coverage_array),
                'coverage_percentage': (sum(coverage_array) / len(coverage_array)) * 100
            })

    if not initiatives_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No coverage data available for the selected period",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font={"size": 14, "color": "gray"}
        )
        fig.update_layout(
            title="Coverage Heatmap - No Coverage Data",
            xaxis={"title": "Year"},
            yaxis={"title": "Initiatives"}
        )
        return fig

    # Ordenar iniciativas baseado no critério selecionado
    if sort_by == "Name":
        initiatives_data.sort(key=lambda x: x['initiative'])
    elif sort_by == "First Year":
        initiatives_data.sort(key=lambda x: x['first_year'])
    elif sort_by == "Last Year":
        initiatives_data.sort(key=lambda x: x['last_year'], reverse=True)
    elif sort_by == "Coverage":
        initiatives_data.sort(key=lambda x: x['coverage_percentage'], reverse=True)

    # Preparar dados para o heatmap
    z_data = [item['coverage'] for item in initiatives_data]
    y_labels = [item['initiative'] for item in initiatives_data]

    # Criar texto customizado para hover
    hover_text = []
    for _, item in enumerate(initiatives_data):
        row_text = []
        for j, year in enumerate(years_range):
            if item['coverage'][j] == 1:
                status = "Available"
                color = "🟢"
            else:
                status = "Not Available"
                color = "⚪"

            hover_info = (
                f"<b>{item['initiative']}</b><br>"
                f"Year: {year}<br>"
                f"Status: {color} {status}<br>"
                f"Coverage: {item['coverage_percentage']:.1f}%"
            )
            row_text.append(hover_info)
        hover_text.append(row_text)

    # Criar o heatmap
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=years_range,
        y=y_labels,
        colorscale=[
            [0, 'rgba(239, 239, 239, 0.8)'],  # Cinza claro para não disponível
            [1, 'rgba(76, 175, 80, 0.8)']     # Verde para disponível
        ],
        showscale=True,
        colorbar={
            "title": "Data Availability",
            "tickvals": [0, 1],
            "ticktext": ["Not Available", "Available"],
            "thickness": 15,
            "len": 0.7
        },
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_text
    ))

    # Layout do heatmap
    fig.update_layout(
        title={
            'text': f"LULC Initiatives Coverage Heatmap ({start_year}-{end_year})",
            'x': 0.5,
            'xanchor': 'center'
        },
        height=max(400, len(y_labels) * 25),  # Altura dinâmica baseada no número de iniciativas
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis={
            "title": "Year",
            "side": "bottom",
            "tickangle": -45 if len(years_range) > 20 else 0,
            "dtick": 2 if len(years_range) > 20 else 1,
            "showgrid": False
        },
        yaxis={
            "title": "Initiatives",
            "side": "left",
            "automargin": True,
            "showgrid": False
        },
        margin={"l": 150, "r": 100, "t": 80, "b": 100}
    )

    # Adicionar linha de separação visual a cada 5 anos
    for year in range(start_year, end_year + 1, 5):
        if year in years_range:
            fig.add_vline(
                x=year,
                line_color="rgba(0,0,0,0.2)",
                line_width=1,
                line_dash="dot"
            )

    return fig


def display_coverage_statistics(
    temporal_df: pd.DataFrame,
    start_year: int,
    end_year: int
) -> None:
    """
    Exibe estatísticas detalhadas de cobertura.

    Args:
        temporal_df: DataFrame com dados temporais
        start_year: Ano inicial do período
        end_year: Ano final do período
    """
    years_range = list(range(start_year, end_year + 1))
    total_years = len(years_range)

    # Calcular estatísticas por iniciativa
    stats_data = []
    year_coverage = dict.fromkeys(years_range, 0)

    for _, row in temporal_df.iterrows():
        years_list = row['Years_List'] if 'Years_List' in row else row.get('Anos_Lista')
        if isinstance(years_list, list):
            anos_no_periodo = [ano for ano in years_list if start_year <= ano <= end_year]
            coverage_count = len(anos_no_periodo)
            coverage_percentage = (coverage_count / total_years) * 100
            stats_data.append({
                'Initiative': row['Display_Name'],
                'Years Available': coverage_count,
                'Coverage (%)': f"{coverage_percentage:.1f}%",
                'First Year': min(anos_no_periodo) if anos_no_periodo else 'N/A',
                'Last Year': max(anos_no_periodo) if anos_no_periodo else 'N/A',
                'Years in Period': ', '.join(map(str, sorted(anos_no_periodo))) if anos_no_periodo else 'None'
            })
            for ano in anos_no_periodo:
                year_coverage[ano] += 1

    # Exibir tabela de estatísticas por iniciativa
    if stats_data:
        st.write("**Coverage by Initiative:**")
        stats_df = pd.DataFrame(stats_data)
        stats_df = stats_df.sort_values('Coverage (%)', ascending=False)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

        # Estatísticas agregadas
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Period Summary:**")
            avg_coverage = stats_df['Coverage (%)'].str.rstrip('%').astype(float).mean()
            st.write(f"- Average Coverage: {avg_coverage:.1f}%")

            high_coverage = sum(1 for x in stats_df['Coverage (%)'].str.rstrip('%').astype(float) if x >= 75)
            st.write(f"- High Coverage (≥75%): {high_coverage} initiatives")

            complete_coverage = sum(1 for x in stats_df['Coverage (%)'].str.rstrip('%').astype(float) if x == 100)
            st.write(f"- Complete Coverage: {complete_coverage} initiatives")

        with col2:
            st.write("**Year Coverage:**")
            max_coverage_year = max(year_coverage.keys(), key=lambda x: year_coverage[x])
            st.write(f"- Best Covered Year: {max_coverage_year} ({year_coverage[max_coverage_year]} initiatives)")

            min_coverage_year = min(year_coverage.keys(), key=lambda x: year_coverage[x])
            st.write(f"- Least Covered Year: {min_coverage_year} ({year_coverage[min_coverage_year]} initiatives)")

            avg_year_coverage = sum(year_coverage.values()) / len(year_coverage)
            st.write(f"- Average per Year: {avg_year_coverage:.1f} initiatives")

        # Gráfico de cobertura por ano
        st.write("**Coverage by Year:**")
        year_coverage_fig = create_year_coverage_chart(year_coverage)
        st.plotly_chart(year_coverage_fig, use_container_width=True)


def create_year_coverage_chart(year_coverage: dict[int, int]) -> go.Figure:
    """
    Cria gráfico de barras da cobertura por ano.

    Args:
        year_coverage: Dicionário com cobertura por ano

    Returns:
        go.Figure: Gráfico de barras da cobertura por ano
    """
    years = list(year_coverage.keys())
    coverage_counts = list(year_coverage.values())

    fig = go.Figure(data=go.Bar(
        x=years,
        y=coverage_counts,
        marker_color='rgba(76, 175, 80, 0.7)',
        text=coverage_counts,
        textposition='outside',
        hovertemplate='<b>Year: %{x}</b><br>Initiatives: %{y}<extra></extra>'
    ))

    fig.update_layout(
        title="Number of Initiatives Available by Year",
        height=300,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis={
            "title": "Year",
            "showgrid": True,
            "gridcolor": 'rgba(128,128,128,0.2)',
            "tickangle": -45 if len(years) > 15 else 0
        },
        yaxis={
            "title": "Number of Initiatives",
            "showgrid": True,
            "gridcolor": 'rgba(128,128,128,0.2)'
        }
    )

    return fig
