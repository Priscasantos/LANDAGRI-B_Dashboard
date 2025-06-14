import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path

# Add scripts to path for imports
current_dir = Path(__file__).parent.parent.parent
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# Import chart_core at module level
try:
    from scripts.plotting.chart_core import apply_standard_layout
except ImportError:
    apply_standard_layout = None  # Fallback if import fails

# Import English translations

def run():
    st.header("🔍 Detailed Analysis - Custom Comparisons")
    st.markdown("Select two or more initiatives for detailed comparative analysis.")
    
    # Adicionar scripts ao path
    current_dir = Path(__file__).parent.parent.parent
    scripts_path = str(current_dir / "scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
      # Importar módulos localmente
    try:
        from scripts.data_generation.data_wrapper import load_data
        from scripts.utilities.utils import safe_download_image
    except ImportError as e:
        st.error(f"Erro ao importar módulos: {e}")
        return    
    if 'df_geral' not in st.session_state or st.session_state.df_geral.empty:
        # Tentar carregar dados processados diretamente
        df_loaded, metadata_loaded, _ = load_data()  # Fixed tuple unpacking for 3 values
        if df_loaded is not None and not df_loaded.empty:
            st.session_state.df_geral = df_loaded
            st.session_state.metadata = metadata_loaded
        else:
            st.warning("⚠️ Data not found. Run the main page (app.py) first.")
            st.stop()
    df_geral = st.session_state.df_geral
      # Create name to sigla mapping from DataFrame
    nome_to_sigla = {}
    if 'Acronym' in df_geral.columns:
        for _, row in df_geral.iterrows():
            nome_to_sigla[row['Name']] = row['Acronym']
    
    # Add Display_Name column for consistent sigla usage
    df_geral = df_geral.copy()
    df_geral['Display_Name'] = df_geral.apply(
        lambda row: nome_to_sigla.get(row['Name'], row['Name'][:10]), axis=1
    )
      # Initiative selection for comparison
    selected_initiatives = st.multiselect(
        "🎯 Select initiatives to compare:",
        options=df_geral["Name"].tolist(),
        default=df_geral["Name"].tolist()[:min(3, len(df_geral))],
        help="Choose 2 or more initiatives for detailed comparative analysis"
    )
    
    if len(selected_initiatives) < 2:
        st.info("👈 Select at least two initiatives in the menu above to start analysis.")
        return
      # Filter data for selected initiatives
    df_filtered = df_geral[df_geral["Name"].isin(selected_initiatives)].copy()

    # Standardized tabs with English translations
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dual Bars",
        "🎯 Radar",
        "🔥 Heatmap", 
        "📈 Table",
        "📅 Annual Coverage"
    ])
    
    with tab1:
        # Dual Bars using siglas
        df_filtered['resolucao_norm'] = (1 / df_filtered['Resolution (m)']) / (1 / df_filtered['Resolution (m)']).max()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_filtered['Display_Name'],  # Use siglas
            x=df_filtered['Accuracy (%)'],
            name='Accuracy (%)',
            orientation='h',
            marker_color='royalblue'
        ))
        fig.add_trace(go.Bar(
            y=df_filtered['Display_Name'],  # Use siglas
            x=df_filtered['resolucao_norm'] * 100,
            name='Resolution (normalized)',
            orientation='h',
            marker_color='orange'
        ))
        fig.update_layout(
            barmode='group', 
            xaxis_title='Value (%)', 
            yaxis_title='Initiative',
            title='Comparison: Accuracy vs Resolution',
            height=max(400, len(df_filtered) * 25)
        )
        st.plotly_chart(fig, use_container_width=True)
        safe_download_image(fig, "dual_bars_detailed.png", "⬇️ Download Chart")

    with tab2:        # Radar using siglas
        radar_columns = ['Accuracy (%)', 'Resolution (m)', 'Classes']
        available_radar_cols = [col for col in radar_columns if col in df_filtered.columns]
        radar_df = None  # Initialize radar_df
        
        if len(available_radar_cols) >= 2:
            radar_df = df_filtered[['Display_Name'] + available_radar_cols].copy()
            for col in available_radar_cols:
                min_val, max_val = radar_df[col].min(), radar_df[col].max()
                if max_val - min_val > 0:
                    if col == 'Resolution (m)':
                        radar_df[col] = 1 - (radar_df[col] - min_val) / (max_val - min_val)
                    else:
                        radar_df[col] = (radar_df[col] - min_val) / (max_val - min_val)
                else:
                    radar_df[col] = 0.5
            fig_radar = go.Figure()
            colors = px.colors.qualitative.Set1
            for i, (idx, row) in enumerate(radar_df.iterrows()):
                values = row[available_radar_cols].tolist()
                values_closed = values + [values[0]]
                theta_closed = available_radar_cols + [available_radar_cols[0]]
                fig_radar.add_trace(go.Scatterpolar(
                    r=values_closed,
                    theta=theta_closed,
                    fill='toself',
                    name=row['Display_Name'],  # Use siglas
                    line_color=colors[i % len(colors)]
                ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                title='Multi-dimensional Comparison (Radar)',
                height=600
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            safe_download_image(fig_radar, "radar_chart_detailed.png", "⬇️ Download Chart")
        else:
            st.warning("Insufficient data for radar chart.")

    with tab3:
        # Heatmap using siglas
        if len(available_radar_cols) >= 2 and radar_df is not None:
            heatmap_df = radar_df.set_index('Display_Name')[available_radar_cols]  # Use siglas
            fig_heatmap = px.imshow(
                heatmap_df.values,
                x=heatmap_df.columns,
                y=heatmap_df.index,
                color_continuous_scale='viridis',
                aspect='auto',
                title='Performance Heatmap (normalized values)',
                labels=dict(x='Metric', y='Initiative', color='Normalized Value')
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
            safe_download_image(fig_heatmap, "heatmap_detailed.png", "⬇️ Download Chart")
        else:
            st.warning("Insufficient data for heatmap.")

    with tab4:
        # Table
        st.dataframe(df_filtered, use_container_width=True)   
        
    with tab5:
        st.subheader("Annual Coverage by Initiative (Multiple Selection)")
        meta = st.session_state.get('metadata', {})
        
        if not selected_initiatives:
            st.info("Select at least one initiative to view annual coverage.")
        else:            
            try:
                from scripts.plotting.generate_graphics import plot_annual_coverage_multiselect
                fig_annual = plot_annual_coverage_multiselect(meta, df_filtered, selected_initiatives)
                st.plotly_chart(fig_annual, use_container_width=True)
                safe_download_image(fig_annual, "annual_coverage_detailed.png", "⬇️ Download Coverage (PNG)")
            except ImportError:
                st.error("Annual coverage function not available")

def run_non_streamlit(df, metadata, output_dir="graphics/detailed"):
    """
    Run detailed analysis without Streamlit UI and save graphics to files.
    Used when called from command-line scripts like run_full_analysis.py
    """
    from pathlib import Path
    import sys
    
    # Add scripts to path    current_dir = Path(__file__).parent.parent.parent
    sys.path.append(str(current_dir / "scripts"))
    
    from scripts.utilities.chart_saver import save_chart_robust
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("🔄 Gerando análises detalhadas...")
    
    if df is None or df.empty:
        print("❌ Dados insuficientes para análise detalhada.")
        return False
    
    try:
        # Create name to sigla mapping from DataFrame
        nome_to_sigla = {}
        if 'Acronym' in df.columns:
            for _, row in df.iterrows():
                nome_to_sigla[row['Name']] = row['Acronym']
        
        # Add Display_Name column for consistent sigla usage
        df_for_analysis = df.copy()
        df_for_analysis['Display_Name'] = df_for_analysis.apply(
            lambda row: nome_to_sigla.get(row['Name'], row['Name'][:10]), axis=1
        )
          # Use first few initiatives for analysis
        selected_initiatives = df_for_analysis["Name"].tolist()[:min(5, len(df_for_analysis))]
        df_filtered = df_for_analysis[df_for_analysis["Name"].isin(selected_initiatives)].copy()
        
        print("📊 Gerando gráfico de barras duplas...")
        fig_dual_bars = create_dual_bars_chart(df_filtered)
        if fig_dual_bars:
            success, saved_path, format_used = save_chart_robust(
                fig_dual_bars, output_dir, "dual_bars_detailed", 
                width=800, height=600, scale=2
            )
            if success:
                print(f"✅ Barras duplas salvas como {format_used} em: {saved_path}")
        
        print("🎯 Gerando gráfico radar...")
        fig_radar = create_radar_chart(df_filtered)
        if fig_radar:
            success, saved_path, format_used = save_chart_robust(
                fig_radar, output_dir, "radar_chart_detailed", 
                width=800, height=600, scale=2
            )
            if success:
                print(f"✅ Radar chart salvo como {format_used} em: {saved_path}")
        
        print("🔥 Gerando heatmap...")
        fig_heatmap = create_heatmap_chart(df_filtered)
        if fig_heatmap:
            success, saved_path, format_used = save_chart_robust(
                fig_heatmap, output_dir, "heatmap_detailed", 
                width=800, height=600, scale=2
            )
            if success:
                print(f"✅ Heatmap salvo como {format_used} em: {saved_path}")
        
        print("✅ Análises detalhadas concluídas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar análises detalhadas: {e}")
        return False

def create_dual_bars_chart(df_filtered):
    """Create dual bars chart without Streamlit dependencies"""
    try:
        df_filtered['resolucao_norm'] = (1 / df_filtered['Resolution (m)']) / (1 / df_filtered['Resolution (m)']).max()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_filtered['Display_Name'],  # Use siglas
            x=df_filtered['Accuracy (%)'],
            name='Accuracy (%)',
            orientation='h',
            marker_color='royalblue'
        ))
        fig.add_trace(go.Bar(
            y=df_filtered['Display_Name'],  # Use siglas
            x=df_filtered['resolucao_norm'] * 100,
            name='Resolution (normalized)',
            orientation='h',
            marker_color='orange'
        ))
        
        # Apply standardized layout if available
        if apply_standard_layout:
            apply_standard_layout(fig, "Comparison: Accuracy vs Resolution", "Value (%)", "Initiative")
        else:
            # Fallback to manual layout
            fig.update_layout(
                title='Comparison: Accuracy vs Resolution',
                xaxis_title='Value (%)', 
                yaxis_title='Initiative'
            )
        
        fig.update_layout(
            barmode='group',
            height=max(400, len(df_filtered) * 25)
        )
        return fig
    except Exception as e:
        print(f"Erro ao criar dual bars chart: {e}")
        return None

def create_radar_chart(df_filtered):
    """Create radar chart without Streamlit dependencies"""
    try:
        radar_columns = ['Accuracy (%)', 'Resolution (m)', 'Classes']
        available_radar_cols = [col for col in radar_columns if col in df_filtered.columns]
        
        if len(available_radar_cols) < 2:
            print("Dados insuficientes para radar chart.")
            return None
        
        radar_df = df_filtered[['Display_Name'] + available_radar_cols].copy()
        for col in available_radar_cols:
            min_val, max_val = radar_df[col].min(), radar_df[col].max()
            if max_val - min_val > 0:
                if col == 'Resolution (m)':
                    radar_df[col] = 1 - (radar_df[col] - min_val) / (max_val - min_val)
                else:
                    radar_df[col] = (radar_df[col] - min_val) / (max_val - min_val)
            else:
                radar_df[col] = 0.5
        
        fig_radar = go.Figure()
        colors = px.colors.qualitative.Set1
        for i, (idx, row) in enumerate(radar_df.iterrows()):
            values = row[available_radar_cols].tolist()
            values_closed = values + [values[0]]
            theta_closed = available_radar_cols + [available_radar_cols[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=values_closed,
                theta=theta_closed,
                fill='toself',
                name=row['Display_Name'],  # Use siglas
                line_color=colors[i % len(colors)]
            ))
        
        # Apply standardized layout if available
        if apply_standard_layout:
            apply_standard_layout(fig_radar, "Multi-dimensional Comparison (Radar)", "", "")
        else:
            # Fallback to manual layout
            fig_radar.update_layout(title='Multi-dimensional Comparison (Radar)')
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            height=600
        )
        return fig_radar
    except Exception as e:
        print(f"Erro ao criar radar chart: {e}")
        return None

