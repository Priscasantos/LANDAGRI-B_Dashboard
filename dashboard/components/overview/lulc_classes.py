"""
Componente para exibição das classes LULC com design melhorado
============================================================

Este módulo contém funções para renderizar as classes de cobertura do solo
com bolhas coloridas e layout visual aprimorado.
"""

import json

import streamlit as st


def render_lulc_classes_section(class_legend_str: str) -> None:
    """
    Renderiza a seção de classes LULC com design melhorado usando bolhas coloridas.

    Args:
        class_legend_str: String JSON contendo as classes de cobertura do solo
    """
    # Parse das classes
    try:
        class_legend_list = json.loads(class_legend_str)
        if not isinstance(class_legend_list, list):
            class_legend_list = []
    except (json.JSONDecodeError, TypeError):
        class_legend_list = []

    if not class_legend_list:
        return

    # CSS customizado para as bolhas coloridas
    st.markdown(
        """
    <style>
    .lulc-classes-container {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }

    .lulc-classes-title {
        font-size: 20px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .lulc-classes-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 12px;
        margin-top: 16px;
    }

    .lulc-class-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .lulc-class-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
        border-color: #3b82f6;
    }

    .lulc-class-bubble {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        flex-shrink: 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        position: relative;
    }

    .lulc-class-bubble::after {
        content: '';
        position: absolute;
        top: 2px;
        left: 2px;
        width: 6px;
        height: 6px;
        background: rgba(255, 255, 255, 0.4);
        border-radius: 50%;
    }

    .lulc-class-number {
        font-weight: 700;
        color: #64748b;
        font-size: 14px;
        min-width: 20px;
        text-align: center;
    }

    .lulc-class-content {
        flex: 1;
    }

    .lulc-class-name {
        font-weight: 600;
        color: #1e293b;
        font-size: 15px;
        margin-bottom: 2px;
    }

    .lulc-class-description {
        font-size: 13px;
        color: #64748b;
        line-height: 1.4;
    }

    .total-classes-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Cores para as bolhas (palette de cores para LULC)
    lulc_colors = [
        "#22c55e",  # Forest - Verde
        "#84cc16",  # Shrubland - Verde limão
        "#65a30d",  # Herbaceous Vegetation - Verde oliva
        "#06b6d4",  # Herbaceous Wetland - Ciano
        "#8b5cf6",  # Moss And Lichen - Roxo
        "#f59e0b",  # Bare/Sparse Vegetation - Âmbar
        "#eab308",  # Cropland - Amarelo
        "#ef4444",  # Urban/Built-Up - Vermelho
        "#e5e7eb",  # Snow And Ice - Cinza claro
        "#3b82f6",  # Permanent Water Bodies - Azul
    ]

    # Cabeçalho da seção
    st.markdown(
        f"""
    <div class="lulc-classes-container">
        <div class="lulc-classes-title">
            🏷️ Detalhes da Classificação
            <span class="total-classes-badge">
                📊 Total de Classes: {len(class_legend_list)}
            </span>
        </div>

        <div style="margin-bottom: 16px;">
            <strong style="color: #475569; font-size: 16px;">📋 Classes de Cobertura do Solo (Legenda)</strong>
        </div>

        <div class="lulc-classes-grid">
    """,
        unsafe_allow_html=True,
    )

    # Renderizar cada classe com bolha colorida
    for i, class_item in enumerate(class_legend_list):
        color = lulc_colors[i % len(lulc_colors)]

        if isinstance(class_item, dict):
            class_name = class_item.get("class_name", f"Classe {i + 1}")
            class_desc = class_item.get("description", "Sem descrição disponível")
        else:
            class_name = str(class_item)
            class_desc = "Sem descrição disponível"

        st.markdown(
            f"""
            <div class="lulc-class-item">
                <div class="lulc-class-number">{i + 1}</div>
                <div class="lulc-class-bubble" style="background: {color};"></div>
                <div class="lulc-class-content">
                    <div class="lulc-class-name">{class_name}</div>
                    <div class="lulc-class-description">{class_desc}</div>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    # Fechar container
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_classification_summary(
    total_classes: int, total_initiatives: int = 0
) -> None:
    """
    Renderiza um resumo das classificações com métricas visuais.

    Args:
        total_classes: Número total de classes
        total_initiatives: Número total de iniciativas (opcional)
    """
    st.markdown(
        """
    <style>
    .classification-summary {
        display: flex;
        gap: 16px;
        margin: 16px 0;
        flex-wrap: wrap;
    }

    .summary-metric {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
        flex: 1;
        min-width: 140px;
        transition: all 0.3s ease;
    }

    .summary-metric:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    }

    .summary-metric-icon {
        font-size: 24px;
        margin-bottom: 8px;
    }

    .summary-metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 4px;
    }

    .summary-metric-label {
        font-size: 14px;
        color: #64748b;
        font-weight: 500;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    metrics_html = f"""
    <div class="classification-summary">
        <div class="summary-metric">
            <div class="summary-metric-icon">🏷️</div>
            <div class="summary-metric-value">{total_classes}</div>
            <div class="summary-metric-label">Classes Totais</div>
        </div>
    """

    if total_initiatives > 0:
        metrics_html += f"""
        <div class="summary-metric">
            <div class="summary-metric-icon">🛰️</div>
            <div class="summary-metric-value">{total_initiatives}</div>
            <div class="summary-metric-label">Iniciativas</div>
        </div>
        """

    metrics_html += "</div>"

    st.markdown(metrics_html, unsafe_allow_html=True)
