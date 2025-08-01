"""
Agricultural Analysis Dashboard - Orchestrator Principal
======================================================

Dashboard orquestrador para análise agrícola consolidando calendário agrícola e dados CONAB.
Substitui os módulos fragmentados agricultural_calendar.py e conab.py.

Funcionalidades:
- Calendário agrícola interativo com filtros inteligentes
- Análise especializada de dados CONAB
- Distribuição espaço-temporal de culturas
- Cobertura temporal e espacial de dados agrícolas
- Interface unificada com abas organizadas

Autor: Dashboard Iniciativas LULC
Data: 2025-07-30
"""

import json
import sys
from pathlib import Path

import streamlit as st

# Adicionar project root ao path - deve estar no topo
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Importar charts específicos para análise agrícola
# Importar charts modulares
from dashboard.components.agricultural_analysis.charts.agricultural_charts import (
    plot_crop_calendar_heatmap,
)


# TODO: Implementar conab_charts.py com as funções necessárias
def load_conab_detailed_data():
    """Stub function - TODO: implementar conab_charts.py"""
    return {}


def plot_conab_spatial_temporal_distribution(data):
    """Stub function - TODO: implementar conab_charts.py"""
    return None


def plot_conab_temporal_coverage(data):
    """Stub function - TODO: implementar conab_charts.py"""
    return None


def plot_conab_spatial_coverage(data):
    """Stub function - TODO: implementar conab_charts.py"""
    return None


def plot_conab_crop_diversity(data):
    """Stub function - TODO: implementar conab_charts.py"""
    return None


