"""
Overview Dashboard - Versão Moderna e Responsiva
==============================================

Dashboard principal para iniciativas LULC com:
- Interface moderna e responsiva
- Componentes colapsáveis para melhor organização
- Filtros interativos otimizados
- Visualizações temporais melhoradas
- Detalhes organizados por iniciativa

Author: Dashboard Iniciativas LULC
Date: 2025-07-22
Version: 2.0 - Otimizada
"""

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from scripts.utilities.ui_elements import setup_download_form

# Configuração de caminhos
current_dir = Path(__file__).parent.parent
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)


def _format_year_ranges(years_list: list) -> str:
    """Formata lista de anos em ranges consecutivos."""
    if not years_list:
        return ""

    try:
        years = sorted({int(y) for y in years_list if str(y).isdigit()})
    except ValueError:
        return ", ".join(sorted({str(y) for y in years_list}))

    if not years:
        return ""

    ranges = []
    start_range = years[0]

    for i in range(1, len(years)):
        if years[i] != years[i - 1] + 1:
            if start_range == years[i - 1]:
                ranges.append(str(start_range))
            else:
                ranges.append(f"{start_range}-{years[i - 1]}")
            start_range = years[i]

    # Adiciona o último range
    if start_range == years[-1]:
        ranges.append(str(start_range))
    else:
        ranges.append(f"{start_range}-{years[-1]}")

    return ", ".join(ranges)


def _load_data():
    """Carrega dados da sessão e sensores."""
    # Verifica dados na sessão
    if (
        "df_interpreted" not in st.session_state
        or st.session_state.df_interpreted.empty
    ):
        st.error(
            "❌ Dados não encontrados na sessão. Verifique se o app.py carregou os dados corretamente."
        )
        return pd.DataFrame(), {}, {}

    df = st.session_state.get("df_interpreted", pd.DataFrame())
    meta = st.session_state.get("metadata", {})

    # Carrega metadados dos sensores
    sensors_meta = {}
    try:
        from scripts.utilities.json_interpreter import _load_jsonc_file

        sensors_metadata_path = current_dir / "data" / "json" / "sensors_metadata.jsonc"
        if sensors_metadata_path.exists():
            sensors_meta_loaded = _load_jsonc_file(sensors_metadata_path)
            if isinstance(sensors_meta_loaded, dict):
                sensors_meta = sensors_meta_loaded
                st.session_state.sensors_meta = sensors_meta
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar metadados dos sensores: {e}")

    return df, meta, sensors_meta


