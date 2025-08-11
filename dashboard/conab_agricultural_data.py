"""
Componente de Dashboard para Dados Agrícolas da CONAB
Integrado com o sistema de orcherstração do agricultural_analysis.py
"""

import streamlit as st

def render():
    """Renderiza dados específicos da CONAB"""
    
    st.markdown("### 📊 Dados Estimados CONAB")
    st.markdown("*Estimativas oficiais de produção, área e produtividade*")
    
    # Tentar carregar dados da CONAB
    data = load_conab_data()
    
    if not data:
        st.warning("⚠️ Dados da CONAB não disponíveis no momento")
        
        # Informações sobre a CONAB
        st.markdown("""
        ### 📈 Sobre a CONAB
        
        A **Companhia Nacional de Abastecimento (CONAB)** é uma empresa pública vinculada ao 
        Ministério da Agricultura, Pecuária e Abastecimento (MAPA) responsável por:
        
        - 🌾 **Levantamentos de Safras**: Estimativas mensais de produção, área e produtividade
        - 📊 **Acompanhamento de Mercado**: Preços, estoques e comercialização
        - 🗺️ **Mapeamentos Agrícolas**: Uso de sensoriamento remoto para monitoramento
        - 📋 **Política Agrícola**: Apoio às políticas públicas do setor
        
        ### 🎯 Principais Culturas Monitoradas
        
        - Soja, Milho (1ª e 2ª safra)
        - Algodão, Arroz, Feijão
        - Trigo, Sorgo, Girassol
        - Amendoim, Mamona, Canola
        
        ### 📅 Safras Acompanhadas
        
        - **Safra de Verão**: Outubro a Março
        - **Safra de Inverno**: Abril a Setembro
        - **Dados Históricos**: 2003 até presente
        
        **Fonte:** [CONAB - Séries Históricas](https://www.conab.gov.br/info-agro/safras/serie-historica-das-safras)
        """)
        
        return
    
    # Se tiver dados, renderizar visualizações
    render_conab_visualizations(data)


def load_conab_data():
    """Carrega dados agrícolas da CONAB"""
    try:
        import json
        import os
        
        data_path = os.path.join('data', 'conab_agricultural_data.json')
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return None
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados CONAB: {e}")
        return None


def render_conab_visualizations(data):
    """Renderiza visualizações dos dados CONAB"""
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        total_crops = len(data.get('crops', {}))
        latest_year = "2023/24"  # Safra mais recente
        
        with col1:
            st.metric("🌾 Culturas", total_crops)
        
        with col2:
            st.metric("📅 Safra Atual", latest_year)
        
        with col3:
            # Calcular produção total (simplificado)
            total_production = 0
            for crop_data in data.get('crops', {}).values():
                if latest_year in crop_data.get('production_data', {}):
                    total_production += crop_data['production_data'][latest_year].get('production', 0)
            
            st.metric("📈 Produção Total", f"{total_production/1000:.1f}M ton")
        
        with col4:
            # Calcular área total (simplificado)
            total_area = 0
            for crop_data in data.get('crops', {}).values():
                if latest_year in crop_data.get('production_data', {}):
                    total_area += crop_data['production_data'][latest_year].get('area', 0)
            
            st.metric("🗺️ Área Total", f"{total_area/1000:.1f}M ha")
    
    except Exception as e:
        st.warning(f"⚠️ Erro ao calcular métricas: {e}")
    
    st.divider()
    
    # Gráficos principais
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            fig_production = create_production_chart(data)
            if fig_production:
                st.plotly_chart(fig_production, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Gráfico de produção: {e}")
    
    with col2:
        try:
            fig_area = create_area_chart(data)
            if fig_area:
                st.plotly_chart(fig_area, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Gráfico de área: {e}")


def create_production_chart(data):
    """Cria gráfico de produção por cultura"""
    try:
        import plotly.express as px
        import pandas as pd
        
        # Dados da safra mais recente
        chart_data = []
        latest_year = "2023/24"
        
        for crop_key, crop_data in data.get('crops', {}).items():
            if latest_year in crop_data.get('production_data', {}):
                production_data = crop_data['production_data'][latest_year]
                chart_data.append({
                    'Cultura': crop_data.get('name', crop_key),
                    'Produção': production_data.get('production', 0) / 1000  # Converter para milhões
                })
        
        if not chart_data:
            return None
        
        df = pd.DataFrame(chart_data)
        df = df.sort_values('Produção', ascending=True)
        
        fig = px.bar(
            df,
            x='Produção',
            y='Cultura',
            orientation='h',
            title=f'Produção por Cultura - Safra {latest_year} (CONAB)',
            labels={'Produção': 'Produção (Milhões de t)', 'Cultura': 'Cultura'},
            color='Produção',
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(height=400)
        return fig
        
    except Exception as e:
        st.error(f"Erro no gráfico de produção: {e}")
        return None


def create_area_chart(data):
    """Cria gráfico de área plantada"""
    try:
        import plotly.express as px
        import pandas as pd
        
        # Dados da safra mais recente
        chart_data = []
        latest_year = "2023/24"
        
        for crop_key, crop_data in data.get('crops', {}).items():
            if latest_year in crop_data.get('production_data', {}):
                production_data = crop_data['production_data'][latest_year]
                chart_data.append({
                    'Cultura': crop_data.get('name', crop_key),
                    'Área': production_data.get('area', 0) / 1000  # Converter para milhões
                })
        
        if not chart_data:
            return None
        
        df = pd.DataFrame(chart_data)
        
        fig = px.pie(
            df,
            values='Área',
            names='Cultura',
            title=f'Distribuição de Área Plantada - Safra {latest_year} (CONAB)'
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig
        
    except Exception as e:
        st.error(f"Erro no gráfico de área: {e}")
        return None


if __name__ == "__main__":
    render()
