"""
Componente para filtros da página Comparison
============================================

Este módulo contém funções para renderizar os filtros da página de comparação
e aplicar filtros aos dados das iniciativas.
"""

import pandas as pd
import streamlit as st


def get_slider_range(
    series_min: pd.Series,
    series_max: pd.Series,
    default_min: int | float,
    default_max: int | float,
    data_type: type[int] | type[float] = int,
) -> tuple[int | float, int | float, tuple[int | float, int | float]]:
    """
    Helper function to safely get min/max for sliders.

    Args:
        series_min: Series with minimum values
        series_max: Series with maximum values
        default_min: Default minimum value
        default_max: Default maximum value
        data_type: Type to cast the values to (int or float)

    Returns:
        Tuple containing (overall_min, overall_max, default_range_tuple)
    """
    # Ensure series are not empty and contain valid numbers
    s_min_numeric = pd.to_numeric(series_min.dropna(), errors="coerce")
    s_max_numeric = pd.to_numeric(series_max.dropna(), errors="coerce")

    s_min_valid = s_min_numeric.dropna()
    s_max_valid = s_max_numeric.dropna()

    if s_min_valid.empty or s_max_valid.empty:
        return (
            data_type(default_min),
            data_type(default_max),
            (data_type(default_min), data_type(default_max)),
        )

    try:
        overall_min_val = s_min_valid.min()
        overall_max_val = s_max_valid.max()
    except Exception:  # Broad exception for any calculation error
        return (
            data_type(default_min),
            data_type(default_max),
            (data_type(default_min), data_type(default_max)),
        )

    if pd.isna(overall_min_val) or pd.isna(overall_max_val):
        return (
            data_type(default_min),
            data_type(default_max),
            (data_type(default_min), data_type(default_max)),
        )

    overall_min = data_type(overall_min_val)
    overall_max = data_type(overall_max_val)

    if overall_min > overall_max:  # Fallback if data is inconsistent
        overall_min, overall_max = data_type(default_min), data_type(default_max)

    return overall_min, overall_max, (overall_min, overall_max)


