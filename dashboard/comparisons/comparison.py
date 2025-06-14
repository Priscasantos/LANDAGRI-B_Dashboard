import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import sys
from pathlib import Path
from typing import Type, Union

# Adicionar scripts ao path
current_dir = Path(__file__).parent.parent.parent
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)


# Import graphics functions
try:
    from scripts.plotting.generate_graphics import (
        plot_annual_coverage_multiselect,
        plot_classes_por_iniciativa,
        plot_distribuicao_classes,
        plot_distribuicao_metodologias,
        plot_acuracia_por_metodologia
    )
    from scripts.plotting.charts.timeline_chart import timeline_with_controls
except ImportError:
    # Placeholders otimizados
    def timeline_with_controls(metadata, filtered_df):
        """Placeholder para timeline_with_controls"""
        fig = go.Figure().add_annotation(text="Função não disponível", xref="paper", yref="paper", x=0.5, y=0.5)
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_annual_coverage_multiselect(metadata, filtered_df, selected_initiatives):
        """Placeholder para plot_annual_coverage_multiselect"""
        return go.Figure().add_annotation(text="Função não disponível", xref="paper", yref="paper", x=0.5, y=0.5)
    
    def plot_classes_por_iniciativa(filtered_df):
        """Placeholder para plot_classes_por_iniciativa"""
        return go.Figure().add_annotation(text="Função não disponível", xref="paper", yref="paper", x=0.5, y=0.5)
    
    def plot_distribuicao_classes(filtered_df):
        """Placeholder para plot_distribuicao_classes"""
        return go.Figure().add_annotation(text="Função não disponível", xref="paper", yref="paper", x=0.5, y=0.5)
    
    def plot_distribuicao_metodologias(method_counts):
        """Placeholder para plot_distribuicao_metodologias"""
        return go.Figure().add_annotation(text="Função não disponível", xref="paper", yref="paper", x=0.5, y=0.5)
    
    def plot_acuracia_por_metodologia(filtered_df):
        """Placeholder para plot_acuracia_por_metodologia"""
        return go.Figure().add_annotation(text="Função não disponível", xref="paper", yref="paper", x=0.5, y=0.5)

# Add standalone placeholder for plot_resolucao_acuracia (not available in module)
def plot_resolucao_acuracia(metadata, filtered_df):
    """Placeholder para plot_resolucao_acuracia"""
    return go.Figure().add_annotation(text="Função não disponível", xref="paper", yref="paper", x=0.5, y=0.5)



# Import table functions
try:
    from scripts.utilities.tables import gap_analysis
except ImportError:
    def gap_analysis(metadata, filtered_df):
        """Placeholder para gap_analysis"""
        return pd.DataFrame()

# Helper function to safely get min/max for sliders
def get_slider_range(series_min: pd.Series, series_max: pd.Series, 
                     default_min: Union[int, float], default_max: Union[int, float], 
                     data_type: Union[Type[int], Type[float]] = int):
    s_min = series_min.dropna()
    s_max = series_max.dropna()
    
    if s_min.empty or s_max.empty:
        return data_type(default_min), data_type(default_max), (data_type(default_min), data_type(default_max))
    
    try:
        # Attempt to convert to float first for broader compatibility
        overall_min_val = s_min.astype(float).min()
        overall_max_val = s_max.astype(float).max()
    except ValueError: # Fallback if astype(float) fails
        return data_type(default_min), data_type(default_max), (data_type(default_min), data_type(default_max))

    # Ensure values are not NaN before converting to the target data_type
    if pd.isna(overall_min_val) or pd.isna(overall_max_val):
        return data_type(default_min), data_type(default_max), (data_type(default_min), data_type(default_max))

    overall_min = data_type(overall_min_val)
    overall_max = data_type(overall_max_val)
    
    if overall_min > overall_max: # Fallback if data is inconsistent
        overall_min, overall_max = data_type(default_min), data_type(default_max)

    return overall_min, overall_max, (overall_min, overall_max)


