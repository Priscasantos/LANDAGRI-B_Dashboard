"""
Calendar Availability Analysis
=============================

Módulo para análise de disponibilidade baseada em dados de calendário agrícola.
Gera gráficos de score de disponibilidade por estado e cultura.
"""

import pandas as pd
import plotly.express as px
import streamlit as st


def render_calendar_availability_analysis(calendar_data: dict) -> None:
    """
    Renderizar análise de disponibilidade do calendário.
    
    Parameters:
    -----------
    calendar_data : dict
        Dados do calendário agrícola contendo informações de plantio e colheita
        
    Returns:
    --------
    None
        Renderiza diretamente no Streamlit
    """
    try:
        crop_calendar = calendar_data.get('crop_calendar', {})
        states_info = calendar_data.get('states', {})
        
        if not crop_calendar:
            st.info("📊 Nenhum dado de calendário disponível para análise de disponibilidade")
            return

        # Preparar dados de disponibilidade
        availability_data = []
        
        for crop, crop_states in crop_calendar.items():
            for state_entry in crop_states:
                state_code = state_entry.get('state_code', '')
                state_name = state_entry.get('state_name', state_code)
                calendar_entry = state_entry.get('calendar', {})
                
                # Contar meses com atividade
                active_months = sum(1 for activity in calendar_entry.values() if activity)
                planting_months = sum(1 for activity in calendar_entry.values() if 'P' in activity)
                harvest_months = sum(1 for activity in calendar_entry.values() if 'H' in activity)
                
                availability_data.append({
                    'crop': crop,
                    'state': state_name,
                    'state_code': state_code,
                    'active_months': active_months,
                    'planting_months': planting_months,
                    'harvest_months': harvest_months,
                    'availability_score': active_months / 12.0  # Normalizar para 0-1
                })

        if availability_data:
            df_availability = pd.DataFrame(availability_data)
            
            # Gráfico de disponibilidade por estado
            col1, col2 = st.columns(2)
            
            with col1:
                # Disponibilidade média por estado
                state_avg = df_availability.groupby('state')['availability_score'].mean().reset_index()
                state_avg = state_avg.sort_values('availability_score', ascending=False)
                
                fig_state = px.bar(
                    state_avg.head(15),
                    x='availability_score',
                    y='state',
                    orientation='h',
                    title="Score de Disponibilidade por Estado",
                    labels={'availability_score': 'Score de Disponibilidade', 'state': 'Estado'}
                )
                st.plotly_chart(fig_state, use_container_width=True)
            
            with col2:
                # Disponibilidade por cultura
                crop_avg = df_availability.groupby('crop')['availability_score'].mean().reset_index()
                crop_avg = crop_avg.sort_values('availability_score', ascending=False)
                
                fig_crop = px.bar(
                    crop_avg,
                    x='crop',
                    y='availability_score',
                    title="Score de Disponibilidade por Cultura",
                    labels={'availability_score': 'Score de Disponibilidade', 'crop': 'Cultura'}
                )
                fig_crop.update_layout(xaxis_tickangle=45)
                st.plotly_chart(fig_crop, use_container_width=True)

            # Tabela de resumo
            st.markdown("##### 📋 Resumo da Disponibilidade")
            summary_stats = df_availability.groupby('crop').agg({
                'state': 'count',
                'active_months': 'mean',
                'availability_score': 'mean'
            }).round(2)
            summary_stats.columns = ['Estados Cobertos', 'Meses Ativos (Média)', 'Score Disponibilidade']
            st.dataframe(summary_stats, use_container_width=True)

    except Exception as e:
        st.error(f"Erro na análise de disponibilidade do calendário: {e}")
