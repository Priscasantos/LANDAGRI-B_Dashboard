"""
Exemplo de Uso - Gráficos Consolidados do Calendar
==================================================

Demonstra como usar os componentes consolidados do old_calendar
em diferentes contextos dentro do dashboard.

Autor: LANDAGRI-B Project Team 
Data: 2025-08-07
"""

import streamlit as st
from typing import Dict


def example_complete_analysis(filtered_data: Dict) -> None:
    """
    Exemplo 1: Análise completa usando a função consolidada principal.
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
    """
    from dashboard.components.agricultural_analysis.charts.calendar import render_complete_calendar_analysis
    
    st.markdown("## 📅 Exemplo 1: Análise Completa")
    st.markdown("Usa a função principal que renderiza todos os gráficos organizados:")
    
    # Uma única chamada renderiza toda a análise
    render_complete_calendar_analysis(filtered_data)


def example_modular_usage(filtered_data: Dict) -> None:
    """
    Exemplo 2: Uso modular de seções específicas.
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
    """
    from dashboard.components.agricultural_analysis.charts.calendar import (
        render_crop_distribution_charts,
        render_monthly_activity_charts,
        render_regional_analysis_for_region
    )
    
    st.markdown("## 🧩 Exemplo 2: Uso Modular")
    st.markdown("Renderiza apenas seções específicas conforme necessário:")
    
    # Seletor de análise
    analysis_type = st.selectbox(
        "Escolha o tipo de análise:",
        [
            "Distribuição de Culturas",
            "Atividades Mensais", 
            "Análise Regional Específica"
        ]
    )
    
    if analysis_type == "Distribuição de Culturas":
        render_crop_distribution_charts(filtered_data)
    
    elif analysis_type == "Atividades Mensais":
        render_monthly_activity_charts(filtered_data)
    
    elif analysis_type == "Análise Regional Específica":
        # Seleciona região específica
        from dashboard.components.agricultural_analysis.charts.calendar import get_region_states
        regions = list(get_region_states().keys())
        selected_region = st.selectbox("Selecione uma região:", regions)
        
        if selected_region:
            render_regional_analysis_for_region(filtered_data, selected_region)


def example_individual_charts(filtered_data: Dict) -> None:
    """
    Exemplo 3: Uso de gráficos individuais.
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
    """
    from dashboard.components.agricultural_analysis.charts.calendar import (
        create_crop_type_distribution_chart,
        create_planting_vs_harvesting_per_month_chart,
        create_regional_heatmap_chart
    )
    
    st.markdown("## 🎯 Exemplo 3: Gráficos Individuais")
    st.markdown("Usa gráficos específicos em layouts customizados:")
    
    # Layout customizado com 3 colunas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🌾 Distribuição")
        fig1 = create_crop_type_distribution_chart(filtered_data)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("#### 📅 Plantio vs Colheita")
        fig2 = create_planting_vs_harvesting_per_month_chart(filtered_data)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
    
    with col3:
        st.markdown("#### 🗺️ Regional - Sul")
        fig3 = create_regional_heatmap_chart(filtered_data, "Sul")
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)


def example_custom_dashboard(filtered_data: Dict) -> None:
    """
    Exemplo 4: Dashboard customizado usando múltiplos componentes.
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
    """
    from dashboard.components.agricultural_analysis.charts.calendar import (
        create_consolidated_calendar_matrix_chart,
        create_main_crops_seasonality_chart,
        render_all_regional_analysis,
        create_total_activities_per_month_chart
    )
    
    st.markdown("## 🏗️ Exemplo 4: Dashboard Customizado")
    st.markdown("Combina diferentes componentes em um layout personalizado:")
    
    # Header com métricas
    st.markdown("### 📊 Visão Geral Nacional")
    
    # Primeira linha: matriz e sazonalidade
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🗓️ Matriz Consolidada")
        fig_matrix = create_consolidated_calendar_matrix_chart(filtered_data)
        if fig_matrix:
            st.plotly_chart(fig_matrix, use_container_width=True)
    
    with col2:
        st.markdown("#### 🌟 Sazonalidade")
        fig_season = create_main_crops_seasonality_chart(filtered_data)
        if fig_season:
            st.plotly_chart(fig_season, use_container_width=True)
    
    # Segunda linha: atividades mensais
    st.markdown("#### 📈 Atividades Mensais")
    fig_monthly = create_total_activities_per_month_chart(filtered_data)
    if fig_monthly:
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Terceira seção: análise regional
    st.markdown("---")
    st.markdown("### 🌍 Análise Regional Detalhada")
    render_all_regional_analysis(filtered_data)