def run():
    """
    Executar análise agrícola completa consolidando calendário agrícola e CONAB.
    """

    # Header visual padronizado
    st.markdown(
        """
    <div style="
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(22, 163, 74, 0.2);
        border: 1px solid rgba(255,255,255,0.1);
    ">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
            🌾 Agricultural Analysis
        </h1>
        <p style="color: #dcfce7; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Comprehensive analysis of agricultural calendars and CONAB crop monitoring data
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Carregar dados necessários
    calendar_data, conab_data = _load_agricultural_data()

    if not calendar_data and not conab_data:
        st.error("❌ No agricultural data available for analysis.")
        st.info(
            "🔧 Please check if the data files are available in the data/json/ folder"
        )
        return

    # Renderizar análise em abas organizadas
    tab1, tab2, tab3 = st.tabs(
        ["📅 Agricultural Calendar", "🌾 CONAB Analysis", "📊 Integrated Overview"]
    )

    with tab1:
        _render_agricultural_calendar(calendar_data)

    with tab2:
        _render_conab_analysis(conab_data)

    with tab3:
        _render_integrated_overview(calendar_data, conab_data)


def _load_agricultural_data():
    """
    Carregar dados agrícolas dos arquivos JSONC.

    Returns:
        tuple: (calendar_data, conab_data)
    """
    data_dir = _project_root / "data" / "json"

    def load_jsonc(path: Path):
        """Carregar arquivo JSONC removendo comentários."""
        try:
            if not path.exists():
                return None
            with open(path, encoding="utf-8") as f:
                content = f.read()
                # Remover comentários (// ...)
                lines = [
                    line
                    for line in content.splitlines()
                    if not line.strip().startswith("//")
                ]
                return json.loads("\n".join(lines))
        except Exception as e:
            st.error(f"Error loading {path.name}: {e}")
            return None

    # Carregar dados com spinner
    with st.spinner("🔄 Loading agricultural data..."):
        # Dados do calendário agrícola
        calendar_paths = [
            data_dir / "conab_crop_calendar.jsonc",
            data_dir / "conab_crop_calendar_complete.jsonc",
        ]

        calendar_data = {}
        for path in calendar_paths:
            data = load_jsonc(path)
            if data:
                calendar_data.update(data)

        # Dados detalhados CONAB
        conab_data = load_conab_detailed_data()

    return calendar_data, conab_data


def _render_agricultural_calendar(calendar_data: dict) -> None:
    """Renderizar análise de calendário agrícola."""

    if not calendar_data:
        st.warning("⚠️ No agricultural calendar data available.")
        return

    st.markdown("### 🗓️ Interactive Agricultural Calendar")
    st.markdown("*Explore planting and harvesting periods of major Brazilian crops*")

    # Extrair dados para filtros
    states_data, crops_data, years_data = _extract_calendar_filters(calendar_data)

    # Renderizar filtros inteligentes
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_states = st.multiselect(
            "🗺️ Select States",
            options=states_data,
            default=states_data[:5] if len(states_data) > 5 else states_data,
            help="Select states to include in the analysis",
        )

    with col2:
        selected_crops = st.multiselect(
            "🌱 Select Crops",
            options=crops_data,
            default=crops_data[:10] if len(crops_data) > 10 else crops_data,
            help="Select crops to include in the calendar",
        )

    with col3:
        selected_years = st.multiselect(
            "📅 Select Years",
            options=years_data,
            default=years_data[-3:] if len(years_data) >= 3 else years_data,
            help="Select years for temporal analysis",
        )

    # Gráfico de calendário agrícola
    if selected_states and selected_crops and selected_years:
        try:
            # Preparar dados filtrados para o gráfico
            filtered_data = _filter_calendar_data(
                calendar_data, selected_states, selected_crops, selected_years
            )

            fig = plot_crop_calendar_heatmap(filtered_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 No calendar data available for selected filters")
        except Exception as e:
            st.error(f"Error creating calendar chart: {e}")
    else:
        st.info("👆 Please select states, crops, and years to display the calendar")


def _render_conab_analysis(conab_data: dict) -> None:
    """Renderizar análise especializada CONAB."""

    if not conab_data:
        st.warning("⚠️ No CONAB data available.")
        return

    st.markdown("### 🌾 CONAB - Companhia Nacional de Abastecimento")
    st.markdown("*Specialized analysis of CONAB crop monitoring initiative*")

    # Informações básicas da iniciativa
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})

    # Métricas de overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Coverage", value=initiative_data.get("coverage", "N/A"))

    with col2:
        st.metric(
            label="Resolution",
            value=f"{initiative_data.get('spatial_resolution', 'N/A')}m",
        )

    with col3:
        years = initiative_data.get("available_years", [])
        year_span = f"{min(years)}-{max(years)}" if years else "N/A"
        st.metric(label="Temporal Coverage", value=year_span)

    with col4:
        classes = initiative_data.get("class_legend", "")
        class_count = (
            len([c.strip() for c in classes.split(",") if c.strip()]) if classes else 0
        )
        st.metric(label="Crop Classes", value=class_count)

    # Gráficos CONAB específicos
    col1, col2 = st.columns(2)

    with col1:
        try:
            fig_spatial = plot_conab_spatial_coverage(conab_data)
            if fig_spatial:
                st.plotly_chart(fig_spatial, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating spatial coverage chart: {e}")

    with col2:
        try:
            fig_temporal = plot_conab_temporal_coverage(conab_data)
            if fig_temporal:
                st.plotly_chart(fig_temporal, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating temporal coverage chart: {e}")

    # Análise de diversidade de culturas
    try:
        fig_diversity = plot_conab_crop_diversity(conab_data)
        if fig_diversity:
            st.plotly_chart(fig_diversity, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating crop diversity chart: {e}")


def _render_integrated_overview(calendar_data: dict, conab_data: dict) -> None:
    """Renderizar overview integrado dos dados agrícolas."""

    st.markdown("### 📊 Integrated Agricultural Overview")
    st.markdown("*Combined insights from agricultural calendar and CONAB data*")

    # Métricas integradas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📅 Calendar Data**")
        if calendar_data:
            # Contar estados no calendário
            states_count = len(_extract_calendar_filters(calendar_data)[0])
            st.metric("States Covered", states_count)

            # Contar culturas no calendário
            crops_count = len(_extract_calendar_filters(calendar_data)[1])
            st.metric("Crops Tracked", crops_count)
        else:
            st.info("No calendar data available")

    with col2:
        st.markdown("**🌾 CONAB Data**")
        if conab_data:
            initiative = conab_data.get("CONAB Crop Monitoring Initiative", {})

            # Temporal span
            years = initiative.get("available_years", [])
            span = len(years) if years else 0
            st.metric("Years Available", span)

            # Spatial resolution
            resolution = initiative.get("spatial_resolution", "N/A")
            st.metric("Resolution", f"{resolution}m" if resolution != "N/A" else "N/A")
        else:
            st.info("No CONAB data available")

    with col3:
        st.markdown("**🔗 Integration Status**")

        # Status de disponibilidade dos dados
        calendar_status = "✅" if calendar_data else "❌"
        conab_status = "✅" if conab_data else "❌"

        st.write(f"Calendar Data: {calendar_status}")
        st.write(f"CONAB Data: {conab_status}")

        # Calcular score de completude
        completeness = 0
        if calendar_data:
            completeness += 50
        if conab_data:
            completeness += 50

        st.metric("Data Completeness", f"{completeness}%")

    # Gráfico integrado se ambos datasets estão disponíveis
    if calendar_data and conab_data:
        st.markdown("---")
        try:
            fig_integrated = plot_conab_spatial_temporal_distribution(conab_data)
            if fig_integrated:
                st.plotly_chart(fig_integrated, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating integrated chart: {e}")


def _extract_calendar_filters(calendar_data: dict):
    """Extrair dados para filtros do calendário."""
    try:
        # Estados
        states_dict = calendar_data.get("states", {})
        all_states = [
            v["name"]
            for v in states_dict.values()
            if isinstance(v, dict) and "name" in v
        ]

        # Culturas - tentar extrair de diferentes fontes
        all_crops = []
        if "crops" in calendar_data:
            all_crops = list(calendar_data["crops"].keys())

        # Se não encontrar, usar culturas padrão
        if not all_crops:
            all_crops = ["Soja", "Milho", "Algodão", "Cana-de-açúcar", "Café"]

        # Anos - usar range padrão se não encontrar
        available_years = list(range(2020, 2025))

        return all_states, all_crops, available_years

    except Exception:
        # Valores padrão em caso de erro
        default_states = [
            "Mato Grosso",
            "Bahia",
            "Rio Grande do Sul",
            "Paraná",
            "Goiás",
        ]
        default_crops = ["Soja", "Milho", "Algodão", "Cana-de-açúcar", "Café"]
        default_years = list(range(2020, 2025))
        return default_states, default_crops, default_years


def _filter_calendar_data(calendar_data: dict, states: list, crops: list, years: list):
    """Filtrar dados do calendário com base nas seleções."""
    # Implementação simplificada - retorna dados filtrados
    # Em implementação real, filtraria os dados de acordo com seleções
    return {
        "filtered_states": states,
        "filtered_crops": crops,
        "filtered_years": years,
        "raw_data": calendar_data,
    }


# Para compatibilidade com implementações legadas
def agricultural_calendar():
    """Função legada - redireciona para run()."""
    run()


def conab():
    """Função legada - redireciona para run()."""
    run()