def _create_filters(df):
    """Cria filtros interativos com layout responsivo e moderno."""
    st.markdown("### 🔎 **Filtros de Iniciativas**")

    # Layout responsivo - adapta para mobile
    if "mobile_view" not in st.session_state:
        st.session_state.mobile_view = False

    # Toggle para view mobile/desktop
    view_toggle = st.toggle(
        "📱 Visualização Compacta", value=st.session_state.mobile_view
    )
    st.session_state.mobile_view = view_toggle

    if st.session_state.mobile_view:
        # Layout mobile - filtros em acordeões
        with st.expander("🏷️ **Filtros por Tipo e Resolução**", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                tipos = (
                    df["Type"].unique().tolist()
                    if not df.empty and "Type" in df.columns
                    else []
                )
                selected_types = st.multiselect(
                    "📋 Tipo de Iniciativa",
                    options=tipos,
                    default=tipos,
                    help="Selecione os tipos de iniciativas para filtrar",
                )

            with col2:
                if not df.empty and "Resolution" in df.columns:
                    resolutions_numeric = pd.to_numeric(
                        df["Resolution"], errors="coerce"
                    ).dropna()
                    if not resolutions_numeric.empty:
                        min_res, max_res = (
                            int(resolutions_numeric.min()),
                            int(resolutions_numeric.max()),
                        )
                        selected_res = st.slider(
                            "🔍 Resolução Espacial (metros)",
                            min_value=min_res,
                            max_value=max_res,
                            value=(min_res, max_res),
                            help=f"Filtrar por resolução espacial entre {min_res}m e {max_res}m",
                        )
                    else:
                        selected_res = st.slider(
                            "🔍 Resolução Espacial (metros)",
                            min_value=0,
                            max_value=1000,
                            value=(0, 1000),
                            disabled=True,
                            help="Dados de resolução não disponíveis",
                        )
                else:
                    selected_res = st.slider(
                        "🔍 Resolução Espacial (metros)",
                        min_value=0,
                        max_value=1000,
                        value=(0, 1000),
                        disabled=True,
                        help="Dados de resolução não disponíveis",
                    )

        with st.expander("🎯 **Filtros por Precisão e Classes**", expanded=False):
            col3, col4 = st.columns(2)

            with col3:
                if not df.empty and "Accuracy" in df.columns:
                    accuracy_numeric = pd.to_numeric(
                        df["Accuracy"], errors="coerce"
                    ).dropna()
                    if not accuracy_numeric.empty:
                        min_acc, max_acc = (
                            float(accuracy_numeric.min()),
                            float(accuracy_numeric.max()),
                        )
                        selected_acc = st.slider(
                            "🎯 Precisão (%)",
                            min_value=min_acc,
                            max_value=max_acc,
                            value=(min_acc, max_acc),
                            step=0.1,
                            help=f"Filtrar por precisão entre {min_acc:.1f}% e {max_acc:.1f}%",
                        )
                    else:
                        selected_acc = st.slider(
                            "🎯 Precisão (%)",
                            min_value=0.0,
                            max_value=100.0,
                            value=(0.0, 100.0),
                            disabled=True,
                            help="Dados de precisão não disponíveis",
                        )
                else:
                    selected_acc = st.slider(
                        "🎯 Precisão (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=(0.0, 100.0),
                        disabled=True,
                        help="Dados de precisão não disponíveis",
                    )

            with col4:
                if not df.empty and "Classes" in df.columns:
                    classes_numeric = pd.to_numeric(
                        df["Classes"], errors="coerce"
                    ).dropna()
                    if not classes_numeric.empty:
                        min_classes, max_classes = (
                            int(classes_numeric.min()),
                            int(classes_numeric.max()),
                        )
                        selected_classes = st.slider(
                            "🏷️ Número de Classes",
                            min_value=min_classes,
                            max_value=max_classes,
                            value=(min_classes, max_classes),
                            help=f"Filtrar por número de classes entre {min_classes} e {max_classes}",
                        )
                    else:
                        selected_classes = st.slider(
                            "🏷️ Número de Classes",
                            min_value=1,
                            max_value=50,
                            value=(1, 50),
                            disabled=True,
                            help="Dados de classes não disponíveis",
                        )
                else:
                    selected_classes = st.slider(
                        "🏷️ Número de Classes",
                        min_value=1,
                        max_value=50,
                        value=(1, 50),
                        disabled=True,
                        help="Dados de classes não disponíveis",
                    )

        with st.expander("📅 **Filtros Temporais**", expanded=False):
            anos_disponiveis = set()
            if not df.empty and "Available_Years" in df.columns:
                for anos_str in df["Available_Years"].dropna():
                    try:
                        anos_data = (
                            json.loads(anos_str)
                            if isinstance(anos_str, str)
                            else anos_str
                        )
                        if isinstance(anos_data, list):
                            anos_disponiveis.update(anos_data)
                    except (json.JSONDecodeError, TypeError):
                        continue

            if anos_disponiveis:
                anos_sorted = sorted(
                    [int(ano) for ano in anos_disponiveis if str(ano).isdigit()]
                )
                if anos_sorted:
                    selected_year_range = st.slider(
                        "🗓️ Período de Interesse",
                        min_value=min(anos_sorted),
                        max_value=max(anos_sorted),
                        value=(min(anos_sorted), max(anos_sorted)),
                        help=f"Filtrar iniciativas por período entre {min(anos_sorted)} e {max(anos_sorted)}",
                    )
                else:
                    selected_year_range = None
            else:
                selected_year_range = None

    else:
        # Layout desktop - filtros em linha
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            tipos = (
                df["Type"].unique().tolist()
                if not df.empty and "Type" in df.columns
                else []
            )
            selected_types = st.multiselect("📋 Tipo", options=tipos, default=tipos)

        with col2:
            if not df.empty and "Resolution" in df.columns:
                resolutions_numeric = pd.to_numeric(
                    df["Resolution"], errors="coerce"
                ).dropna()
                if not resolutions_numeric.empty:
                    min_res, max_res = (
                        int(resolutions_numeric.min()),
                        int(resolutions_numeric.max()),
                    )
                    selected_res = st.slider(
                        "🔍 Resolução (m)",
                        min_value=min_res,
                        max_value=max_res,
                        value=(min_res, max_res),
                    )
                else:
                    selected_res = st.slider(
                        "🔍 Resolução (m)",
                        min_value=0,
                        max_value=1000,
                        value=(0, 1000),
                        disabled=True,
                    )
            else:
                selected_res = st.slider(
                    "🔍 Resolução (m)",
                    min_value=0,
                    max_value=1000,
                    value=(0, 1000),
                    disabled=True,
                )

        with col3:
            if not df.empty and "Accuracy" in df.columns:
                accuracy_numeric = pd.to_numeric(
                    df["Accuracy"], errors="coerce"
                ).dropna()
                if not accuracy_numeric.empty:
                    min_acc, max_acc = (
                        float(accuracy_numeric.min()),
                        float(accuracy_numeric.max()),
                    )
                    selected_acc = st.slider(
                        "🎯 Precisão (%)",
                        min_value=min_acc,
                        max_value=max_acc,
                        value=(min_acc, max_acc),
                        step=0.1,
                    )
                else:
                    selected_acc = st.slider(
                        "🎯 Precisão (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=(0.0, 100.0),
                        disabled=True,
                    )
            else:
                selected_acc = st.slider(
                    "🎯 Precisão (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=(0.0, 100.0),
                    disabled=True,
                )

        with col4:
            if not df.empty and "Classes" in df.columns:
                classes_numeric = pd.to_numeric(df["Classes"], errors="coerce").dropna()
                if not classes_numeric.empty:
                    min_classes, max_classes = (
                        int(classes_numeric.min()),
                        int(classes_numeric.max()),
                    )
                    selected_classes = st.slider(
                        "🏷️ Classes",
                        min_value=min_classes,
                        max_value=max_classes,
                        value=(min_classes, max_classes),
                    )
                else:
                    selected_classes = st.slider(
                        "🏷️ Classes",
                        min_value=1,
                        max_value=50,
                        value=(1, 50),
                        disabled=True,
                    )
            else:
                selected_classes = st.slider(
                    "🏷️ Classes",
                    min_value=1,
                    max_value=50,
                    value=(1, 50),
                    disabled=True,
                )

        with col5:
            anos_disponiveis = set()
            if not df.empty and "Available_Years" in df.columns:
                for anos_str in df["Available_Years"].dropna():
                    try:
                        anos_data = (
                            json.loads(anos_str)
                            if isinstance(anos_str, str)
                            else anos_str
                        )
                        if isinstance(anos_data, list):
                            anos_disponiveis.update(anos_data)
                    except (json.JSONDecodeError, TypeError):
                        continue

            if anos_disponiveis:
                anos_sorted = sorted(
                    [int(ano) for ano in anos_disponiveis if str(ano).isdigit()]
                )
                if anos_sorted:
                    selected_year_range = st.slider(
                        "🗓️ Período",
                        min_value=min(anos_sorted),
                        max_value=max(anos_sorted),
                        value=(min(anos_sorted), max(anos_sorted)),
                    )
                else:
                    selected_year_range = None
            else:
                selected_year_range = None

    # Aplicar filtros ao dataframe
    filtered_df = df.copy()

    if selected_types:
        filtered_df = filtered_df[filtered_df["Type"].isin(selected_types)]

    if "Resolution" in filtered_df.columns:
        resolutions_numeric = pd.to_numeric(filtered_df["Resolution"], errors="coerce")
        mask_resolution = (resolutions_numeric >= selected_res[0]) & (
            resolutions_numeric <= selected_res[1]
        )
        filtered_df = filtered_df[mask_resolution | resolutions_numeric.isna()]

    if "Accuracy" in filtered_df.columns:
        accuracy_numeric = pd.to_numeric(filtered_df["Accuracy"], errors="coerce")
        mask_accuracy = (accuracy_numeric >= selected_acc[0]) & (
            accuracy_numeric <= selected_acc[1]
        )
        filtered_df = filtered_df[mask_accuracy | accuracy_numeric.isna()]

    if "Classes" in filtered_df.columns:
        classes_numeric = pd.to_numeric(filtered_df["Classes"], errors="coerce")
        mask_classes = (classes_numeric >= selected_classes[0]) & (
            classes_numeric <= selected_classes[1]
        )
        filtered_df = filtered_df[mask_classes | classes_numeric.isna()]

    if selected_year_range and "Available_Years" in filtered_df.columns:
        year_mask = []
        for _, row in filtered_df.iterrows():
            try:
                anos_str = row["Available_Years"]
                if pd.isna(anos_str):
                    year_mask.append(False)
                    continue

                anos_data = (
                    json.loads(anos_str) if isinstance(anos_str, str) else anos_str
                )
                if isinstance(anos_data, list):
                    anos_numeric = [int(ano) for ano in anos_data if str(ano).isdigit()]
                    has_overlap = any(
                        selected_year_range[0] <= ano <= selected_year_range[1]
                        for ano in anos_numeric
                    )
                    year_mask.append(has_overlap)
                else:
                    year_mask.append(False)
            except (json.JSONDecodeError, TypeError, ValueError):
                year_mask.append(False)

        filtered_df = filtered_df[year_mask]

    return filtered_df


def _apply_filters(
    df,
    selected_types,
    selected_res,
    selected_acc,
    selected_methods,
    selected_agri_range,
):
    """Aplica filtros ao DataFrame."""
    conditions = []

    if "Type" in df.columns and selected_types:
        conditions.append(df["Type"].isin(selected_types))

    if "Resolution" in df.columns and selected_res:
        df_temp = df.copy()
        df_temp["Resolution_numeric"] = pd.to_numeric(
            df_temp["Resolution"], errors="coerce"
        )
        conditions.append(
            df_temp["Resolution_numeric"].between(selected_res[0], selected_res[1])
        )

    if "Accuracy (%)" in df.columns and selected_acc:
        df_temp = df.copy()
        df_temp["Accuracy_numeric"] = pd.to_numeric(
            df_temp["Accuracy (%)"], errors="coerce"
        )
        conditions.append(
            df_temp["Accuracy_numeric"].between(selected_acc[0], selected_acc[1])
        )

    if "Methodology" in df.columns and selected_methods:
        conditions.append(df["Methodology"].isin(selected_methods))

    if "Num_Agri_Classes" in df.columns and selected_agri_range:
        df_temp = df.copy()
        df_temp["Num_Agri_Classes_numeric"] = pd.to_numeric(
            df_temp["Num_Agri_Classes"], errors="coerce"
        )
        conditions.append(
            df_temp["Num_Agri_Classes_numeric"].between(
                selected_agri_range[0], selected_agri_range[1]
            )
        )

    if conditions:
        final_condition = pd.Series(True, index=df.index)
        for cond in conditions:
            final_condition &= cond
        return df[final_condition]

    return df.copy()


def _display_key_metrics(filtered_df):
    """Exibe métricas-chave agregadas."""
    st.subheader("📈 Métricas Principais")

    # CSS para cartões de métricas
    st.markdown(
        """
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-value {
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1.1rem;
        opacity: 0.9;
        text-transform: uppercase;
    }
    .metric-sublabel {
        font-size: 0.9rem;
        opacity: 0.7;
        margin-top: 0.3rem;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_accuracy_series = pd.to_numeric(
            filtered_df["Accuracy (%)"], errors="coerce"
        ).dropna()
        if not avg_accuracy_series.empty:
            avg_accuracy = avg_accuracy_series.mean()
            st.markdown(
                f"""
            <div class="metric-card">
                <div class="metric-value">🎯 {avg_accuracy:.1f}%</div>
                <div class="metric-label">Acurácia Média</div>
                <div class="metric-sublabel">Iniciativas filtradas</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with col2:
        avg_resolution_series = pd.to_numeric(
            filtered_df["Resolution"], errors="coerce"
        ).dropna()
        if not avg_resolution_series.empty:
            avg_resolution = avg_resolution_series.mean()
            st.markdown(
                f"""
            <div class="metric-card">
                <div class="metric-value">🔬 {avg_resolution:.0f}m</div>
                <div class="metric-label">Resolução Média</div>
                <div class="metric-sublabel">Precisão espacial</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with col3:
        total_classes = 0
        if "Classes" in filtered_df.columns:
            classes_series = pd.to_numeric(
                filtered_df["Classes"], errors="coerce"
            ).dropna()
            if not classes_series.empty:
                total_classes = classes_series.sum()

        if total_classes > 0:
            st.markdown(
                f"""
            <div class="metric-card">
                <div class="metric-value">🏷️ {total_classes}</div>
                <div class="metric-label">Total de Classes</div>
                <div class="metric-sublabel">Categorias de classificação</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with col4:
        if "Type" in filtered_df.columns:
            global_initiatives = len(filtered_df[filtered_df["Type"] == "Global"])
            if global_initiatives > 0:
                st.markdown(
                    f"""
                <div class="metric-card">
                    <div class="metric-value">🌍 {global_initiatives}</div>
                    <div class="metric-label">Iniciativas Globais</div>
                    <div class="metric-sublabel">Cobertura mundial</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )


def _display_initiative_details(filtered_df, meta, sensors_meta):
    """Exibe detalhes das iniciativas selecionadas."""
    st.markdown("---")
    st.subheader("🔍 Exploração Detalhada por Iniciativa")

    # Mapeamento nome -> sigla
    nome_to_sigla = {}
    if "Acronym" in filtered_df.columns and "Name" in filtered_df.columns:
        for _, row in filtered_df.iterrows():
            if pd.notna(row["Name"]) and pd.notna(row["Acronym"]):
                nome_to_sigla[row["Name"]] = row["Acronym"]

    # Opções formatadas para selectbox
    formatted_options = []
    formatted_to_original_name = {}

    if not filtered_df.empty and "Name" in filtered_df.columns:
        for name in filtered_df["Name"].tolist():
            acronym = nome_to_sigla.get(name, "N/A")
            formatted_display = f"{name} ({acronym})"
            formatted_options.append(formatted_display)
            formatted_to_original_name[formatted_display] = name

    selected_initiative_formatted = st.selectbox(
        "Selecione uma iniciativa para ver detalhes:",
        options=formatted_options,
        help="Escolha uma iniciativa para informações detalhadas",
    )

    selected_initiative = formatted_to_original_name.get(selected_initiative_formatted)

    if selected_initiative:
        init_data = filtered_df[filtered_df["Name"] == selected_initiative].iloc[0]
        init_metadata = meta.get(selected_initiative, {})
        initiative_acronym = nome_to_sigla.get(
            selected_initiative, selected_initiative[:10]
        )

        # Header da iniciativa
        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white; padding: 1.5rem; border-radius: 15px; margin: 1rem 0;">
            <h2 style="margin: 0;">🛰️ {initiative_acronym}</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{selected_initiative}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        col1_detail, col2_detail = st.columns([1, 2])

        with col1_detail:
            st.markdown("#### 📊 Métricas Principais")

            # Métricas específicas da iniciativa
            accuracy_val = pd.to_numeric(init_data.get("Accuracy (%)"), errors="coerce")
            resolution_val = pd.to_numeric(init_data.get("Resolution"), errors="coerce")
            classes_val = pd.to_numeric(
                init_data.get("Classes", init_data.get("Number_of_Classes", "")),
                errors="coerce",
            )

            if pd.notna(accuracy_val):
                st.metric("🎯 Acurácia", f"{accuracy_val:.1f}%")
            if pd.notna(resolution_val):
                st.metric("🔬 Resolução", f"{resolution_val:.0f}m")
            if pd.notna(classes_val):
                st.metric("🏷️ Classes", f"{classes_val:.0f}")

            # Informações técnicas
            st.markdown("#### ⚙️ Informações Técnicas")

            type_val = str(init_data.get("Type", "")).strip()
            if type_val and type_val.lower() not in ["n/a", "none"]:
                st.info(f"🏷️ **Tipo:** {type_val}")

            methodology_val = str(init_data.get("Methodology", "")).strip()
            if methodology_val and methodology_val.lower() not in ["n/a", "none"]:
                st.info(f"🔬 **Metodologia:** {methodology_val}")

            coverage_val = str(init_data.get("Coverage", "")).strip()
            if coverage_val and coverage_val.lower() not in ["n/a", "none"]:
                st.info(f"🌍 **Cobertura:** {coverage_val}")

        with col2_detail:
            st.markdown("#### 📋 Detalhes Metodológicos")

            # Abordagem e algoritmo
            methodology_approach = str(init_metadata.get("methodology", "")).strip()
            algorithm_info = str(init_metadata.get("algorithm", "")).strip()

            if methodology_approach and methodology_approach.lower() not in [
                "not available",
                "none",
                "n/a",
            ]:
                st.success(f"**Abordagem:** {methodology_approach}")

            if algorithm_info and algorithm_info.lower() not in [
                "not available",
                "none",
                "n/a",
            ]:
                st.success(f"**Algoritmo:** {algorithm_info}")

            # Provedor e fontes
            provider_info = str(init_metadata.get("provider", "")).strip()
            source_info = str(init_metadata.get("source", "")).strip()

            if provider_info and provider_info.lower() not in [
                "not available",
                "none",
                "n/a",
            ]:
                st.info(f"**Provedor:** {provider_info}")

            if source_info and source_info.lower() not in [
                "not available",
                "none",
                "n/a",
            ]:
                st.info(f"**Fonte de Dados:** {source_info}")

            # Anos disponíveis
            available_years_str = init_data.get("Available_Years_List", "[]")
            try:
                available_years_list = (
                    json.loads(available_years_str) if available_years_str else []
                )
                if isinstance(available_years_list, list) and available_years_list:
                    formatted_years_str = _format_year_ranges(available_years_list)
                    if formatted_years_str:
                        st.warning(f"📅 **Anos Disponíveis:** {formatted_years_str}")
            except json.JSONDecodeError:
                pass

        # Seção de detalhes de classificação - VERSÃO MODERNA E RESPONSIVA
        with st.expander("🏷️ **Detalhes de Classificação**", expanded=False):
            col1, col2 = st.columns([1, 2])

            with col1:
                # Métricas principais em cards
                num_total_classes = pd.to_numeric(
                    init_data.get("Classes", init_data.get("Number_of_Classes", "N/A")),
                    errors="coerce",
                )
                if pd.notna(num_total_classes):
                    st.metric(
                        "🔢 Total de Classes",
                        f"{num_total_classes:.0f}",
                        help="Número total de classes de cobertura da terra",
                    )

                # Classes agrícolas
                num_agri_classes = pd.to_numeric(
                    init_data.get("Num_Agri_Classes", "N/A"), errors="coerce"
                )
                if pd.notna(num_agri_classes):
                    st.metric(
                        "🌾 Classes Agrícolas",
                        f"{num_agri_classes:.0f}",
                        help="Número de classes relacionadas à agricultura",
                    )

            with col2:
                # Legenda de classes em formato responsivo
                class_legend_str = init_data.get("Class_Legend", "[]")
                try:
                    class_legend_list = (
                        json.loads(class_legend_str)
                        if isinstance(class_legend_str, str)
                        else class_legend_str
                    )
                    if isinstance(class_legend_list, list) and class_legend_list:
                        st.markdown("**🌍 Classes de Cobertura da Terra:**")

                        # Organizar classes em colunas para melhor layout
                        if len(class_legend_list) <= 5:
                            # Para poucas classes, mostrar em lista simples
                            for cls in class_legend_list:
                                st.markdown(f"• {cls}")
                        else:
                            # Para muitas classes, usar acordeão
                            with st.container():
                                # Mostrar primeiras 10 classes
                                primary_classes = class_legend_list[:10]

                                # Classes principais em duas colunas
                                subcol1, subcol2 = st.columns(2)
                                mid_point = len(primary_classes) // 2

                                with subcol1:
                                    for cls in primary_classes[:mid_point]:
                                        st.markdown(f"• **{cls}**")

                                with subcol2:
                                    for cls in primary_classes[mid_point:]:
                                        st.markdown(f"• **{cls}**")

                                # Mostrar classes adicionais se houver
                                if len(class_legend_list) > 10:
                                    remaining_classes = class_legend_list[10:]
                                    with st.expander(
                                        f"➕ Ver mais {len(remaining_classes)} classes",
                                        expanded=False,
                                    ):
                                        # Organizar classes restantes em 3 colunas
                                        num_cols = min(3, len(remaining_classes))
                                        cols = st.columns(num_cols)

                                        for i, cls in enumerate(remaining_classes):
                                            col_idx = i % num_cols
                                            with cols[col_idx]:
                                                st.markdown(f"• {cls}")

                except (json.JSONDecodeError, TypeError):
                    st.info("⚠️ Informações de classificação não disponíveis")

        # Informações adicionais em componente colapsável
        additional_info = []
        if "Methodology" in init_data and init_data["Methodology"] != "N/A":
            additional_info.append(f"**🔬 Metodologia:** {init_data['Methodology']}")

        if "Reference" in init_data and init_data["Reference"] != "N/A":
            additional_info.append(f"**📚 Referência:** {init_data['Reference']}")

        # Nova seção: Informações dos Sensores
        with st.expander("🛰️ **Informações de Sensores e Satélites**", expanded=False):
            # Primeiro, verificar se há dados de sensores referenciados
            sensors_referenced = init_data.get("Sensors_Referenced", "")
            source_column = init_data.get("Source", "")

            if sensors_referenced and str(sensors_referenced).strip().lower() not in [
                "n/a",
                "none",
                "",
                "[]",
            ]:
                # Processar dados estruturados de sensores
                try:
                    import json

                    sensors_list = (
                        json.loads(sensors_referenced)
                        if isinstance(sensors_referenced, str)
                        else sensors_referenced
                    )
                    if sensors_list and isinstance(sensors_list, list):
                        st.markdown(f"**📡 Fonte de Dados:** {source_column}")

                        # Processar cada sensor referenciado
                        sensor_info_found = False
                        for sensor_ref in sensors_list:
                            if (
                                isinstance(sensor_ref, dict)
                                and "sensor_key" in sensor_ref
                            ):
                                sensor_key = sensor_ref["sensor_key"]

                                # Buscar metadados do sensor
                                if sensors_meta and sensor_key in sensors_meta:
                                    sensor_info = sensors_meta[sensor_key]
                                    sensor_info_found = True

                                    # Mostrar nome do sensor
                                    if "display_name" in sensor_info:
                                        st.markdown(
                                            f"**🛰️ Sensor:** {sensor_info['display_name']}"
                                        )

                                    # Criar layout em colunas para organizar informações
                                    sensor_col1, sensor_col2 = st.columns(2)

                                    with sensor_col1:
                                        if "platform_name" in sensor_info:
                                            st.info(
                                                f"🛰️ **Plataforma:** {sensor_info['platform_name']}"
                                            )

                                        if "spatial_resolutions_m" in sensor_info:
                                            resolutions = sensor_info[
                                                "spatial_resolutions_m"
                                            ]
                                            if (
                                                isinstance(resolutions, list)
                                                and resolutions
                                            ):
                                                res_str = (
                                                    f"{min(resolutions)}-{max(resolutions)}m"
                                                    if len(resolutions) > 1
                                                    else f"{resolutions[0]}m"
                                                )
                                                st.metric(
                                                    "🔍 Resolução Espacial", res_str
                                                )

                                        if "revisit_time_days" in sensor_info:
                                            st.metric(
                                                "⏰ Tempo de Revisita",
                                                f"{sensor_info['revisit_time_days']} dias",
                                            )

                                    with sensor_col2:
                                        if "spectral_bands" in sensor_info:
                                            bands = sensor_info["spectral_bands"]
                                            if isinstance(bands, list):
                                                st.metric(
                                                    "🌈 Bandas Espectrais", len(bands)
                                                )
                                            elif isinstance(bands, str):
                                                st.metric("🌈 Bandas Espectrais", bands)

                                        if "swath_width_km" in sensor_info:
                                            st.metric(
                                                "📐 Largura de Varredura",
                                                f"{sensor_info['swath_width_km']} km",
                                            )

                                        if "sensor_type_description" in sensor_info:
                                            st.info(
                                                f"� **Tipo:** {sensor_info['sensor_type_description']}"
                                            )

                                    # Informações técnicas adicionais
                                    technical_info = []
                                    if "launch_date" in sensor_info:
                                        technical_info.append(
                                            f"**🚀 Data de Lançamento:** {sensor_info['launch_date']}"
                                        )

                                    if "status" in sensor_info:
                                        technical_info.append(
                                            f"**📊 Status:** {sensor_info['status']}"
                                        )

                                    if "agency" in sensor_info:
                                        technical_info.append(
                                            f"**🏢 Agência:** {sensor_info['agency']}"
                                        )

                                    if "data_access_url" in sensor_info:
                                        technical_info.append(
                                            f"**� Acesso aos Dados:** [Link]({sensor_info['data_access_url']})"
                                        )

                                    if technical_info:
                                        st.markdown("---")
                                        st.markdown(
                                            "**ℹ️ Informações Técnicas Adicionais:**"
                                        )
                                        for info in technical_info:
                                            st.markdown(info)

                                    # Quebra de linha entre sensores se houver múltiplos
                                    if len(sensors_list) > 1:
                                        st.markdown("---")

                        if not sensor_info_found:
                            # Caso não encontre metadados específicos
                            st.info("🔍 Metadados detalhados do sensor não disponíveis")

                            # Tentar extrair informações básicas de outras colunas
                            resolution_info = init_data.get("Resolution", "")
                            if resolution_info and str(
                                resolution_info
                            ).strip().lower() not in ["n/a", "none", ""]:
                                st.metric("🔍 Resolução", f"{resolution_info}m")

                except (json.JSONDecodeError, Exception):
                    # Fallback para dados de origem básicos
                    st.markdown(f"**📡 Fonte de Dados:** {source_column}")
                    st.info("🔍 Erro ao processar metadados detalhados do sensor")

                    # Tentar extrair informações básicas de outras colunas
                    resolution_info = init_data.get("Resolution", "")
                    if resolution_info and str(resolution_info).strip().lower() not in [
                        "n/a",
                        "none",
                        "",
                    ]:
                        st.metric("🔍 Resolução", f"{resolution_info}m")

            elif source_column and str(source_column).strip().lower() not in [
                "n/a",
                "none",
                "",
            ]:
                # Fallback para coluna Source
                st.markdown(f"**📡 Fonte de Dados:** {source_column}")

                # Tentar extrair informações básicas de outras colunas
                resolution_info = init_data.get("Resolution", "")
                if resolution_info and str(resolution_info).strip().lower() not in [
                    "n/a",
                    "none",
                    "",
                ]:
                    st.metric("🔍 Resolução", f"{resolution_info}m")

            else:
                st.info(
                    "📡 Informações de sensor não especificadas para esta iniciativa"
                )

        if additional_info:
            with st.expander("📋 **Informações Adicionais**", expanded=False):
                for info in additional_info:
                    st.markdown(info)


def _display_temporal_analysis(filtered_df, meta):
    """Exibe análise temporal das iniciativas."""
    st.markdown("---")
    st.subheader("🌊 Densidade Temporal das Iniciativas LULC")

    if meta:
        density_data = []
        all_years = set()

        for nome, meta_item in meta.items():
            if nome in filtered_df["Name"].values:
                if "available_years" in meta_item and meta_item["available_years"]:
                    for ano in meta_item["available_years"]:
                        density_data.append({"nome": nome, "ano": ano})
                        all_years.add(ano)

        if density_data:
            density_df = pd.DataFrame(density_data)
            year_counts = density_df["ano"].value_counts().sort_index()

            # Gráfico de densidade por ano
            fig_density = go.Figure()
            fig_density.add_trace(
                go.Bar(
                    x=year_counts.index,
                    y=year_counts.values,
                    name="Iniciativas Ativas",
                    marker={
                        "color": "rgba(0,150,136,0.8)",
                        "line": {"color": "rgba(0,150,136,1)", "width": 1},
                    },
                    hovertemplate="<b>Ano: %{x}</b><br>Iniciativas Ativas: %{y}<extra></extra>",
                )
            )

            fig_density.update_layout(
                title="📊 Densidade Temporal: Número de Iniciativas por Ano",
                xaxis_title="Ano",
                yaxis_title="Número de Iniciativas Ativas",
                height=450,
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            )

            st.plotly_chart(fig_density, use_container_width=True)

            # Botão de download
            if fig_density:
                setup_download_form(
                    fig_density,
                    default_filename="densidade_temporal_overview",
                    key_prefix="densidade_overview",
                )

            # Métricas temporais
            st.markdown("#### 📈 Métricas Temporais")

            if all_years:
                first_year = min(all_years)
                last_year = max(all_years)
                peak_activity_year = year_counts.idxmax()
                avg_initiatives_per_year = year_counts.mean()

                tm_col1, tm_col2, tm_col3, tm_col4 = st.columns(4)

                with tm_col1:
                    st.metric("🗓️ Primeiro Ano", first_year)
                with tm_col2:
                    st.metric("🗓️ Último Ano", last_year)
                with tm_col3:
                    st.metric("🚀 Pico de Atividade", peak_activity_year)
                with tm_col4:
                    st.metric("📊 Média/Ano", f"{avg_initiatives_per_year:.1f}")
        else:
            st.info("ℹ️ Nenhum dado temporal disponível com os filtros atuais.")


def run():
    """Função principal do dashboard overview."""
    # Carrega dados
    df, meta, sensors_meta = _load_data()

    if df.empty:
        st.error(
            "❌ Nenhum dado disponível. Verifique o processo de carregamento de dados."
        )
        return

    # Usa a nova função de filtros responsivos
    filtered_df = _create_filters(df)

    # Aplica filtros básicos de metodologia se necessário
    if "Methodology" in filtered_df.columns:
        metodologias = filtered_df["Methodology"].unique().tolist()
        selected_methods = metodologias  # Usar todas por padrão
    else:
        selected_methods = []

    # Aplica filtros básicos de classes agrícolas se necessário
    if "Num_Agri_Classes" in filtered_df.columns:
        num_agri_classes_numeric = pd.to_numeric(
            filtered_df["Num_Agri_Classes"], errors="coerce"
        ).dropna()
        if not num_agri_classes_numeric.empty:
            min_agri, max_agri = (
                int(num_agri_classes_numeric.min()),
                int(num_agri_classes_numeric.max()),
            )
            selected_agri_range = (min_agri, max_agri)
        else:
            selected_agri_range = (0, 50)
    else:
        selected_agri_range = (0, 50)

    # Aplica filtros adicionais se necessário (mantém compatibilidade)
    if "Methodology" in filtered_df.columns and selected_methods:
        filtered_df = filtered_df[filtered_df["Methodology"].isin(selected_methods)]

    if "Num_Agri_Classes" in filtered_df.columns and selected_agri_range:
        df_temp = filtered_df.copy()
        df_temp["Num_Agri_Classes_numeric"] = pd.to_numeric(
            df_temp["Num_Agri_Classes"], errors="coerce"
        )
        filtered_df = filtered_df[
            df_temp["Num_Agri_Classes_numeric"].between(
                selected_agri_range[0], selected_agri_range[1]
            )
        ]

    # Armazena dados filtrados na sessão
    st.session_state.filtered_df = filtered_df

    if filtered_df.empty:
        st.warning(
            "⚠️ Nenhuma iniciativa corresponde aos filtros selecionados. Ajuste os filtros para visualizar dados."
        )
        st.stop()

    # Exibe métricas principais
    _display_key_metrics(filtered_df)

    # Exibe detalhes das iniciativas
    _display_initiative_details(filtered_df, meta, sensors_meta)

    # Exibe análise temporal
    _display_temporal_analysis(filtered_df, meta)

    # Link para análises detalhadas
    st.markdown("---")
    st.info(
        "💡 **Para comparações detalhadas entre múltiplas iniciativas**, vá para a página **'🔍 Análises Detalhadas'** na barra lateral."
    )


if __name__ == "__main__":
    run()