def example_export_capabilities(filtered_data: Dict) -> None:
    """
    Exemplo 5: Capacidades de exportação e download.
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
    """
    from dashboard.components.agricultural_analysis.charts.calendar import (
        create_crop_diversity_by_region_chart,
        create_calendar_heatmap_chart
    )
    
    st.markdown("## 📥 Exemplo 5: Exportação de Gráficos")
    st.markdown("Demonstra como exportar gráficos individuais:")
    
    # Gráfico de diversidade
    st.markdown("#### 🌱 Diversidade por Região")
    fig_diversity = create_crop_diversity_by_region_chart(filtered_data)
    
    if fig_diversity:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.plotly_chart(fig_diversity, use_container_width=True)
        
        with col2:
            st.markdown("##### 📊 Opções de Export")
            
            # Opções de download usando utilitários do projeto
            try:
                from scripts.utilities.utils import export_plotly_figure
                
                if st.button("📥 Download PNG", key="diversity_png"):
                    export_plotly_figure(
                        fig_diversity, 
                        "diversidade_por_regiao.png",
                        "⬇️ Download Diversidade (PNG)"
                    )
                
                if st.button("📄 Download HTML", key="diversity_html"):
                    fig_html = fig_diversity.to_html()
                    st.download_button(
                        "📄 Download HTML",
                        fig_html,
                        "diversidade_por_regiao.html",
                        "text/html"
                    )
                    
            except ImportError:
                st.info("💡 Funções de export não available")
    
    # Gráfico de heatmap
    st.markdown("#### 🔥 Heatmap Nacional")
    fig_heatmap = create_calendar_heatmap_chart(filtered_data)
    
    if fig_heatmap:
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Mostra código para replicar
        with st.expander("🔧 Ver código para replicar"):
            st.code("""
from dashboard.components.agricultural_analysis.charts.calendar import create_calendar_heatmap_chart

# Criar o gráfico
fig = create_calendar_heatmap_chart(filtered_data)

# Exibir no Streamlit
if fig:
    st.plotly_chart(fig, use_container_width=True)

# Salvar arquivo
if fig:
    fig.write_html("heatmap_calendario.html")
    fig.write_image("heatmap_calendario.png")
""", language="python")


def main_example_selector(filtered_data: Dict) -> None:
    """
    Seletor principal de exemplos.
    
    Args:
        filtered_data: Dados filtrados do calendário agrícola
    """
    st.title("📚 Exemplos de Uso - Gráficos Calendar Consolidados")
    st.markdown("*Demonstrações práticas dos componentes migrados do old_calendar*")
    
    # Seletor de exemplo
    example_choice = st.selectbox(
        "Escolha um exemplo:",
        [
            "Análise Completa (render_complete_calendar_analysis)",
            "Uso Modular (seções específicas)",
            "Gráficos Individuais (customização)",
            "Dashboard Personalizado (combinação)",
            "Capacidades de Exportação"
        ]
    )
    
    st.markdown("---")
    
    # Executa exemplo selecionado
    if example_choice.startswith("Análise Completa"):
        example_complete_analysis(filtered_data)
    
    elif example_choice.startswith("Uso Modular"):
        example_modular_usage(filtered_data)
    
    elif example_choice.startswith("Gráficos Individuais"):
        example_individual_charts(filtered_data)
    
    elif example_choice.startswith("Dashboard Personalizado"):
        example_custom_dashboard(filtered_data)
    
    elif example_choice.startswith("Capacidades de Exportação"):
        example_export_capabilities(filtered_data)


# Função para ser usada em páginas do Streamlit
def run_calendar_examples() -> None:
    """
    Função principal para executar os exemplos em uma página Streamlit.
    """
    # Verifica se há dados na sessão
    if "agricultural_data" not in st.session_state:
        st.error("❌ Dados agrícolas não found. Por favor, carregue os dados primeiro.")
        st.info("💡 Vá para a página Agricultural Analysis para carregar os dados.")
        return
    
    filtered_data = st.session_state.get("agricultural_data", {})
    
    if not filtered_data:
        st.warning("⚠️ Dados filtrados não available.")
        return
    
    # Executa seletor de exemplos
    main_example_selector(filtered_data)


if __name__ == "__main__":
    # Para teste local
    st.set_page_config(
        page_title="Calendar Examples",
        page_icon="📅",
        layout="wide"
    )
    
    # Dados de exemplo para teste
    example_data = {
        'crop_calendar': {
            'Soja': {
                'Mato Grosso': {
                    'planting_months': ['Sep', 'Oct', 'Nov'],
                    'harvesting_months': ['Jan', 'Feb', 'Mar']
                },
                'Rio Grande do Sul': {
                    'planting_months': ['Oct', 'Nov', 'Dec'],
                    'harvesting_months': ['Feb', 'Mar', 'Apr']
                }
            },
            'Milho': {
                'São Paulo': {
                    'planting_months': ['Sep', 'Oct'],
                    'harvesting_months': ['Feb', 'Mar']
                },
                'Paraná': {
                    'planting_months': ['Sep', 'Oct', 'Nov'],
                    'harvesting_months': ['Jan', 'Feb', 'Mar']
                }
            }
        }
    }
    
    main_example_selector(example_data)
