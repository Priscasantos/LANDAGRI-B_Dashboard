"""
Summary Cards Component
======================

Componente para cards de resumo da página de visão geral.
Mostra métricas principais das iniciativas LULC com Performance Metrics.

Author: LANDAGRI-B Project Team 
Date: 2025-07-30
"""

import pandas as pd
import streamlit as st


def render(df: pd.DataFrame) -> None:
    """
    Renderiza cards de resumo com métricas principais e Performance Metrics.

    Args:
        df: DataFrame com dados das iniciativas
    """
    # CSS para cards modernos com gradientes
    st.markdown(
        """
    <style>
    .modern-metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        transition: transform 0.2s ease;
    }
    .modern-metric-card:hover {
        transform: translateY(-3px);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        margin: 0.5rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.95;
        font-weight: 500;
    }
    .metric-sublabel {
        font-size: 0.8rem;
        opacity: 0.8;
        margin-top: 0.2rem;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Calcular métricas principais
    total_initiatives = len(df)

    # Calcular coverage distribution
    coverage_stats = {"Global": 0, "Regional": 0, "National": 0, "Other": 0}
    if "Coverage" in df.columns:
        for coverage in df["Coverage"]:
            coverage_str = str(coverage).strip().lower()
            if coverage_str in ["global", "worldwide"]:
                coverage_stats["Global"] += 1
            elif coverage_str in ["regional", "continental"]:
                coverage_stats["Regional"] += 1
            elif coverage_str in ["national", "country"]:
                coverage_stats["National"] += 1
            elif coverage_str not in ["n/a", "none", "", "-"]:
                coverage_stats["Other"] += 1

    # Calcular performance metrics
    avg_accuracy = 0
    avg_resolution = 0
    total_classes = 0
    min_classes = 0
    max_classes = 0
    temporal_coverage = 0

    if "Accuracy (%)" in df.columns:
        accuracy_values = pd.to_numeric(df["Accuracy (%)"], errors="coerce").dropna()
        avg_accuracy = accuracy_values.mean() if not accuracy_values.empty else 0

    if "Resolution" in df.columns:
        resolution_values = pd.to_numeric(df["Resolution"], errors="coerce").dropna()
        avg_resolution = resolution_values.mean() if not resolution_values.empty else 0

    if "Classes" in df.columns:
        classes_values = pd.to_numeric(df["Classes"], errors="coerce").dropna()
        classes_values = pd.to_numeric(df["Classes"], errors="coerce").dropna()
        if not classes_values.empty:
            total_classes = int(classes_values.sum())
            min_classes = int(classes_values.min())
            max_classes = int(classes_values.max())
        elif "Number_of_Classes" in df.columns:
            classes_values = pd.to_numeric(
            df["Number_of_Classes"], errors="coerce"
        ).dropna()
            max_classes = int(classes_values.max())
        else:
            total_classes = 0
            min_classes = 0
            max_classes = 0

    # Calcular cobertura temporal (anos únicos)
    year_columns = [col for col in df.columns if col.isdigit() and len(col) == 4]
    print(year_columns)
    if year_columns:
        temporal_coverage = len(year_columns)
    else:
        temporal_coverage = 40

    # Renderizar seção de métricas principais
    st.markdown("#### LULC Initiative Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
        <div class="modern-metric-card">
            <div class="metric-value">🌍 {coverage_stats["Global"]}</div>
            <div class="metric-label">Global</div>
            <div class="metric-sublabel">Worldwide coverage</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div class="modern-metric-card">
            <div class="metric-value">🗺️ {coverage_stats["Regional"]}</div>
            <div class="metric-label">Regional</div>
            <div class="metric-sublabel">Continental/regional</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div class="modern-metric-card">
            <div class="metric-value">🏛️ {coverage_stats["National"]}</div>
            <div class="metric-label">National</div>
            <div class="metric-sublabel">Country-specific</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
        <div class="modern-metric-card">
            <div class="metric-value">📍 {coverage_stats["Other"]}</div>
            <div class="metric-label">Other Coverage</div>
            <div class="metric-sublabel">Specialized scope</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Renderizar Performance Metrics
    st.markdown("#### Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
        <div class="modern-metric-card">
            <div class="metric-value">🎯 {avg_accuracy:.1f}%</div>
            <div class="metric-label">Average Accuracy</div>
            <div class="metric-sublabel">Classification precision</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        avg_resolution_display = (
            f"{avg_resolution:.0f}m" if avg_resolution > 0 else "N/A"
        )
        st.markdown(
            f"""
        <div class="modern-metric-card">
            <div class="metric-value">🔬 {avg_resolution_display}</div>
            <div class="metric-label">Average Resolution</div>
            <div class="metric-sublabel">Spatial precision</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div class="modern-metric-card">
            <div class="metric-value">🏷️ {min_classes:.0f} - {max_classes:.0f}</div>
            <div class="metric-label">Minimum and Maximum Classes</div>
            <div class="metric-sublabel">Classification categories</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
        <div class="modern-metric-card">
            <div class="metric-value">📅 {temporal_coverage}</div>
            <div class="metric-label">Temporal Coverage</div>
            <div class="metric-sublabel">Years of data</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
