"""
Componente para filtros da página Overview
==========================================

Este módulo contém funções para renderizar os filtros modernos
e interativos do dashboard de visão geral.
"""

import pandas as pd
import streamlit as st


def render_initiative_filters(
    df: pd.DataFrame,
) -> tuple[list[str], tuple[int, int], tuple[int, int], tuple[int, int]]:
    """
    Renderiza os filtros da página overview com design moderno.

    Args:
        df: DataFrame com os dados das iniciativas

    Returns:
        Tuple contendo os valores selecionados nos filtros:
        (selected_types, selected_res, selected_acc, selected_agri_classes)
    """
    # CSS customizado para os filtros
    st.markdown(
        """
    <style>
    .filters-container {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }

    .filters-title {
        font-size: 20px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .filter-description {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 20px;
        padding: 12px 16px;
        background: rgba(59, 130, 246, 0.05);
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="filters-container">', unsafe_allow_html=True)
    st.markdown(
        '<div class="filters-title">🔎 Filtros das Iniciativas</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="filter-description">'
        "Use os filtros abaixo para refinar sua análise das iniciativas LULC. "
        "Os filtros são aplicados em tempo real e afetam todas as visualizações da página."
        "</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        # Filtro de Tipo
        tipos = (
            df["Type"].unique().tolist()
            if not df.empty and "Type" in df.columns and df["Type"].notna().any()
            else []
        )
        selected_types = st.multiselect(
            "🏷️ Tipo",
            options=tipos,
            default=tipos,
            help="Selecione os tipos de iniciativas para análise",
        )

    with col2:
        # Filtro de Resolução
        if (
            not df.empty
            and "Resolution" in df.columns
            and df["Resolution"].notna().any()
        ):
            resolutions_numeric = pd.to_numeric(
                df["Resolution"], errors="coerce"
            ).dropna()
            if not resolutions_numeric.empty:
                min_res, max_res = (
                    int(resolutions_numeric.min()),
                    int(resolutions_numeric.max()),
                )
                selected_res = st.slider(
                    "📐 Resolução (m)",
                    min_value=min_res,
                    max_value=max_res,
                    value=(min_res, max_res),
                    help="Filtre por resolução espacial em metros",
                )
            else:
                selected_res = st.slider(
                    "📐 Resolução (m)",
                    min_value=0,
                    max_value=1000,
                    value=(0, 1000),
                    disabled=True,
                    help="Dados de resolução não disponíveis",
                )
                st.caption("⚠️ Dados de resolução não disponíveis ou não numéricos.")
        else:
            selected_res = st.slider(
                "📐 Resolução (m)",
                min_value=0,
                max_value=1000,
                value=(0, 1000),
                disabled=True,
                help="Dados de resolução não disponíveis",
            )
            st.caption("⚠️ Dados de resolução não disponíveis para a seleção atual.")

    with col3:
        # Filtro de Acurácia
        if (
            not df.empty
            and "Accuracy (%)" in df.columns
            and df["Accuracy (%)"].notna().any()
        ):
            accuracies_numeric = pd.to_numeric(
                df["Accuracy (%)"], errors="coerce"
            ).dropna()
            if not accuracies_numeric.empty:
                min_acc, max_acc = (
                    int(accuracies_numeric.min()),
                    int(accuracies_numeric.max()),
                )
                selected_acc = st.slider(
                    "🎯 Acurácia (%)",
                    min_value=min_acc,
                    max_value=max_acc,
                    value=(min_acc, max_acc),
                    help="Filtre por acurácia da classificação",
                )
            else:
                selected_acc = st.slider(
                    "🎯 Acurácia (%)",
                    min_value=0,
                    max_value=100,
                    value=(0, 100),
                    disabled=True,
                    help="Dados de acurácia não disponíveis",
                )
                st.caption("⚠️ Dados de acurácia não disponíveis ou não numéricos.")
        else:
            selected_acc = st.slider(
                "🎯 Acurácia (%)",
                min_value=0,
                max_value=100,
                value=(0, 100),
                disabled=True,
                help="Dados de acurácia não disponíveis",
            )
            st.caption("⚠️ Dados de acurácia não disponíveis para a seleção atual.")

    with col4:
        # Filtro de Classes Agrícolas
        if (
            not df.empty
            and "Num_Agri_Classes" in df.columns
            and df["Num_Agri_Classes"].notna().any()
        ):
            agri_classes_numeric = pd.to_numeric(
                df["Num_Agri_Classes"], errors="coerce"
            ).dropna()
            if not agri_classes_numeric.empty:
                min_agri_classes, max_agri_classes = (
                    int(agri_classes_numeric.min()),
                    int(agri_classes_numeric.max()),
                )
                if min_agri_classes == max_agri_classes:
                    max_agri_classes = min_agri_classes + 1
                selected_agri_classes = st.slider(
                    "🌾 Classes Agrícolas",
                    min_value=min_agri_classes,
                    max_value=max_agri_classes,
                    value=(min_agri_classes, max_agri_classes),
                    help="Filtre por número de classes agrícolas",
                )
            else:
                selected_agri_classes = st.slider(
                    "🌾 Classes Agrícolas",
                    min_value=0,
                    max_value=20,
                    value=(0, 20),
                    disabled=True,
                    help="Dados de classes agrícolas não disponíveis",
                )
                st.caption(
                    "⚠️ Dados de classes agrícolas não disponíveis ou não numéricos."
                )
        else:
            selected_agri_classes = st.slider(
                "🌾 Classes Agrícolas",
                min_value=0,
                max_value=20,
                value=(0, 20),
                disabled=True,
                help="Dados de classes agrícolas não disponíveis",
            )
            st.caption(
                "⚠️ Dados de classes agrícolas não disponíveis para a seleção atual."
            )

    with col5:
        # Botão de reset dos filtros
        if st.button(
            "🔄 Resetar Filtros", help="Restaurar todos os filtros para valores padrão"
        ):
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    return selected_types, selected_res, selected_acc, selected_agri_classes


def apply_filters(
    df: pd.DataFrame,
    selected_types: list[str],
    selected_res: tuple[int, int],
    selected_acc: tuple[int, int],
    selected_agri_classes: tuple[int, int],
) -> pd.DataFrame:
    """
    Aplica os filtros selecionados ao DataFrame.

    Args:
        df: DataFrame original
        selected_types: Tipos selecionados
        selected_res: Range de resolução selecionado
        selected_acc: Range de acurácia selecionado
        selected_agri_classes: Range de classes agrícolas selecionado

    Returns:
        DataFrame filtrado
    """
    # Copiar DataFrame para não modificar o original
    filtered_df = df.copy()

    # Aplicar filtros sequencialmente
    conditions = []

    # Filtro por tipo
    if selected_types:
        conditions.append(filtered_df["Type"].isin(selected_types))

    # Filtro por resolução
    if "Resolution" in filtered_df.columns:
        filtered_df["Resolution_numeric"] = pd.to_numeric(
            filtered_df["Resolution"], errors="coerce"
        )
        res_condition = (filtered_df["Resolution_numeric"] >= selected_res[0]) & (
            filtered_df["Resolution_numeric"] <= selected_res[1]
        )
        conditions.append(res_condition)

    # Filtro por acurácia
    if "Accuracy (%)" in filtered_df.columns:
        filtered_df["Accuracy_numeric"] = pd.to_numeric(
            filtered_df["Accuracy (%)"], errors="coerce"
        )
        acc_condition = (filtered_df["Accuracy_numeric"] >= selected_acc[0]) & (
            filtered_df["Accuracy_numeric"] <= selected_acc[1]
        )
        conditions.append(acc_condition)

    # Filtro por classes agrícolas
    if "Num_Agri_Classes" in filtered_df.columns:
        filtered_df["Num_Agri_Classes_numeric"] = pd.to_numeric(
            filtered_df["Num_Agri_Classes"], errors="coerce"
        )
        agri_condition = (
            filtered_df["Num_Agri_Classes_numeric"] >= selected_agri_classes[0]
        ) & (filtered_df["Num_Agri_Classes_numeric"] <= selected_agri_classes[1])
        conditions.append(agri_condition)

    # Combinar todas as condições
    if conditions:
        final_condition = conditions[0]
        for condition in conditions[1:]:
            final_condition = final_condition & condition
        filtered_df = filtered_df[final_condition]

    # Limpar colunas auxiliares
    columns_to_drop = [
        "Resolution_numeric",
        "Accuracy_numeric",
        "Num_Agri_Classes_numeric",
    ]
    for col in columns_to_drop:
        if col in filtered_df.columns:
            filtered_df = filtered_df.drop(columns=[col])

    return filtered_df


def display_filter_results(original_count: int, filtered_count: int) -> None:
    """
    Exibe o resultado dos filtros aplicados.

    Args:
        original_count: Número de iniciativas original
        filtered_count: Número de iniciativas após filtros
    """
    if filtered_count != original_count:
        st.markdown(
            f"""
        <div style="
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border: 1px solid #0ea5e9;
            border-radius: 12px;
            padding: 16px;
            margin: 16px 0;
            text-align: center;
        ">
            <strong style="color: #0369a1;">
                📊 Filtros Aplicados: {filtered_count} de {original_count} iniciativas selecionadas
            </strong>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
        <div style="
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border: 1px solid #22c55e;
            border-radius: 12px;
            padding: 16px;
            margin: 16px 0;
            text-align: center;
        ">
            <strong style="color: #15803d;">
                ✅ Exibindo todas as {original_count} iniciativas disponíveis
            </strong>
        </div>
        """,
            unsafe_allow_html=True,
        )
