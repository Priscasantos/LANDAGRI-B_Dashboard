"""
Optimized Streamlit UI Elements
==============================

Modern, simplified UI components with clean interface and minimal customization.
Focused on user-friendly experience without excessive options.

Author: Dashboard Iniciativas LULC
Date: 2025
"""

import plotly.graph_objects as go
import streamlit as st


def simple_download_button(
    fig: go.Figure, filename: str = "chart", key_prefix: str = "download"
) -> None:
    """
    Simple, modern download button with minimal customization.

    Args:
        fig: Plotly figure to download
        filename: Base filename for download
        key_prefix: Unique key prefix for widget
    """
    if fig and st.button(f"📥 Download {filename}", key=f"{key_prefix}_btn"):
        st.success("Chart ready for download! Use browser context menu to save.")


def modern_metric_cards(metrics: dict, columns: int = 4) -> None:
    """
    Display metrics in a modern card layout.

    Args:
        metrics: Dictionary with metric_name: (value, delta) pairs
        columns: Number of columns for layout
    """
    cols = st.columns(columns)
    for i, (name, (value, delta)) in enumerate(metrics.items()):
        with cols[i % columns]:
            st.metric(name, value, delta if delta else None)


def info_expander(title: str, content: dict, expanded: bool = False) -> None:
    """
    Modern expandable info panel.

    Args:
        title: Panel title with emoji
        content: Dictionary of content to display
        expanded: Whether to start expanded
    """
    with st.expander(title, expanded=expanded):
        for key, value in content.items():
            if isinstance(value, dict):
                st.subheader(key)
                for sub_key, sub_value in value.items():
                    st.write(f"**{sub_key}**: {sub_value}")
            elif isinstance(value, list):
                st.subheader(key)
                for item in value:
                    st.write(f"• {item}")
            else:
                st.write(f"**{key}**: {value}")


def quick_filter_bar(filter_options: dict, key_prefix: str = "filter") -> dict:
    """
    Create a horizontal filter bar with common controls.

    Args:
        filter_options: Dictionary of filter configurations
        key_prefix: Unique key prefix

    Returns:
        Dictionary of selected filter values
    """
    st.subheader("🔍 Quick Filters")

    cols = st.columns(len(filter_options))
    selected_filters = {}

    for i, (filter_name, config) in enumerate(filter_options.items()):
        with cols[i]:
            if config.get("type") == "selectbox":
                selected_filters[filter_name] = st.selectbox(
                    config["label"],
                    options=config["options"],
                    index=config.get("default_index", 0),
                    key=f"{key_prefix}_{filter_name}",
                )
            elif config.get("type") == "multiselect":
                selected_filters[filter_name] = st.multiselect(
                    config["label"],
                    options=config["options"],
                    default=config.get("default", []),
                    key=f"{key_prefix}_{filter_name}",
                )
            elif config.get("type") == "slider":
                selected_filters[filter_name] = st.slider(
                    config["label"],
                    min_value=config["min_value"],
                    max_value=config["max_value"],
                    value=config.get("default", config["min_value"]),
                    key=f"{key_prefix}_{filter_name}",
                )

    return selected_filters


def status_indicator(status: str, message: str = "") -> None:
    """
    Display status with appropriate styling.

    Args:
        status: 'success', 'warning', 'error', 'info'
        message: Status message
    """
    if status == "success":
        st.success(f"✅ {message}")
    elif status == "warning":
        st.warning(f"⚠️ {message}")
    elif status == "error":
        st.error(f"❌ {message}")
    elif status == "info":
        st.info(f"ℹ️ {message}")


def modern_tabs(tab_config: dict) -> str:
    """
    Create modern tab interface with content.

    Args:
        tab_config: Dictionary with tab_name: content pairs

    Returns:
        Selected tab name
    """
    tab_names = list(tab_config.keys())
    selected_tabs = st.tabs(tab_names)

    for i, (_tab_name, content) in enumerate(tab_config.items()):
        with selected_tabs[i]:
            if callable(content):
                content()
            else:
                st.write(content)

    return tab_names[0]  # Return first tab as default


def loading_placeholder(message: str = "Loading...") -> None:
    """
    Show loading placeholder with spinner.

    Args:
        message: Loading message
    """
    with st.spinner(message):
        st.empty()


def data_table_modern(df, title: str = "", show_download: bool = False) -> None:
    """
    Display data in modern table format with optional download.
    CSV downloads disabled per user request.

    Args:
        df: DataFrame to display
        title: Table title
        show_download: Whether to show download button (disabled by default)
    """
    if title:
        st.subheader(title)

    st.dataframe(df, use_container_width=True, hide_index=True)

    if show_download and not df.empty:
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                "📄 Download CSV",
                csv,
                file_name=f"{title.lower().replace(' ', '_')}.csv",
                mime="text/csv",
            )
        with col2:
            excel_buffer = df.to_excel(index=False)
            if excel_buffer:
                st.download_button(
                    "📊 Download Excel",
                    excel_buffer,
                    file_name=f"{title.lower().replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )


def setup_download_form(
    fig: go.Figure, default_filename: str = "chart", key_prefix: str = "download"
) -> None:
    """
    Legacy compatibility function - redirects to simple download button.

    Args:
        fig: Plotly figure
        default_filename: Base filename
        key_prefix: Unique key prefix
    """
    simple_download_button(fig, default_filename, key_prefix)


# Modern color scheme constants
MODERN_COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "warning": "#d62728",
    "info": "#17becf",
    "light": "#f8f9fa",
    "dark": "#343a40",
}
