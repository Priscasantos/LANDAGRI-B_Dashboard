"""
Modular component for temporal gaps analysis in LULC initiatives.
Identifies and visualizes gaps in data availability over time.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from typing import Dict, Any


def render_gaps_analysis(temporal_df: pd.DataFrame) -> None:
    """
    Render temporal gaps analysis with interactive controls.
    
    Args:
        temporal_df: DataFrame with temporal data of initiatives
    """
    st.markdown("### ⚠️ Temporal Gaps Analysis")
    st.markdown("*Identifying data availability gaps in LULC initiatives.*")
    
    if temporal_df.empty:
        st.warning("❌ No temporal data available for gaps analysis.")
        return
    
    # Calculate gap statistics
    gaps_stats = calculate_gaps_statistics(temporal_df)
    
    # Show summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_gap = gaps_stats['average_gap']
        st.metric("Average Gap", f"{avg_gap:.1f} years", "per initiative")
    
    with col2:
        max_gap = gaps_stats['max_gap']
        max_gap_initiative = gaps_stats['max_gap_initiative']
        st.metric("Largest Gap", f"{max_gap} years", f"in {max_gap_initiative}")
    
    with col3:
        initiatives_with_gaps = gaps_stats['initiatives_with_gaps']
        total_initiatives = len(temporal_df)
        st.metric("Initiatives with Gaps", initiatives_with_gaps, f"of {total_initiatives}")
    
    with col4:
        total_missing_years = gaps_stats['total_missing_years']
        st.metric("Total Missing Years", total_missing_years, "across all initiatives")
    
    # Visualization controls
    col1, col2 = st.columns(2)
    
    with col1:
        show_only_gaps = st.checkbox("Show only initiatives with gaps", value=False)
        
    with col2:
        min_gap_size = st.slider("Minimum gap size to show", 0, 10, 1, key="min_gap_slider")
    
    # Calcular maior gap para cada iniciativa
    def get_largest_gap(years_list):
        if isinstance(years_list, list) and len(years_list) > 1:
            anos_sorted = sorted(set(years_list))
            return max([anos_sorted[i+1] - anos_sorted[i] - 1 for i in range(len(anos_sorted)-1)] + [0])
        return 0

    filtered_gaps_df = temporal_df.copy()
    # Compatibilidade: garantir coluna correta
    if 'Anos_Lista' in filtered_gaps_df.columns and 'Years_List' not in filtered_gaps_df.columns:
        filtered_gaps_df = filtered_gaps_df.rename(columns={'Anos_Lista': 'Years_List'})
    filtered_gaps_df['Maior_Gap'] = filtered_gaps_df['Years_List'].apply(get_largest_gap)

    if show_only_gaps:
        filtered_gaps_df = filtered_gaps_df[filtered_gaps_df['Maior_Gap'] > 0]

    if min_gap_size > 0:
        filtered_gaps_df = filtered_gaps_df[filtered_gaps_df['Maior_Gap'] >= min_gap_size]

    if filtered_gaps_df.empty:
        st.info("No initiatives match the selected criteria.")
        return

    # Gerar e exibir o gráfico
    fig = plot_gaps_bar_chart(filtered_gaps_df)
    st.plotly_chart(fig, use_container_width=True, key="temporal_gaps_chart")

    # Detailed gaps information in tabular format
    with st.expander("📋 Detailed Gaps Information"):
        display_gaps_table(filtered_gaps_df)


def calculate_gaps_statistics(temporal_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate detailed statistics about temporal gaps.
    
    Args:
        temporal_df: DataFrame with temporal data
        
    Returns:
        dict: Statistics about gaps
    """
    stats = {}
    
    # Calcular gaps para cada iniciativa
    gaps_data = []
    for _, row in temporal_df.iterrows():
        years_list = row['Years_List'] if 'Years_List' in row else row.get('Anos_Lista')
        if isinstance(years_list, list) and len(years_list) > 1:
            anos_sorted = sorted(set(years_list))
            gaps = []
            for i in range(len(anos_sorted) - 1):
                gap_size = anos_sorted[i + 1] - anos_sorted[i] - 1
                if gap_size > 0:
                    gaps.append({
                        'start_year': anos_sorted[i],
                        'end_year': anos_sorted[i + 1],
                        'gap_size': gap_size
                    })
            total_gap = sum(gap['gap_size'] for gap in gaps)
            gaps_data.append({
                'initiative': row['Name'],
                'display_name': row['Display_Name'],
                'total_gap': total_gap,
                'largest_gap': max([gap['gap_size'] for gap in gaps]) if gaps else 0,
                'gap_count': len(gaps),
                'gaps_detail': gaps
            })
    
    # Calcular estatísticas agregadas
    if gaps_data:
        stats['average_gap'] = sum(item['total_gap'] for item in gaps_data) / len(gaps_data)
        stats['max_gap'] = max(item['largest_gap'] for item in gaps_data)
        stats['max_gap_initiative'] = next(
            item['display_name'] for item in gaps_data 
            if item['largest_gap'] == stats['max_gap']
        )
        stats['initiatives_with_gaps'] = sum(1 for item in gaps_data if item['total_gap'] > 0)
        stats['total_missing_years'] = sum(item['total_gap'] for item in gaps_data)
    else:
        stats = {
            'average_gap': 0,
            'max_gap': 0,
            'max_gap_initiative': 'N/A',
            'initiatives_with_gaps': 0,
            'total_missing_years': 0
        }
    
    return stats


