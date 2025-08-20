"""
Class Details Component - Comparison Analysis
============================================

Advanced component for detailed class information visualization with comparative charts.
Features class distribution analysis, agricultural capabilities comparison, and interactive visualizations.

Author: LANDAGRI-B Project Team 
Date: 2025-08-01
"""

import hashlib
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_class_details_tab(filtered_df: pd.DataFrame) -> None:
    """
    Render comprehensive class details analysis with interactive visualizations.
    
    Args:
        filtered_df: Filtered DataFrame with initiative data
    """
    st.markdown("#### 🏷️ Initiative Class Details Analysis")
    
    if filtered_df.empty:
        st.warning("⚠️ No initiative data available for class analysis.")
        return
    
    # Access metadata from session state
    metadata = st.session_state.get("metadata", {})
    if not metadata:
        st.warning("⚠️ Metadata not available for class details analysis.")
        return
    
    # Tab-based visualization
    tab1, tab2, tab3 = st.tabs([
        "🔎 Class Overview", 
        "🌾 Agricultural Analysis", 
        "📈 Comparative Charts"
    ])
    
    with tab1:
        render_class_overview(filtered_df, metadata)
    
    with tab2:
        render_agricultural_analysis(filtered_df, metadata)
    
    with tab3:
        render_comparative_charts(filtered_df, metadata)


def render_class_overview(filtered_df: pd.DataFrame, metadata: dict) -> None:
    """Render class overview with detailed information for each initiative."""
    st.markdown("##### Class Information Overview")
    
    class_data = []
    
    for idx, row in filtered_df.iterrows():
        initiative_name = row.get('Name', 'Unknown Initiative')
        display_name = row.get('Display_Name', row.get('Acronym', initiative_name))
        
        # Get class information from metadata
        initiative_meta = metadata.get(initiative_name, {})
        class_legend = initiative_meta.get("class_legend", "")
        number_of_classes = initiative_meta.get("number_of_classes", 0)
        agri_classes = initiative_meta.get("number_of_agriculture_classes", 0)
        agri_capabilities = initiative_meta.get("agricultural_capabilities", "")
        
        # Parse classes if available
        classes = []
        if class_legend and isinstance(class_legend, str):
            classes = [cls.strip() for cls in class_legend.split(',') if cls.strip()]
        
        class_data.append({
            'Initiative': display_name,
            'Total Classes': number_of_classes or len(classes),
            'Agricultural Classes': agri_classes,
            'Agricultural Capabilities': agri_capabilities[:100] + "..." if len(str(agri_capabilities)) > 100 else agri_capabilities,
            'Class Details Available': len(classes) > 0
        })
    
    # Create overview DataFrame
    overview_df = pd.DataFrame(class_data)
    
    if not overview_df.empty:
        st.dataframe(overview_df, use_container_width=True, hide_index=True)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Initiatives", len(overview_df))
        with col2:
            avg_classes = overview_df['Total Classes'].mean()
            st.metric("Avg Classes", f"{avg_classes:.1f}")
        with col3:
            total_agri = overview_df['Agricultural Classes'].sum()
            st.metric("Total Agri Classes", total_agri)
        with col4:
            with_details = overview_df['Class Details Available'].sum()
            st.metric("With Details", f"{with_details}/{len(overview_df)}")


