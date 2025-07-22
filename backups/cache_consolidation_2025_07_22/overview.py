"""
Overview Dashboard Module
=========================

Main overview page for LULC initiatives dashboard featuring:
- Key metrics and statistics
- Interactive visualizations
- Geographic distribution
- Technology overview

Author: Dashboard Iniciativas LULC
Date: 2025
"""

import json
import sys
from pathlib import Path
from typing import List, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from scripts.utilities.ui_elements import setup_download_form

# Setup paths
current_dir = Path(__file__).parent.parent
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# Importa sistema de cache consolidado
try:
    from utilities.cache_system import (
        load_optimized_data,
        setup_performance_sidebar,
        get_filtered_data,
        calculate_statistics,
        prepare_geographic_data,
        prepare_chart_data,
        display_performance_metrics,
        preload_dashboard_data
    )
    OPTIMIZATION_ENABLED = True
except ImportError as e:
    # Funções dummy para quando otimização não está disponível
    def load_optimized_data():
        return None, {}, {}
    def setup_performance_sidebar():
        try:
            with st.sidebar:
                st.markdown("### 📊 Status")
                st.info("💡 Sistema de otimização não ativo")
        except Exception:
            pass
    def get_filtered_data(df, filters):
        return df
    def calculate_statistics(df):
        return {}
    def prepare_geographic_data(df):
        return {}
    def prepare_chart_data(df):
        return {}
    def display_performance_metrics():
        pass
    def preload_dashboard_data():
        return False
    
    st.warning(f"⚠️ Módulos de otimização não disponíveis: {e}")
    OPTIMIZATION_ENABLED = False


def _format_year_ranges(years_list: List[int]) -> str:
    """
    Format a list of years into readable ranges.

    Args:
        years_list: List of years to format

    Returns:
        String with formatted year ranges (e.g., "2015-2017, 2019, 2021-2023")
    """
    if not years_list:
        return ""

    try:
        years = sorted(list(set(int(y) for y in years_list if str(y).isdigit())))
    except (ValueError, TypeError):
        return ", ".join(sorted(list(set(str(y) for y in years_list))))

    if not years:
        return ""

    ranges = []
    start_range = years[0]

    for i in range(1, len(years)):
        if years[i] != years[i - 1] + 1:
            if start_range == years[i - 1]:
                ranges.append(str(start_range))
            else:
                ranges.append(f"{start_range}-{years[i-1]}")
            start_range = years[i]

    # Add the last range
    if start_range == years[-1]:
        ranges.append(str(start_range))
    else:
        ranges.append(f"{start_range}-{years[-1]}")

    return ", ".join(ranges)