def plot_gaps_bar_chart(gaps_data: pd.DataFrame) -> go.Figure:
    """Generate a bar chart for temporal gaps analysis.

    Args:
        gaps_data: DataFrame with gaps data

    Returns:
        go.Figure: Plotly figure with the gaps bar chart
    """
    if gaps_data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No gaps data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font={"size": 14, "color": "gray"}
        )
        fig.update_layout(
            title="Temporal Gaps Analysis - No Data",
            xaxis={"title": "Initiatives"},
            yaxis={"title": "Gap Size (Years)"}
        )
        return fig
    
    # Preparar dados para o gráfico
    initiatives = gaps_data['Display_Name'].tolist()
    gaps = gaps_data['Maior_Gap'].tolist()
    
    # Definir cores baseadas no tamanho do gap
    colors = []
    for gap in gaps:
        if gap == 0:
            colors.append('rgba(76, 175, 80, 0.8)')  # Verde para sem gaps
        elif gap <= 2:
            colors.append('rgba(255, 193, 7, 0.8)')  # Amarelo para gaps pequenos
        elif gap <= 5:
            colors.append('rgba(255, 152, 0, 0.8)')  # Laranja para gaps médios
        else:
            colors.append('rgba(244, 67, 54, 0.8)')  # Vermelho para gaps grandes
    
    # Criar o gráfico
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=initiatives,
        y=gaps,
        marker_color=colors,
        text=gaps,
        textposition='outside',
        texttemplate='%{text} years',
        hovertemplate='<b>%{x}</b><br>Largest Gap: %{y} years<extra></extra>',
        name='Temporal Gaps'
    ))
    
    # Layout do gráfico
    fig.update_layout(
        title={
            'text': "Largest Consecutive Gaps by Initiative",
            'x': 0.0,
            'xanchor': 'left'
        },
        height=500,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis={
            "title": "Initiatives",
            "tickangle": -45 if len(initiatives) > 10 else 0,
            "showgrid": True,
            "gridcolor": 'rgba(128,128,128,0.2)',
            "gridwidth": 1
        },
        yaxis={
            "title": "Gap Size (Years)",
            "showgrid": True,
            "gridcolor": 'rgba(128,128,128,0.2)',
            "gridwidth": 1,
            "zeroline": True,
            "zerolinecolor": 'rgba(128,128,128,0.4)',
            "zerolinewidth": 1
        },
    margin={"b": 120}  # larger bottom margin for rotated labels
    )
    
    # Adicionar linha de referência para gap médio
    if gaps:
        avg_gap = sum(gaps) / len(gaps)
        fig.add_hline(
            y=avg_gap,
            line_dash="dash",
            line_color="rgba(128,128,128,0.6)",
            annotation_text=f"Average: {avg_gap:.1f} years",
            annotation_position="top right"
        )
    
    # Adicionar anotação explicativa fora da área do gráfico (embaixo)
    fig.add_annotation(
        text="🟢 No gaps | 🟡 Small gaps (≤2y) | 🟠 Medium gaps (3-5y) | 🔴 Large gaps (>5y)",
        xref="paper", yref="paper",
        x=0.5, y=-0.35,  # y negativo coloca a anotação fora (abaixo) do plot
        showarrow=False,
        font={"size": 11, "color": "gray"},
        align="center"
    )

    # Aumentar margem inferior para acomodar a anotação fora do gráfico
    fig.update_layout(margin={"b": 200})
    return fig


def display_gaps_table(temporal_df: pd.DataFrame) -> None:
    """
    Exibe tabela detalhada com informações dos gaps.
    
    Args:
        temporal_df: DataFrame com dados temporais
    """
    # Criar tabela de gaps detalhada
    gaps_table_data = []
    
    for _, row in temporal_df.iterrows():
        years_list = row['Years_List'] if 'Years_List' in row else row.get('Anos_Lista')
        if isinstance(years_list, list) and len(years_list) > 1:
            anos_sorted = sorted(set(years_list))
            total_span = anos_sorted[-1] - anos_sorted[0] + 1
            available_years = len(anos_sorted)
            coverage_percentage = (available_years / total_span) * 100
            gaps_table_data.append({
                'Initiative': row['Display_Name'],
                'First Year': anos_sorted[0],
                'Last Year': anos_sorted[-1],
                'Total Span': total_span,
                'Available Years': available_years,
                'Coverage (%)': f"{coverage_percentage:.1f}%",
                'Largest Gap': max([anos_sorted[i+1] - anos_sorted[i] - 1 for i in range(len(anos_sorted)-1)] + [0]) if len(anos_sorted) > 1 else 0,
                'Years Range': f"{anos_sorted[0]}-{anos_sorted[-1]}"
            })
    
    if gaps_table_data:
        gaps_df = pd.DataFrame(gaps_table_data)
        
        # Ordenar por maior gap
        gaps_df = gaps_df.sort_values('Largest Gap', ascending=False)
        
        st.dataframe(
            gaps_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Estatísticas adicionais
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Coverage Statistics:**")
            avg_coverage = gaps_df['Coverage (%)'].str.rstrip('%').astype(float).mean()
            st.write(f"- Average Coverage: {avg_coverage:.1f}%")
            
            high_coverage = sum(1 for x in gaps_df['Coverage (%)'].str.rstrip('%').astype(float) if x >= 80)
            st.write(f"- High Coverage (≥80%): {high_coverage} initiatives")
        
        with col2:
            st.write("**Gap Distribution:**")
            no_gaps = sum(1 for x in gaps_df['Largest Gap'] if x == 0)
            st.write(f"- No gaps: {no_gaps} initiatives")
            
            large_gaps = sum(1 for x in gaps_df['Largest Gap'] if x > 5)
            st.write(f"- Large gaps (>5y): {large_gaps} initiatives")
    else:
        st.info("No detailed gap information available.")
