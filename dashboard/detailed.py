import streamlit as st
import pandas as pd
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

def run():
    st.header("🔍 Detailed Analysis - Custom Comparisons")
    st.markdown("Select two or more initiatives for detailed comparative analysis.")
    
    # Add scripts to path
    current_dir = Path(__file__).parent.parent.parent
    scripts_path = str(current_dir / "scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)    # Import modules locally
    try:
        from scripts.utilities.json_interpreter import interpret_initiatives_metadata, _load_jsonc_file
    except ImportError as e:
        st.error(f"Error importing modules: {e}")
        return
    
    # Load data using the new JSON interpreter system
    # Rely on app.py to load and cache data into st.session_state.df_interpreted
    if 'df_interpreted' not in st.session_state or st.session_state.df_interpreted.empty:
        st.error("❌ Interpreted data not found in session state. Ensure app.py loads data correctly.")
        # Fallback or attempt to load if necessary, though app.py should be the source of truth
        # For now, we assume app.py handles it. If direct loading is needed here, add similar try-except as in comparison.py
        # and ensure path is correct (current_dir / "data" / "initiatives_metadata.jsonc")
        return # Stop if data isn't loaded
            
    df_geral = st.session_state.get('df_interpreted', pd.DataFrame())
    if df_geral.empty:
        st.error("❌ No data available. Please check the data loading process.")
        return
    
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
        st.info("👈 Select at least two initiatives in the menu above to start analysis.") # Translated
        return
    
    # Filter data for selected initiatives
    df_filtered = df_geral[df_geral["Name"].isin(selected_initiatives)].copy()    # Standardized tabs with English translations
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dual Bars",
        "🎯 Radar Chart", # Translated
        "🔥 Heatmap", 
        "📈 Data Table", # Translated
        "📅 Annual Coverage",
        "⏰ Temporal Analysis"
    ])
    with tab1:
        st.subheader("Accuracy vs. Resolution (Normalized)") # Added subheader
        # Dual Bars using siglas
        df_filtered['resolution_norm'] = (1 / df_filtered['Resolution']) / (1 / df_filtered['Resolution']).max()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_filtered['Display_Name'],  # Use siglas
            x=df_filtered['Accuracy (%)'], # Changed from 'Overall_Accuracy' to 'Accuracy (%)'
            name='Accuracy (%)',
            orientation='h',
            marker_color='royalblue'
        ))
        fig.add_trace(go.Bar(
            y=df_filtered['Display_Name'],  # Use siglas
            x=df_filtered['resolution_norm'] * 100,
            name='Resolution (Normalized)', # Translated
            orientation='h',
            marker_color='orange'
        ))
        fig.update_layout(
            barmode='group', 
            xaxis_title='Value (%)', 
            yaxis_title='Initiative',
            title='Comparison: Accuracy vs Resolution',
            height=max(400, len(df_filtered) * 30 + 100) # Adjusted height for better readability
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:  
        st.subheader("Multi-dimensional Performance Radar") # Added subheader
        # Radar using siglas
        radar_columns = ['Accuracy (%)', 'Resolution', 'Classes', 'Num_Agri_Classes'] # Fixed column names and added more dimensions
        available_radar_cols = [col for col in radar_columns if col in df_filtered.columns]
        radar_df = None  # Initialize radar_df
        
        # Ensure we have at least 3 columns for a proper radar chart
        if len(available_radar_cols) >= 3:
            radar_df = df_filtered[['Display_Name'] + available_radar_cols].copy()
            for col in available_radar_cols:
                # Convert to numeric and handle NaN values
                radar_df[col] = pd.to_numeric(radar_df[col], errors='coerce').fillna(0)
                min_val, max_val = radar_df[col].min(), radar_df[col].max()
                if max_val - min_val > 0:
                    if col == 'Resolution': # Lower is better for resolution, so invert normalization
                        radar_df[col] = 1 - (radar_df[col] - min_val) / (max_val - min_val)
                    else: # Higher is better for accuracy and classes
                        radar_df[col] = (radar_df[col] - min_val) / (max_val - min_val)
                else:
                    radar_df[col] = 0.5 # Assign a neutral value if all values are the same
            
            fig_radar = go.Figure()
            colors = px.colors.qualitative.Plotly # Using Plotly colors for better distinction
            
            for i, (idx, row) in enumerate(radar_df.iterrows()):
                values = row[available_radar_cols].tolist()
                values_closed = values + [values[0]] # Close the radar shape
                theta_closed = available_radar_cols + [available_radar_cols[0]] # Close the theta
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=values_closed,
                    theta=theta_closed,
                    fill='toself',
                    name=row['Display_Name'],  # Use siglas
                    line_color=colors[i % len(colors)],
                    line_width=2
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True, 
                        range=[0, 1],
                        showticklabels=True,
                        ticks="outside"
                    ),
                    angularaxis=dict(
                        showticklabels=True,
                        rotation=90,
                        direction="counterclockwise"
                    )
                ),
                showlegend=True,
                title='Multi-dimensional Performance Radar',
                height=600,
                font=dict(size=12)
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            

                
        elif len(available_radar_cols) == 2:
            st.warning("⚠️ Only 2 dimensions available. Radar charts work best with 3 or more dimensions. Adding a third dimension for better visualization.")
            # Add a dummy third dimension for visualization purposes
            radar_df = df_filtered[['Display_Name'] + available_radar_cols].copy()
            radar_df['Temporal_Coverage'] = 0.5  # Add a neutral dimension
            extended_radar_cols = available_radar_cols + ['Temporal_Coverage']
            
            for col in extended_radar_cols:
                if col == 'Temporal_Coverage':
                    continue  # Skip normalization for dummy column
                radar_df[col] = pd.to_numeric(radar_df[col], errors='coerce').fillna(0)
                min_val, max_val = radar_df[col].min(), radar_df[col].max()
                if max_val - min_val > 0:
                    if col == 'Resolution':
                        radar_df[col] = 1 - (radar_df[col] - min_val) / (max_val - min_val)
                    else:
                        radar_df[col] = (radar_df[col] - min_val) / (max_val - min_val)
                else:
                    radar_df[col] = 0.5
            
            fig_radar = go.Figure()
            colors = px.colors.qualitative.Plotly
            
            for i, (idx, row) in enumerate(radar_df.iterrows()):
                values = row[extended_radar_cols].tolist()
                values_closed = values + [values[0]]
                theta_closed = extended_radar_cols + [extended_radar_cols[0]]
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=values_closed,
                    theta=theta_closed,
                    fill='toself',
                    name=row['Display_Name'],
                    line_color=colors[i % len(colors)],
                    line_width=2
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True, 
                        range=[0, 1],
                        showticklabels=True,
                        ticks="outside"
                    ),
                    angularaxis=dict(
                        showticklabels=True,
                        rotation=90,
                        direction="counterclockwise"
                    )
                ),
                showlegend=True,
                title='Multi-dimensional Performance Radar (with Temporal Coverage)',
                height=600,
                font=dict(size=12)
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            

        else:
            st.warning("⚠️ Insufficient data for radar chart. At least 2 dimensions needed. Select more initiatives or ensure data includes accuracy, resolution, and class information.")

    with tab3:
        st.subheader("Normalized Performance Heatmap") # Added subheader
        # Heatmap using siglas
        # Ensure radar_df is computed (it's computed in tab2, but let's be safe)
        if radar_df is None and len(available_radar_cols) >=2: # Recalculate if not available
            radar_df = df_filtered[['Display_Name'] + available_radar_cols].copy()
            for col in available_radar_cols:
                # Convert to numeric and handle NaN values
                radar_df[col] = pd.to_numeric(radar_df[col], errors='coerce').fillna(0)
                min_val, max_val = radar_df[col].min(), radar_df[col].max()
                if max_val - min_val > 0:
                    if col == 'Resolution':
                        radar_df[col] = 1 - (radar_df[col] - min_val) / (max_val - min_val)
                    else:
                        radar_df[col] = (radar_df[col] - min_val) / (max_val - min_val)
                else:
                    radar_df[col] = 0.5

        if len(available_radar_cols) >= 2 and radar_df is not None:
            heatmap_df = radar_df.set_index('Display_Name')[available_radar_cols]  # Use siglas
            fig_heatmap = px.imshow(
                heatmap_df.values,
                x=heatmap_df.columns,
                y=heatmap_df.index,
                color_continuous_scale='Viridis', # Changed to Viridis for better perception
                aspect='auto',
                title='Performance Heatmap (Normalized Values)', # Translated
                labels=dict(x='Metric', y='Initiative', color='Normalized Value')
            )
            fig_heatmap.update_layout(height=max(400, len(df_filtered) * 30 + 100))
            st.plotly_chart(fig_heatmap, use_container_width=True)
            # Use the new download form setup

        else:
            st.warning("Insufficient data for heatmap. Select more metrics or initiatives.") # Translated

    with tab4:
        st.subheader("Detailed Data Table") # Added subheader
        # Table
        st.dataframe(df_filtered, use_container_width=True)   
        
    with tab5:
        st.subheader("Annual Coverage by Initiative") # Translated and added subheader
        meta = st.session_state.get('metadata', {})
        
        if not selected_initiatives:
            st.info("Select at least one initiative to view annual coverage.") # Translated
        else:            
            try:
                from scripts.plotting.generate_graphics import plot_annual_coverage_multiselect
                # Ensure df_filtered contains the 'Name' column for plot_annual_coverage_multiselect
                fig_annual = plot_annual_coverage_multiselect(meta, df_filtered, selected_initiatives)
                st.plotly_chart(fig_annual, use_container_width=True)
                # Use the new download form setup


            except ImportError:
                st.error("Annual coverage function not available.") # Translated
            except Exception as e:
                st.error(f"Error generating annual coverage chart: {e}")

    with tab6:
        st.subheader("⏰ Temporal Analysis")
        
        # Load metadata for temporal analysis
        meta = st.session_state.get('metadata', {})
        
        if not meta:
            st.warning("⚠️ Metadata not available for temporal analysis.")
            return
        
        # Filter metadata for selected initiatives only
        filtered_meta = {name: details for name, details in meta.items() if name in selected_initiatives}
        
        if not filtered_meta:
            st.warning("⚠️ No temporal data available for selected initiatives.")
            return
        
        # === TEMPORAL GAPS ANALYSIS ===
        st.markdown("### ⚠️ Temporal Gaps Analysis")
        st.markdown("This section highlights initiatives with missing years in their time series.")
        
        # Analyze temporal gaps
        gap_analysis_data = []
        for init_name, details in filtered_meta.items():
            if 'available_years' in details and details['available_years']:
                years = sorted(details['available_years'])
                if len(years) > 1:
                    # Find gaps in the time series
                    full_range = list(range(min(years), max(years) + 1))
                    missing_years = [year for year in full_range if year not in years]
                    
                    if missing_years:
                        gap_analysis_data.append({
                            'Initiative': nome_to_sigla.get(init_name, init_name[:15]),
                            'Full_Name': init_name,
                            'Total_Years': len(years),
                            'Missing_Years': len(missing_years),
                            'Missing_Years_List': missing_years,
                            'Coverage_Percentage': (len(years) / len(full_range)) * 100
                        })
        
        if gap_analysis_data:
            st.markdown("#### 📊 Missing Years by Initiative")
            
            # Create bar chart for missing years
            gap_df = pd.DataFrame(gap_analysis_data)
            fig_gaps = go.Figure()
            
            fig_gaps.add_trace(go.Bar(
                x=gap_df['Initiative'],
                y=gap_df['Missing_Years'],
                name='Missing Years',
                marker_color='rgba(255, 99, 71, 0.8)',
                hovertemplate='<b>%{x}</b><br>' +
                             'Missing Years: %{y}<br>' +
                             'Coverage: %{customdata:.1f}%<extra></extra>',
                customdata=gap_df['Coverage_Percentage']
            ))
            
            fig_gaps.update_layout(
                title='Missing Years in Time Series by Initiative',
                xaxis_title='Initiative',
                yaxis_title='Number of Missing Years',
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_gaps, use_container_width=True)

            
            # Show detailed gap information
            with st.expander("📋 Detailed Gap Information"):
                for gap_info in gap_analysis_data:
                    st.markdown(f"**{gap_info['Initiative']}** ({gap_info['Full_Name']})")
                    st.markdown(f"- Coverage: {gap_info['Coverage_Percentage']:.1f}%")
                    st.markdown(f"- Missing years: {', '.join(map(str, gap_info['Missing_Years_List']))}")
                    st.markdown("---")
        else:
            st.success("✅ No temporal gaps found in selected initiatives!")
        
        # === DATA AVAILABILITY EVOLUTION ===
        st.markdown("### 📈 Data Availability Evolution")
        st.markdown("Number of Initiatives Over Time")
          # Create evolution data
        evolution_data = []
        all_years_set = set()
        
        for init_name, details in filtered_meta.items():
            if 'available_years' in details and details['available_years']:
                for year in details['available_years']:
                    evolution_data.append({
                        'year': year,
                        'initiative': nome_to_sigla.get(init_name, init_name[:15]),
                        'full_name': init_name
                    })
                    all_years_set.add(year)
        
        # Initialize evolution_df to avoid unbound variable issues
        evolution_df = pd.DataFrame()
        if evolution_data:
            evolution_df = pd.DataFrame(evolution_data)
            year_counts = evolution_df['year'].value_counts().sort_index()
            
            # Create evolution line chart
            fig_evolution = go.Figure()
            
            fig_evolution.add_trace(go.Scatter(
                x=year_counts.index,
                y=year_counts.values,
                mode='lines+markers',
                name='Active Initiatives',
                line=dict(color='rgba(0, 150, 136, 1)', width=3),
                marker=dict(size=8, color='rgba(0, 150, 136, 0.8)'),
                fill='tonexty',
                fillcolor='rgba(0, 150, 136, 0.2)',
                hovertemplate='<b>Year: %{x}</b><br>' +
                             'Active Initiatives: %{y}<extra></extra>'
            ))
            
            fig_evolution.update_layout(
                title='Evolution of Data Availability Over Time',
                xaxis_title='Year',
                yaxis_title='Number of Active Initiatives',
                height=450,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
            )
            
            st.plotly_chart(fig_evolution, use_container_width=True)

        
        # === INITIATIVE AVAILABILITY HEATMAP ===
        st.markdown("### 🔥 Initiative Availability Heatmap (by Type and Year)")
        st.markdown("Availability by Type and Year (Heatmap)")
        
        # Create heatmap data
        heatmap_data = []
        for init_name, details in filtered_meta.items():
            if 'available_years' in details and details['available_years']:
                # Get initiative type from df_filtered
                init_row = df_filtered[df_filtered['Name'] == init_name]
                init_type = init_row['Type'].iloc[0] if not init_row.empty and 'Type' in init_row.columns else 'Unknown'
                
                for year in details['available_years']:
                    heatmap_data.append({
                        'Year': year,
                        'Type': init_type,
                        'Initiative': nome_to_sigla.get(init_name, init_name[:15]),
                        'Available': 1
                    })
        
        if heatmap_data:
            heatmap_df = pd.DataFrame(heatmap_data)
            
            # Create pivot table for heatmap
            pivot_df = heatmap_df.pivot_table(
                values='Available',
                index='Type',
                columns='Year',
                aggfunc='sum',
                fill_value=0
            )
            
            # Create heatmap
            fig_heatmap_temporal = go.Figure(data=go.Heatmap(
                z=pivot_df.values,
                x=pivot_df.columns,
                y=pivot_df.index,
                colorscale='Viridis',
                hoverongaps=False,
                hovertemplate='<b>Type: %{y}</b><br>' +
                             'Year: %{x}<br>' +
                             'Active Initiatives: %{z}<extra></extra>'
            ))
            
            fig_heatmap_temporal.update_layout(
                title='Initiative Availability by Type and Year',
                xaxis_title='Year',
                yaxis_title='Initiative Type',
                height=400,
                xaxis=dict(type='category'),
                yaxis=dict(type='category')
            )
            
            st.plotly_chart(fig_heatmap_temporal, use_container_width=True)
            
            # Summary statistics
            st.markdown("#### 📊 Temporal Coverage Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_years_covered = len(all_years_set)
                st.metric("Years Covered", f"{min(all_years_set)}-{max(all_years_set)}" if all_years_set else "N/A", 
                         f"{total_years_covered} years")
            
            with col2:
                avg_initiatives_per_year = evolution_df['year'].value_counts().mean() if not evolution_df.empty else 0
                st.metric("Avg. Initiatives/Year", f"{avg_initiatives_per_year:.1f}")
            
            with col3:
                peak_year = evolution_df['year'].value_counts().idxmax() if not evolution_df.empty else "N/A"
                peak_count = evolution_df['year'].value_counts().max() if not evolution_df.empty else 0
                st.metric("Peak Activity", f"{peak_year}", f"{peak_count} initiatives")
        
        else:
            st.warning("⚠️ No temporal data available for heatmap visualization.")

def run_non_streamlit(df, metadata, output_dir="graphics/detailed"):
    """
    Run detailed analysis without Streamlit UI and save graphics to files.
    Used when called from command-line scripts like run_full_analysis.py
    """
    from pathlib import Path
    
    # Add scripts to path
    # current_dir is defined at the module level in detailed.py
    # For non-streamlit runs, ensure PROJECT_ROOT is correctly determined if current_dir is not suitable.
    # Assuming PROJECT_ROOT is dashboard-iniciativas/
    project_root_for_script = Path(__file__).resolve().parent.parent.parent 
    sys.path.append(str(project_root_for_script / "scripts"))
    
    from scripts.utilities.chart_saver import save_chart_robust
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("🔄 Generating detailed analyses...") # Translated
    
    if df is None or df.empty:
        print("❌ Insufficient data for detailed analysis.") # Translated
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
        selected_initiatives_names = df_for_analysis["Name"].tolist()[:min(5, len(df_for_analysis))]
        df_filtered_non_st = df_for_analysis[df_for_analysis["Name"].isin(selected_initiatives_names)].copy()
        
        print("📊 Generating dual bars chart...") # Translated
        fig_dual_bars = create_dual_bars_chart(df_filtered_non_st)
        if fig_dual_bars:
            success, saved_path, format_used = save_chart_robust(
                fig_dual_bars, output_dir, "dual_bars_detailed", 
                width=1000, height=max(400, len(df_filtered_non_st) * 30 + 150), scale=2 # Adjusted dimensions
            )
            if success:
                print(f"✅ Dual bars saved as {format_used} in: {saved_path}") # Translated
        
        print("🎯 Generating radar chart...") # Translated
        fig_radar = create_radar_chart(df_filtered_non_st)
        if fig_radar:
            success, saved_path, format_used = save_chart_robust(
                fig_radar, output_dir, "radar_chart_detailed", 
                width=800, height=700, scale=2 # Adjusted dimensions
            )
            if success:
                print(f"✅ Radar chart saved as {format_used} in: {saved_path}") # Translated
        
        print("🔥 Generating heatmap...") # Translated
        fig_heatmap = create_heatmap_chart(df_filtered_non_st)
        if fig_heatmap:
            success, saved_path, format_used = save_chart_robust(
                fig_heatmap, output_dir, "heatmap_detailed", 
                width=900, height=max(400, len(df_filtered_non_st) * 30 + 150), scale=2 # Adjusted dimensions
            )
            if success:
                print(f"✅ Heatmap saved as {format_used} in: {saved_path}") # Translated
        
        # Generate Annual Coverage Chart (Non-Streamlit)
        if metadata:
            print("📅 Generating annual coverage chart...") # Translated
            try:
                from scripts.plotting.generate_graphics import plot_annual_coverage_multiselect
                fig_annual_coverage = plot_annual_coverage_multiselect(metadata, df_filtered_non_st, selected_initiatives_names)
                if fig_annual_coverage:
                    success, saved_path, format_used = save_chart_robust(
                        fig_annual_coverage, output_dir, "annual_coverage_detailed",
                        width=1200, height=700, scale=2 # Adjusted dimensions
                    )
                    if success:
                        print(f"✅ Annual coverage chart saved as {format_used} in: {saved_path}") # Translated
            except ImportError:
                print("❌ Annual coverage function not available for non-Streamlit execution.") # Translated
            except Exception as e:
                print(f"❌ Error generating annual coverage chart (non-Streamlit): {e}")

        print("✅ Detailed analyses completed successfully!") # Translated
        return True
        
    except Exception as e:
        print(f"❌ Error generating detailed analyses: {e}") # Translated
        return False


def create_dual_bars_chart(df_filtered_chart):
    """Create dual bars chart without Streamlit dependencies"""
    try:
        df_filtered_chart = df_filtered_chart.copy() # Avoid SettingWithCopyWarning
        df_filtered_chart['resolution_norm'] = (1 / df_filtered_chart['Resolution']) / (1 / df_filtered_chart['Resolution']).max()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_filtered_chart['Display_Name'], 
            x=df_filtered_chart['Accuracy (%)'],
            name='Accuracy (%)',
            orientation='h',
            marker_color='royalblue'
        ))
        fig.add_trace(go.Bar(
            y=df_filtered_chart['Display_Name'],
            x=df_filtered_chart['resolution_norm'] * 100,
            name='Resolution (Normalized)', # Translated
            orientation='h',
            marker_color='orange'
        ))
        
        if apply_standard_layout:
            apply_standard_layout(fig, "Comparison: Accuracy vs Resolution", "Value (%)", "Initiative")
        else:
            fig.update_layout(
                title='Comparison: Accuracy vs Resolution',
                xaxis_title='Value (%)', 
                yaxis_title='Initiative'
            )
        
        fig.update_layout(
            barmode='group',
            height=max(400, len(df_filtered_chart) * 30 + 100) # Adjusted height
        )
        return fig
    except Exception as e:
        print(f"Error creating dual bars chart: {e}") # Translated
        return None

