import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add scripts to path if necessary
current_dir = Path(__file__).parent.parent.parent
scripts_path = str(current_dir / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# Import modules locally
try:
    from scripts.utilities.json_interpreter import interpret_initiatives_metadata, _load_jsonc_file
    from scripts.utilities.ui_elements import get_chart_save_params
    from scripts.utilities.chart_saver import save_chart_robust
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

def run():
    # Load data using the new JSON interpreter system
    if 'df_interpreted' not in st.session_state:
        try:
            metadata_file_path = current_dir / "data" / "raw" / "initiatives_metadata.jsonc"
            df_interpreted = interpret_initiatives_metadata(metadata_file_path)
            if df_interpreted.empty:
                st.error("❌ Data interpretation resulted in an empty DataFrame.")
                return
            st.session_state.df_interpreted = df_interpreted
            
            # Also load raw metadata for temporal analysis
            raw_metadata = _load_jsonc_file(metadata_file_path)
            st.session_state.metadata = raw_metadata
            
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            return

    df = st.session_state.get('df_interpreted', pd.DataFrame())
    meta = st.session_state.get('metadata', {})

    if df.empty:
        st.error("❌ No data available. Please check the data loading process.")
        return

    # Create nome_to_sigla mapping from the DataFrame
    nome_to_sigla = {}
    if 'Acronym' in df.columns and 'Name' in df.columns:
        for _, row in df.iterrows():
            if pd.notna(row['Name']) and pd.notna(row['Acronym']):
                nome_to_sigla[row['Name']] = row['Acronym']




    # Modern filters at the top of the page
    st.markdown("### 🔎 Initiative Filters")
    col1, col2, col3, col4 = st.columns(4)    
    with col1:
        # Ensure df is not empty and 'Type' column exists before accessing unique values
        tipos = df["Type"].unique().tolist() if not df.empty and "Type" in df.columns else []
        selected_types = st.multiselect("Type", options=tipos, default=tipos)
    with col2:        # Ensure df is not empty and 'Resolution' column exists  
        if not df.empty and "Resolution" in df.columns and df["Resolution"].notna().any():
            min_res, max_res = int(df["Resolution"].min()), int(df["Resolution"].max())
            selected_res = st.slider("Resolution (m)", min_value=min_res, max_value=max_res, value=(min_res, max_res))
        else:
            selected_res = st.slider("Resolution (m)", min_value=0, max_value=1000, value=(0, 1000), disabled=True)
            st.caption("Resolution data not available for current selection.")
    with col3:        # Ensure df is not empty and 'Accuracy' column exists
        if not df.empty and "Accuracy" in df.columns and df["Accuracy"].notna().any():
            min_acc, max_acc = int(df["Accuracy"].min()), int(df["Accuracy"].max())
            selected_acc = st.slider("Accuracy (%)", min_value=min_acc, max_value=max_acc, value=(min_acc, max_acc))
        else:
            selected_acc = st.slider("Accuracy (%)", min_value=0, max_value=100, value=(0,100), disabled=True)
            st.caption("Accuracy data not available for current selection.")
    with col4:
        # Ensure df is not empty and 'Methodology' column exists
        metodologias = df["Methodology"].unique().tolist() if not df.empty and "Methodology" in df.columns else []
        selected_methods = st.multiselect("Methodology", options=metodologias, default=metodologias)    # Apply filters
    filtered_df = df[
        (df["Type"].isin(selected_types)) &
        (df["Resolution"].between(selected_res[0], selected_res[1])) &
        (df["Accuracy"].between(selected_acc[0], selected_acc[1])) &
        (df["Methodology"].isin(selected_methods))
    ]
    st.session_state.filtered_df = filtered_df

    if filtered_df.empty:
        st.warning("⚠️ No initiatives match the selected filters. Adjust the filters to view data.")
        st.stop()    # Main content of the Overview page
    st.subheader("📈 Key Aggregated Metrics")
    
    # Custom CSS for modern metric cards
    st.markdown("""
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
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_accuracy = filtered_df["Accuracy"].mean()
        accuracy_value = f"{avg_accuracy:.1f}" if pd.notna(avg_accuracy) else "N/A"
        st.markdown(f"""
        <div class="metric-card accuracy">
            <span class="metric-icon">🎯</span>
            <div class="metric-value">{accuracy_value}%</div>
            <div class="metric-label">Average Accuracy</div>
            <div class="metric-sublabel">Across all initiatives</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_resolution = filtered_df["Resolution"].mean()
        resolution_value = f"{avg_resolution:.0f}" if pd.notna(avg_resolution) else "N/A"
        st.markdown(f"""
        <div class="metric-card resolution">
            <span class="metric-icon">🔬</span>
            <div class="metric-value">{resolution_value}m</div>
            <div class="metric-label">Average Resolution</div>
            <div class="metric-sublabel">Spatial precision</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if "Classes" in filtered_df.columns:
            total_classes = filtered_df["Classes"].sum() if filtered_df["Classes"].notna().any() else 0
        elif "Number_of_Classes" in filtered_df.columns:
            total_classes = filtered_df["Number_of_Classes"].sum() if filtered_df["Number_of_Classes"].notna().any() else 0
        else:
            total_classes = 0
        st.markdown(f"""
        <div class="metric-card classes">
            <span class="metric-icon">🏷️</span>
            <div class="metric-value">{total_classes}</div>
            <div class="metric-label">Total Classes</div>
            <div class="metric-sublabel">Classification categories</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        global_initiatives = len(filtered_df[filtered_df["Type"] == "Global"]) if "Type" in filtered_df.columns else 0
        st.markdown(f"""
        <div class="metric-card global">
            <span class="metric-icon">🌍</span>
            <div class="metric-value">{global_initiatives}</div>
            <div class="metric-label">Global Initiatives</div>
            <div class="metric-sublabel">Worldwide coverage</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

    st.subheader("🔍 Detailed Exploration by Initiative")
    
    # CSS for modern initiative details
    st.markdown("""
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
    """, unsafe_allow_html=True)
    
    selected_initiative_detailed = st.selectbox(
        "Select an initiative to see details:",
        options=filtered_df["Name"].tolist(),
        help="Choose an initiative for detailed information",
        key="overview_detailed_select" 
    )
    
    if selected_initiative_detailed:
        init_data = filtered_df[filtered_df["Name"] == selected_initiative_detailed].iloc[0]
        init_metadata = meta.get(selected_initiative_detailed, {})
        # Get the acronym for the selected initiative
        initiative_acronym = nome_to_sigla.get(selected_initiative_detailed, selected_initiative_detailed[:10])

        # Modern initiative header
        st.markdown(f"""
        <div class="initiative-header">
            <h2 class="initiative-title">🛰️ {initiative_acronym}</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{selected_initiative_detailed}</p>
        </div>
        """, unsafe_allow_html=True)        
        st.markdown("""
        <div class="detail-card">
        """, unsafe_allow_html=True)

        col1_detail, col2_detail = st.columns([2, 3])
        
        with col1_detail:
            st.markdown("#### 📊 Key Metrics")
            
            # Modern metric grid
            accuracy_val = init_data.get('Accuracy', 'N/A')
            resolution_val = init_data.get('Resolution', 'N/A')
            classes_val = init_data.get("Classes", init_data.get("Number_of_Classes", "N/A"))
            frequency_val = init_data.get("Temporal_Frequency", "N/A")
            
            st.markdown(f"""
            <div class="metric-grid">
                <div class="mini-metric">
                    <div class="mini-metric-value">🎯 {accuracy_val}%</div>
                    <div class="mini-metric-label">Accuracy</div>
                </div>
                <div class="mini-metric">
                    <div class="mini-metric-value">🔬 {resolution_val}m</div>
                    <div class="mini-metric-label">Resolution</div>
                </div>
                <div class="mini-metric">
                    <div class="mini-metric-value">🏷️ {classes_val}</div>
                    <div class="mini-metric-label">Classes</div>
                </div>
                <div class="mini-metric">
                    <div class="mini-metric-value">📅 {frequency_val}</div>
                    <div class="mini-metric-label">Frequency</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### ⚙️ Technical Information")            # Modern badges for technical info
            type_val = init_data.get('Type', 'N/A')
            methodology_val = init_data.get('Methodology', 'N/A')
            scope_val = init_data.get('Type', 'N/A')  # Using Type as scope
            years_val = init_data.get('Available_Years', 'N/A')  # Now it's a string
            
            st.markdown(f"""
            <div style="margin: 1rem 0;">
                <p><strong>🏷️ Type:</strong></p>
                <span class="badge badge-type">{type_val}</span>
                
                <p style="margin-top: 1rem;"><strong>🔬 Methodology:</strong></p>
                <span class="badge badge-methodology">{methodology_val}</span>
                
                <p style="margin-top: 1rem;"><strong>🌍 Scope:</strong></p>
                <span class="badge badge-scope">{scope_val}</span>
                
                <p style="margin-top: 1rem;"><strong>📅 Available Years:</strong></p>
                <span class="badge badge-years">{years_val}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2_detail:
            st.markdown("#### 📋 Methodological Details")
              # Modern info sections - using correct JSON fields
            methodology_info = init_metadata.get("methodology", "Not available")
            algorithm_info = init_metadata.get("algorithm", init_metadata.get("classification_method", "Not available"))
            provider_info = init_metadata.get("provider", "Not available") 
            source_info = init_metadata.get("source", "Not available")
            update_freq_info = init_metadata.get("update_frequency", "Not available")
            reference_sys_info = init_metadata.get("reference_system", "Not available")
            
            st.markdown(f"""
            <div class="info-section">
                <div class="info-title">🔬 Methodology</div>
                <p><strong>Approach:</strong> {methodology_info}</p>
                <p><strong>Algorithm:</strong> {algorithm_info}</p>
            </div>
            
            <div class="info-section" style="border-left-color: #28a745;">
                <div class="info-title">🏢 Provider & Sources</div>
                <p><strong>Provider:</strong> {provider_info}</p>
                <p><strong>Data Source:</strong> {source_info}</p>
            </div>
            
            <div class="info-section" style="border-left-color: #ffc107;">
                <div class="info-title">🔄 Update Information</div>
                <p><strong>Update Frequency:</strong> {update_freq_info}</p>
                <p><strong>Temporal Frequency:</strong> {init_data.get('Temporal Frequency', 'N/A')}</p>
            </div>
            
            <div class="info-section" style="border-left-color: #17a2b8;">
                <div class="info-title">�️ Technical Specifications</div>
                <p><strong>Reference System:</strong> {reference_sys_info if isinstance(reference_sys_info, str) else 'Multiple systems'}</p>
                <p><strong>Resolution:</strong> {init_data.get('Resolution', 'N/A')} meters</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Additional section for class information
        if 'class_legend' in init_metadata and init_metadata['class_legend']:
            st.markdown("#### 🏷️ Classification Details")
            class_legend = init_metadata.get('class_legend', '')
            classes_list = [cls.strip() for cls in class_legend.split(',') if cls.strip()]
            
            st.markdown("""
            <div class="info-section" style="margin-top: 1rem;">
                <div class="info-title">📋 Land Cover Classes</div>
            """, unsafe_allow_html=True)
            
            # Display classes as badges
            classes_html = ""
            for i, cls in enumerate(classes_list):
                color = ["#e3f2fd", "#f3e5f5", "#e8f5e8", "#fff3e0", "#fce4ec", "#e0f2f1"][i % 6]
                classes_html += f'<span class="badge" style="background: {color}; margin: 0.2rem;">{cls}</span>'            
            st.markdown(f"""
                <p style="line-height: 2;">
                    {classes_html}
                </p>
            </div>
            """, unsafe_allow_html=True)

        # New Technical Specifications Section - following remote sensing best practices
        st.markdown("#### 🛰️ Technical Specifications")
        
        # Sensor and Data Acquisition Information
        technical_info = []
        if init_data.get('Spectral_Bands') and init_data['Spectral_Bands'] != 'None':
            technical_info.append(f"**Spectral Bands:** {init_data['Spectral_Bands']}")
        if init_data.get('Platform') and init_data['Platform'] != 'None':
            technical_info.append(f"**Platform:** {init_data['Platform']}")
        if init_data.get('Sensor_Type') and init_data['Sensor_Type'] != 'None':
            technical_info.append(f"**Sensor Type:** {init_data['Sensor_Type']}")
        if init_data.get('Revisit_Time') and init_data['Revisit_Time'] != 'None':
            technical_info.append(f"**Revisit Time:** {init_data['Revisit_Time']}")
            
        if technical_info:
            st.markdown("""
            <div class="info-section" style="margin-top: 1rem;">
                <div class="info-title">🛰️ Sensor & Data Acquisition</div>
            """, unsafe_allow_html=True)
            
            for info in technical_info:
                st.markdown(f"• {info}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Processing and Quality Information
        processing_info = []
        if init_data.get('Preprocessing_Level') and init_data['Preprocessing_Level'] != 'None':
            processing_info.append(f"**Preprocessing Level:** {init_data['Preprocessing_Level']}")
        if init_data.get('Atmospheric_Correction') and init_data['Atmospheric_Correction'] != 'None':
            processing_info.append(f"**Atmospheric Correction:** {init_data['Atmospheric_Correction']}")
        if init_data.get('Geometric_Correction') and init_data['Geometric_Correction'] != 'None':
            processing_info.append(f"**Geometric Correction:** {init_data['Geometric_Correction']}")
        if init_data.get('Cloud_Masking') and init_data['Cloud_Masking'] != 'None':
            processing_info.append(f"**Cloud Masking:** {init_data['Cloud_Masking']}")
            
        if processing_info:
            st.markdown("""
            <div class="info-section" style="margin-top: 1rem;">
                <div class="info-title">⚙️ Processing & Quality Control</div>
            """, unsafe_allow_html=True)
            
            for info in processing_info:
                st.markdown(f"• {info}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Validation and Data Characteristics
        validation_info = []
        if init_data.get('Validation_Method') and init_data['Validation_Method'] != 'None':
            validation_info.append(f"**Validation Method:** {init_data['Validation_Method']}")
        if init_data.get('Minimum_Mapping_Unit') and init_data['Minimum_Mapping_Unit'] != 'None':
            validation_info.append(f"**Minimum Mapping Unit:** {init_data['Minimum_Mapping_Unit']}")
        if init_data.get('Data_Format') and init_data['Data_Format'] != 'None':
            validation_info.append(f"**Data Format:** {init_data['Data_Format']}")
            
        if validation_info:
            st.markdown("""
            <div class="info-section" style="margin-top: 1rem;">
                <div class="info-title">📊 Validation & Data Characteristics</div>
            """, unsafe_allow_html=True)
            
            for info in validation_info:
                st.markdown(f"• {info}")
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Link to detailed comparisons
    st.markdown("---")
    st.info("💡 **For detailed comparisons between multiple initiatives**, go to the **'🔍 Detailed Analyses'** page in the sidebar.")
    st.markdown("---")

    # Temporal density chart
    st.subheader("🌊 Temporal Density of LULC Initiatives")
    
    if meta:        # Create density data using metadata
        density_data = []
        all_years = set()
        
        for nome, meta_item in meta.items():
            # Ensure the initiative is in the filtered_df before processing
            if nome in filtered_df["Name"].values:
                if 'available_years' in meta_item and meta_item['available_years']:
                    for ano in meta_item['available_years']:
                        density_data.append({'nome': nome, 'ano': ano})
                        all_years.add(ano)
        
        if density_data:
            density_df = pd.DataFrame(density_data)
            year_counts = density_df['ano'].value_counts().sort_index()
            
            # Density chart by year (line + area)
            fig_density_line = go.Figure()
            fig_density_line.add_trace(go.Scatter(
                x=year_counts.index,
                y=year_counts.values,
                mode='lines+markers',
                fill='tonexty',
                name='Active Initiatives', # Translated
                line=dict(color='rgba(0,150,136,0.8)', width=3),
                marker=dict(size=8, color='rgba(0,150,136,1)')
            ))
            
            fig_density_line.update_layout(
                title='📊 Temporal Density: Number of Initiatives per Year', # Simplified title
                xaxis_title='Year', # Translated
                yaxis_title='Number of Active Initiatives', # Translated
                height=450,
                hovermode='x unified',
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128,128,128,0.2)'
                ),
                yaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128,128,128,0.2)'
                )
            )
            st.plotly_chart(fig_density_line, use_container_width=True)
            
            # Add download button using the new UI
            filename_density, format_density, width_density, height_density, scale_density, save_clicked_density = get_chart_save_params(
                default_filename="temporal_density_overview", 
                key_prefix="density_overview"
            )
            if save_clicked_density:
                # Ensure the 'graphics/detailed' directory exists
                output_dir = Path(current_dir) / "graphics" / "detailed"
                output_dir.mkdir(parents=True, exist_ok=True)
                
                success, message, _ = save_chart_robust(
                    fig_density_line,
                    str(output_dir), # Pass directory path
                    filename_density, # Pass base filename
                    width=width_density,
                    height=height_density,
                    scale=scale_density,
                    file_format=format_density.lower() 
                )
                if success:
                    st.success(f"Chart '{filename_density}.{format_density.lower()}' saved successfully in '{output_dir}'.")
                else:
                    st.error(f"Failed to save chart: {message}")
              # Enhanced temporal metrics - Modern cards
            st.markdown("#### 📈 Temporal Metrics")
            
            # CSS for temporal metrics
            st.markdown("""
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
            .timeline-card {
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            }
            .initiative-item {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0.8rem;
                margin: 0.5rem 0;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #007bff;
                transition: all 0.3s ease;
            }
            .initiative-item:hover {
                background: #e9ecef;
                transform: translateX(5px);
            }
            .initiative-name {
                font-weight: 600;
                color: #495057;
            }
            .initiative-year {
                background: #007bff;
                color: white;
                padding: 0.3rem 0.8rem;
                border-radius: 15px;
                font-size: 0.9rem;
                font-weight: 500;
            }
            .coverage-stats {
                font-size: 0.9rem;
                color: #6c757d;
                margin-left: 0.5rem;
            }
            </style>
            """, unsafe_allow_html=True)
            
            col1_temp, col2_temp, col3_temp, col4_temp = st.columns(4)
            
            with col1_temp:
                first_year = min(all_years) if all_years else "N/A"
                st.markdown(f"""
                <div class="temporal-metric">
                    <div class="temporal-metric-value">🗓️ {first_year}</div>
                    <div class="temporal-metric-label">First Year</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col2_temp:
                last_year = max(all_years) if all_years else "N/A"
                st.markdown(f"""
                <div class="temporal-metric">
                    <div class="temporal-metric-value">📅 {last_year}</div>
                    <div class="temporal-metric-label">Last Year</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col3_temp:
                if not year_counts.empty:
                    peak_year = year_counts.idxmax()
                    peak_value = max(year_counts.values)
                    st.markdown(f"""
                    <div class="temporal-metric">
                        <div class="temporal-metric-value">🎯 {peak_value}</div>
                        <div class="temporal-metric-label">Peak Activity</div>
                        <div class="temporal-metric-delta">In {peak_year}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="temporal-metric">
                        <div class="temporal-metric-value">🎯 N/A</div>
                        <div class="temporal-metric-label">Peak Activity</div>
                    </div>                    """, unsafe_allow_html=True)
                
            with col4_temp:
                if not year_counts.empty:
                    avg_per_year = year_counts.mean()  # Using pandas mean instead of numpy
                    st.markdown(f"""
                    <div class="temporal-metric">
                        <div class="temporal-metric-value">📈 {avg_per_year:.1f}</div>
                        <div class="temporal-metric-label">Average per Year</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="temporal-metric">
                        <div class="temporal-metric-value">📈 N/A</div>
                        <div class="temporal-metric-label">Average per Year</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Modern timeline details
            st.markdown("#### 📅 Timeline Details")
            col_timeline1, col_timeline2 = st.columns(2)
            
            with col_timeline1:
                st.markdown("""
                <div class="timeline-card">
                    <h5 style="color: #495057; margin-bottom: 1rem;">🚀 Most Recent Initiatives</h5>
                """, unsafe_allow_html=True)
                
                recent_initiatives = []
                for nome, meta_item in meta.items():
                    if nome in filtered_df["Name"].values:
                        if 'available_years' in meta_item and meta_item['available_years']:
                            latest_year = max(meta_item['available_years'])
                            acronym = nome_to_sigla.get(nome, nome[:10])
                            recent_initiatives.append((acronym, latest_year, nome))
                
                # Show top 5 most recent with modern styling
                recent_initiatives.sort(key=lambda x: x[1], reverse=True)
                for acronym, year, original_name in recent_initiatives[:5]:
                    st.markdown(f"""
                    <div class="initiative-item">
                        <span class="initiative-name">{acronym}</span>
                        <span class="initiative-year">{year}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col_timeline2:
                st.markdown("""
                <div class="timeline-card">
                    <h5 style="color: #495057; margin-bottom: 1rem;">📊 Coverage Period by Initiative</h5>
                """, unsafe_allow_html=True)
                
                coverage_info = []
                for nome, meta_item in meta.items():
                    if nome in filtered_df["Name"].values:
                        if 'available_years' in meta_item and meta_item['available_years']:
                            years_list = meta_item['available_years']
                            if years_list:
                                span = max(years_list) - min(years_list) + 1
                                acronym = nome_to_sigla.get(nome, nome[:10])
                                coverage_info.append((acronym, span, len(years_list), nome))
                
                # Show initiatives with longest coverage
                coverage_info.sort(key=lambda x: x[1], reverse=True)
                for acronym, span, count, original_name in coverage_info[:5]:
                    st.markdown(f"""
                    <div class="initiative-item">
                        <span class="initiative-name">{acronym}</span>
                        <span class="coverage-stats">{span} years ({count} datasets)</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                    
        else:
            st.warning("📅 Temporal data not found for the selected initiatives in the processed metadata.") # Updated message
            st.info("💡 **Tip:** Check if the metadata contains information about available years for the selected initiatives.") # Updated message
    else:
        st.error("Metadata not available for temporal analysis.") # Translated

    st.markdown("---")
