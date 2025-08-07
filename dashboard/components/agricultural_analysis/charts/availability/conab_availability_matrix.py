"""
CONAB Availability Matrix Chart
==============================

Módulo para criação de matriz de disponibilidade de culturas CONAB.
Analisa safras simples e duplas por região.
"""

import pandas as pd
import plotly.express as px
import streamlit as st


def create_conab_availability_matrix(conab_data: dict):
    """
    Criar matriz de disponibilidade personalizada para dados CONAB.
    
    Parameters:
    -----------
    conab_data : dict
        Dados CONAB contendo informações de cobertura detalhada
        
    Returns:
    --------
    plotly.graph_objects.Figure or None
        Figura do heatmap de disponibilidade ou None se erro
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if not detailed_coverage:
            return None
        
        # Preparar dados para a matriz
        matrix_data = []
        
        for crop, crop_data in detailed_coverage.items():
            first_crop_years = crop_data.get('first_crop_years', {})
            second_crop_years = crop_data.get('second_crop_years', {})
            
            # Combinar todas as regiões
            all_regions = set(first_crop_years.keys()) | set(second_crop_years.keys())
            
            for region in all_regions:
                first_years = first_crop_years.get(region, [])
                second_years = second_crop_years.get(region, [])
                
                # Calcular disponibilidade
                has_first = len(first_years) > 0
                has_second = len(second_years) > 0
                
                availability_score = 0
                if has_first and has_second:
                    availability_score = 2  # Dupla safra
                elif has_first:
                    availability_score = 1  # Safra única
                
                matrix_data.append({
                    'crop': crop,
                    'region': region,
                    'availability': availability_score,
                    'years_coverage': len(set(first_years + second_years))
                })
        
        if not matrix_data:
            return None
        
        df_matrix = pd.DataFrame(matrix_data)
        
        # Criar pivot para heatmap
        pivot_matrix = df_matrix.pivot(index='crop', columns='region', values='availability')
        pivot_matrix = pivot_matrix.fillna(0)
        
        # Criar heatmap
        fig = px.imshow(
            pivot_matrix.values,
            x=pivot_matrix.columns,
            y=pivot_matrix.index,
            color_continuous_scale=['white', 'lightblue', 'darkblue'],
            title="Matriz de Disponibilidade CONAB (0=Sem dados, 1=Safra única, 2=Dupla safra)",
            labels={'x': 'Região', 'y': 'Cultura', 'color': 'Disponibilidade'}
        )
        
        fig.update_layout(
            height=max(400, len(pivot_matrix.index) * 30),
            xaxis_tickangle=45
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro criando matriz de disponibilidade: {e}")
        return None
