"""
Offline (Non-Streamlit) Temporal Chart Generation
==================================================

This module contains functions to generate temporal analysis charts 
(gaps, evolution line, evolution heatmap) without Streamlit dependencies,
suitable for batch processing or direct script execution.

Author: Dashboard Iniciativas LULC
Date: 2025
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import traceback

# Assuming chart_core.py is in the parent directory or accessible via PYTHONPATH
from ..chart_core import apply_standard_layout, get_initiative_color_map 
# If chart_core is in a different relative path, adjust the import accordingly.
# For example, if chart_core is in scripts.plotting.chart_core:
# from ...plotting.chart_core import apply_standard_layout, get_initiative_color_map


def create_timeline_chart_non_streamlit(temporal_data):
    """Create timeline chart without Streamlit UI dependencies. Uses English titles."""
    try:
        if temporal_data is None or temporal_data.empty:
            print("Error: Temporal data is empty or null for timeline chart.")
            return None
            
        gantt_data = []
        # Ensure 'Nome' column exists for color mapping, or adapt as needed
        if 'Nome' not in temporal_data.columns:
            print("Warning: 'Nome' column not found for color mapping in timeline chart. Using default colors.")
            # Fallback: create a dummy 'Nome' if it's critical for get_initiative_color_map
            # or modify get_initiative_color_map to handle 'Display_Name'
            # For now, we'll proceed, and colors might be default.
            # temporal_data['Nome'] = temporal_data['Display_Name'] 
            
        # Use Display_Name for color mapping if Nome is absent and it's preferred
        # This depends on how get_initiative_color_map is designed
        # For now, assuming get_initiative_color_map can handle missing 'Nome' or uses a fallback
        color_map_keys = temporal_data['Nome'] if 'Nome' in temporal_data.columns else temporal_data['Display_Name']
        color_map = get_initiative_color_map(color_map_keys.tolist())
        
        for idx, row in temporal_data.iterrows():
            # Determine key for color map
            color_key = row['Nome'] if 'Nome' in temporal_data.columns else row['Display_Name']
            
            gantt_data.append({
                'Task': row['Display_Name'],
                'FullName': row.get('Nome', row['Display_Name']), # Fallback for FullName
                'Start': f"{row['Primeiro_Ano']}-01-01",
                'Finish': f"{row['Ultimo_Ano']}-12-31",
                'Resource': row['Tipo'],
                'Description': f"{row['Display_Name']} ({row['Primeiro_Ano']}-{row['Ultimo_Ano']})",
                'Color': color_map.get(color_key, '#3B82F6') 
            })
        
        gantt_df = pd.DataFrame(gantt_data)
        fig = go.Figure()
        
        for idx, row in gantt_df.iterrows():
            fig.add_trace(go.Scatter(
                x=[row['Start'], row['Finish']],
                y=[row['Task'], row['Task']],
                mode='lines',
                line=dict(color=row['Color'], width=20),
                name=row['Task'],
                hovertemplate=f"<b>{row['Task']}</b><br>" +
                             f"Start: {row['Start'][:4]}<br>" +
                             f"End: {row['Finish'][:4]}<br>" +
                             f"Type: {row['Resource']}<extra></extra>",
                showlegend=False
            ))
        
        apply_standard_layout(fig, "LULC Initiatives Availability Timeline", "Year", "Initiatives", "timeline")
        
        fig.update_layout(
            height=max(600, len(temporal_data) * 30),
            xaxis=dict(tickmode='linear', dtick=2),
            yaxis=dict(
                categoryorder='array',
                categoryarray=temporal_data.sort_values('Primeiro_Ano')['Display_Name'].tolist()
            )
        )
        return fig
    except Exception as e:
        print(f"Error creating timeline chart (non-Streamlit): {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return None

def create_gaps_chart_non_streamlit(temporal_data):
    """Create a bar chart of temporal gaps for non-Streamlit (batch) use. Uses English titles."""
    try:
        if temporal_data is None or temporal_data.empty:
            print("Error: Temporal data is empty or null for gaps chart.")
            return None

        gaps_data = temporal_data[temporal_data['Anos_Faltando'] > 0].copy()

        if gaps_data.empty:
            print("No initiatives have significant temporal gaps. Skipping gaps chart generation.")
            return None

        fig_gaps = px.bar(
            gaps_data.sort_values('Anos_Faltando', ascending=True),
            x='Anos_Faltando',
            y='Display_Name',
            color='Maior_Lacuna',
            labels={'Anos_Faltando': 'Missing Years', 'Display_Name': 'Initiative', 'Maior_Lacuna': 'Largest Gap (Years)'},
            color_continuous_scale='Reds',
            orientation='h'
        )
        
        apply_standard_layout(fig_gaps, "Missing Years by Initiative", "Missing Years", "Initiative")
        fig_gaps.update_layout(
            yaxis={'categoryorder': 'total ascending'}, 
            height=max(400, len(gaps_data) * 25) # Dynamic height
        )
        
        return fig_gaps
    except Exception as e:
        print(f"Error creating gaps chart (non-Streamlit): {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return None

def create_evolution_charts_non_streamlit(temporal_data):
    """
    Create evolution line chart and heatmap for non-Streamlit (batch) use.
    Returns two figures: fig_evolution (line chart) and fig_heatmap_evolution (heatmap).
    Uses English titles.
    """
    try:
        if temporal_data is None or temporal_data.empty:
            print("Error: Temporal data is empty or null for evolution charts.")
            return None, None

        # 1. Line Chart: Evolution of number of initiatives
        all_years = []
        for _, row in temporal_data.iterrows():
            if isinstance(row['Anos_Lista'], list): # Ensure Anos_Lista is a list
                all_years.extend(row['Anos_Lista'])
        
        fig_evolution = None # Initialize
        if not all_years:
            print("Insufficient data for evolution line chart (all_years is empty).")
        else:
            year_counts = pd.Series(all_years).value_counts().sort_index()
            years_df = pd.DataFrame({
                'Year': year_counts.index,
                'Number_Initiatives': year_counts.values
            })

            fig_evolution = px.line(
                years_df,
                x='Year',
                y='Number_Initiatives',
                markers=True,
                labels={'Number_Initiatives': 'Number of Active Initiatives'}
            )
            fig_evolution.update_traces(line_color='#1f77b4', marker_size=8)
            apply_standard_layout(fig_evolution, "Number of Initiatives with Data by Year", "Year", "Number of Initiatives")

        # 2. Heatmap: Availability by Type and Year
        heatmap_data_evolution = []
        for _, row in temporal_data.iterrows():
            if isinstance(row['Anos_Lista'], list): # Ensure Anos_Lista is a list
                for ano in row['Anos_Lista']:
                    heatmap_data_evolution.append({
                        'Year': ano,
                        'Type': row['Tipo'],
                        'Initiative': row['Display_Name'] 
                    })
        
        fig_heatmap_evolution = None # Initialize
        if not heatmap_data_evolution:
            print("Insufficient data for evolution heatmap (heatmap_data_evolution is empty).")
        else:
            heatmap_df_evolution = pd.DataFrame(heatmap_data_evolution)
            pivot_df_evolution = heatmap_df_evolution.groupby(['Type', 'Year']).size().reset_index(name='Count')
            pivot_table_evolution = pivot_df_evolution.pivot(index='Type', columns='Year', values='Count').fillna(0)
            
            fig_heatmap_evolution = px.imshow(
                pivot_table_evolution,
                labels=dict(x="Year", y="Initiative Type", color="Number of Initiatives"),
                color_continuous_scale="Greens"
            )
            apply_standard_layout(fig_heatmap_evolution, "Heatmap of Initiative Availability by Type & Year", "Year", "Initiative Type")
            fig_heatmap_evolution.update_layout(height=max(400, len(pivot_table_evolution.index) * 40 if not pivot_table_evolution.empty else 400))

        return fig_evolution, fig_heatmap_evolution

    except Exception as e:
        print(f"Error creating evolution charts (non-Streamlit): {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return None, None

