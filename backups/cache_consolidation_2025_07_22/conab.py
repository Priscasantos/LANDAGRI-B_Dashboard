#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONAB Dashboard Module
======================

Specialized dashboard for CONAB (Companhia Nacional de Abastecimento) data analysis.
Provides comprehensive analysis of crop monitoring data with modern visualizations.

Author: Dashboard Iniciativas LULC
Date: 2025
"""

import streamlit as st
from typing import Dict, Any, Optional

# ========================================
# 🚀 SISTEMA DE CACHE OTIMIZADO - CONAB
# ========================================
try:
    from utilities.cache_system import (
        load_optimized_data, 
        setup_performance_sidebar,
        get_filtered_data,
        calculate_statistics,
        prepare_chart_data
    )
    OPTIMIZATION_ENABLED = True
    st.sidebar.success("⚡ Sistema consolidado ativo - CONAB")
except ImportError:
    OPTIMIZATION_ENABLED = False
    st.sidebar.warning("⚠️ Cache não disponível - CONAB")
    st.error("Sistema de cache consolidado não disponível. Verifique a instalação.")

from scripts.utilities.ui_elements import setup_download_form
from scripts.plotting.charts.temporal_charts import display_brazilian_geographic_tables

# Import CONAB-specific charts
from scripts.plotting.charts.conab_charts import (
    load_conab_detailed_data,
    plot_conab_spatial_temporal_distribution,
    plot_conab_temporal_coverage,
    plot_conab_spatial_coverage,
    plot_conab_crop_diversity,
)


def _display_header() -> None:
    """Display the main page header with modern styling."""
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
        ">
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 600;">
                🌾 CONAB Dashboard
            </h1>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                Companhia Nacional de Abastecimento - Crop Monitoring Analysis
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _display_overview_metrics(initiative_data: Dict[str, Any]) -> None:
    """Display overview metrics in a modern card layout."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Coverage", value=initiative_data.get("coverage", "N/A"))

    with col2:
        st.metric(
            label="Spatial Resolution",
            value=f"{initiative_data.get('spatial_resolution', 'N/A')}m",
        )

    with col3:
        available_years = initiative_data.get("available_years", [])
        year_range = (
            f"{min(available_years)}-{max(available_years)}"
            if available_years
            else "N/A"
        )
        st.metric(label="Time Period", value=year_range)

    with col4:
        st.metric(
            label="Agricultural Classes",
            value=initiative_data.get("number_of_agriculture_classes", "N/A"),
        )


def _display_spatial_temporal_tab(conab_data: Dict[str, Any]) -> None:
    """Display spatial-temporal distribution analysis."""
    st.markdown("### Spatial and Temporal Distribution of CONAB Mapping Initiatives")
    st.markdown(
        "This chart shows the coverage of CONAB mapping across different states and time periods."
    )

    with st.spinner("Generating spatial-temporal distribution chart..."):
        fig_spatial_temporal = plot_conab_spatial_temporal_distribution(conab_data)
        if fig_spatial_temporal:
            st.plotly_chart(fig_spatial_temporal, use_container_width=True)
            setup_download_form(
                fig_spatial_temporal,
                default_filename="conab_spatial_temporal_distribution",
                key_prefix="conab_spatial_temporal",
            )

    with st.expander("ℹ️ Chart Information"):
        st.markdown(
            """
            **About this chart:**
            - Shows which states/regions are covered by CONAB mapping over time
            - Each colored bar represents a continuous period of coverage for a state
            - Gaps in coverage indicate years when mapping was not performed in that state
            - Colors distinguish between different states for easy identification
            """
        )


def _display_temporal_coverage_tab(conab_data: Dict[str, Any]) -> None:
    """Display temporal coverage evolution analysis."""
    st.markdown("### Temporal Coverage Evolution")
    st.markdown("Percentage of Brazilian states covered by CONAB mapping over time.")

    with st.spinner("Generating temporal coverage chart..."):
        fig_temporal = plot_conab_temporal_coverage(conab_data)
        if fig_temporal:
            st.plotly_chart(fig_temporal, use_container_width=True)
            setup_download_form(
                fig_temporal,
                default_filename="conab_temporal_coverage",
                key_prefix="conab_temporal",
            )

    with st.expander("ℹ️ Chart Information"):
        st.markdown(
            """
            **About this chart:**
            - Shows the percentage of Brazilian states covered each year
            - Total of 27 states + Federal District = 100% coverage
            - Peaks indicate years with broader geographic coverage
            - Useful for identifying trends in CONAB's mapping expansion
            """
        )


