"""
Methodology Deep Dive Component - Comparison Analysis
====================================================

Component for comprehensive methodology analysis with interactive visualizations.
Features methodology distribution charts, technique analysis, and comparative insights.

Every chart here is driven by the single source of truth
(:mod:`dashboard.components.shared.methodology_taxonomy`): the canonical
``Methodology`` column, the flat MECE :data:`LEAVES` and the shared
:data:`METHODOLOGY_COLORS`. The "Methodology Deep Dive" treemap therefore can
never fold *Deep Learning* back into a "Machine Learning" bucket.

Author: LULC Initiatives Dashboard
Date: 2025-08-01
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.components.shared.methodology_taxonomy import (
    LEAVES,
    METHODOLOGY_COLORS,
    canonical_label,
    label_counts,
    membership,
    present_leaves,
)

#: Pinned canonical column — never take ``methodology_cols[0]``.
CANONICAL_METHODOLOGY_COLUMN = "Methodology"

#: Visible caveat shown next to every methodology chart.
METHODOLOGY_NOTE = (
    "Deep Learning ⊂ Machine Learning; 'Shallow ML' = ML clássico (raso)."
)

_METHODOLOGY_TEXT_COLUMNS: tuple[str, ...] = (
    "Methodology",
    "methodology",
    "Classification Method",
    "classification_method",
)


def methodology_distribution_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Return canonical ``[Acronym, Methodology]`` rows for the pie/bar path.

    Pins the canonical ``Methodology`` column when present. Values are passed
    through :func:`canonical_label`, which is idempotent on leaves, so an
    already-canonical column is never re-classified. This is the one path the
    pie, the bar and the shared membership check all consume.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["Acronym", "Methodology"])

    text_column = next(
        (column for column in _METHODOLOGY_TEXT_COLUMNS if column in df.columns), None
    )
    if text_column is None:
        return pd.DataFrame(columns=["Acronym", "Methodology"])

    if "Acronym" in df.columns:
        acronyms = [str(value) for value in df["Acronym"]]
    else:
        acronyms = [str(index) for index in range(len(df))]

    return pd.DataFrame(
        {
            "Acronym": acronyms,
            "Methodology": [canonical_label(value) for value in df[text_column]],
        }
    )


def methodology_counts(df: pd.DataFrame) -> dict[str, int]:
    """Count initiatives per MECE leaf, always returning all six leaves."""
    frame = methodology_distribution_frame(df)
    raw = label_counts(frame["Methodology"].tolist()) if not frame.empty else {}
    return {leaf: raw.get(leaf, 0) for leaf in LEAVES}


def methodology_membership(df: pd.DataFrame) -> dict[str, frozenset[str]]:
    """Map every MECE leaf to its initiative acronyms via the SSoT.

    Leaves with no member map to an empty frozenset so callers can rely on the
    full six-key shape. This is the drill-down twin of :func:`methodology_counts`
    and shares its canonical frame, so counts and members can never diverge.
    """
    frame = methodology_distribution_frame(df)
    if frame.empty:
        return {leaf: frozenset() for leaf in LEAVES}
    resolved = membership(frame)
    return {leaf: resolved.get(leaf, frozenset()) for leaf in LEAVES}


def render_methodology_deepdive_tab(filtered_df: pd.DataFrame) -> None:
    """
    Render comprehensive methodology deep dive analysis with interactive charts.

    Args:
        filtered_df: Filtered DataFrame with initiative data
    """
    st.markdown("#### 🔬 Methodology Deep Dive Analysis")
    st.markdown("*Comparative analysis of methodology performance and accuracy across initiatives.*")

    if filtered_df.empty:
        st.warning("⚠️ No initiative data available for methodology analysis.")
        return

    if not any(column in filtered_df.columns for column in _METHODOLOGY_TEXT_COLUMNS):
        st.warning("⚠️ No methodology information available in the data.")
        return

    st.caption(f"ℹ️ {METHODOLOGY_NOTE}")

    # Tab-based visualization
    tab1, tab2, tab3 = st.tabs([
        "📊 Methodology Distribution",
        "🔄 Technique Comparison",
        "📈 Methodology Trends",
    ])

    with tab1:
        render_methodology_distribution(filtered_df)

    with tab2:
        render_technique_comparison(filtered_df)

    with tab3:
        render_methodology_trends(filtered_df)


def render_methodology_distribution(
    df: pd.DataFrame, methodology_col: str | None = None
) -> None:
    """Render the methodology pie and bar from the canonical present leaves."""
    counts = methodology_counts(df)
    visible = present_leaves(counts)

    if not visible:
        st.info("No methodology data available for distribution analysis.")
        return

    distribution = pd.DataFrame(
        {"Methodology": list(visible), "Count": [counts[leaf] for leaf in visible]}
    )

    st.caption(f"ℹ️ {METHODOLOGY_NOTE}")

    col1, col2 = st.columns(2)

    with col1:
        fig_pie = px.pie(
            distribution,
            values="Count",
            names="Methodology",
            title="<b>Methodology Distribution</b>",
            color="Methodology",
            color_discrete_map=METHODOLOGY_COLORS,
        )
        fig_pie.update_layout(
            font=dict(family="Inter", size=12),
            title_font=dict(size=16, family="Inter", color="#1f2937"),
            legend_title_text="Methodology",
        )
        col1.plotly_chart(fig_pie, use_container_width=True, key="methodology_pie_chart")

    with col2:
        fig_bar = px.bar(
            distribution,
            x="Count",
            y="Methodology",
            orientation="h",
            title="<b>Methodology Frequency</b>",
            color="Methodology",
            color_discrete_map=METHODOLOGY_COLORS,
        )
        fig_bar.update_layout(
            font=dict(family="Inter", size=12),
            title_font=dict(size=16, family="Inter", color="#1f2937"),
            yaxis=dict(categoryorder="array", categoryarray=list(reversed(visible))),
            showlegend=False,
        )
        col2.plotly_chart(fig_bar, use_container_width=True, key="methodology_bar_chart")

    # Summary metrics
    st.markdown("##### Summary Statistics")
    present = distribution[distribution["Count"] > 0]
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Methodologies", len(present))
    with col2:
        if present.empty:
            st.metric("Most Common", "—")
        else:
            most_common = present.sort_values("Count", ascending=False).iloc[0]
            label = most_common["Methodology"]
            st.metric("Most Common", label if len(label) <= 25 else f"{label[:25]}...")
    with col3:
        st.metric("Usage Count", int(present["Count"].max()) if not present.empty else 0)
    with col4:
        coverage_pct = (
            (present["Count"].max() / len(df)) * 100 if not present.empty and len(df) else 0.0
        )
        st.metric("Coverage", f"{coverage_pct:.1f}%")


def render_technique_comparison(
    df: pd.DataFrame, methodology_col: str | None = None
) -> None:
    """Render the treemap from the SSoT leaf counts (Deep Learning stays apart)."""
    counts = categorize_methodologies(df)
    visible = present_leaves(counts)

    if not visible:
        st.info("No technique categorization available.")
        return

    technique_df = pd.DataFrame(
        {"Methodology": list(visible), "Count": [counts[leaf] for leaf in visible]}
    )

    st.caption(f"ℹ️ {METHODOLOGY_NOTE}")

    fig = px.treemap(
        technique_df,
        path=["Methodology"],
        values="Count",
        title="<b>Methodology Techniques Breakdown</b>",
        color="Methodology",
        color_discrete_map=METHODOLOGY_COLORS,
    )
    fig.update_traces(root_color="lightgrey")
    fig.update_layout(
        font=dict(family="Inter", size=12),
        title_font=dict(size=14, family="Inter", color="#1f2937"),
        margin=dict(t=60, l=10, r=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True, key="methodology_techniques_treemap")


def render_methodology_trends(
    df: pd.DataFrame, methodology_col: str | None = None
) -> None:
    """
    Render methodology usage trends over time.

    Detects a temporal column (year/start/date), coerces it to a year
    integer when possible, drops invalid rows, groups by year and
    methodology, and renders a Plotly line chart with SSoT colors.
    """
    # Pin the canonical methodology column (fallback to the passed one)
    methodology_col = (
        CANONICAL_METHODOLOGY_COLUMN
        if CANONICAL_METHODOLOGY_COLUMN in df.columns
        else methodology_col
    )
    if not methodology_col or methodology_col not in df.columns:
        st.warning("No methodology column found.")
        return

    # Heuristic search for temporal columns
    temporal_keys = ("year", "start", "date", "timestamp")
    year_cols = [col for col in df.columns if any(k in col.lower() for k in temporal_keys)]
    if not year_cols:
        st.info("No temporal data available for trend analysis.")
        return

    # Prefer an explicit 'year' column if present
    year_col = next((c for c in year_cols if c.lower() == "year"), year_cols[0])

    # Work on a small copy to avoid SettingWithCopyWarning
    tmp = df[[year_col, methodology_col]].copy()

    # Canonicalise labels so colors/labels come from the SSoT
    tmp[methodology_col] = [canonical_label(value) for value in tmp[methodology_col]]

    # Drop rows missing methodology (they cannot be grouped)
    tmp = tmp.dropna(subset=[methodology_col])
    if tmp.empty:
        st.info("No valid methodology data available for trend analysis.")
        return

    # Try to coerce the temporal column to a year integer
    try:
        parsed = pd.to_datetime(tmp[year_col], errors="coerce")
        if parsed.notna().any():
            tmp[year_col] = parsed.dt.year
        else:
            tmp[year_col] = pd.to_numeric(tmp[year_col], errors="coerce")
    except Exception:
        tmp[year_col] = pd.to_numeric(tmp[year_col], errors="coerce")

    # Drop rows where year parsing failed
    tmp = tmp.dropna(subset=[year_col])
    if tmp.empty:
        st.info("No valid temporal data available for trend analysis.")
        return

    # Ensure integer year type for consistent grouping/sorting
    tmp[year_col] = tmp[year_col].astype(int)

    trend_df = (
        tmp.groupby([year_col, methodology_col])
        .size()
        .reset_index(name="count")
        .sort_values(by=year_col)
    )

    fig = px.line(
        trend_df,
        x=year_col,
        y="count",
        color=methodology_col,
        title="<b>Methodology Usage Trends Over Time</b>",
        markers=True,
        color_discrete_map=METHODOLOGY_COLORS,
    )
    fig.update_layout(
        font=dict(family="Inter", size=12),
        title_font=dict(size=16, family="Inter", color="#1f2937"),
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Number of Initiatives</b>",
        legend_title_text="Methodology",
    )
    st.plotly_chart(fig, use_container_width=True, key="methodology_trends_chart")


def categorize_methodologies(source) -> dict[str, int]:
    """Categorize methodologies with the SSoT rule engine.

    Accepts a DataFrame (canonical ``Methodology`` column, same path as the
    pie/bar) or an iterable of strings. Always returns all six :data:`LEAVES`
    (zero-count leaves included) so a leaf can never silently disappear into
    another bucket.

    Args:
        source: DataFrame or iterable of methodology strings.

    Returns:
        Mapping ``{leaf: count}`` in ``LEAVES`` order.
    """
    if isinstance(source, pd.DataFrame):
        return methodology_counts(source)

    raw = label_counts([canonical_label(value) for value in source])
    return {leaf: raw.get(leaf, 0) for leaf in LEAVES}