def create_radar_chart(df_filtered_chart):
    """Create radar chart without Streamlit dependencies"""
    try:
        radar_columns = ['Accuracy (%)', 'Resolution', 'Classes', 'Num_Agri_Classes']
        available_radar_cols_chart = [col for col in radar_columns if col in df_filtered_chart.columns]
        
        if len(available_radar_cols_chart) < 2:
            print("Insufficient data for radar chart.") # Translated
            return None
        
        radar_df_chart = df_filtered_chart[['Display_Name'] + available_radar_cols_chart].copy()
        for col in available_radar_cols_chart:
            # Convert to numeric and handle NaN values
            radar_df_chart[col] = pd.to_numeric(radar_df_chart[col], errors='coerce').fillna(0)
            min_val, max_val = radar_df_chart[col].min(), radar_df_chart[col].max()
            if max_val - min_val > 0:
                if col == 'Resolution':
                    radar_df_chart[col] = 1 - (radar_df_chart[col] - min_val) / (max_val - min_val)
                else:
                    radar_df_chart[col] = (radar_df_chart[col] - min_val) / (max_val - min_val)
            else:
                radar_df_chart[col] = 0.5
        
        fig_radar = go.Figure()
        colors = px.colors.qualitative.Plotly # Using Plotly colors
        for i, (idx, row) in enumerate(radar_df_chart.iterrows()):
            values = row[available_radar_cols_chart].tolist()
            values_closed = values + [values[0]]
            theta_closed = available_radar_cols_chart + [available_radar_cols_chart[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=values_closed,
                theta=theta_closed,
                fill='toself',
                name=row['Display_Name'],
                line_color=colors[i % len(colors)],
                line_width=2
            ))
        
        if apply_standard_layout:
            apply_standard_layout(fig_radar, "Multi-dimensional Comparison (Radar)", "", "")
        else:
            fig_radar.update_layout(title='Multi-dimensional Comparison (Radar)')
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1]),
                angularaxis=dict(rotation=90, direction="counterclockwise")
            ),
            showlegend=True,
            height=600
        )
        return fig_radar
    except Exception as e:
        print(f"Error creating radar chart: {e}") # Translated
        return None