def create_heatmap_chart(df_filtered):
    """Create heatmap chart without Streamlit dependencies"""
    try:
        radar_columns = ['Accuracy (%)', 'Resolution (m)', 'Classes']
        available_radar_cols = [col for col in radar_columns if col in df_filtered.columns]
        
        if len(available_radar_cols) < 2:
            print("Dados insuficientes para heatmap.")
            return None
        
        radar_df = df_filtered[['Display_Name'] + available_radar_cols].copy()
        for col in available_radar_cols:
            min_val, max_val = radar_df[col].min(), radar_df[col].max()
            if max_val - min_val > 0:
                if col == 'Resolution (m)':
                    radar_df[col] = 1 - (radar_df[col] - min_val) / (max_val - min_val)
                else:
                    radar_df[col] = (radar_df[col] - min_val) / (max_val - min_val)
            else:
                radar_df[col] = 0.5
        
        heatmap_df = radar_df.set_index('Display_Name')[available_radar_cols]  # Use siglas
        fig_heatmap = px.imshow(
            heatmap_df.values,
            x=heatmap_df.columns,
            y=heatmap_df.index,
            color_continuous_scale='viridis',
            aspect='auto',
            labels=dict(x='Metric', y='Initiative', color='Normalized Value')
        )
        
        # Apply standardized layout if available
        if apply_standard_layout:
            apply_standard_layout(fig_heatmap, "Performance Heatmap (normalized values)", "Metric", "Initiative")
        else:
            # Fallback to manual layout
            fig_heatmap.update_layout(title='Performance Heatmap (normalized values)')
        
        return fig_heatmap
    except Exception as e:
        print(f"Erro ao criar heatmap: {e}")
        return None