def _display_spatial_coverage_tab(conab_data: Dict[str, Any]) -> None:
    """Display spatial coverage by state analysis."""
    st.markdown("### Spatial Coverage by State")
    st.markdown("Overall coverage percentage for each Brazilian state (2000-2023).")

    with st.spinner("Generating spatial coverage chart..."):
        fig_spatial = plot_conab_spatial_coverage(conab_data)
        if fig_spatial:
            st.plotly_chart(fig_spatial, use_container_width=True)
            setup_download_form(
                fig_spatial,
                default_filename="conab_spatial_coverage",
                key_prefix="conab_spatial",
            )

    with st.expander("ℹ️ Chart Information"):
        st.markdown(
            """
            **About this chart:**
            - Shows the percentage of years each state was covered (out of 24 years: 2000-2023)
            - Color coding: Red (low coverage) to Blue (high coverage)
            - Helps identify states with consistent vs. sporadic coverage
            - States with higher coverage have more historical data available
            """
        )


def _display_crop_diversity_tab(conab_data: Dict[str, Any]) -> None:
    """Display crop diversity analysis."""
    st.markdown("### Crop Type Diversity by State")
    st.markdown("Number and types of crops monitored in each state.")

    with st.spinner("Generating crop diversity chart..."):
        fig_diversity = plot_conab_crop_diversity(conab_data)
        if fig_diversity:
            st.plotly_chart(fig_diversity, use_container_width=True)
            setup_download_form(
                fig_diversity,
                default_filename="conab_crop_diversity",
                key_prefix="conab_diversity",
            )

    with st.expander("ℹ️ Chart Information"):
        st.markdown(
            """
            **About this chart:**
            - Shows the variety of crop types monitored in each state
            - Stacked bars represent different crop types
            - Longer bars indicate states with more diverse crop monitoring
            - Colors distinguish between different crop types
            - Useful for understanding agricultural diversity across regions
            """
        )


def _display_initiative_details(initiative_data: Dict[str, Any]) -> None:
    """Display detailed information about the CONAB initiative."""
    st.markdown("### 📋 CONAB Initiative Details")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Technical Specifications:**")
        st.markdown(f"- **Provider:** {initiative_data.get('provider', 'N/A')}")
        st.markdown(f"- **Source:** {initiative_data.get('source', 'N/A')}")
        st.markdown(f"- **Methodology:** {initiative_data.get('methodology', 'N/A')}")
        st.markdown(
            f"- **Classification Method:** {initiative_data.get('classification_method', 'N/A')}"
        )
        st.markdown(
            f"- **Reference System:** {initiative_data.get('reference_system', 'N/A')}"
        )

    with col2:
        st.markdown("**Agricultural Capabilities:**")
        agricultural_capabilities = initiative_data.get(
            "agricultural_capabilities", "N/A"
        )
        st.markdown(f"- **Capabilities:** {agricultural_capabilities}")

        class_legend = initiative_data.get("class_legend", "N/A")
        if class_legend != "N/A":
            st.markdown("**Crop Classes:**")
            crops = [crop.strip() for crop in class_legend.split(",")]
            for crop in crops:
                st.markdown(f"  - {crop}")

    # Data quality information
    accuracy_info = initiative_data.get("accuracy", {})
    if accuracy_info:
        st.markdown("**Data Quality:**")
        if accuracy_info.get("status") == "incomplete":
            st.warning(
                f"⚠️ {accuracy_info.get('description', 'Accuracy information incomplete')}"
            )
        else:
            overall_accuracy = accuracy_info.get("overall")
            if overall_accuracy:
                st.success(f"✅ Overall Accuracy: {overall_accuracy}%")


def run() -> None:
    """Main function to run the CONAB dashboard."""
    # ========================================
    # 🚀 SISTEMA DE CACHE OTIMIZADO - CONAB
    # ========================================
    if OPTIMIZATION_ENABLED:
        # Setup performance sidebar
        setup_performance_sidebar()
        
        # Carrega dados otimizados
        metadata, df_original, cache_info = load_optimized_data()
        
        # Mostra informações de cache
        if cache_info.get('cache_hits', 0) > 0:
            st.sidebar.success(f"⚡ Cache hits: {cache_info['cache_hits']}")
    
    _display_header()

    # Load CONAB detailed data
    with st.spinner("Loading CONAB data..."):
        conab_data = load_conab_detailed_data()

    if not conab_data:
        st.error("❌ Failed to load CONAB data. Please check the data files.")
        return

    # Display basic information
    initiative_data = conab_data.get("CONAB Crop Monitoring Initiative", {})

    # Overview metrics
    _display_overview_metrics(initiative_data)

    st.markdown("---")

    # Chart selection tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📊 Spatial-Temporal Distribution",
            "📈 Temporal Coverage",
            "🗺️ Spatial Coverage",
            "🌱 Crop Diversity",
        ]
    )

    with tab1:
        _display_spatial_temporal_tab(conab_data)

    with tab2:
        _display_temporal_coverage_tab(conab_data)

    with tab3:
        _display_spatial_coverage_tab(conab_data)

    with tab4:
        _display_crop_diversity_tab(conab_data)

    # Additional information section
    st.markdown("---")
    _display_initiative_details(initiative_data)

    st.markdown("---")
    st.markdown(
        "*Data source: CONAB (Companhia Nacional de Abastecimento) - Brazilian National Supply Company*"
    )

    # Add Brazilian geographic tables at the end of the overview
    st.markdown("---")
    display_brazilian_geographic_tables()