def create_heatmap_chart(df_filtered_chart):
    """Create heatmap chart without Streamlit dependencies"""
    try:
        radar_columns = ['Accuracy (%)', 'Resolution', 'Classes', 'Num_Agri_Classes']
        available_radar_cols_chart = [col for col in radar_columns if col in df_filtered_chart.columns]
        
        if len(available_radar_cols_chart) < 2:
            print("Insufficient data for heatmap.") # Translated
            return None
        
        # Recalculate radar_df_chart for heatmap context to ensure it's fresh
        radar_df_chart = df_filtered_chart[['Display_Name'] + available_radar_cols_chart].copy()
        for col in available_radar_cols_chart:
            # Convert to numeric and handle NaN values
            radar_df_chart[col] = pd.to_numeric(radar_df_chart[col], errors='coerce').fillna(0)
            min_val, max_val = radar_df_chart[col].min(), radar_df_chart[col].max()
            if max_val - min_val > 0:
                if col == 'Resolution':
                    radar_df_chart[col] = 1 - (radar_df_chart[col] - min_val) / (max_val - min_val)
                else:
                    radar_df_chart[col] = (radar_df_chart[col] - min_val) / (max_val - min_val)
            else:
                radar_df_chart[col] = 0.5
        
        heatmap_df_chart = radar_df_chart.set_index('Display_Name')[available_radar_cols_chart]
        fig_heatmap = px.imshow(
            heatmap_df_chart.values,
            x=heatmap_df_chart.columns,
            y=heatmap_df_chart.index,
            color_continuous_scale='Viridis',
            aspect='auto',
            labels=dict(x='Metric', y='Initiative', color='Normalized Value')
        )
        
        if apply_standard_layout:
            apply_standard_layout(fig_heatmap, "Performance Heatmap (Normalized Values)", "Metric", "Initiative")
        else:
            fig_heatmap.update_layout(title='Performance Heatmap (Normalized Values)')
        
        fig_heatmap.update_layout(height=max(400, len(df_filtered_chart) * 30 + 100)) # Adjusted height
        return fig_heatmap
    except Exception as e:
        print(f"Error creating heatmap: {e}") # Translated
        return None