def render_comparison_filters(df: pd.DataFrame) -> dict:
    """
    Renderiza os filtros da página comparison com design moderno.

    Args:
        df: DataFrame com os dados das iniciativas

    Returns:
        Dict contendo os valores selecionados nos filtros
    """
    # CSS customizado para os filtros
    st.markdown(
        """
    <style>
    .comparison-filters {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 15px;
        padding: 24px;
        margin: 16px 0;
        border: 1px solid rgba(148, 163, 184, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    }

    .filter-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 16px;
        text-align: center;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Header com estilo
    st.markdown(
        """
    <div class="comparison-filters">
        <div class="filter-header">🔎 Initiative Filters</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Row 1: Type and Methodology
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        tipos = (
            sorted(df["Type"].dropna().unique().tolist())
            if "Type" in df.columns
            else []
        )
        selected_types = st.multiselect(
            "Type",
            options=tipos,
            default=tipos,
            key="type_filter",
            help="Select initiative types to include in comparison",
        )

    with filter_col2:
        metodologias = (
            sorted(df["Methodology"].dropna().unique().tolist())
            if "Methodology" in df.columns
            else []
        )
        selected_methods = st.multiselect(
            "Methodology",
            options=metodologias,
            default=metodologias,
            key="methodology_filter",
            help="Select methodologies to include in comparison",
        )

    # Row 2: Resolution and Accuracy ranges
    filter_col3, filter_col4 = st.columns(2)
    with filter_col3:
        # Use the new min/max columns from the interpreter
        res_min_series = df.get("Resolution_min_val", pd.Series(dtype=float))
        res_max_series = df.get("Resolution_max_val", pd.Series(dtype=float))
        min_r, max_r, default_r_val = get_slider_range(
            res_min_series, res_max_series, 0, 1000, data_type=int
        )
        selected_res_range = st.slider(
            "Resolution (m)",
            min_value=min_r,
            max_value=max_r,
            value=default_r_val,
            help="Filters initiatives whose resolution range overlaps with the selected range.",
            key="resolution_filter",
        )

    with filter_col4:
        # Use the new min/max columns from the interpreter
        acc_min_series = df.get("Accuracy_min_val", pd.Series(dtype=float))
        acc_max_series = df.get("Accuracy_max_val", pd.Series(dtype=float))
        min_a, max_a, default_a_val = get_slider_range(
            acc_min_series, acc_max_series, 0.0, 100.0, data_type=float
        )
        selected_acc_range = st.slider(
            "Accuracy (%)",
            min_value=min_a,
            max_value=max_a,
            value=default_a_val,
            format="%.1f",
            help="Filters initiatives whose accuracy range overlaps with the selected range.",
            key="accuracy_filter",
        )

    # Row 3: Reference System (if available)
    filter_col5, filter_col6 = st.columns(2)
    with filter_col5:
        # Assuming Reference_System is a string or list of strings from the interpreter
        all_ref_systems = set()
        if "Reference_System" in df.columns:
            for item in df["Reference_System"].dropna():
                if isinstance(item, list):  # If interpreter returns a list
                    all_ref_systems.update(item)
                elif isinstance(item, str):  # If interpreter returns a string
                    all_ref_systems.update(
                        item.split(", ")
                    )  # Simple split if it's a comma-sep string
        selected_ref_systems = st.multiselect(
            "Reference System",
            options=sorted(all_ref_systems),
            default=sorted(all_ref_systems),
            key="ref_system_filter",
            help="Select coordinate reference systems",
        )

    with filter_col6:
        # Additional filter placeholder - could be used for other criteria
        st.info("Additional filters can be added here as needed")

    return {
        "selected_types": selected_types,
        "selected_methods": selected_methods,
        "selected_res_range": selected_res_range,
        "selected_acc_range": selected_acc_range,
        "selected_ref_systems": selected_ref_systems,
    }


def apply_comparison_filters(df: pd.DataFrame, filter_values: dict) -> pd.DataFrame:
    """
    Aplica os filtros aos dados das iniciativas.

    Args:
        df: DataFrame original
        filter_values: Dict com valores dos filtros do render_comparison_filters

    Returns:
        DataFrame filtrado
    """
    filtered_df = df.copy()

    # Apply type filter
    if filter_values["selected_types"]:
        filtered_df = filtered_df[
            filtered_df["Type"].isin(filter_values["selected_types"])
        ]

    # Apply methodology filter
    if filter_values["selected_methods"]:
        filtered_df = filtered_df[
            filtered_df["Methodology"].isin(filter_values["selected_methods"])
        ]

    # Resolution filtering: an initiative is included if its range [res_min, res_max] overlaps with selected_res_range [sel_min, sel_max]
    # Overlap condition: sel_min <= res_max AND sel_max >= res_min
    if (
        "Resolution_min_val" in filtered_df.columns
        and "Resolution_max_val" in filtered_df.columns
    ):
        sel_res_min, sel_res_max = filter_values["selected_res_range"]
        filtered_df = filtered_df[
            (filtered_df["Resolution_max_val"] >= sel_res_min)
            & (filtered_df["Resolution_min_val"] <= sel_res_max)
        ]

    # Accuracy filtering (similar logic)
    if (
        "Accuracy_min_val" in filtered_df.columns
        and "Accuracy_max_val" in filtered_df.columns
    ):
        sel_acc_min, sel_acc_max = filter_values["selected_acc_range"]
        filtered_df = filtered_df[
            (filtered_df["Accuracy_max_val"] >= sel_acc_min)
            & (filtered_df["Accuracy_min_val"] <= sel_acc_max)
        ]

    # Reference system filter
    if (
        filter_values["selected_ref_systems"]
        and "Reference_System" in filtered_df.columns
    ):
        # This filter needs to be robust if Reference_System can be a list or a string
        def check_ref_system(row_val):
            if isinstance(row_val, list):
                return any(
                    rs in filter_values["selected_ref_systems"] for rs in row_val
                )
            elif isinstance(row_val, str):
                return any(
                    rs in filter_values["selected_ref_systems"]
                    for rs in row_val.split(", ")
                )  # Simple split
            return False

        filtered_df = filtered_df[
            filtered_df["Reference_System"].apply(check_ref_system)
        ]

    return filtered_df


def display_filter_status(original_count: int, filtered_count: int) -> None:
    """
    Exibe o status dos filtros aplicados.

    Args:
        original_count: Número original de iniciativas
        filtered_count: Número de iniciativas após filtros
    """
    if filtered_count != original_count:
        st.markdown(
            f"""
        <div style="
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            border: 1px solid #3b82f6;
            border-radius: 12px;
            padding: 16px;
            margin: 16px 0;
            text-align: center;
        ">
            <strong style="color: #1d4ed8;">
                📊 Filters Applied: {filtered_count} of {original_count} initiatives selected
            </strong>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
        <div style="
            background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
            border: 1px solid #22c55e;
            border-radius: 12px;
            padding: 16px;
            margin: 16px 0;
            text-align: center;
        ">
            <strong style="color: #15803d;">
                ✅ Showing all {original_count} available initiatives
            </strong>
        </div>
        """,
            unsafe_allow_html=True,
        )