def render_agricultural_analysis(filtered_df: pd.DataFrame, metadata: dict) -> None:
    """Render agricultural classification analysis."""
    
    agri_data = []
    
    for idx, row in filtered_df.iterrows():
        initiative_name = row.get('Name', 'Unknown Initiative')
        display_name = row.get('Display_Name', row.get('Acronym', initiative_name))
        
        initiative_meta = metadata.get(initiative_name, {})
        agri_classes = initiative_meta.get("number_of_agriculture_classes", 0)
        total_classes = initiative_meta.get("number_of_classes", 0)
        agri_capabilities = initiative_meta.get("agricultural_capabilities", "")
        
        if agri_classes > 0:
            agri_data.append({
                'Initiative': display_name,
                'Agricultural Classes': agri_classes,
                'Total Classes': total_classes,
                'Agricultural Ratio': (agri_classes / total_classes * 100) if total_classes > 0 else 0,
                'Capabilities': agri_capabilities
            })
    
    if not agri_data:
        st.info("No agricultural classification data available.")
        return
    
    agri_df = pd.DataFrame(agri_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Agricultural classes bar chart
        fig_agri = px.bar(
            agri_df,
            x="Initiative",
            y="Agricultural Classes",
            title="<b>Agricultural Classes by Initiative</b>",
            color="Agricultural Classes",
            color_continuous_scale="Greens"
        )
        fig_agri.update_layout(
            font=dict(family="Inter", size=12),
            title_font=dict(size=14, family="Inter", color="#1f2937"),
            xaxis_tickangle=-45
        )
        # Add unique key for Streamlit
        st.plotly_chart(fig_agri, use_container_width=True, key=f"agri-bar-{hashlib.md5(str(fig_agri).encode()).hexdigest()}")
    
    with col2:
        # Agricultural ratio pie chart
        fig_ratio = px.pie(
            agri_df,
            values="Agricultural Ratio",
            names="Initiative",
            title="<b>Agricultural Focus Distribution</b>",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_ratio.update_layout(
            font=dict(family="Inter", size=12),
            title_font=dict(size=14, family="Inter", color="#1f2937"),
            legend_title_text="Initiative"
        )
        st.plotly_chart(fig_ratio, use_container_width=True, key=f"agri-pie-{hashlib.md5(str(fig_ratio).encode()).hexdigest()}")
    
    # Agricultural capabilities analysis
    st.markdown("##### 🌱 Agricultural Capabilities Summary")
    capabilities_summary = {}
    
    for _, row in agri_df.iterrows():
        caps = str(row['Capabilities']).lower()
        if 'crop' in caps:
            capabilities_summary['Crops'] = capabilities_summary.get('Crops', 0) + 1
        if 'pasture' in caps:
            capabilities_summary['Pasture'] = capabilities_summary.get('Pasture', 0) + 1
        if 'soybean' in caps:
            capabilities_summary['Soybean'] = capabilities_summary.get('Soybean', 0) + 1
        if 'corn' in caps or 'maize' in caps:
            capabilities_summary['Corn/Maize'] = capabilities_summary.get('Corn/Maize', 0) + 1
        if 'rice' in caps:
            capabilities_summary['Rice'] = capabilities_summary.get('Rice', 0) + 1
    
    if capabilities_summary:
        caps_df = pd.DataFrame(list(capabilities_summary.items()), columns=['Capability', 'Count'])
        fig_caps = px.bar(
            caps_df,
            x="Capability",
            y="Count",
            title="<b>Common Agricultural Capabilities</b>",
            color="Count",
            color_continuous_scale="YlOrRd"
        )
        fig_caps.update_layout(
            font=dict(family="Inter", size=12),
            title_font=dict(size=14, family="Inter", color="#1f2937")
        )
        st.plotly_chart(fig_caps, use_container_width=True, key=f"agri-caps-{hashlib.md5(str(fig_caps).encode()).hexdigest()}")


def render_comparative_charts(filtered_df: pd.DataFrame, metadata: dict) -> None:
    """Render comparative charts for class analysis."""
    
    # Prepare comparative data
    comp_data = []
    
    for idx, row in filtered_df.iterrows():
        initiative_name = row.get('Name', 'Unknown Initiative')
        display_name = row.get('Display_Name', row.get('Acronym', initiative_name))
        
        initiative_meta = metadata.get(initiative_name, {})
        total_classes = initiative_meta.get("number_of_classes", 0)
        agri_classes = initiative_meta.get("number_of_agriculture_classes", 0)
        non_agri_classes = total_classes - agri_classes if total_classes > agri_classes else 0
        
        comp_data.append({
            'Initiative': display_name,
            'Agricultural': agri_classes,
            'Non-Agricultural': non_agri_classes,
            'Total': total_classes
        })
    
    if not comp_data:
        st.info("No comparative data available.")
        return
    
    comp_df = pd.DataFrame(comp_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Triple bar chart (Agricultural vs Non-Agricultural vs Total)
        fig_triple = go.Figure()
        
        fig_triple.add_trace(go.Bar(
            name='Agricultural',
            x=comp_df['Initiative'],
            y=comp_df['Agricultural'],
            marker_color='#10b981'
        ))
        
        fig_triple.add_trace(go.Bar(
            name='Non-Agricultural',
            x=comp_df['Initiative'],
            y=comp_df['Non-Agricultural'],
            marker_color='#6b7280'
        ))
        
        fig_triple.add_trace(go.Bar(
            name='Total Classes',
            x=comp_df['Initiative'],
            y=comp_df['Total'],
            marker_color='#3b82f6',
            opacity=0.7
        ))
        
        fig_triple.update_layout(
            title="<b>Class Distribution Comparison</b>",
            xaxis_title="<b>Initiative</b>",
            yaxis_title="<b>Number of Classes</b>",
            barmode='group',
            font=dict(family="Inter", size=12),
            title_font=dict(size=14, family="Inter", color="#1f2937"),
            xaxis_tickangle=-45,
            legend_title_text="Class Type"
        )
        
        st.plotly_chart(fig_triple, use_container_width=True, key=f"comp-triple-{hashlib.md5(str(fig_triple).encode()).hexdigest()}")
    
    with col2:
        # Stacked bar chart
        fig_stacked = go.Figure()
        
        fig_stacked.add_trace(go.Bar(
            name='Agricultural',
            x=comp_df['Initiative'],
            y=comp_df['Agricultural'],
            marker_color='#10b981'
        ))
        
        fig_stacked.add_trace(go.Bar(
            name='Non-Agricultural',
            x=comp_df['Initiative'],
            y=comp_df['Non-Agricultural'],
            marker_color='#f59e0b'
        ))
        
        fig_stacked.update_layout(
            title="<b>Class Composition (Stacked)</b>",
            xaxis_title="<b>Initiative</b>",
            yaxis_title="<b>Number of Classes</b>",
            barmode='stack',
            font=dict(family="Inter", size=12),
            title_font=dict(size=14, family="Inter", color="#1f2937"),
            xaxis_tickangle=-45,
            legend_title_text="Class Type"
        )
        
        st.plotly_chart(fig_stacked, use_container_width=True, key=f"comp-stacked-{hashlib.md5(str(fig_stacked).encode()).hexdigest()}")
    
    # Class efficiency scatter plot
    if len(comp_df) > 1:
        fig_scatter = px.scatter(
            comp_df,
            x="Total",
            y="Agricultural",
            size="Agricultural",
            hover_name="Initiative",
            title="<b>Agriculture Classes versus Total Classes Relationship</b>",
            labels={"Total": "Total Classes", "Agricultural": "Agricultural Classes"},
            color="Agricultural",
            color_continuous_scale="RdYlGn"
        )
        fig_scatter.update_layout(
            font=dict(family="Inter", size=12),
            title_font=dict(size=14, family="Inter", color="#1f2937")
        )
        st.plotly_chart(fig_scatter, use_container_width=True, key=f"comp-scatter-{hashlib.md5(str(fig_scatter).encode()).hexdigest()}")