def run():
    # Load original data and prepare for filters
    if 'df_original' not in st.session_state or 'metadata' not in st.session_state:
        try:
            # Always use the wrapper for loading standardized data
            from scripts.data_generation.data_wrapper import load_data, prepare_plot_data
            df_loaded, metadata_loaded, _ = load_data()
        except ImportError as e:
            st.error(f"❌ Error importing data modules: {e}")
            st.info("Please check if the data_wrapper module is available.")
            return
        st.session_state.df_original = df_loaded
        st.session_state.metadata = metadata_loaded
        # Ensure df_prepared_initial contains the necessary processed columns for filtering
        st.session_state.df_prepared_initial = prepare_plot_data(df_loaded.copy())['data']

    # Initialize df and meta_geral safely
    df = st.session_state.get('df_prepared_initial', pd.DataFrame())
    meta_geral = st.session_state.get('metadata', {})
    df_geral_original = st.session_state.get('df_original', pd.DataFrame())

    if df.empty:
        st.error("❌ Initial data is not loaded or is empty. Cannot proceed.")
        return

    nome_to_sigla = {}
    if df_geral_original is not None and not df_geral_original.empty and 'Acronym' in df_geral_original.columns:
        for _, row in df_geral_original.iterrows():
            nome_to_sigla[row['Name']] = row['Acronym']

    if 'Display_Name' not in df.columns and 'Name' in df.columns:
        df['Display_Name'] = df['Name'].map(lambda x: nome_to_sigla.get(x, str(x)[:10]))

    st.markdown("### 🔎 Initiative Filters")
    
    # Row 1 for filters
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        tipos = sorted(df["Type"].dropna().unique().tolist()) if "Type" in df.columns else []
        selected_types = st.multiselect("Type", options=tipos, default=tipos, key="type_filter")
    
    with filter_col2:
        metodologias = sorted(df["Methodology"].dropna().unique().tolist()) if "Methodology" in df.columns else []
        selected_methods = st.multiselect("Methodology", options=metodologias, default=metodologias, key="methodology_filter")

    # Row 2 for filters - Resolution and Accuracy
    filter_col3, filter_col4 = st.columns(2)
    with filter_col3:
        # Assumed processed columns: 'Resolution_min_val', 'Resolution_max_val'
        res_min_series = df.get('Resolution_min_val', pd.Series(dtype=float))
        res_max_series = df.get('Resolution_max_val', pd.Series(dtype=float))
        min_r, max_r, default_r_val = get_slider_range(res_min_series, res_max_series, 0, 1000, data_type=int)
        selected_res_range = st.slider("Resolution (m)", 
                                       min_value=min_r, 
                                       max_value=max_r, 
                                       value=default_r_val,
                                       # step=1, # Optional for integer steps
                                       help="Filters initiatives whose resolution range overlaps with the selected range.",
                                       key="resolution_filter")
    
    with filter_col4:
        # Assumed processed columns: 'Accuracy_min_val', 'Accuracy_max_val'
        acc_min_series = df.get('Accuracy_min_val', pd.Series(dtype=float))
        acc_max_series = df.get('Accuracy_max_val', pd.Series(dtype=float))
        min_a, max_a, default_a_val = get_slider_range(acc_min_series, acc_max_series, 0.0, 100.0, data_type=float)
        selected_acc_range = st.slider("Accuracy (%)", 
                                       min_value=min_a, 
                                       max_value=max_a, 
                                       value=default_a_val,
                                       # step=0.1, # Optional for float steps
                                       format="%.1f", # Display one decimal place
                                       help="Filters initiatives whose accuracy range overlaps with the selected range.",
                                       key="accuracy_filter")

    # Row 3 for new filters - Reference System and Detailed Products
    filter_col5, filter_col6 = st.columns(2)
    with filter_col5:
        # Assumed processed column: 'Reference_Systems' (list of strings or NaN)
        all_ref_systems = set()
        if 'Reference_Systems' in df.columns:
            for item_list in df['Reference_Systems'].dropna():
                if isinstance(item_list, list):
                    all_ref_systems.update(item_list)
                elif isinstance(item_list, str): 
                    all_ref_systems.add(item_list)
        unique_ref_systems = sorted(list(all_ref_systems))
        selected_ref_systems = st.multiselect("Reference System", 
                                              options=unique_ref_systems, 
                                              default=unique_ref_systems,
                                              help="Select one or more reference systems.",
                                              key="ref_system_filter")
    
    with filter_col6:
        # Assumed processed column: 'Has_Detailed_Products' (boolean)
        has_detailed_options = ["Yes", "No"] 
        selected_has_detailed_user = st.multiselect("Has Detailed Products?", 
                                                options=has_detailed_options, 
                                                default=has_detailed_options,
                                                help="Filter by presence of detailed products.",
                                                key="detailed_prod_filter")
    
    # Apply filters
    filtered_df = df.copy()

    if selected_types and 'Type' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Type"].isin(selected_types)]
    
    if selected_methods and 'Methodology' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Methodology"].isin(selected_methods)]

    # Resolution filter (overlap logic)
    if 'Resolution_min_val' in filtered_df.columns and 'Resolution_max_val' in filtered_df.columns:
        filter_min_res, filter_max_res = selected_res_range
        filtered_df = filtered_df[
            ~( (filtered_df['Resolution_max_val'] < filter_min_res) | \
               (filtered_df['Resolution_min_val'] > filter_max_res) ) & \
            filtered_df['Resolution_min_val'].notna() & \
            filtered_df['Resolution_max_val'].notna()
        ]
    
    # Accuracy filter (overlap logic)
    if 'Accuracy_min_val' in filtered_df.columns and 'Accuracy_max_val' in filtered_df.columns:
        filter_min_acc, filter_max_acc = selected_acc_range
        filtered_df = filtered_df[
            ~( (filtered_df['Accuracy_max_val'] < filter_min_acc) | \
               (filtered_df['Accuracy_min_val'] > filter_max_acc) ) & \
            filtered_df['Accuracy_min_val'].notna() & \
            filtered_df['Accuracy_max_val'].notna()
        ]

    # Reference System filter
    if 'Reference_Systems' in filtered_df.columns and unique_ref_systems: # Check if there are options to filter by
        # Apply only if not all unique systems are selected (otherwise no filtering needed)
        if set(selected_ref_systems) != set(unique_ref_systems):
            def check_ref_system(val_list):
                if pd.isna(val_list): 
                    return False
                if isinstance(val_list, list):
                    return any(rs in selected_ref_systems for rs in val_list)
                if isinstance(val_list, str):
                     return val_list in selected_ref_systems
                return False
            filtered_df = filtered_df[filtered_df['Reference_Systems'].apply(check_ref_system)]

    # Has Detailed Products filter
    if 'Has_Detailed_Products' in filtered_df.columns:
        allowed_detailed_bools = []
        if "Yes" in selected_has_detailed_user: 
            allowed_detailed_bools.append(True)
        if "No" in selected_has_detailed_user: 
            allowed_detailed_bools.append(False)
        
        if len(allowed_detailed_bools) == 1: # Only if one option is chosen (e.g. only "Yes" or only "No")
            filtered_df = filtered_df[filtered_df['Has_Detailed_Products'].isin(allowed_detailed_bools)]
        # If len is 0 (user deselects both) or 2 (user selects both, default), no filtering on this criterion.

    st.session_state.filtered_df = filtered_df

    if filtered_df.empty:
        st.warning("⚠️ No initiatives match the selected filters. Adjust filters to view data.")
        # Do not stop if you want to allow users to adjust filters without a full stop.
        # Consider if st.stop() is appropriate or if just showing the warning is enough.
        # For now, let it proceed to show empty tabs if that's the desired behavior.

    df_filt = filtered_df
    # Apply basic filters
    df_filt_limited = df_filt.copy()

    # Tabs with English translations
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dual Bars",
        "🎯 Resolution vs Accuracy",
        "📅 Temporal Coverage",
        "🏷️ Number of Classes",
        "⚙️ Methodologies",
        "🕸️ Radar Analysis"
    ])

    with tab1:
        st.subheader("Dual Bars: Accuracy x Resolution")
        # Ensure necessary columns exist before plotting
        if 'Resolution_min_val' in df_filt_limited.columns and \
           'Resolution_max_val' in df_filt_limited.columns and \
           'Accuracy_min_val' in df_filt_limited.columns and \
           'Accuracy_max_val' in df_filt_limited.columns and \
           'Display_Name' in df_filt_limited.columns:

            plot_df_tab1 = df_filt_limited.copy()

            # Consolidate Resolution for plotting
            if 'Resolution (m)' in plot_df_tab1.columns:
                plot_df_tab1['Plot_Resolution'] = pd.to_numeric(plot_df_tab1['Resolution (m)'], errors='coerce')
            elif 'Resolution_min_val' in plot_df_tab1.columns: # Fallback to min value if single value not present
                plot_df_tab1['Plot_Resolution'] = pd.to_numeric(plot_df_tab1['Resolution_min_val'], errors='coerce')
            else:
                plot_df_tab1['Plot_Resolution'] = np.nan

            # Consolidate Accuracy for plotting
            if 'Accuracy (%)' in plot_df_tab1.columns:
                plot_df_tab1['Plot_Accuracy'] = pd.to_numeric(plot_df_tab1['Accuracy (%)'], errors='coerce')
            elif 'Accuracy_max_val' in plot_df_tab1.columns: # Fallback to max value
                plot_df_tab1['Plot_Accuracy'] = pd.to_numeric(plot_df_tab1['Accuracy_max_val'], errors='coerce')
            else:
                plot_df_tab1['Plot_Accuracy'] = np.nan

            plot_df_tab1.dropna(subset=['Plot_Resolution', 'Plot_Accuracy', 'Display_Name'], inplace=True)


            if not plot_df_tab1.empty:
                plot_df_tab1['resolucao_norm_temp'] = plot_df_tab1['Plot_Resolution'].replace(0, np.nan)
                plot_df_tab1['resolucao_norm'] = (1 / plot_df_tab1['resolucao_norm_temp'])
                
                if plot_df_tab1['resolucao_norm'].notna().any() and plot_df_tab1['resolucao_norm'].nunique() > 1:
                    max_norm_res = plot_df_tab1['resolucao_norm'].dropna().max()
                    if max_norm_res > 0:
                        plot_df_tab1['resolucao_norm'] = (plot_df_tab1['resolucao_norm'] / max_norm_res) * 100
                    else:
                        plot_df_tab1['resolucao_norm'] = 0
                elif plot_df_tab1['resolucao_norm'].notna().any():
                    plot_df_tab1['resolucao_norm'] = 50
                else:
                    plot_df_tab1['resolucao_norm'] = 0

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=plot_df_tab1['Display_Name'],
                    x=plot_df_tab1['Plot_Accuracy'],
                    name='Accuracy (%)',
                    orientation='h',
                    marker_color='royalblue'
                ))
                fig.add_trace(go.Bar(
                    y=plot_df_tab1['Display_Name'],
                    x=plot_df_tab1['resolucao_norm'],
                    name='Resolution (normalized)',
                    orientation='h',
                    marker_color='orange'
                ))
                fig.update_layout(
                    barmode='group',
                    xaxis_title='Value (% for Accuracy, Normalized Score for Resolution)',
                    yaxis_title='Initiative',
                    title='Comparison: Accuracy vs Resolution',
                    height=max(400, len(plot_df_tab1) * 25)
                )
                st.plotly_chart(fig, use_container_width=True, key="dual_bars_chart")
            else:
                st.info("Not enough data to display the dual bars chart after filtering for valid Resolution and Accuracy.")
        elif df_filt_limited.empty:
            st.info("No data to display after applying filters.")
        else:
            st.info("Required data columns (Display_Name, Resolution, Accuracy) are missing or insufficient for the dual bars chart.")
        # Enhanced Analysis Features (translated to English)
        st.markdown("---")
        st.markdown("### 📊 Advanced Analysis")
        
        # Methodology Comparative Analysis
        st.markdown("#### 📈 Comparative Analysis by Methodology")
        
        if meta_geral:
            # Create timeline data for methodology analysis
            timeline_data = []
            produto_info = {}
            
            # Map products to get technical characteristics
            if df_geral_original is not None and not df_geral_original.empty:
                for _, row in df_geral_original.iterrows():
                    produto_info[row['Name']] = {
                        'metodologia': row.get('Methodology', 'N/A'),
                        'escopo': row.get('Scope', 'N/A'),
                        'acuracia': row.get('Accuracy (%)', 0),
                        'resolucao': row.get('Resolution (m)', 0)
                    }
            
            # Collect all years from all initiatives
            for nome, meta in meta_geral.items():
                # Try both possible keys for temporal data
                years_key = 'available_years' if 'available_years' in meta else 'anos_disponiveis'
                if years_key in meta and meta[years_key]:
                    info = produto_info.get(nome, {})
                    for ano in meta[years_key]:
                        timeline_data.append({
                            'produto': nome,
                            'ano': ano,
                            'disponivel': 1,
                            'metodologia': info.get('metodologia', 'N/A'),
                            'escopo': info.get('escopo', 'N/A')
                        })
            
            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data)
                produtos_unicos = sorted(timeline_df['produto'].unique())
                metodologias_unicas = timeline_df['metodologia'].unique()
                
                # Statistics by methodology
                metod_stats = timeline_df.groupby('metodologia').agg({
                    'produto': 'nunique',
                    'ano': ['min', 'max', 'count']
                }).round(1)
                metod_stats.columns = ['Products', 'First Year', 'Last Year', 'Total Product-Years']
                
                # Calculate average coverage period
                periodo_medio = {}
                for metodologia in metodologias_unicas:
                    produtos_metod = timeline_df[timeline_df['metodologia'] == metodologia]['produto'].unique()
                    periodos = []
                    for produto in produtos_metod:
                        anos_produto = timeline_df[
                            (timeline_df['produto'] == produto) & 
                            (timeline_df['metodologia'] == metodologia)
                        ]['ano'].tolist()
                        if anos_produto:
                            periodos.append(max(anos_produto) - min(anos_produto) + 1)
                    periodo_medio[metodologia] = np.mean(periodos) if periodos else 0
                metod_stats['Average Period'] = [periodo_medio.get(metod, 0) for metod in metod_stats.index]
                
                st.dataframe(metod_stats, use_container_width=True)
                
                # LULC Products Accuracy Ranking
                if df_geral_original is not None and not df_geral_original.empty and 'Accuracy (%)' in df_geral_original.columns:
                    st.markdown("#### 🏆 Ranking de Acurácia dos Produtos LULC")
                    
                    # Create ranking data
                    ranking_data = []
                    for produto in produtos_unicos:
                        produto_timeline = timeline_df[timeline_df['produto'] == produto].iloc[0]
                        metodologia = produto_timeline['metodologia']
                        
                        # Get accuracy data
                        produto_row = df_geral_original[df_geral_original['Name'] == produto]
                        if not produto_row.empty:
                            acuracia = produto_row['Accuracy (%)'].iloc[0] if pd.notna(produto_row['Accuracy (%)'].iloc[0]) else 0
                            resolucao = produto_row['Resolution (m)'].iloc[0] if 'Resolution (m)' in produto_row.columns and pd.notna(produto_row['Resolution (m)'].iloc[0]) else 0
                        else:
                            acuracia = 0
                            resolucao = 0
                        
                        # Calculate temporal coverage
                        anos_produto = timeline_df[timeline_df['produto'] == produto]['ano'].unique()
                        cobertura_temporal = len(anos_produto)
                        periodo_inicio = min(anos_produto) if len(anos_produto) > 0 else 0
                        periodo_fim = max(anos_produto) if len(anos_produto) > 0 else 0
                        
                        ranking_data.append({
                            'produto': produto,
                            'metodologia': metodologia,
                            'acuracia': acuracia,
                            'resolucao': resolucao,
                            'cobertura_temporal': cobertura_temporal,
                            'periodo_inicio': periodo_inicio,
                            'periodo_fim': periodo_fim
                        })
                    
                    ranking_df = pd.DataFrame(ranking_data)
                    
                    # Horizontal ranking chart by accuracy
                    if ranking_df['acuracia'].sum() > 0:  # If there's accuracy data
                        ranking_sorted = ranking_df.sort_values('acuracia', ascending=True)
                        
                        fig_ranking = px.bar(
                            ranking_sorted,
                            x='acuracia',
                            y='produto',
                            color='metodologia',
                            orientation='h',
                            title='🏆 Ranking de Acurácia dos Produtos LULC',
                            labels={'acuracia': 'Accuracy (%)', 'produto': 'Produto'},
                            color_discrete_sequence=px.colors.qualitative.Set1,
                            text='acuracia'
                        )
                        
                        fig_ranking.update_traces(
                            texttemplate='%{text:.1f}%', 
                            textposition='outside',
                            marker_line=dict(width=2, color='white')
                        )
                        
                        fig_ranking.update_layout(
                            height=max(400, len(ranking_sorted) * 25),
                            xaxis_title='Accuracy (%)',
                            yaxis_title='Produtos LULC',
                            font=dict(size=12, color="#2D3748"),
                            plot_bgcolor="#FFFFFF",
                            paper_bgcolor="#FFFFFF",
                            showlegend=True,
                            legend=dict(
                                orientation="v",
                                yanchor="middle",
                                y=0.5,
                                xanchor="left",
                                x=1.02,
                                title="Metodologia",
                                font=dict(color="#2D3748")
                            )
                        )
                        
                        st.plotly_chart(fig_ranking, use_container_width=True, key="ranking_acuracia_tab1")
                        
                        # Top 5 and Bottom 5
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("##### 🥇 Top 5 - Maior Acurácia")
                            top_5 = ranking_sorted.tail(5)[['produto', 'acuracia', 'metodologia']]
                            top_5 = top_5.sort_values('acuracia', ascending=False)
                            
                            for idx, row in top_5.iterrows():
                                st.success(f"**{row['produto']}**: {row['acuracia']:.1f}% ({row['metodologia']})")
                        
                        with col2:
                            st.markdown("##### 📉 Bottom 5 - Menor Acurácia")
                            bottom_5 = ranking_sorted.head(5)[['produto', 'acuracia', 'metodologia']]
                            
                            for idx, row in bottom_5.iterrows():
                                st.warning(f"**{row['produto']}**: {row['acuracia']:.1f}% ({row['metodologia']})")
                        
                        # Ranking statistics
                        st.markdown("##### 📊 Estatísticas do Ranking")
                        ranking_col1, ranking_col2, ranking_col3, ranking_col4 = st.columns(4)
                        
                        with ranking_col1:
                            st.metric("🏆 Melhor Acurácia", f"{ranking_df['acuracia'].max():.1f}%")
                        with ranking_col2:
                            st.metric("📊 Acurácia Média", f"{ranking_df['acuracia'].mean():.1f}%")                        
                        with ranking_col3:
                            st.metric("📉 Menor Acurácia", f"{ranking_df['acuracia'].min():.1f}%")
                        with ranking_col4:
                            desvio = ranking_df['acuracia'].std()
                            st.metric("📈 Desvio Padrão", f"{desvio:.1f}%")
                    
                    else:
                        st.info("ℹ️ Dados de acurácia não disponíveis para criar ranking.")
                else:
                    st.warning("⚠️ Dados de acurácia não disponíveis nos dados originais.")
            else:
                st.info("ℹ️ Dados temporais insuficientes para análise de metodologia.")
        else:
            st.warning("⚠️ Metadados não disponíveis para análise de metodologia.")
    
    with tab2:
        st.subheader("Spatial Resolution vs Accuracy (Scatter)")        # Modern scatterplot with siglas
        fig_scatter = px.scatter(
            df_filt_limited,
            x='Resolution (m)',
            y='Accuracy (%)',
            color='Methodology' if 'Methodology' in df_filt_limited.columns else None,
            hover_name='Display_Name',  # Use siglas for hover
            size='Classes' if 'Classes' in df_filt_limited.columns else None,
            title="Accuracy vs Spatial Resolution",
            labels={
                'Resolution (m)': 'Spatial Resolution (m)',
                'Accuracy (%)': 'Accuracy (%)',
                'Methodology': 'Methodology',
                'Classes': 'No. of Classes'
            },
            height=500        )
        fig_scatter.update_traces(marker=dict(size=14, opacity=0.8, line=dict(width=2, color='white')))
        st.plotly_chart(fig_scatter, use_container_width=True, key="scatter_resolution_accuracy")
        
        st.subheader("Temporal Availability of Initiatives")
        try:
            from scripts.plotting.generate_graphics import plot_ano_overlap
            fig_disp = plot_ano_overlap(meta_geral, df_filt_limited)
        except ImportError:
            fig_disp = go.Figure()
            fig_disp.add_annotation(text="Overlap function not available", 
                                  xref="paper", yref="paper", x=0.5, y=0.5)
        st.plotly_chart(fig_disp, use_container_width=True, key="temporal_availability")

    with tab3:
        st.markdown('<div class="timeline-container"><h2 class="timeline-title">📅 General Timeline of Initiatives</h2></div>', unsafe_allow_html=True)
        timeline_with_controls(meta_geral, df_geral_original)
        
        # Methodology Evolution Over Time Chart (translated to English)
        if meta_geral and df_geral_original is not None and not df_geral_original.empty:
            st.markdown("#### ⏰ Evolution of Methodologies Over Time")
            
            # Create enhanced timeline data for methodology analysis
            timeline_data = []
            produto_info = {}
              # Map products to get methodology information
            for _, row in df_geral_original.iterrows():
                produto_info[row['Name']] = {
                    'metodologia': row.get('Methodology', 'N/A'),
                    'escopo': row.get('Scope', 'N/A')
                }
              # Collect all years from all initiatives with methodology info
            for nome, meta in meta_geral.items():
                # Try both possible keys for temporal data
                years_key = 'available_years' if 'available_years' in meta else 'anos_disponiveis'
                if years_key in meta and meta[years_key]:
                    info = produto_info.get(nome, {})
                    for ano in meta[years_key]:
                        timeline_data.append({
                            'produto': nome,
                            'ano': ano,
                            'disponivel': 1,
                            'metodologia': info.get('metodologia', 'N/A')
                        })
            
            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data)
                anos_reais = sorted(list(set(timeline_df['ano'].tolist())))
                
                # Create data for stacked area chart by methodology
                timeline_pivot = timeline_df.groupby(['ano', 'metodologia']).size().reset_index(name='count')
                
                fig_metodologia_evolucao = px.area(
                    timeline_pivot,
                    x='ano',
                    y='count',
                    color='metodologia',
                    title='📈 Evolution of LULC Methodology Adoption',
                    labels={'ano': 'Year', 'count': 'Number of Products', 'metodologia': 'Methodology'},
                    color_discrete_sequence=px.colors.qualitative.Set1
                )
                
                fig_metodologia_evolucao.update_layout(
                    height=400,
                    font=dict(size=12, color="#2D3748"),
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    xaxis=dict(range=[min(anos_reais), max(anos_reais)], color="#2D3748"),
                    yaxis=dict(color="#2D3748"),
                    legend=dict(font=dict(color="#2D3748")),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_metodologia_evolucao, use_container_width=True, key="metodologia_evolucao_tab3")
            else:
                st.info("Dados insuficientes para análise de evolução de metodologias.")
        
        gap_df = gap_analysis(meta_geral, df_geral_original)
        if not gap_df.empty:
            st.markdown('#### Lacunas Temporais nas Séries (Todas Iniciativas)')
            # Tabela interativa com ordenação e sem índice
            st.dataframe(
                gap_df.sort_values('Maior lacuna temporal', ascending=False),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Nome": st.column_config.TextColumn("Nome", width="large"),
                    "Primeiro Ano": st.column_config.NumberColumn("Primeiro ano de cobertura", format="%d"),
                    "Último Ano": st.column_config.NumberColumn("Último ano de cobertura", format="%d"),
                    "Número de anos com lacuna temporal": st.column_config.NumberColumn("Número de anos com lacuna temporal", format="%d"),
                    "Maior lacuna temporal": st.column_config.NumberColumn("Maior lacuna temporal", format="%d"),
                    "Tipo": st.column_config.TextColumn("Tipo", width="medium")
                }
            )
            # Botão para download da tabela de lacunas temporais
            st.download_button(
                "⬇️ Baixar Tabela de Lacunas Temporais (CSV)",
                data=gap_df.sort_values('Maior lacuna temporal', ascending=False).to_csv(index=False).encode('utf-8'),
                file_name="lacunas_temporais_iniciativas.csv",
                mime="text/csv",
                help="Baixa a tabela completa de lacunas temporais das iniciativas"
            )
        else:
            st.info('Todas as iniciativas possuem séries temporais contínuas ou apenas um ano disponível.')        # Análise de sobreposição de anos
        st.markdown("#### Análise de Sobreposição de Anos")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Heatmap de Cobertura Anual")
            # Criar dados anuais a partir dos metadados
            if meta_geral:
                yearly_data = []
                for nome, meta in meta_geral.items():
                    # Try both possible keys for temporal data
                    years_key = 'available_years' if 'available_years' in meta else 'anos_disponiveis'
                    if years_key in meta and meta[years_key]:
                        # Get accuracy from df_geral_original
                        produto_row = df_geral_original[df_geral_original['Name'] == nome]
                        acuracia = produto_row['Accuracy (%)'].iloc[0] if not produto_row.empty and pd.notna(produto_row['Accuracy (%)'].iloc[0]) else 0
                        resolucao = produto_row['Resolution (m)'].iloc[0] if not produto_row.empty and 'Resolution (m)' in produto_row.columns and pd.notna(produto_row['Resolution (m)'].iloc[0]) else 0
                        
                        for ano in meta[years_key]:
                            yearly_data.append({
                                'Ano': ano,
                                'Name': nome,
                                'Accuracy (%)': acuracia,
                                'Resolution (m)': resolucao
                            })
                
                if yearly_data:
                    yearly_df = pd.DataFrame(yearly_data)
                    cobertura_anual = yearly_df.groupby('Ano').agg(
                        iniciativas_totais=('Name', 'count'),
                        acuracia_media=('Accuracy (%)', 'mean'),
                        resolucao_media=('Resolution (m)', 'mean')
                    ).reset_index()
                    
                    fig_heatmap = px.bar(
                        cobertura_anual,
                        x='Ano',
                        y='iniciativas_totais',
                        color='iniciativas_totais',
                        color_continuous_scale='Viridis',
                        title="📈 Cobertura Anual das Iniciativas",
                        labels={'Ano': 'Ano', 'iniciativas_totais': 'Número de Iniciativas'}
                    )   
                    fig_heatmap.update_layout(
                        font=dict(color="#2D3748"),
                        plot_bgcolor="#FFFFFF",
                        paper_bgcolor="#FFFFFF",
                        xaxis=dict(color="#2D3748"),                        
                        yaxis=dict(color="#2D3748")
                    )
                    st.plotly_chart(fig_heatmap, use_container_width=True, key="heatmap_cobertura_anual")
                else:
                    st.info("Dados insuficientes para criar heatmap de cobertura anual.")
            else:
                st.warning("Metadados não disponíveis para análise temporal.")
        
        with col2:
            st.markdown("##### Tendência da Acurácia ao Longo dos Anos")
            # Verificar se yearly_df foi criado adequadamente 
            yearly_df = None
            if meta_geral:
                try:
                    # Criar yearly_df novamente se necessário
                    yearly_data = []
                    for nome, meta in meta_geral.items():
                        years = meta.get('available_years', [])
                        if isinstance(years, str):
                            try:
                                years = [int(y.strip()) for y in years.split(',') if y.strip().isdigit()]
                            except (ValueError, AttributeError):
                                years = []
                        elif not isinstance(years, list):
                            years = []
                        
                        for year in years:
                            # Buscar acurácia no DataFrame principal
                            matching_row = df[df['Name'] == nome] if 'Name' in df.columns else pd.DataFrame()
                            if not matching_row.empty:
                                accuracy_col = 'Accuracy (%)' if 'Accuracy (%)' in matching_row.columns else 'Acuracia'
                                accuracy = matching_row.iloc[0].get(accuracy_col, 0)
                                yearly_data.append({
                                    'Name': nome,
                                    'Ano': year,
                                    'Accuracy (%)': accuracy
                                })
                    
                    if yearly_data:
                        yearly_df = pd.DataFrame(yearly_data)
                        
                except Exception as e:
                    st.warning(f"Erro ao processar dados temporais: {e}")
            
            if yearly_df is not None and not yearly_df.empty:
                tendencia_acuracia = yearly_df.groupby('Ano').agg(
                    acuracia_media=('Accuracy (%)', 'mean')
                ).reset_index()
                
                fig_tendencia_acuracia = px.line(
                    tendencia_acuracia,
                    x='Ano',
                    y='acuracia_media',
                    title="📉 Tendência da Acurácia Média ao Longo dos Anos",
                    labels={"Ano": "Ano", "acuracia_media": "Acurácia Média (%)"},
                    markers=True
                )
                fig_tendencia_acuracia.update_traces(line=dict(width=2))
                fig_tendencia_acuracia.update_layout(
                    font=dict(color="#2D3748"),
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    xaxis=dict(color="#2D3748"),
                    yaxis=dict(color="#2D3748")
                )
                st.plotly_chart(fig_tendencia_acuracia, use_container_width=True, key="tendencia_acuracia")
            else:
                st.info("Dados insuficientes para análise de tendência.")
    
    with tab4:
        st.subheader("Distribution of Number of Classes")
        col1_tab3, col2_tab3 = st.columns(2)
        with col1_tab3:
            fig_bar_classes = plot_classes_por_iniciativa(df_filt)
            st.plotly_chart(fig_bar_classes, use_container_width=True, key="bar_classes")
        with col2_tab3:
            fig_hist_classes = plot_distribuicao_classes(df_filt)
            st.plotly_chart(fig_hist_classes, use_container_width=True, key="hist_classes")

    with tab5:
        st.subheader("Distribution by Methodologies")
        col1_tab4, col2_tab4 = st.columns(2)
        with col1_tab4:
            method_counts = df_filt['Methodology'].value_counts()
            fig_metodologias = plot_distribuicao_metodologias(method_counts)
            st.plotly_chart(fig_metodologias, use_container_width=True, key="methodology_distribution")
        
        with col2_tab4:
            st.markdown("#### Accuracy by Methodology")
            fig_acuracia_metodologia = plot_acuracia_por_metodologia(df_filt)
            st.plotly_chart(fig_acuracia_metodologia, use_container_width=True, key="accuracy_methodology")

    with tab6:
        st.subheader("🕸️ Radar Analysis - Multi-dimensional Comparison")
        radar_columns = ['Accuracy (%)', 'Resolution (m)', 'Classes']
        df_radar_source = df_filt.copy() # Start with the filtered data for this tab

        # Ensure Display_Name exists
        if 'Display_Name' not in df_radar_source.columns and 'Name' in df_radar_source.columns:
            # This mapping should ideally happen once after data loading
            # Re-applying here for safety if df_filt was manipulated directly
            nome_to_sigla_radar = {}
            if df_geral_original is not None and not df_geral_original.empty and 'Acronym' in df_geral_original.columns:
                 for _, row_orig in df_geral_original.iterrows():
                    nome_to_sigla_radar[row_orig['Name']] = row_orig['Acronym']
            df_radar_source['Display_Name'] = df_radar_source['Name'].map(lambda x: nome_to_sigla_radar.get(x, str(x)[:10]))
        elif 'Display_Name' not in df_radar_source.columns:
            df_radar_source['Display_Name'] = "Unknown Initiative" # Fallback

        # Convert radar columns to numeric, coercing errors.
        for col in radar_columns:
            if col in df_radar_source.columns:
                # If data comes from min/max columns, use those (e.g. 'Accuracy_max_val')
                # This logic needs to be robust based on what data_wrapper provides.
                # For now, assume direct columns or fallbacks are handled by data_wrapper into these names.
                df_radar_source[col] = pd.to_numeric(df_radar_source[col], errors='coerce')
            else:
                df_radar_source[col] = np.nan
        
        df_radar_source.dropna(subset=radar_columns + ['Display_Name'], how='any', inplace=True)

        available_radar_cols = [col for col in radar_columns if col in df_radar_source.columns and df_radar_source[col].notna().any()]
        

        top_iniciativas_for_radar = pd.DataFrame()
        sort_by_radar = None # Initialize

        if len(available_radar_cols) >= 2 and len(df_radar_source) >= 2:
            col1_radar, col2_radar = st.columns(2)
            with col1_radar:
                max_slider_val = min(8, len(df_radar_source))
                # Since len(df_radar_source) >= 2 (from the outer if condition),
                # max_slider_val will also be >= 2.
                # Thus, the slider is always appropriate here to set num_iniciativas_for_radar.
                num_iniciativas_for_radar = st.slider(
                    "Number of initiatives in radar",
                    min_value=2, max_value=max_slider_val,
                    value=min(5, max_slider_val), # Default to 5 or fewer if less are available
                    help="Select how many initiatives to display in the radar chart",
                    key="radar_num_iniciativas_slider"
                )
            
            with col2_radar:
                sort_options = [col for col in ['Accuracy (%)', 'Resolution (m)', 'Classes'] if col in available_radar_cols]
                if sort_options:
                    sort_by_radar = st.selectbox(
                        "Sort by for Radar", options=sort_options,
                        help="Criteria to select top initiatives for radar",
                        key="radar_sort_by_selectbox"
                    )
                else:
                    st.warning("No valid columns available for sorting radar iniciativas.")

            if num_iniciativas_for_radar > 0 and sort_by_radar and sort_by_radar in df_radar_source.columns:
                if sort_by_radar == 'Resolution (m)':
                    top_iniciativas_for_radar = df_radar_source.nsmallest(num_iniciativas_for_radar, sort_by_radar)
                else:
                    top_iniciativas_for_radar = df_radar_source.nlargest(num_iniciativas_for_radar, sort_by_radar)
            elif num_iniciativas_for_radar > 0: 
                st.warning(f"Could not sort by '{sort_by_radar if sort_by_radar else 'N/A'}'. Using first {num_iniciativas_for_radar} available initiatives.")
                top_iniciativas_for_radar = df_radar_source.head(num_iniciativas_for_radar)
            # If num_iniciativas_for_radar is 0, top_iniciativas_for_radar remains an empty DataFrame

            if not top_iniciativas_for_radar.empty:
                radar_df_plot = top_iniciativas_for_radar[['Display_Name'] + available_radar_cols].copy()
                
                for col_norm in available_radar_cols:
                    min_val_norm, max_val_norm = df_radar_source[col_norm].min(), df_radar_source[col_norm].max()
                    if pd.notna(min_val_norm) and pd.notna(max_val_norm) and (max_val_norm - min_val_norm > 0):
                        if col_norm == 'Resolution (m)':
                            radar_df_plot[col_norm] = 1 - (radar_df_plot[col_norm] - min_val_norm) / (max_val_norm - min_val_norm)
                        else:
                            radar_df_plot[col_norm] = (radar_df_plot[col_norm] - min_val_norm) / (max_val_norm - min_val_norm)
                    elif pd.notna(min_val_norm) and pd.notna(max_val_norm) and (max_val_norm - min_val_norm == 0):
                        radar_df_plot[col_norm] = 0.5 
                    else: 
                        radar_df_plot[col_norm] = 0.5 
                
                fig_radar = go.Figure()
                colors = px.colors.qualitative.Set1
                
                for i, (idx, row_radar) in enumerate(radar_df_plot.iterrows()):
                    values_radar = row_radar[available_radar_cols].tolist()
                    values_closed_radar = values_radar + ([values_radar[0]] if values_radar else []) 
                    theta_closed_radar = available_radar_cols + ([available_radar_cols[0]] if available_radar_cols else [])
                    
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values_closed_radar,
                        theta=theta_closed_radar,
                        fill='toself',
                        name=row_radar['Display_Name'],
                        line_color=colors[i % len(colors)],
                        opacity=0.7
                    ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True, range=[0, 1], tickmode='array',
                            tickvals=[0, 0.25, 0.5, 0.75, 1],
                            ticktext=['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High']
                        )
                    ),
                    showlegend=True,
                    title=f'🎯 Radar Comparison - Top {num_iniciativas_for_radar} by {sort_by_radar if sort_by_radar else "N/A"}',
                    height=600, font=dict(size=12)
                )
                st.plotly_chart(fig_radar, use_container_width=True, key="radar_comparison_chart")
                
                st.markdown("#### 📊 Normalized Values (0-1 Scale)")
                display_df_radar = radar_df_plot.copy()
                for col_disp_radar in available_radar_cols:
                    display_df_radar[col_disp_radar] = display_df_radar[col_disp_radar].round(3)
                
                st.dataframe(
                    display_df_radar, use_container_width=True, hide_index=True,
                    column_config={
                        "Display_Name": st.column_config.TextColumn("Initiative", width="large"),
                        "Accuracy (%)": st.column_config.NumberColumn("Accuracy (norm.)", format="%.3f"),
                        "Resolution (m)": st.column_config.NumberColumn("Resolution (norm.)", format="%.3f", help="Inverted: 1 = better resolution"),
                        "Classes": st.column_config.NumberColumn("Classes (norm.)", format="%.3f")}
                )
                
                st.markdown("#### 💡 Radar Analysis Insights")
                insights_col1, insights_col2 = st.columns(2)
                
                with insights_col1:
                    if not radar_df_plot.empty and available_radar_cols:
                        radar_df_plot['score_total'] = radar_df_plot[available_radar_cols].mean(axis=1)
                        if not radar_df_plot.empty and 'score_total' in radar_df_plot.columns and radar_df_plot['score_total'].notna().any():
                             best_overall = radar_df_plot.loc[radar_df_plot['score_total'].idxmax(), 'Display_Name']
                             st.success(f"🏆 **Best Overall Performance:** {best_overall}")

                        for col_insight in available_radar_cols:
                            if col_insight in radar_df_plot.columns and radar_df_plot[col_insight].notna().any():
                                specialist = radar_df_plot.loc[radar_df_plot[col_insight].idxmax(), 'Display_Name']
                                col_display_insight = "Resolution" if col_insight == "Resolution (m)" else col_insight.replace(" (%)", "")
                                st.info(f"🎯 **Specialist in {col_display_insight}:** {specialist}")
                
                with insights_col2:
                    if not radar_df_plot.empty and available_radar_cols:
                        st.markdown("**📈 Performance Distribution:**")
                        for col_perf in available_radar_cols:
                            if col_perf in radar_df_plot.columns and radar_df_plot[col_perf].notna().any():
                                avg_performance = radar_df_plot[col_perf].mean()
                                col_display_perf = "Resolution" if col_perf == "Resolution (m)" else col_perf.replace(" (%)", "")
                                performance_level = "High" if avg_performance > 0.7 else "Medium" if avg_performance > 0.4 else "Low"
                                st.write(f"• **{col_display_perf}:** {performance_level} ({avg_performance:.2f})")
                        
                        if available_radar_cols: 
                            balance_scores = radar_df_plot[available_radar_cols].std(axis=1)
                            if not balance_scores.empty and balance_scores.notna().any():
                                most_balanced = radar_df_plot.loc[balance_scores.idxmin(), 'Display_Name']
                                st.info(f"⚖️ **Most Balanced:** {most_balanced}")
            elif num_iniciativas_for_radar > 0:
                 st.warning(f"⚠️ Could not select top {num_iniciativas_for_radar} iniciativas for radar. Check data availability and filters.")

        else: # Conditions for radar chart not met
            if len(df_radar_source) < 2 :
                st.warning("⚠️ At least 2 initiatives with complete data are needed for radar comparison after filtering.")
            elif len(available_radar_cols) < 2:
                 st.warning("⚠️ At least 2 valid data dimensions (e.g., Accuracy, Resolution) are needed for radar. Check data and filters.")
            else:
                st.warning("⚠️ Insufficient data for radar chart. Verify data and selected filters.")

            st.info("📋 **Radar Data Info:**")
            st.write(f"• Initiatives with complete radar data after filtering: {len(df_radar_source)}")
            st.write(f"• Available numeric columns for radar: {available_radar_cols}")
            st.write(f"• Required columns for radar: {radar_columns}")
        
        # Enhanced Timeline Analysis - Additional Features
        st.markdown("---")
        st.markdown("### 📊 Análise Avançada do Timeline")
        
        # Create enhanced timeline data for analysis
        if meta_geral:
            timeline_data = []
            produto_info = {}
            
            # Map products to get technical characteristics
            if df_geral_original is not None and not df_geral_original.empty:
                for _, row in df_geral_original.iterrows():
                    produto_info[row['Name']] = {
                        'metodologia': row.get('Methodology', 'N/A'),
                        'escopo': row.get('Scope', 'N/A'),
                        'acuracia': row.get('Accuracy (%)', 0),
                        'resolucao': row.get('Resolution (m)', 0)
                    }
              # Collect all years from all initiatives
            for nome, meta in meta_geral.items():
                # Try both possible keys for temporal data
                years_key = 'available_years' if 'available_years' in meta else 'anos_disponiveis'
                if years_key in meta and meta[years_key]:
                    info = produto_info.get(nome, {})
                    for ano in meta[years_key]:
                        timeline_data.append({
                            'produto': nome,
                            'ano': ano,
                            'disponivel': 1,
                            'metodologia': info.get('metodologia', 'N/A'),
                            'escopo': info.get('escopo', 'N/A')
                        })
            
            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data)
                produtos_unicos = sorted(timeline_df['produto'].unique())
                metodologias_unicas = timeline_df['metodologia'].unique()
                
                # Methodology Comparative Analysis
                st.markdown("#### 📈 Análise Comparativa por Metodologia")
                
                # Statistics by methodology
                metod_stats = timeline_df.groupby('metodologia').agg({
                    'produto': 'nunique',
                    'ano': ['min', 'max', 'count']
                }).round(1)
                metod_stats.columns = ['Products', 'First Year', 'Last Year', 'Total Product-Years']
                
                # Calculate average coverage period
                periodo_medio = {}
                for metodologia in metodologias_unicas:
                    produtos_metod = timeline_df[timeline_df['metodologia'] == metodologia]['produto'].unique()
                    periodos = []
                    for produto in produtos_metod:
                        anos_produto = timeline_df[
                            (timeline_df['produto'] == produto) & 
                            (timeline_df['metodologia'] == metodologia)
                        ]['ano'].tolist()
                        if anos_produto:
                            periodos.append(max(anos_produto) - min(anos_produto) + 1)
                    periodo_medio[metodologia] = np.mean(periodos) if periodos else 0
                metod_stats['Average Period'] = [periodo_medio.get(metod, 0) for metod in metod_stats.index]
                
                st.dataframe(metod_stats, use_container_width=True)
                
                # LULC Products Accuracy Ranking
                if df_geral_original is not None and not df_geral_original.empty and 'Accuracy (%)' in df_geral_original.columns:
                    st.markdown("#### 🏆 Ranking de Acurácia dos Produtos LULC")
                    
                    # Create ranking data
                    ranking_data = []
                    for produto in produtos_unicos:
                        produto_timeline = timeline_df[timeline_df['produto'] == produto].iloc[0]
                        metodologia = produto_timeline['metodologia']
                        
                        # Get accuracy data
                        produto_row = df_geral_original[df_geral_original['Name'] == produto]
                        if not produto_row.empty:
                            acuracia = produto_row['Accuracy (%)'].iloc[0] if pd.notna(produto_row['Accuracy (%)'].iloc[0]) else 0
                            resolucao = produto_row['Resolution (m)'].iloc[0] if 'Resolution (m)' in produto_row.columns and pd.notna(produto_row['Resolution (m)'].iloc[0]) else 0
                        else:
                            acuracia = 0
                            resolucao = 0
                        
                        # Calculate temporal coverage
                        anos_produto = timeline_df[timeline_df['produto'] == produto]['ano'].unique()
                        cobertura_temporal = len(anos_produto)
                        periodo_inicio = min(anos_produto) if len(anos_produto) > 0 else 0
                        periodo_fim = max(anos_produto) if len(anos_produto) > 0 else 0
                        
                        ranking_data.append({
                            'produto': produto,
                            'metodologia': metodologia,
                            'acuracia': acuracia,
                            'resolucao': resolucao,
                            'cobertura_temporal': cobertura_temporal,
                            'periodo_inicio': periodo_inicio,
                            'periodo_fim': periodo_fim
                        })
                    
                    ranking_df = pd.DataFrame(ranking_data)
                    
                    # Horizontal ranking chart by accuracy
                    if ranking_df['acuracia'].sum() > 0:  # If there's accuracy data
                        ranking_sorted = ranking_df.sort_values('acuracia', ascending=True)
                        
                        fig_ranking = px.bar(
                            ranking_sorted,
                            x='acuracia',
                            y='produto',
                            color='metodologia',
                            orientation='h',
                            title='🏆 Ranking de Acurácia dos Produtos LULC',
                            labels={'acuracia': 'Accuracy (%)', 'produto': 'Produto'},
                            color_discrete_sequence=px.colors.qualitative.Set1,
                            text='acuracia'
                        )
                        
                        fig_ranking.update_traces(
                            texttemplate='%{text:.1f}%', 
                            textposition='outside',
                            marker_line=dict(width=2, color='white')
                        )
                        
                        fig_ranking.update_layout(
                            height=max(400, len(ranking_sorted) * 25),
                            xaxis_title='Accuracy (%)',
                            yaxis_title='Produtos LULC',
                            font=dict(size=12, color="#2D3748"),
                            plot_bgcolor="#FFFFFF",
                            paper_bgcolor="#FFFFFF",
                            showlegend=True,
                            legend=dict(
                                orientation="v",
                                yanchor="middle",
                                y=0.5,
                                xanchor="left",
                                x=1.02,
                                title="Metodologia",
                                font=dict(color="#2D3748")
                            )
                        )
                        
                        st.plotly_chart(fig_ranking, use_container_width=True, key="ranking_acuracia_tab6")
                        
                        # Top 5 and Bottom 5
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("##### 🥇 Top 5 - Maior Acurácia")
                            top_5 = ranking_sorted.tail(5)[['produto', 'acuracia', 'metodologia']]
                            top_5 = top_5.sort_values('acuracia', ascending=False)
                            
                            for idx, row in top_5.iterrows():
                                st.success(f"**{row['produto']}**: {row['acuracia']:.1f}% ({row['metodologia']})")
                        
                        with col2:
                            st.markdown("##### 📉 Bottom 5 - Menor Acurácia")
                            bottom_5 = ranking_sorted.head(5)[['produto', 'acuracia', 'metodologia']]
                            
                            for idx, row in bottom_5.iterrows():
                                st.warning(f"**{row['produto']}**: {row['acuracia']:.1f}% ({row['metodologia']})")
                        
                        # Ranking statistics
                        st.markdown("##### 📊 Estatísticas do Ranking")
                        ranking_col1, ranking_col2, ranking_col3, ranking_col4 = st.columns(4)
                        
                        with ranking_col1:
                            st.metric("🏆 Melhor Acurácia", f"{ranking_df['acuracia'].max():.1f}%")
                        with ranking_col2:
                            st.metric("📊 Acurácia Média", f"{ranking_df['acuracia'].mean():.1f}%")
                        with ranking_col3:
                            st.metric("📉 Menor Acurácia", f"{ranking_df['acuracia'].min():.1f}%")
                        with ranking_col4:
                            desvio = ranking_df['acuracia'].std()
                            st.metric("📈 Desvio Padrão", f"{desvio:.1f}%")
                
                # General timeline statistics
                st.markdown("#### 📈 Estatísticas Gerais do Timeline")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📊 Total de Produtos", len(produtos_unicos))
                with col2:
                    anos_reais = sorted(list(set(timeline_df['ano'].tolist())))
                    st.metric("📅 Período Real", f"{min(anos_reais)}-{max(anos_reais)}")
                with col3:
                    ano_mais_ativo = timeline_df['ano'].value_counts().idxmax()
                    produtos_ano_ativo = timeline_df['ano'].value_counts().max()
                    st.metric("🔥 Ano Mais Ativo", f"{ano_mais_ativo} ({produtos_ano_ativo} produtos)")
                with col4:
                    st.metric("🔬 Metodologias", len(metodologias_unicas))
                
                # Methodology evolution over time chart
                st.markdown("#### ⏰ Evolução das Metodologias ao Longo do Tempo")
                
                # Create data for stacked area chart by methodology
                timeline_pivot = timeline_df.groupby(['ano', 'metodologia']).size().reset_index(name='count')
                
                fig_metodologia_evolucao = px.area(
                    timeline_pivot,
                    x='ano',
                    y='count',
                    color='metodologia',
                    title='📈 Evolução da Adoção de Metodologias LULC',
                    labels={'ano': 'Ano', 'count': 'Número de Produtos', 'metodologia': 'Metodologia'},
                    color_discrete_sequence=px.colors.qualitative.Set1
                )
                fig_metodologia_evolucao.update_layout(
                    height=400,
                    font=dict(size=12, color="#2D3748"),
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    xaxis=dict(range=[min(anos_reais), max(anos_reais)], color="#2D3748"),
                    yaxis=dict(color="#2D3748"),
                    legend=dict(font=dict(color="#2D3748")),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_metodologia_evolucao, use_container_width=True, key="metodologia_evolucao_tab6")
