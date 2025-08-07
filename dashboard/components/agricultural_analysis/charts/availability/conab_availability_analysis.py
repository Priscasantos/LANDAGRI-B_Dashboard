"""
CONAB Availability Analysis
==========================

Módulo para análise de disponibilidade de dados CONAB.
Inclui análise de dupla safra e matriz de disponibilidade.
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from .conab_availability_matrix import create_conab_availability_matrix


def render_conab_availability_analysis(conab_data: dict) -> None:
    """
    Renderizar análise de disponibilidade CONAB.
    
    Parameters:
    -----------
    conab_data : dict
        Dados CONAB contendo informações de cobertura detalhada
        
    Returns:
    --------
    None
        Renderiza diretamente no Streamlit
    """
    try:
        initiative = conab_data.get('CONAB Crop Monitoring Initiative', {})
        detailed_coverage = initiative.get('detailed_crop_coverage', {})
        
        if not detailed_coverage:
            st.info("📊 Nenhum dado CONAB disponível para análise de disponibilidade")
            return

        # Análise de matriz de disponibilidade
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🗺️ Matriz de Disponibilidade")
            try:
                # Criar matriz de disponibilidade personalizada
                fig_matrix = create_conab_availability_matrix(conab_data)
                if fig_matrix:
                    st.plotly_chart(fig_matrix, use_container_width=True)
            except Exception as e:
                st.error(f"Erro criando matriz de disponibilidade: {e}")
        
        with col2:
            st.markdown("##### 🔄 Análise de Dupla Safra")
            
            # Análise de dupla safra
            double_crop_data = []
            
            for crop, crop_data in detailed_coverage.items():
                first_crop_years = crop_data.get('first_crop_years', {})
                second_crop_years = crop_data.get('second_crop_years', {})
                
                first_regions = len([r for r, years in first_crop_years.items() if years])
                second_regions = len([r for r, years in second_crop_years.items() if years])
                
                double_crop_data.append({
                    'crop': crop,
                    'single_crop': first_regions - second_regions if first_regions > second_regions else 0,
                    'double_crop': second_regions
                })
            
            if double_crop_data:
                df_double = pd.DataFrame(double_crop_data)
                
                fig_double = px.bar(
                    df_double,
                    x='crop',
                    y=['single_crop', 'double_crop'],
                    title="Regiões com Safra Única vs Dupla Safra",
                    barmode='stack',
                    labels={
                        'value': 'Número de Regiões',
                        'crop': 'Cultura',
                        'variable': 'Tipo de Safra'
                    }
                )
                fig_double.update_layout(xaxis_tickangle=45)
                st.plotly_chart(fig_double, use_container_width=True)

    except Exception as e:
        st.error(f"Erro na análise de disponibilidade CONAB: {e}")