def run():
    """
    Main overview dashboard function with optimized performance.
    """
    # ===== INICIALIZAÇÃO OTIMIZADA =====
    if OPTIMIZATION_ENABLED:
        # Configura sidebar de performance
        setup_performance_sidebar()
        
        # Pré-carrega dados se necessário
        if "optimized_data_loaded" not in st.session_state:
            if preload_dashboard_data():
                st.session_state.optimized_data_loaded = True
            else:
                st.error("❌ Falha no carregamento otimizado")
                return
    
    # Carrega dados principais
    if (
        "df_interpreted" not in st.session_state
        or st.session_state.df_interpreted.empty
    ):
        if OPTIMIZATION_ENABLED:
            # Usa carregamento otimizado
            df, optimized_data, sensors_meta = load_optimized_data()
            if df is not None:
                st.session_state.df_interpreted = df
                st.session_state.optimized_data = optimized_data
                st.session_state.sensors_meta = sensors_meta
            else:
                st.error("❌ Dados não disponíveis")
                return
        else:
            st.error("❌ Data not available. Please ensure the data is loaded correctly.")
            return

    df = st.session_state.get("df_interpreted", pd.DataFrame())
    sensors_meta = _load_sensor_metadata()

    # Modern header with metrics
    st.markdown(
        """
    <div style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); 
                padding: 2rem; border-radius: 12px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; font-weight: 600; font-size: 2.5rem;">
            🌍 LULC Initiatives Overview
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Comprehensive analysis of Land Use Land Cover monitoring initiatives
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Key metrics in modern cards
    _display_key_metrics(df)

    # Main dashboard content with tabs - reorganized for proper function order
    if df.empty:
        st.error("❌ No data available. Please check the data loading process.")
        return

    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Statistics", "🗺️ Geographic", "📈 Technology", "📋 Details"]
    )

    with tab1:
        _display_statistics_tab(df)

    with tab2:
        _display_geographic_tab(df)

    with tab3:
        _display_technology_tab(df, sensors_meta)

    with tab4:
        _display_details_tab(df)


def _load_sensor_metadata():
    """Load sensor metadata with error handling and simple caching."""
    # Verifica cache simples no session_state
    if "sensors_meta_cached" in st.session_state:
        return st.session_state.sensors_meta_cached
    
    sensors_meta = {}
    try:
        from scripts.utilities.json_interpreter import _load_jsonc_file

        sensors_metadata_path = current_dir / "data" / "sensors_metadata.jsonc"
        if sensors_metadata_path.exists():
            sensors_meta_loaded = _load_jsonc_file(sensors_metadata_path)
            if isinstance(sensors_meta_loaded, dict):
                sensors_meta = sensors_meta_loaded
                st.session_state.sensors_meta = sensors_meta
                st.session_state.sensors_meta_cached = sensors_meta  # Cache simples
            else:
                st.warning("⚠️ Sensor metadata did not load as expected.")
        else:
            st.warning("⚠️ Sensor metadata file not found.")
    except Exception as e:
        st.warning(f"⚠️ Error loading sensor metadata: {e}")

    return sensors_meta


def _display_key_metrics(df: pd.DataFrame):
    """Display key metrics in modern card layout."""
    if df.empty:
        st.warning("No data available for metrics calculation.")
        return

    # Calculate metrics
    total_initiatives = len(df)
    countries = df["pais"].nunique() if "pais" in df.columns else 0
    avg_accuracy = (
        df["global_accuracy"].mean() if "global_accuracy" in df.columns else 0
    )
    active_initiatives = (
        len(df[df["status"] == "Active"]) if "status" in df.columns else 0
    )

    # Display in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
        <div class="metric-card">
            <h3 style="color: #3b82f6; margin: 0;">📊 Total Initiatives</h3>
            <h2 style="margin: 0.5rem 0 0 0; color: #0f172a;">{}</h2>
        </div>
        """.format(
                total_initiatives
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="metric-card">
            <h3 style="color: #10b981; margin: 0;">🌍 Countries</h3>
            <h2 style="margin: 0.5rem 0 0 0; color: #0f172a;">{}</h2>
        </div>
        """.format(
                countries
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div class="metric-card">
            <h3 style="color: #f59e0b; margin: 0;">🎯 Avg. Accuracy</h3>
            <h2 style="margin: 0.5rem 0 0 0; color: #0f172a;">{:.1f}%</h2>
        </div>
        """.format(
                avg_accuracy
            ),
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
        <div class="metric-card">
            <h3 style="color: #ef4444; margin: 0;">🔄 Active</h3>
            <h2 style="margin: 0.5rem 0 0 0; color: #0f172a;">{}</h2>
        </div>
        """.format(
                active_initiatives
            ),
            unsafe_allow_html=True,
        )


def _display_details_tab(df: pd.DataFrame):
    """Display detailed information tab."""
    st.markdown("### 📋 Detailed Information")
    
    if not df.empty:
        # Search and filter
        search_term = st.text_input(
            "🔍 Search initiatives:",
            placeholder="Search by name, type, or description...",
            help="Enter keywords to filter the initiatives"
        )
        
        # Filter dataframe based on search
        filtered_df = df.copy()
        if search_term:
            mask = (
                df['Name'].str.contains(search_term, case=False, na=False) |
                df['Type'].str.contains(search_term, case=False, na=False)
            )
            if 'Description' in df.columns:
                mask |= df['Description'].str.contains(search_term, case=False, na=False)
            filtered_df = df[mask]
        
        if filtered_df.empty:
            st.warning(f"🔍 No initiatives found matching '{search_term}'")
            return
        
        # Display count
        total_count = len(df)
        filtered_count = len(filtered_df)
        
        if search_term:
            st.info(f"📊 Showing {filtered_count} of {total_count} initiatives")
        else:
            st.info(f"📊 Showing all {total_count} initiatives")
        
        # Display mode selection
        display_mode = st.radio(
            "Display Mode:",
            ["📊 Table View", "📋 Card View"],
            horizontal=True
        )
        
        if display_mode == "📊 Table View":
            # Table view with pagination
            page_size = st.selectbox("Items per page:", [10, 25, 50, 100], index=1)
            
            total_pages = max(1, (len(filtered_df) + page_size - 1) // page_size)
            page = st.selectbox("Page:", list(range(1, total_pages + 1)))
            
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, len(filtered_df))
            
            page_df = filtered_df.iloc[start_idx:end_idx]
            
            # Select columns to display
            available_columns = list(df.columns)
            default_columns = [col for col in ['Name', 'Type', 'Acronym', 'Start Year', 'Coverage'] if col in available_columns]
            
            selected_columns = st.multiselect(
                "Select columns to display:",
                available_columns,
                default=default_columns
            )
            
            if selected_columns:
                display_df = page_df[selected_columns].copy()
                
                # Format the dataframe for better display
                for col in display_df.columns:
                    if display_df[col].dtype == 'object':
                        display_df[col] = display_df[col].fillna('N/A')
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download button
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download filtered data as CSV",
                    data=csv,
                    file_name=f"initiatives_filtered_{search_term or 'all'}.csv",
                    mime="text/csv"
                )
        
        else:  # Card View
            # Card view with detailed information
            items_per_page = st.selectbox("Cards per page:", [5, 10, 20], index=1)
            
            total_pages = max(1, (len(filtered_df) + items_per_page - 1) // items_per_page)
            page = st.selectbox("Page:", list(range(1, total_pages + 1)), key="card_page")
            
            start_idx = (page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, len(filtered_df))
            
            for idx in range(start_idx, end_idx):
                row = filtered_df.iloc[idx]
                
                with st.expander(f"🛰️ {row.get('Name', 'Unknown')} ({row.get('Acronym', 'N/A')})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📋 Basic Information**")
                        st.write(f"**Type:** {row.get('Type', 'N/A')}")
                        st.write(f"**Coverage:** {row.get('Coverage', 'N/A')}")
                        st.write(f"**Start Year:** {row.get('Start Year', 'N/A')}")
                        if 'End Year' in row and pd.notna(row['End Year']):
                            st.write(f"**End Year:** {row['End Year']}")
                    
                    with col2:
                        st.markdown("**🛰️ Technical Details**")
                        if 'Resolution' in row and pd.notna(row['Resolution']):
                            st.write(f"**Resolution:** {row['Resolution']}")
                        if 'Sensors' in row and pd.notna(row['Sensors']):
                            sensors = row['Sensors']
                            if isinstance(sensors, str):
                                sensor_list = [s.strip() for s in sensors.split(',')]
                            else:
                                sensor_list = sensors
                            st.write(f"**Sensors:** {', '.join(sensor_list) if sensor_list else 'N/A'}")
                    
                    # Description if available
                    if 'Description' in row and pd.notna(row['Description']):
                        st.markdown("**📝 Description**")
                        st.write(row['Description'])
    else:
        st.info("ℹ️ No data available for detailed view.")


def _display_main_dashboard(df: pd.DataFrame, sensors_meta: dict):
    """Display main dashboard content with tabs and visualizations."""
    if df.empty:
        st.error("❌ No data available. Please check the data loading process.")
        return

    # Create filters
    _display_filters(df, sensors_meta)

    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Statistics", "🗺️ Geographic", "📈 Technology", "📋 Details"]
    )

    with tab1:
        _display_statistics_tab(df)

    with tab2:
        _display_geographic_tab(df)

    with tab3:
        _display_technology_tab(df, sensors_meta)

    with tab4:
        _display_details_tab(df)


def _display_filters(df: pd.DataFrame, sensors_meta: Optional[dict] = None):
    """Display modern filter interface."""
    st.markdown("### 🔎 Initiative Filters")

    # Load metadata if needed
    try:
        from scripts.utilities.json_interpreter import _load_jsonc_file
        from pathlib import Path
        current_dir = Path(__file__).parent.parent
        metadata_file_path = current_dir / "data" / "initiatives_metadata.jsonc"
        meta = _load_jsonc_file(metadata_file_path)
    except Exception as e:
        st.warning(f"⚠️ Could not load metadata: {e}")
        meta = {}

    # Fallback for sensors_meta
    if sensors_meta is None:
        sensors_meta = {}

    # Create name to acronym mapping
    nome_to_sigla = {}
    if "Acronym" in df.columns and "Name" in df.columns:
        for _, row in df.iterrows():
            if pd.notna(row["Name"]) and pd.notna(row["Acronym"]):
                nome_to_sigla[row["Name"]] = row["Acronym"]

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        tipos = df["Type"].unique().tolist() if "Type" in df.columns else []
        selected_types = st.multiselect("Type", options=tipos, default=tipos)
    with col2:  # Ensure df is not empty and 'Resolution' column exists
        if (
            not df.empty
            and "Resolution" in df.columns
            and df["Resolution"].notna().any()
        ):
            # Convert to numeric, coercing errors to NaN, then drop NaNs for min/max
            resolutions_numeric = pd.to_numeric(
                df["Resolution"], errors="coerce"
            ).dropna()
            if not resolutions_numeric.empty:
                min_res, max_res = int(resolutions_numeric.min()), int(
                    resolutions_numeric.max()
                )
                selected_res = st.slider(
                    "Resolution (m)",
                    min_value=min_res,
                    max_value=max_res,
                    value=(min_res, max_res),
                )
            else:
                selected_res = st.slider(
                    "Resolution (m)",
                    min_value=0,
                    max_value=1000,
                    value=(0, 1000),
                    disabled=True,
                )
                st.caption("Resolution data not available or not numeric.")
        else:
            selected_res = st.slider(
                "Resolution (m)",
                min_value=0,
                max_value=1000,
                value=(0, 1000),
                disabled=True,
            )
            st.caption("Resolution data not available for current selection.")
    with col3:  # Ensure df is not empty and 'Accuracy (%)' column exists
        if (
            not df.empty
            and "Accuracy (%)" in df.columns
            and df["Accuracy (%)"].notna().any()
        ):  # Changed "Accuracy" to "Accuracy (%)"
            # Convert to numeric, coercing errors to NaN, then drop NaNs for min/max
            accuracies_numeric = pd.to_numeric(
                df["Accuracy (%)"], errors="coerce"
            ).dropna()  # Changed "Accuracy" to "Accuracy (%)"
            if not accuracies_numeric.empty:
                min_acc, max_acc = int(accuracies_numeric.min()), int(
                    accuracies_numeric.max()
                )
                selected_acc = st.slider(
                    "Accuracy (%)",
                    min_value=min_acc,
                    max_value=max_acc,
                    value=(min_acc, max_acc),
                )
            else:
                selected_acc = st.slider(
                    "Accuracy (%)",
                    min_value=0,
                    max_value=100,
                    value=(0, 100),
                    disabled=True,
                )
                st.caption("Accuracy data not available or not numeric.")
        else:
            selected_acc = st.slider(
                "Accuracy (%)",
                min_value=0,
                max_value=100,
                value=(0, 100),
                disabled=True,
            )
            st.caption("Accuracy data not available for current selection.")
    with col4:
        # Ensure df is not empty and 'Methodology' column exists
        metodologias = (
            df["Methodology"].unique().tolist()
            if not df.empty
            and "Methodology" in df.columns
            and df["Methodology"].notna().any()
            else []
        )
        selected_methods = st.multiselect(
            "Methodology", options=metodologias, default=metodologias
        )
    with col5:  # New filter for Number of Agricultural Classes
        if (
            not df.empty
            and "Num_Agri_Classes" in df.columns
            and df["Num_Agri_Classes"].notna().any()
        ):
            # Convert to numeric, coercing errors to NaN, then drop NaNs for min/max
            num_agri_classes_numeric = pd.to_numeric(
                df["Num_Agri_Classes"], errors="coerce"
            ).dropna()
            if not num_agri_classes_numeric.empty:
                min_agri_classes, max_agri_classes = int(
                    num_agri_classes_numeric.min()
                ), int(num_agri_classes_numeric.max())
                # Ensure min is not greater than max, can happen if only one value
                if min_agri_classes > max_agri_classes:
                    max_agri_classes = min_agri_classes
                selected_agri_classes_range = st.slider(
                    "Agricultural Classes",
                    min_value=min_agri_classes,
                    max_value=max_agri_classes,
                    value=(min_agri_classes, max_agri_classes),
                )
            else:
                selected_agri_classes_range = st.slider(
                    "Agricultural Classes",
                    min_value=0,
                    max_value=50,
                    value=(0, 50),
                    disabled=True,
                )
                st.caption(
                    "Number of agricultural classes data not available or not numeric."
                )
        else:
            selected_agri_classes_range = st.slider(
                "Agricultural Classes",
                min_value=0,
                max_value=50,
                value=(0, 50),
                disabled=True,
            )
            st.caption(
                "Number of agricultural classes data not available for current selection."
            )

    # Apply filters

    # Ensure columns used for filtering exist and handle potential errors
    conditions = []
    if "Type" in df.columns and selected_types:
        conditions.append(df["Type"].isin(selected_types))
    if "Resolution" in df.columns and selected_res:
        df["Resolution_numeric"] = pd.to_numeric(df["Resolution"], errors="coerce")
        conditions.append(
            df["Resolution_numeric"].between(selected_res[0], selected_res[1])
        )
    if (
        "Accuracy (%)" in df.columns and selected_acc
    ):  # Changed "Accuracy" to "Accuracy (%)"
        df["Accuracy_numeric"] = pd.to_numeric(
            df["Accuracy (%)"], errors="coerce"
        )  # Changed "Accuracy" to "Accuracy (%)"
        conditions.append(
            df["Accuracy_numeric"].between(selected_acc[0], selected_acc[1])
        )
    if "Methodology" in df.columns and selected_methods:
        conditions.append(df["Methodology"].isin(selected_methods))
    if (
        "Num_Agri_Classes" in df.columns and selected_agri_classes_range
    ):  # Add filter condition for Num_Agri_Classes
        df["Num_Agri_Classes_numeric"] = pd.to_numeric(
            df["Num_Agri_Classes"], errors="coerce"
        )
        conditions.append(
            df["Num_Agri_Classes_numeric"].between(
                selected_agri_classes_range[0], selected_agri_classes_range[1]
            )
        )

    if conditions:
        final_condition = pd.Series(True, index=df.index)
        for cond in conditions:
            final_condition &= cond
        filtered_df = df[final_condition]
    else:  # If no filters are applicable or df is empty
        filtered_df = (
            df.copy()
        )  # Or pd.DataFrame() if you prefer an empty df when no conditions

    # Clean up temporary numeric columns if they were created
    if "Resolution_numeric" in filtered_df.columns:
        filtered_df = filtered_df.drop(columns=["Resolution_numeric"])
    if "Accuracy_numeric" in filtered_df.columns:
        filtered_df = filtered_df.drop(columns=["Accuracy_numeric"])
    if "Num_Agri_Classes_numeric" in filtered_df.columns:  # Clean up temp column
        filtered_df = filtered_df.drop(columns=["Num_Agri_Classes_numeric"])

    st.session_state.filtered_df = filtered_df

    if filtered_df.empty:
        st.warning(
            "⚠️ No initiatives match the selected filters. Adjust the filters to view data."
        )
        st.stop()  # Main content of the Overview page
    st.subheader("📈 Key Aggregated Metrics")

    # Custom CSS for modern metric cards
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
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        margin: 0.5rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }
    .metric-card.accuracy { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .metric-card.resolution { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .metric-card.classes { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .metric-card.global { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    .metric-card.agri-classes { background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%); } /* New style for agri classes */
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    .metric-value {
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .metric-label {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-sublabel {
        font-size: 0.9rem;
        opacity: 0.7;
        margin-top: 0.3rem;
    }
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.2rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        text-decoration: none;
    }
    .badge-type { background: #e3f2fd; color: #1976d2; border: 1px solid #bbdefb; }
    .badge-methodology { background: #f3e5f5; color: #7b1fa2; border: 1px solid #ce93d8; }
    .badge-scope { background: #e8f5e8; color: #388e3c; border: 1px solid #a5d6a7; }
    .badge-years { background: #fff3e0; color: #f57c00; border: 1px solid #ffcc02; }
    .badge-sensor { background: #e0f7fa; color: #00796b; border: 1px solid #b2dfdb; margin-right: 0.5rem; margin-bottom: 0.5rem; } /* Added style for sensor badges */
    .info-section {
        margin: 1.5rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        border-left: 4px solid #28a745;
    }
    .info-title {
        font-weight: 600;
        color: #495057;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Calculate mean only on numeric 'Accuracy (%)' data, dropping NaNs
        avg_accuracy_series = pd.to_numeric(
            filtered_df["Accuracy (%)"], errors="coerce"
        ).dropna()  # Changed "Accuracy" to "Accuracy (%)"
        if not avg_accuracy_series.empty:
            avg_accuracy = avg_accuracy_series.mean()
            st.markdown(
                f"""
            <div class="metric-card accuracy">
                <span class="metric-icon">🎯</span>
                <div class="metric-value">{avg_accuracy:.1f}%</div>
                <div class="metric-label">Average Accuracy</div>
                <div class="metric-sublabel">Across filtered initiatives</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with col2:
        # Calculate mean only on numeric 'Resolution' data, dropping NaNs
        avg_resolution_series = pd.to_numeric(
            filtered_df["Resolution"], errors="coerce"
        ).dropna()
        if not avg_resolution_series.empty:
            avg_resolution = avg_resolution_series.mean()
            st.markdown(
                f"""
            <div class="metric-card resolution">
                <span class="metric-icon">🔬</span>
                <div class="metric-value">{avg_resolution:.0f}m</div>
                <div class="metric-label">Average Resolution</div>
                <div class="metric-sublabel">Spatial precision</div>
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
        elif "Number_of_Classes" in filtered_df.columns:
            num_classes_series = pd.to_numeric(
                filtered_df["Number_of_Classes"], errors="coerce"
            ).dropna()
            if not num_classes_series.empty:
                total_classes = num_classes_series.sum()

        if total_classes > 0:  # Only show if there are classes to sum
            st.markdown(
                f"""
            <div class="metric-card classes">
                <span class="metric-icon">🏷️</span>
                <div class="metric-value">{total_classes}</div>
                <div class="metric-label">Total Classes</div>
                <div class="metric-sublabel">Classification categories</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with col4:
        if "Type" in filtered_df.columns:
            global_initiatives = len(filtered_df[filtered_df["Type"] == "Global"])
            if global_initiatives > 0:  # Only show if there are global initiatives
                st.markdown(
                    f"""
                <div class="metric-card global">
                    <span class="metric-icon">🌍</span>
                    <div class="metric-value">{global_initiatives}</div>
                    <div class="metric-label">Global Initiatives</div>
                    <div class="metric-sublabel">Worldwide coverage</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    st.subheader("🔍 Detailed Exploration by Initiative")

    # CSS for modern initiative details
    st.markdown(
        """    
    <style>
    .initiative-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px 15px 0 0;
        margin: 1rem 0 0 0;
    }
    .initiative-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .detail-card {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 0 0 15px 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    .mini-metric {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border-left: 4px solid #007bff;
    }
    .mini-metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #007bff;
        margin: 0.3rem 0;
    }
    .mini-metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 500;
    }
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.2rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        text-decoration: none;
    }
    .badge-type { background: #e3f2fd; color: #1976d2; border: 1px solid #bbdefb; }
    .badge-methodology { background: #f3e5f5; color: #7b1fa2; border: 1px solid #ce93d8; }
    .badge-scope { background: #e8f5e8; color: #388e3c; border: 1px solid #a5d6a7; }
    .badge-years { background: #fff3e0; color: #f57c00; border: 1px solid #ffcc02; }
    .badge-sensor { background: #e0f7fa; color: #00796b; border: 1px solid #b2dfdb; margin-right: 0.5rem; margin-bottom: 0.5rem; } /* Added style for sensor badges */
    .info-section {
        margin: 1.5rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        border-left: 4px solid #28a745;
    }
    .info-title {
        font-weight: 600;
        color: #495057;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Create name to acronym mapping for this section
    nome_to_sigla = {}
    if "Acronym" in filtered_df.columns and "Name" in filtered_df.columns:
        for _, row in filtered_df.iterrows():
            if pd.notna(row["Name"]) and pd.notna(row["Acronym"]):
                nome_to_sigla[row["Name"]] = row["Acronym"]

    # Create formatted options for the selectbox
    formatted_options = []
    # Create a reverse mapping from formatted string to original name for easy lookup
    formatted_to_original_name = {}

    if not filtered_df.empty and "Name" in filtered_df.columns:
        for name in filtered_df["Name"].tolist():
            acronym = nome_to_sigla.get(
                name, "N/A"
            )  # Get acronym, default to N/A if not found
            formatted_display = f"{name} ({acronym})"
            formatted_options.append(formatted_display)
            formatted_to_original_name[formatted_display] = name

    selected_initiative_formatted = st.selectbox(
        "Select an initiative to see details:",
        options=formatted_options,  # Use the new formatted options
        help="Choose an initiative for detailed information",
        key="overview_detailed_select",
    )

    # Get the original initiative name from the formatted selection
    selected_initiative_detailed = formatted_to_original_name.get(
        selected_initiative_formatted
    )

    if selected_initiative_detailed:
        init_data = filtered_df[
            filtered_df["Name"] == selected_initiative_detailed
        ].iloc[0]
        init_metadata = meta.get(selected_initiative_detailed, {})
        # Get the acronym for the selected initiative
        initiative_acronym = nome_to_sigla.get(
            selected_initiative_detailed, selected_initiative_detailed[:10]
        )

        # Modern initiative header
        st.markdown(
            f"""
        <div class="initiative-header">
            <h2 class="initiative-title">🛰️ {initiative_acronym}</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{selected_initiative_detailed}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("""<div class="detail-card">""", unsafe_allow_html=True)

        col1_detail, col2_detail = st.columns([2, 3])

        with col1_detail:
            st.markdown("#### 📊 Key Metrics")

            # Modern metric grid - Conditional rendering
            metrics_html_parts = []
            accuracy_val = pd.to_numeric(
                init_data.get("Accuracy (%)"), errors="coerce"
            )  # Corrected key to 'Accuracy (%)'
            if pd.notna(accuracy_val):
                metrics_html_parts.append(
                    f"""<div class="mini-metric">
                    <div class="mini-metric-value">🎯 {accuracy_val:.1f}%</div>
                    <div class="mini-metric-label">Accuracy</div></div>"""
                )

            resolution_val = pd.to_numeric(init_data.get("Resolution"), errors="coerce")
            if pd.notna(resolution_val):
                metrics_html_parts.append(
                    f"""<div class="mini-metric">
                    <div class="mini-metric-value">🔬 {resolution_val:.0f}m</div>
                    <div class="mini-metric-label">Resolution</div></div>"""
                )

            classes_val_str = str(
                init_data.get("Classes", init_data.get("Number_of_Classes", ""))
            ).strip()
            classes_val = pd.to_numeric(classes_val_str, errors="coerce")
            if (
                pd.notna(classes_val) and classes_val_str
            ):  # Ensure original was not empty
                metrics_html_parts.append(
                    f"""<div class="mini-metric">
                    <div class="mini-metric-value">🏷️ {classes_val:.0f}</div>
                    <div class="mini-metric-label">Classes</div></div>"""
                )

            frequency_val = str(init_data.get("Temporal_Frequency", "")).strip()
            if (
                frequency_val
                and frequency_val.lower() != "n/a"
                and frequency_val.lower() != "none"
            ):
                metrics_html_parts.append(
                    f"""<div class="mini-metric">
                    <div class="mini-metric-value">📅 {frequency_val}</div>
                    <div class="mini-metric-label">Frequency</div></div>"""
                )

            if metrics_html_parts:
                st.markdown(
                    f"""<div class="metric-grid">{"".join(metrics_html_parts)}</div>""",
                    unsafe_allow_html=True,
                )

            st.markdown("#### ⚙️ Technical Information")
            tech_info_html_parts = []
            type_val = str(init_data.get("Type", "")).strip()
            if type_val and type_val.lower() != "n/a" and type_val.lower() != "none":
                tech_info_html_parts.append(
                    f"""<div class="info-section" style="border-left-color: #17a2b8;">
                                                    <div class="info-title">🏷️ Type</div>
                                                    <p>{type_val}</p></div>"""
                )

            methodology_val = str(init_data.get("Methodology", "")).strip()
            if (
                methodology_val
                and methodology_val.lower() != "n/a"
                and methodology_val.lower() != "none"
            ):
                tech_info_html_parts.append(
                    f"""<div class="info-section" style="border-left-color: #6f42c1;">
                                                    <div class="info-title">🔬 Methodology</div>
                                                    <p>{methodology_val}</p></div>"""
                )

            scope_val = str(
                init_data.get("Coverage", "")
            ).strip()  # Using Coverage for scope
            if scope_val and scope_val.lower() != "n/a" and scope_val.lower() != "none":
                tech_info_html_parts.append(
                    f"""<div class="info-section" style="border-left-color: #28a745;">
                                                    <div class="info-title">🌍 Scope</div>
                                                    <p>{scope_val}</p></div>"""
                )

            # Get available_years from DataFrame (already processed as JSON string then list)
            available_years_str_from_df = init_data.get("Available_Years_List", "[]")
            try:
                available_years_list = (
                    json.loads(available_years_str_from_df)
                    if available_years_str_from_df
                    else []
                )
            except json.JSONDecodeError:
                available_years_list = []

            if isinstance(available_years_list, list) and available_years_list:
                # sorted_years_str = ", ".join(sorted(map(str, set(available_years_list)))) # Old way
                formatted_years_str = _format_year_ranges(
                    available_years_list
                )  # New way
                if formatted_years_str:  # Check if the formatted string is not empty
                    tech_info_html_parts.append(
                        f"""<div class="info-section" style="border-left-color: #fd7e14;">
                                                        <div class="info-title">📅 Available Years</div>
                                                        <p>{formatted_years_str}</p></div>"""
                    )

            # Display Sensors Referenced using info-section and badges inside it
            sensors_referenced_str_from_df = init_data.get("Sensors_Referenced", "[]")
            try:
                sensors_referenced_list_for_display = (
                    json.loads(sensors_referenced_str_from_df)
                    if sensors_referenced_str_from_df
                    else []
                )
            except json.JSONDecodeError:
                sensors_referenced_list_for_display = []

            if (
                isinstance(sensors_referenced_list_for_display, list)
                and sensors_referenced_list_for_display
            ):
                sensor_badges_html_parts = (
                    []
                )  # Keep using badges for individual sensors within the section
                sensor_details_expanders = []  # For expanders

                for sensor_ref_obj in sensors_referenced_list_for_display:
                    current_sensor_key_str = None  # Initialize
                    years_used_list = []

                    if isinstance(sensor_ref_obj, dict):
                        _key_from_dict = sensor_ref_obj.get("sensor_key")
                        if _key_from_dict is not None:
                            current_sensor_key_str = str(
                                _key_from_dict
                            )  # Ensure string
                        years_used_list = sensor_ref_obj.get("years_used", [])
                    elif isinstance(sensor_ref_obj, str):
                        current_sensor_key_str = sensor_ref_obj  # Already a string

                    # Proceed only if current_sensor_key_str is a valid (non-empty) string
                    if (
                        current_sensor_key_str
                    ):  # Check if current_sensor_key_str is not None and not empty
                        sensor_info_from_meta = sensors_meta.get(
                            str(current_sensor_key_str), {}
                        )
                        display_name = sensor_info_from_meta.get(
                            "display_name",
                            str(current_sensor_key_str).replace("_", " ").title(),
                        )

                        sensor_display_text_for_badge = display_name
                        if years_used_list and isinstance(years_used_list, list):
                            years_used_str = _format_year_ranges(
                                years_used_list
                            )  # Use the formatter
                            sensor_display_text_for_badge += (
                                f" (Years: {years_used_str})"
                            )
                        sensor_badges_html_parts.append(
                            f'<span class="badge badge-sensor">{sensor_display_text_for_badge}</span>'
                        )  # Prepare content for expander
                        expander_title = f"🛰️ {display_name} Details"
                        expander_content = ""

                        # Add all details from sensors_meta for this sensor
                        if (
                            sensor_info_from_meta
                        ):  # Check if sensor_info_from_meta is not empty
                            expander_content += "**General Specifications:**\n"
                            for spec_key, spec_value in sensor_info_from_meta.items():
                                if spec_key not in ["display_name", "notes"]:
                                    formatted_spec_key = spec_key.replace(
                                        "_", " "
                                    ).title()
                                    if isinstance(spec_value, list):
                                        # If list of dicts (like spectral_bands)
                                        if all(
                                            isinstance(item, dict)
                                            for item in spec_value
                                        ):
                                            expander_content += (
                                                f"  - **{formatted_spec_key}:**\n"
                                            )
                                            for item_dict in spec_value:
                                                band_details = []
                                                for k, v in item_dict.items():
                                                    band_details.append(
                                                        f"{k.replace('_', ' ').title()}: {v}"
                                                    )
                                                expander_content += (
                                                    f"    - {', '.join(band_details)}\n"
                                                )
                                        else:  # Simple list
                                            expander_content += f"  - **{formatted_spec_key}:** {', '.join(map(str, spec_value))}\n"
                                    elif isinstance(spec_value, dict):
                                        expander_content += (
                                            f"  - **{formatted_spec_key}:**\n"
                                        )
                                        for sub_k, sub_v in spec_value.items():
                                            expander_content += f"    - {sub_k.replace('_', ' ').title()}: {sub_v}\n"
                                    else:
                                        expander_content += f"  - **{formatted_spec_key}:** {spec_value}\n"
                            if "notes" in sensor_info_from_meta:
                                expander_content += (
                                    f"\n**Notes:** {sensor_info_from_meta['notes']}\n"
                                )
                        else:
                            expander_content += "_No detailed specifications found in sensor metadata._\n"

                        sensor_details_expanders.append(
                            (expander_title, expander_content)
                        )
                    # else: current_sensor_key_str was None or empty, so this sensor_ref_obj is skipped

                if sensor_badges_html_parts:
                    tech_info_html_parts.append(
                        f"""<div class="info-section" style="border-left-color: #00bcd4;">
                                                        <div class="info-title">🛰️ Sensors Referenced</div>
                                                        <p>{" ".join(sensor_badges_html_parts)}</p></div>"""
                    )

                # Display expanders for sensor details
                if sensor_details_expanders:
                    st.markdown("#### 🛰️ Detailed Sensor Specifications")
                    for title, content in sensor_details_expanders:
                        with st.expander(title):
                            st.markdown(
                                content, unsafe_allow_html=True
                            )  # Allow markdown for formatting

            if tech_info_html_parts:
                st.markdown(
                    f"""<div style="margin: 1rem 0;">{"".join(tech_info_html_parts)}</div>""",
                    unsafe_allow_html=True,
                )

        with col2_detail:
            st.markdown("#### 📋 Methodological Details")

            methodology_section_html = []

            # Approach and Algorithm
            methodology_approach = str(init_metadata.get("methodology", "")).strip()
            algorithm_info = str(
                init_metadata.get(
                    "algorithm", init_metadata.get("classification_method", "")
                )
            ).strip()
            approach_algo_html = []
            if methodology_approach and methodology_approach.lower() not in [
                "not available",
                "none",
                "n/a",
            ]:
                approach_algo_html.append(
                    f"<p><strong>Approach:</strong> {methodology_approach}</p>"
                )
            if algorithm_info and algorithm_info.lower() not in [
                "not available",
                "none",
                "n/a",
            ]:
                approach_algo_html.append(
                    f"<p><strong>Algorithm:</strong> {algorithm_info}</p>"
                )
            if approach_algo_html:
                methodology_section_html.append(
                    f"""<div class="info-section">
                                                    <div class="info-title">🔬 Methodology</div>
                                                    {"".join(approach_algo_html)}</div>"""
                )

            # Provider & Sources
            provider_info = str(init_metadata.get("provider", "")).strip()
            source_info = str(init_metadata.get("source", "")).strip()
            provider_source_html = []
            if provider_info and provider_info.lower() not in [
                "not available",
                "none",
                "n/a",
            ]:
                provider_source_html.append(
                    f"<p><strong>Provider:</strong> {provider_info}</p>"
                )
            if source_info and source_info.lower() not in [
                "not available",
                "none",
                "n/a",
            ]:
                provider_source_html.append(
                    f"<p><strong>Data Source:</strong> {source_info}</p>"
                )
            if provider_source_html:
                methodology_section_html.append(
                    f"""<div class="info-section" style="border-left-color: #28a745;">
                                                    <div class="info-title">🏢 Provider & Sources</div>
                                                    {"".join(provider_source_html)}</div>"""
                )

            # Update Information & Sensors Referenced (Combined Section)
            update_freq_info = str(init_metadata.get("update_frequency", "")).strip()
            temporal_freq_init_data = str(
                init_data.get("Temporal_Frequency", "")
            ).strip()
            # Initialize sensors_referenced_metadata earlier to ensure it's available
            # sensors_referenced_metadata = init_metadata.get('sensors_referenced', [])
            # Now, get it from the DataFrame (it was stored as a JSON string)
            sensors_referenced_str = init_data.get("Sensors_Referenced", "[]")
            try:
                sensors_referenced_metadata = (
                    json.loads(sensors_referenced_str) if sensors_referenced_str else []
                )
            except json.JSONDecodeError:
                sensors_referenced_metadata = []  # Default to empty list on error

            update_info_html_parts = []

            if update_freq_info and update_freq_info.lower() not in [
                "not available",
                "none",
                "n/a",
            ]:
                update_info_html_parts.append(
                    f"<p><strong>Update Frequency (Metadata):</strong> {update_freq_info}</p>"
                )
            if temporal_freq_init_data and temporal_freq_init_data.lower() not in [
                "not available",
                "none",
                "n/a",
            ]:
                update_info_html_parts.append(
                    f"<p><strong>Temporal Frequency (Data):</strong> {temporal_freq_init_data}</p>"
                )

            # Display Sensors Referenced in this section as well, if not already covered or if more detail is needed here
            if (
                isinstance(sensors_referenced_metadata, list)
                and sensors_referenced_metadata
            ):
                sensors_display_parts = []
                for sensor_ref in sensors_referenced_metadata:
                    if isinstance(sensor_ref, dict):
                        sensor_key_from_dict = sensor_ref.get("sensor_key")
                        sensor_key = (
                            str(sensor_key_from_dict)
                            if sensor_key_from_dict is not None
                            else None
                        )  # Ensure string or None
                        years_used = sensor_ref.get("years_used")

                        # Get display_name from sensors_meta for this section as well
                        sensor_details_from_meta = {}
                        if sensor_key:  # Only proceed if sensor_key is a valid string
                            sensor_details_from_meta = sensors_meta.get(sensor_key, {})
                        display_name = sensor_details_from_meta.get(
                            "display_name",
                            sensor_key if sensor_key else "Unknown Sensor",
                        )

                        sensor_detail_display = display_name
                        if years_used and isinstance(years_used, list):
                            years_used_str = ", ".join(
                                map(str, sorted(list(set(years_used))))
                            )
                            sensor_detail_display += f" (Used in: {years_used_str})"
                        sensors_display_parts.append(
                            f"<li>{sensor_detail_display}</li>"
                        )

            # New section for detailed sensor information
            if (
                isinstance(sensors_referenced_metadata, list)
                and sensors_referenced_metadata
            ):
                detailed_sensor_info_html = [
                    '<div class="info-section" style="border-left-color: #6f42c1;"><div class="info-title">🛰️ Detailed Sensor Specifications</div>'
                ]
                for sensor_ref in sensors_referenced_metadata:
                    if isinstance(sensor_ref, dict):
                        sensor_key_from_ref = sensor_ref.get("sensor_key")

                        key_to_use_for_get = None
                        if (
                            isinstance(sensor_key_from_ref, str)
                            and sensor_key_from_ref.strip()
                        ):
                            key_to_use_for_get = sensor_key_from_ref.strip()

                        sensor_details_from_meta = {}
                        display_name_for_sensor_heading = "Unknown Sensor"

                        if (
                            key_to_use_for_get
                        ):  # This ensures key_to_use_for_get is a non-empty string
                            sensor_details_from_meta = sensors_meta.get(
                                key_to_use_for_get, {}
                            )
                            display_name_for_sensor_heading = (
                                sensor_details_from_meta.get(
                                    "display_name", key_to_use_for_get
                                )
                            )
                        elif (
                            sensor_key_from_ref is not None
                        ):  # Original key was present but not a valid string
                            display_name_for_sensor_heading = (
                                f"Invalid Sensor Key ({str(sensor_key_from_ref)})"
                            )
                        # else: sensor_key_from_ref was None, display_name_for_sensor_heading remains 'Unknown Sensor'

                        detailed_sensor_info_html.append(
                            f"<h5 style='margin-top: 1rem; color: #6f42c1;'>{display_name_for_sensor_heading}</h5><ul style='list-style-type: disc; margin-left: 20px;'>"
                        )

                        family = sensor_details_from_meta.get("sensor_family")
                        platform = sensor_details_from_meta.get("platform_name")
                        sensor_type = sensor_details_from_meta.get(
                            "sensor_type_description"
                        )
                        agency = sensor_details_from_meta.get("agency")
                        status = sensor_details_from_meta.get("status")
                        revisit = sensor_details_from_meta.get("revisit_time_days")

                        if family:
                            detailed_sensor_info_html.append(
                                f"<li><strong>Family:</strong> {family}</li>"
                            )
                        if platform:
                            detailed_sensor_info_html.append(
                                f"<li><strong>Platform:</strong> {platform}</li>"
                            )
                        if sensor_type:
                            detailed_sensor_info_html.append(
                                f"<li><strong>Type:</strong> {sensor_type}</li>"
                            )
                        if agency:
                            detailed_sensor_info_html.append(
                                f"<li><strong>Agency:</strong> {agency}</li>"
                            )
                        if status:
                            detailed_sensor_info_html.append(
                                f"<li><strong>Status:</strong> {status}</li>"
                            )
                        if revisit:
                            detailed_sensor_info_html.append(
                                f"<li><strong>Revisit Time:</strong> {revisit} days</li>"
                            )

                        detailed_sensor_info_html.append("</ul>")
                detailed_sensor_info_html.append("</div>")
                # Ensure this is appended to methodology_section_html, not update_info_html_parts, to place it correctly.
                methodology_section_html.append("".join(detailed_sensor_info_html))

            if update_info_html_parts:  # This section is for update frequency, etc.
                methodology_section_html.append(
                    f"""<div class="info-section" style="border-left-color: #fd7e14;">
                                                    <div class="info-title">🔄 Update & Temporal Info</div>
                                                    {"".join(update_info_html_parts)}</div>"""
                )

            # Detailed Temporal Coverage Analysis from init_metadata['available_years']
            # available_years_metadata = init_metadata.get('available_years', [])
            # Get available_years_list from the DataFrame instead
            # available_years_metadata = init_data.get('Available_Years_List', [])
            # Parse Available_Years_List from JSON string
            available_years_str = init_data.get("Available_Years_List", "[]")
            try:
                available_years_metadata = (
                    json.loads(available_years_str) if available_years_str else []
                )
            except json.JSONDecodeError:
                available_years_metadata = []
            # sensors_referenced_metadata is already defined above

            processed_years_as_int = []
            if isinstance(available_years_metadata, list):
                for year in available_years_metadata:
                    try:
                        processed_years_as_int.append(int(year))
                    except (ValueError, TypeError):
                        continue  # Skip invalid year values

            if processed_years_as_int:
                min_year = min(processed_years_as_int)
                max_year = max(processed_years_as_int)
                year_range = f"{min_year} - {max_year}"
                temporal_coverage_html = f"<p><strong>🕒 Temporal Coverage:</strong> {year_range} (from metadata)</p>"
            else:
                temporal_coverage_html = (
                    "<p><strong>🕒 Temporal Coverage:</strong> Not available</p>"
                )

            # Append temporal coverage info to the methodology section
            methodology_section_html.append(
                f"""<div class="info-section" style="border-left-color: #fd7e14;">
                                                <div class="info-title">📅 Temporal Coverage</div>
                                                {temporal_coverage_html}
                                              </div>"""
            )

            # Append all methodology sections to the main column
            if methodology_section_html:
                st.markdown("".join(methodology_section_html), unsafe_allow_html=True)

        with col2_detail:
            # This is the duplicated "Methodological Details" section that we will REMOVE.
            # The first instance of "Methodological Details" above should be kept.
            # We will NOT re-print the methodology_section_html here.
            pass

        # The st.markdown("</div>", unsafe_allow_html=True) that closes "detail-card"
        # should be placed after all content for the selected initiative is done.        # Additional section for class information
        # Always show classification details if we have class data
        st.markdown("#### 🏷️ Classification Details")

        # Display Number of Classes (Total)
        num_total_classes_str = str(
            init_data.get("Classes", init_data.get("Number_of_Classes", "N/A"))
        ).strip()
        num_total_classes = pd.to_numeric(num_total_classes_str, errors="coerce")
        if pd.notna(num_total_classes) and num_total_classes_str.lower() not in [
            "n/a",
            "none",
            "not available",
        ]:
            st.markdown(
                f"<p><strong>Total Number of Classes:</strong> {num_total_classes:.0f}</p>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<p><strong>Total Number of Classes:</strong> Not specified</p>",
                unsafe_allow_html=True,
            )

        # Display Class Legend (Total Classes)
        class_legend_json_str = init_data.get(
            "Class_Legend", "[]"
        )  # Get from df_interpreted
        try:
            class_legend_list = (
                json.loads(class_legend_json_str)
                if isinstance(class_legend_json_str, str)
                else class_legend_json_str
            )
            if not isinstance(class_legend_list, list):
                class_legend_list = []  # Ensure it's a list
        except (json.JSONDecodeError, TypeError):
            class_legend_list = []

        if class_legend_list:
            st.markdown(
                """<div class="info-section" style="margin-top: 1rem;">
                            <div class="info-title">📋 Land Cover Classes (Legend)</div>""",
                unsafe_allow_html=True,
            )
            classes_html = ""
            for i, cls in enumerate(class_legend_list):
                # Cycle through a few distinct colors for badges
                badge_colors = [
                    "#e3f2fd",
                    "#f3e5f5",
                    "#e8f5e8",
                    "#fff3e0",
                    "#fce4ec",
                    "#e0f2f1",
                    "#ede7f6",
                    "#b3e5fc",
                    "#b2ebf2",
                    "#c8e6c9",
                    "#fff9c4",
                    "#ffecb3",
                ]
                text_colors = [
                    "#1976d2",
                    "#7b1fa2",
                    "#388e3c",
                    "#f57c00",
                    "#d81b60",
                    "#00796b",
                ]
                border_colors = [
                    "#bbdefb",
                    "#ce93d8",
                    "#a5d6a7",
                    "#ffcc02",
                    "#f8bbd0",
                    "#b2dfdb",
                ]
                bg_color = badge_colors[i % len(badge_colors)]
                text_color = text_colors[i % len(text_colors)]
                border_color = border_colors[i % len(border_colors)]
                classes_html += f'<span class="badge" style="background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color}; margin: 0.2rem;">{cls}</span>'

            st.markdown(
                f"""<p style="line-height: 2;">{classes_html}</p></div>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<p><em>Class legend not available.</em></p>", unsafe_allow_html=True
            )

        # Display Number of Agricultural Classes
        num_agri_classes_str = str(init_data.get("Num_Agri_Classes", "N/A")).strip()
        num_agri_classes = pd.to_numeric(num_agri_classes_str, errors="coerce")
        if pd.notna(num_agri_classes) and num_agri_classes_str.lower() not in [
            "n/a",
            "none",
            "not available",
        ]:
            st.markdown(
                f"<p style='margin-top: 0.5rem;'><strong>Number of Agricultural Classes:</strong> {num_agri_classes:.0f}</p>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<p style='margin-top: 0.5rem;'><strong>Number of Agricultural Classes:</strong> Not specified</p>",
                unsafe_allow_html=True,
            )

        # Display Agricultural Class Legend (if available)
        # This assumes a field like 'Agricultural_Class_Legend' might exist in init_data (from json_interpreter)
        agri_class_legend_json_str = init_data.get("Agricultural_Class_Legend", "[]")
        try:
            agri_class_legend_list = (
                json.loads(agri_class_legend_json_str)
                if isinstance(agri_class_legend_json_str, str)
                else agri_class_legend_json_str
            )
            if not isinstance(agri_class_legend_list, list):
                agri_class_legend_list = []  # Ensure it's a list
        except (json.JSONDecodeError, TypeError):
            agri_class_legend_list = []

        if agri_class_legend_list:
            st.markdown(
                """<div class="info-section" style="margin-top: 1rem;">
                            <div class="info-title">🌾 Agricultural Classes (Legend)</div>""",
                unsafe_allow_html=True,
            )
            agri_classes_html = ""
            for i, cls in enumerate(agri_class_legend_list):
                badge_colors = [
                    "#e8f5e8",
                    "#fff3e0",
                    "#e3f2fd",
                    "#f3e5f5",
                    "#fce4ec",
                    "#e0f2f1",
                ]  # Different color set for agri
                text_colors = [
                    "#388e3c",
                    "#f57c00",
                    "#1976d2",
                    "#7b1fa2",
                    "#d81b60",
                    "#00796b",
                ]
                border_colors = [
                    "#a5d6a7",
                    "#ffcc02",
                    "#bbdefb",
                    "#ce93d8",
                    "#f8bbd0",
                    "#b2dfdb",
                ]
                bg_color = badge_colors[i % len(badge_colors)]
                text_color = text_colors[i % len(text_colors)]
                border_color = border_colors[i % len(border_colors)]
                agri_classes_html += f'<span class="badge" style="background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color}; margin: 0.2rem;">{cls}</span>'
            st.markdown(
                f"""<p style="line-height: 2;">{agri_classes_html}</p></div>""",
                unsafe_allow_html=True,
            )
        elif pd.notna(num_agri_classes) and num_agri_classes > 0:
            st.markdown(
                "<p><em>Agricultural class legend not specified.</em></p>",
                unsafe_allow_html=True,
            )

        # New Technical Specifications Section (from df_interpreted)
        # This section focuses on data from df_interpreted (init_data)
        # The previous "Technical Specifications (Metadata)" was from init_metadata

        tech_specs_from_data_html = []

        # Sensor and Data Acquisition Information
        sensor_data_acq_html = []
        spectral_bands = str(init_data.get("Spectral_Bands", "")).strip()
        if spectral_bands and spectral_bands.lower() not in [
            "none",
            "n/a",
            "not available",
        ]:
            sensor_data_acq_html.append(
                f"<li><strong>Spectral Bands:</strong> {spectral_bands}</li>"
            )
        platform = str(init_data.get("Platform", "")).strip()
        if platform and platform.lower() not in ["none", "n/a", "not available"]:
            sensor_data_acq_html.append(
                f"<li><strong>Platform:</strong> {platform}</li>"
            )
        sensor_type = str(init_data.get("Sensor_Type", "")).strip()
        if sensor_type and sensor_type.lower() not in ["none", "n/a", "not available"]:
            sensor_data_acq_html.append(
                f"<li><strong>Sensor Type:</strong> {sensor_type}</li>"
            )
        revisit_time = str(init_data.get("Revisit_Time", "")).strip()
        if revisit_time and revisit_time.lower() not in [
            "none",
            "n/a",
            "not available",
        ]:
            sensor_data_acq_html.append(
                f"<li><strong>Revisit Time:</strong> {revisit_time}</li>"
            )

        if sensor_data_acq_html:
            tech_specs_from_data_html.append(
                f"""<div class="info-section" style="margin-top: 1rem;">
                                        <div class="info-title">🛰️ Sensor & Data Acquisition (from Interpreted Data)</div>
                                        <ul>{"".join(sensor_data_acq_html)}</ul></div>"""
            )

        # Processing and Quality Information
        processing_quality_html = []
        preprocessing_level = str(init_data.get("Preprocessing_Level", "")).strip()
        if preprocessing_level and preprocessing_level.lower() not in [
            "none",
            "n/a",
            "not available",
        ]:
            processing_quality_html.append(
                f"<li><strong>Preprocessing Level:</strong> {preprocessing_level}</li>"
            )
        atmospheric_correction = str(
            init_data.get("Atmospheric_Correction", "")
        ).strip()
        if atmospheric_correction and atmospheric_correction.lower() not in [
            "none",
            "n/a",
            "not available",
        ]:
            processing_quality_html.append(
                f"<li><strong>Atmospheric Correction:</strong> {atmospheric_correction}</li>"
            )
        geometric_correction = str(init_data.get("Geometric_Correction", "")).strip()
        if geometric_correction and geometric_correction.lower() not in [
            "none",
            "n/a",
            "not available",
        ]:
            processing_quality_html.append(
                f"<li><strong>Geometric Correction:</strong> {geometric_correction}</li>"
            )
        cloud_masking = str(init_data.get("Cloud_Masking", "")).strip()
        if cloud_masking and cloud_masking.lower() not in [
            "none",
            "n/a",
            "not available",
        ]:
            processing_quality_html.append(
                f"<li><strong>Cloud Masking:</strong> {cloud_masking}</li>"
            )

        if processing_quality_html:
            tech_specs_from_data_html.append(
                f"""<div class="info-section" style="margin-top: 1rem;">
                                        <div class="info-title">⚙️ Processing & Quality Control (from Interpreted Data)</div>
                                        <ul>{"".join(processing_quality_html)}</ul></div>"""
            )

        # Validation and Data Characteristics
        validation_data_char_html = []
        validation_method = str(init_data.get("Validation_Method", "")).strip()
        if validation_method and validation_method.lower() not in [
            "none",
            "n/a",
            "not available",
        ]:
            validation_data_char_html.append(
                f"<li><strong>Validation Method:</strong> {validation_method}</li>"
            )
        mmu = str(init_data.get("Minimum_Mapping_Unit", "")).strip()
        if mmu and mmu.lower() not in ["none", "n/a", "not available"]:
            validation_data_char_html.append(
                f"<li><strong>Minimum Mapping Unit:</strong> {mmu}</li>"
            )
        data_format = str(init_data.get("Data_Format", "")).strip()
        if data_format and data_format.lower() not in ["none", "n/a", "not available"]:
            validation_data_char_html.append(
                f"<li><strong>Data Format:</strong> {data_format}</li>"
            )

        if validation_data_char_html:
            tech_specs_from_data_html.append(
                f"""<div class="info-section" style="margin-top: 1rem;">
                                        <div class="info-title">📊 Validation & Data Characteristics (from Interpreted Data)</div>
                                        <ul>{"".join(validation_data_char_html)}</ul></div>"""
            )

        if tech_specs_from_data_html:
            st.markdown("#### 🛰️ Technical Specifications (from Interpreted Data)")
            st.markdown("".join(tech_specs_from_data_html), unsafe_allow_html=True)

        # Ensure the detail-card div is closed after all content for the selected initiative
        st.markdown("</div>", unsafe_allow_html=True)  # Closes detail-card

    # Link to detailed comparisons
    st.markdown("---")
    st.info(
        "💡 **For detailed comparisons between multiple initiatives**, go to the **'🔍 Detailed Analyses'** page in the sidebar."
    )
    st.markdown("---")

    # --- START OF MOVED TEMPORAL DENSITY AND METRICS ---
    # Temporal density chart
    st.subheader("🌊 Temporal Density of LULC Initiatives")

    if meta:  # Create density data using metadata
        density_data = []
        all_years = set()

        for nome, meta_item in meta.items():
            # Ensure the initiative is in the filtered_df before processing
            if nome in filtered_df["Name"].values:
                if "available_years" in meta_item and meta_item["available_years"]:
                    for ano in meta_item["available_years"]:
                        density_data.append({"nome": nome, "ano": ano})
                        all_years.add(ano)

        if density_data:
            density_df = pd.DataFrame(density_data)
            year_counts = density_df["ano"].value_counts().sort_index()

            # Density chart by year (discrete bars)
            fig_density_line = go.Figure()
            fig_density_line.add_trace(
                go.Bar(
                    x=year_counts.index,
                    y=year_counts.values,
                    name="Active Initiatives",
                    marker=dict(
                        color="rgba(0,150,136,0.8)",
                        line=dict(color="rgba(0,150,136,1)", width=1),
                    ),
                    hovertemplate="<b>Year: %{x}</b><br>"
                    + "Active Initiatives: %{y}<extra></extra>",
                )
            )

            fig_density_line.update_layout(
                title="📊 Temporal Density: Number of Initiatives per Year",
                xaxis_title="Year",
                yaxis_title="Number of Active Initiatives",
                height=450,
                hovermode="x unified",
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor="rgba(128,128,128,0.2)",
                    tickmode="linear",
                    dtick=2,
                ),
                yaxis=dict(
                    showgrid=True, gridwidth=1, gridcolor="rgba(128,128,128,0.2)"
                ),
            )
            st.plotly_chart(fig_density_line, use_container_width=True)

            # Add download button using the new UI
            # Ensure all old save logic is removed and only setup_download_form is used.
            if fig_density_line:  # Check if the figure exists
                setup_download_form(
                    fig_density_line,
                    default_filename="temporal_density_overview",
                    key_prefix="density_overview_final",
                )

            # Enhanced temporal metrics - Modern cards
            st.markdown("#### 📈 Temporal Metrics")

            # CSS for temporal metrics
            st.markdown(
                """    
            <style>
            .temporal-metric {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1.2rem;
                border-radius: 12px;
                text-align: center;
                margin: 0.5rem 0;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            .temporal-metric-value {
                font-size: 1.8rem;
                font-weight: 700;
                margin: 0.3rem 0;
            }
            .temporal-metric-label {
                font-size: 0.9rem;
                opacity: 0.9;
            }
            .temporal-metric-delta {
                font-size: 0.8rem;
                opacity: 0.8;
                margin-top: 0.2rem;
            }
            .timeline-card { /* This style might be for the timeline details you mentioned */
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            }
            </style>
            """,
                unsafe_allow_html=True,
            )

            # Calculate and display temporal metrics
            if all_years:  # Ensure all_years is not empty
                first_year = min(all_years) if all_years else "N/A"
                last_year = max(all_years) if all_years else "N/A"
                peak_activity_year = (
                    year_counts.idxmax() if not year_counts.empty else "N/A"
                )
                avg_initiatives_per_year = (
                    year_counts.mean() if not year_counts.empty else 0
                )

                tm_col1, tm_col2, tm_col3, tm_col4 = st.columns(4)
                with tm_col1:
                    st.markdown(
                        f"""<div class="temporal-metric">
                                        <div class="temporal-metric-value">🗓️ {first_year}</div>
                                        <div class="temporal-metric-label">First Year Covered</div>
                                    </div>""",
                        unsafe_allow_html=True,
                    )
                with tm_col2:
                    st.markdown(
                        f"""<div class="temporal-metric">
                                        <div class="temporal-metric-value">🗓️ {last_year}</div>
                                        <div class="temporal-metric-label">Last Year Covered</div>
                                    </div>""",
                        unsafe_allow_html=True,
                    )
                with tm_col3:
                    st.markdown(
                        f"""<div class="temporal-metric">
                                        <div class="temporal-metric-value">🚀 {peak_activity_year}</div>
                                        <div class="temporal-metric-label">Peak Activity Year</div>
                                    </div>""",
                        unsafe_allow_html=True,
                    )
                with tm_col4:
                    st.markdown(
                        f"""<div class="temporal-metric">
                                        <div class="temporal-metric-value">📊 {avg_initiatives_per_year:.1f}</div>
                                        <div class="temporal-metric-label">Avg. Initiatives/Year</div>
                                    </div>""",
                        unsafe_allow_html=True,
                    )
            else:
                st.info(
                    "ℹ️ Temporal metrics cannot be calculated as no year data is available from the filtered initiatives' metadata."
                )
        else:
            st.info(
                "ℹ️ No temporal density data to display based on current filters and available metadata."
            )
    # --- END OF MOVED TEMPORAL DENSITY AND METRICS ---

    # Placeholder for any other final content or footers if needed.
    # For example, if there was a "Timeline Details" section showing most/oldest,
    # it would have been *before* the "Temporal Density" and "Temporal Metrics" above.


def _display_statistics_tab(df: pd.DataFrame):
    """Display statistics tab with key metrics and visualizations."""
    st.markdown("### 📊 Key Statistics")
    
    # Display key metrics
    _display_key_metrics(df)
    
    # Additional statistics visualizations
    if not df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔢 Initiative Types")
            if "Type" in df.columns:
                type_counts = df["Type"].value_counts()
                fig = go.Figure(data=[
                    go.Bar(
                        x=type_counts.values,
                        y=type_counts.index,
                        orientation='h',
                        marker_color='#2E86AB'
                    )
                ])
                fig.update_layout(
                    title="Distribution by Type",
                    xaxis_title="Count",
                    yaxis_title="Type",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🎯 Resolution Distribution")
            if "Resolution" in df.columns and df["Resolution"].notna().any():
                resolution_counts = df["Resolution"].value_counts()
                fig = go.Figure(data=[
                    go.Pie(
                        labels=resolution_counts.index,
                        values=resolution_counts.values,
                        hole=0.4
                    )
                ])
                fig.update_layout(
                    title="Resolution Distribution",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)


def _display_geographic_tab(df: pd.DataFrame):
    """Display geographic distribution tab."""
    st.markdown("### 🗺️ Geographic Distribution")
    
    if not df.empty:
        # Coverage analysis
        if "Coverage" in df.columns:
            coverage_data = df["Coverage"].value_counts()
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = go.Figure(data=[
                    go.Bar(
                        x=coverage_data.index,
                        y=coverage_data.values,
                        marker_color=['#A23B72', '#F18F01', '#C73E1D', '#2E86AB', '#F24236'][:len(coverage_data)]
                    )
                ])
                fig.update_layout(
                    title="Geographic Coverage Distribution",
                    xaxis_title="Coverage Type",
                    yaxis_title="Number of Initiatives",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📍 Coverage Summary")
                for coverage_type, count in coverage_data.items():
                    percentage = (count / len(df)) * 100
                    st.metric(
                        label=str(coverage_type),
                        value=f"{count} initiatives",
                        delta=f"{percentage:.1f}%"
                    )
    else:
        st.info("ℹ️ No geographic data available for current selection.")


def _display_technology_tab(df: pd.DataFrame, sensors_meta: dict):
    """Display technology and sensors tab."""
    st.markdown("### 📈 Technology Overview")
    
    if not df.empty:
        # Sensor analysis
        if "Sensors" in df.columns:
            all_sensors = []
            for sensors in df["Sensors"].dropna():
                if isinstance(sensors, str):
                    sensor_list = [s.strip() for s in sensors.split(",")]
                    all_sensors.extend(sensor_list)
                elif isinstance(sensors, list):
                    all_sensors.extend(sensors)
            
            if all_sensors:
                sensor_counts = pd.Series(all_sensors).value_counts()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🛰️ Most Used Sensors")
                    top_sensors = sensor_counts.head(10)
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=top_sensors.values,
                            y=top_sensors.index,
                            orientation='h',
                            marker_color='#2E86AB'
                        )
                    ])
                    fig.update_layout(
                        title="Top 10 Sensors by Usage",
                        xaxis_title="Number of Initiatives",
                        yaxis_title="Sensor",
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("#### 📊 Sensor Statistics")
                    st.metric("Total Unique Sensors", len(sensor_counts))
                    st.metric("Most Popular Sensor", f"{sensor_counts.index[0]} ({sensor_counts.iloc[0]} uses)")
                    st.metric("Average Sensors per Initiative", f"{len(all_sensors) / len(df):.1f}")
                    
                    # Sensor frequency distribution
                    st.markdown("##### Sensor Usage Frequency")
                    for sensor, count in sensor_counts.head(5).items():
                        st.write(f"**{sensor}**: {count} initiatives")
        
        # Technology trends
        if "Start Year" in df.columns:
            st.markdown("#### 📅 Technology Timeline")
            year_counts = df["Start Year"].value_counts().sort_index()
            
            fig = go.Figure(data=[
                go.Scatter(
                    x=year_counts.index,
                    y=year_counts.values,
                    mode='lines+markers',
                    line=dict(color='#F18F01', width=3),
                    marker=dict(size=8, color='#A23B72')
                )
            ])
            fig.update_layout(
                title="Initiative Launch Timeline",
                xaxis_title="Year",
                yaxis_title="Number of Initiatives Launched",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ No technology data available for current selection.")


if __name__ == "__main__":
    run()
