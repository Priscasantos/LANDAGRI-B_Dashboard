import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import numpy as np
import warnings
import os

# Set environment variable to disable PyArrow optimization
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

# Suppress warnings to clean up output
warnings.filterwarnings('ignore')

# Configure pandas to avoid PyArrow issues
pd.set_option('mode.copy_on_write', True)

# Set pandas display options to avoid potential PyArrow conversion
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Configuração da página
st.set_page_config(
    page_title="Comparador de Iniciativas LULC", 
    layout="wide", 
    page_icon="🌍",
    initial_sidebar_state="expanded"
)

# Clear Streamlit cache to resolve PyArrow serialization issues
if st.sidebar.button("🔄 Limpar Cache", help="Clique se houver problemas de carregamento"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

# Function to convert DataFrame to safe format for Streamlit display
def safe_dataframe_display(df):
    """Convert DataFrame to a format that bypasses PyArrow serialization issues"""
    # Convert DataFrame to HTML table to completely bypass PyArrow
    html_table = df.to_html(classes='streamlit-table', escape=False, index=False)
    return html_table

# Function to convert DataFrame to dictionary format for Plotly
def df_to_dict_safe(df):
    """Convert DataFrame to dictionary format safe for Plotly operations"""
    result = {}
    for col in df.columns:
        if df[col].dtype == 'object':
            result[col] = df[col].astype(str).fillna('').tolist()
        elif df[col].dtype in ['float64', 'int64']:
            result[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).tolist()
        else:
            result[col] = df[col].astype(str).tolist()
    return result

# Function to prepare data for visualization without PyArrow issues
def prepare_plot_data(df):
    """Prepare DataFrame for plotting by converting to native Python types"""
    plot_data = {}
    for col in df.columns:
        if df[col].dtype == 'object':
            plot_data[col] = df[col].astype(str).fillna('N/A').tolist()
        elif df[col].dtype in ['float64', 'int64']:
            plot_data[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).tolist()
        else:
            plot_data[col] = df[col].astype(str).tolist()
    
    # Create a new DataFrame from the safe data
    return pd.DataFrame(plot_data)

# Função para carregar dados
@st.cache_data
def load_data():
    try:
        # Clear any potential cache conflicts
        pd.set_option('mode.copy_on_write', True)
        
        # Define explicit data types to prevent PyArrow conversion issues
        dtype_dict = {
            'Nome': 'str',
            'Tipo': 'str', 
            'Resolução (m)': 'float64',
            'Acurácia (%)': 'float64',
            'Classes': 'float64',
            'Metodologia': 'str',
            'Frequência Temporal': 'str',
            'Anos Disponíveis': 'str',
            'Escopo': 'str',
            'Score Resolução': 'float64',
            'Score Geral': 'float64',
            'Categoria Acurácia': 'str',
            'Categoria Resolução': 'str'
        }
        
        df = pd.read_csv('initiatives_comparison.csv', dtype=dtype_dict)
        
        # Prepare the dataframe for safe display
        df = prepare_plot_data(df)
        
        with open('initiatives_metadata.json', 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        return df, metadata
    except FileNotFoundError as e:
        st.error(f"Arquivo não encontrado: {e}")
        st.stop()

# Carregar dados
df, metadata = load_data()

# CSS customizado para fontes e layout
st.markdown("""
<style>
    /* Fontes principais */
    .main .block-container {
        font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        font-size: 16px;
        line-height: 1.6;
    }
    
    /* Títulos */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        font-weight: 600;
        color: #1f2937;
    }
    
    /* Cards de métricas */
    .metric-card {
        background-color: #f8fafc;
        padding: 1.2rem;
        border-radius: 0.75rem;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    /* Selectboxes */
    .stSelectbox > div > div {
        background-color: #ffffff;
        border-radius: 0.5rem;
        font-size: 15px;
    }
    
    /* Gráficos */
    .plotly-chart {
        font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
    }
    
    /* Informações destacadas */
    .stInfo {
        font-size: 15px;
        font-weight: 500;
    }
    
    /* Timeline customizada */
    .timeline-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        margin: 1rem 0;
    }
    
    .timeline-title {
        font-size: 24px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1.5rem;
        color: white;
    }
    
    /* HTML table styling for safe DataFrame display */
    .streamlit-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-radius: 8px;
        overflow: hidden;
    }
    
    .streamlit-table thead tr {
        background-color: #3b82f6;
        color: white;
        text-align: left;
        font-weight: 600;
    }
    
    .streamlit-table th,
    .streamlit-table td {
        padding: 12px 15px;
        border-bottom: 1px solid #ddd;
    }
    
    .streamlit-table tbody tr:nth-of-type(even) {
        background-color: #f8fafc;
    }
    
    .streamlit-table tbody tr:hover {
        background-color: #e1f5fe;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.title("🌍 Análise Comparativa de Iniciativas de Mapeamento LULC")
st.markdown("""
<div style='background-color: #e8f4fd; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;'>
<h4>🎯 Objetivo</h4>
<p>Explore e compare as principais características das iniciativas globais e brasileiras de mapeamento de cobertura e uso da terra (Land Use Land Cover - LULC).</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros de Análise")
st.sidebar.markdown("---")

# Filtro por tipo
selected_types = st.sidebar.multiselect(
    "📍 Tipo de Iniciativa:",
    options=df['Tipo'].unique(),
    default=df['Tipo'].unique(),
    help="Selecione os tipos de iniciativas para comparar"
)

# Filtro por resolução
min_res, max_res = int(df['Resolução (m)'].min()), int(df['Resolução (m)'].max())
selected_res = st.sidebar.slider(
    "🔬 Resolução Espacial (metros):",
    min_value=min_res,
    max_value=max_res,
    value=(min_res, max_res),
    help="Filtre por intervalo de resolução espacial"
)

# Filtro por acurácia
min_acc, max_acc = int(df['Acurácia (%)'].min()), int(df['Acurácia (%)'].max())
selected_acc = st.sidebar.slider(
    "🎯 Acurácia (%):",
    min_value=min_acc,
    max_value=max_acc,
    value=(min_acc, max_acc),
    help="Filtre por intervalo de acurácia"
)

# Filtro por metodologia
selected_methods = st.sidebar.multiselect(
    "⚙️ Metodologia:",
    options=df['Metodologia'].unique(),
    default=df['Metodologia'].unique(),
    help="Selecione as metodologias de interesse"
)

# Aplicar filtros
filtered_df = df[
    (df['Tipo'].isin(selected_types)) &
    (df['Resolução (m)'].between(selected_res[0], selected_res[1])) &
    (df['Acurácia (%)'].between(selected_acc[0], selected_acc[1])) &
    (df['Metodologia'].isin(selected_methods))
]

# Prepare the filtered dataframe for safe display
filtered_df = prepare_plot_data(filtered_df)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**📊 Iniciativas selecionadas:** {len(filtered_df)}/{len(df)}")

# Verificar se há dados filtrados
if filtered_df.empty:
    st.warning("⚠️ Nenhuma iniciativa corresponde aos filtros selecionados. Ajuste os filtros para visualizar os dados.")
    st.stop()

# Seção 1: Métricas Principais
st.header("📈 Métricas Principais")
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_accuracy = filtered_df['Acurácia (%)'].mean()
    st.metric("🎯 Acurácia Média", f"{avg_accuracy:.1f}%")

with col2:
    avg_resolution = filtered_df['Resolução (m)'].mean()
    st.metric("🔬 Resolução Média", f"{avg_resolution:.0f}m")

with col3:
    total_classes = filtered_df['Classes'].sum()
    st.metric("🏷️ Total de Classes", f"{total_classes}")

with col4:
    global_initiatives = len(filtered_df[filtered_df['Tipo'] == 'Global'])
    st.metric("🌍 Iniciativas Globais", f"{global_initiatives}")

st.markdown("---")

# Seção 2: Gráficos Comparativos
st.header("📊 Análises Comparativas")

# Aba para diferentes visualizações
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Resolução vs Acurácia", "📅 Cobertura Temporal", "🏷️ Número de Classes", "⚙️ Metodologias"])

with tab1:
    st.subheader("Resolução Espacial vs Acurácia")

    fig = px.scatter(
        filtered_df,
        x='Resolução (m)',
        y='Acurácia (%)',
        color='Tipo',
        size='Classes',
        hover_name='Nome',
        hover_data=['Metodologia', 'Frequência Temporal'],
        log_x=True,
        labels={
            'Resolução (m)': 'Resolução Espacial (m) - Escala Log',
            'Acurácia (%)': 'Acurácia (%)'
        },
        title="Relação entre Resolução Espacial e Acurácia das Iniciativas",
        height=600,
        color_discrete_map={'Global': '#ff6b6b', 'Nacional': '#4dabf7', 'Regional': '#51cf66'}
    )

    fig.update_layout(
        font=dict(size=12),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Insights automáticos
    best_accuracy = filtered_df.loc[filtered_df['Acurácia (%)'].idxmax()]
    best_resolution = filtered_df.loc[filtered_df['Resolução (m)'].idxmin()]

    col1, col2 = st.columns(2)
    with col1:
        st.info(f"🏆 **Maior Acurácia:** {best_accuracy['Nome']} ({best_accuracy['Acurácia (%)']}%)")
    with col2:
        st.info(f"🔍 **Melhor Resolução:** {best_resolution['Nome']} ({best_resolution['Resolução (m)']}m)")

with tab2:
    st.markdown('<div class="timeline-container"><h2 class="timeline-title">📅 Análise Temporal das Iniciativas</h2></div>', unsafe_allow_html=True)

    # Processar dados temporais
    temporal_data = []
    yearly_availability = {}
    
    for _, row in filtered_df.iterrows():
        years = row['Anos Disponíveis']
        if '-' in years:
            start, end = years.split('-')
            start_year = int(start)
            end_year = int(end) if end.isdigit() else 2024
        else:
            start_year = end_year = int(years)

        temporal_data.append({
            'Nome': row['Nome'],
            'Início': start_year,
            'Fim': end_year,
            'Tipo': row['Tipo'],
            'Duração': end_year - start_year + 1,
            'Resolução': row['Resolução (m)'],
            'Acurácia': row['Acurácia (%)']
        })
        
        # Contar disponibilidade por ano
        for year in range(start_year, end_year + 1):
            if year not in yearly_availability:
                yearly_availability[year] = 0
            yearly_availability[year] += 1

    temporal_df = pd.DataFrame(temporal_data)

    # --- NOVA TIMELINE USANDO ANOS DISPONÍVEIS DO METADATA ---
    # Carregar anos_disponiveis do metadata
    blocos = []
    for nome, meta in metadata.items():
        if 'anos_disponiveis' in meta:
            anos = sorted(meta['anos_disponiveis'])
            tipo = filtered_df[filtered_df['Nome'] == nome]['Tipo'].iloc[0] if nome in filtered_df['Nome'].values else None
            if not tipo:
                continue
            # Agrupa blocos contínuos
            if anos:
                bloco_inicio = anos[0]
                bloco_fim = anos[0]
                for i in range(1, len(anos)):
                    if anos[i] == bloco_fim + 1:
                        bloco_fim = anos[i]
                    else:
                        blocos.append({'Nome': nome, 'Ano Início': bloco_inicio, 'Ano Fim': bloco_fim, 'Tipo': tipo})
                        bloco_inicio = anos[i]
                        bloco_fim = anos[i]
                blocos.append({'Nome': nome, 'Ano Início': bloco_inicio, 'Ano Fim': bloco_fim, 'Tipo': tipo})
    blocos_df = pd.DataFrame(blocos)
    if not blocos_df.empty:
        min_year = blocos_df['Ano Início'].min()
        max_year = blocos_df['Ano Fim'].max()
        # Escala fixa anual
        fig = px.timeline(
            blocos_df,
            x_start="Ano Início",
            x_end="Ano Fim",
            y="Nome",
            color="Tipo",
            color_discrete_map={
                'Global': '#00BFFF',
                'Nacional': '#FFD700',
                'Regional': '#FF69B4'
            },
            title="📊 Timeline Comparativa das Iniciativas LULC - Períodos de Disponibilidade",
            height=max(600, len(blocos_df['Nome'].unique()) * 35)
        )
        fig.update_layout(
            font=dict(size=13, color="#F3F4F6", family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
            xaxis_title="Ano",
            yaxis_title="Iniciativa",
            title_font_size=16,
            plot_bgcolor="#18181b",
            paper_bgcolor="#18181b",
            margin=dict(l=200, r=50, t=80, b=50),
            xaxis=dict(
                gridcolor="#444",
                gridwidth=1,
                showgrid=True,
                range=[min_year-0.5, max_year+0.5],
                dtick=1,
                tickmode='linear',
                tick0=min_year,
                color="#F3F4F6",
                tickformat='d'
            ),
            yaxis=dict(
                gridcolor="#444",
                gridwidth=1,
                showgrid=True,
                color="#F3F4F6"
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(color="#F3F4F6")
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning('Nenhuma iniciativa com anos_disponiveis encontrada para o filtro atual.')

with tab3:
    st.subheader("Distribuição do Número de Classes")

    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de barras
        fig_bar = px.bar(
            filtered_df.sort_values('Classes', ascending=True),
            x='Classes',
            y='Nome',
            color='Tipo',
            orientation='h',
            title="Número de Classes por Iniciativa",
            height=500,
            color_discrete_map={'Global': '#ff6b6b', 'Nacional': '#4dabf7', 'Regional': '#51cf66'}
        )
        fig_bar.update_layout(
            font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        # Histograma
        fig_hist = px.histogram(
            filtered_df,
            x='Classes',
            color='Tipo',
            title="Distribuição do Número de Classes",
            nbins=10,
            height=500,
            color_discrete_map={'Global': '#ff6b6b', 'Nacional': '#4dabf7', 'Regional': '#51cf66'}
        )
        fig_hist.update_layout(
            font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_hist, use_container_width=True)

with tab4:
    st.subheader("Distribuição por Metodologias")

    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de pizza das metodologias
        method_counts = filtered_df['Metodologia'].value_counts()
        fig_pie = px.pie(
            values=method_counts.values,
            names=method_counts.index,
            title="Distribuição das Metodologias Utilizadas",
            height=400
        )
        fig_pie.update_layout(
            font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Acurácia por metodologia
        fig_box = px.box(
            filtered_df,
            x='Metodologia',
            y='Acurácia (%)',
            color='Tipo',
            title="Acurácia por Metodologia",
            height=400,
            color_discrete_map={'Global': '#ff6b6b', 'Nacional': '#4dabf7', 'Regional': '#51cf66'}
        )
        fig_box.update_xaxes(tickangle=45)
        fig_box.update_layout(
            font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_box, use_container_width=True)

st.markdown("---")

# Seção 3: Heatmap de Características
st.header("🌡️ Matriz de Comparação Técnica")

# Preparar dados para heatmap
features = ['Resolução (m)', 'Acurácia (%)', 'Classes']
heatmap_data = filtered_df[features + ['Nome']].set_index('Nome')

# Normalizar dados para melhor visualização
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
heatmap_normalized = pd.DataFrame(
    scaler.fit_transform(heatmap_data),
    columns=heatmap_data.columns,
    index=heatmap_data.index
)

fig_heatmap = px.imshow(
    heatmap_normalized.T,
    labels=dict(x="Iniciativa", y="Característica", color="Valor Normalizado"),
    x=heatmap_normalized.index,
    y=heatmap_normalized.columns,
    aspect="auto",
    color_continuous_scale='Viridis',
    title="Heatmap de Características Técnicas (Valores Normalizados)",
    height=400
)

fig_heatmap.update_xaxes(tickangle=45)
fig_heatmap.update_layout(
    font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")

# Seção 4: Detalhes da Iniciativa Selecionada
st.header("🔍 Exploração Detalhada")

selected_initiative = st.selectbox(
    "Selecione uma iniciativa para ver detalhes:",
    options=filtered_df['Nome'].tolist(),
    help="Escolha uma iniciativa para ver informações detalhadas"
)

if selected_initiative:
    # Dados da iniciativa selecionada
    init_data = filtered_df[filtered_df['Nome'] == selected_initiative].iloc[0]
    init_metadata = metadata[selected_initiative]

    # Layout em colunas
    col1, col2 = st.columns([2, 3])

    with col1:
        st.markdown(f"### {selected_initiative}")

        # Métricas principais
        st.markdown("#### 📊 Métricas Principais")
        metrics_col1, metrics_col2 = st.columns(2)

        with metrics_col1:
            st.metric("🎯 Acurácia", f"{init_data['Acurácia (%)']}%")
            st.metric("🏷️ Classes", init_data['Classes'])

        with metrics_col2:
            st.metric("🔬 Resolução", f"{init_data['Resolução (m)']}m")
            st.metric("📅 Frequência", init_data['Frequência Temporal'])

        # Informações técnicas
        st.markdown("#### ⚙️ Informações Técnicas")
        st.info(f"**Tipo:** {init_data['Tipo']}")
        st.info(f"**Metodologia:** {init_data['Metodologia']}")
        st.info(f"**Escopo:** {init_data['Escopo']}")
        st.info(f"**Período:** {init_data['Anos Disponíveis']}")

    with col2:
        st.markdown("#### 📋 Detalhes Metodológicos")

        st.markdown("**🔬 Metodologia:**")
        st.write(init_metadata['metodologia'])

        st.markdown("**✅ Validação:**")
        st.success(init_metadata['validacao'])

        st.markdown("**🌍 Cobertura:**")
        st.warning(init_metadata['cobertura'])

        st.markdown("**📡 Fontes de Dados:**")
        st.info(init_metadata['fonte_dados'])

st.markdown("---")

# Seção 5: Comparação Direta
st.header("⚖️ Comparação Direta Entre Iniciativas")

col1, col2 = st.columns(2)

with col1:
    init1 = st.selectbox(
        "Primeira iniciativa:",
        options=filtered_df['Nome'].tolist(),
        key="comparison1"
    )

with col2:
    init2 = st.selectbox(
        "Segunda iniciativa:",
        options=filtered_df['Nome'].tolist(),
        index=1 if len(filtered_df) > 1 else 0,
        key="comparison2"
    )

if init1 and init2 and init1 != init2:
    # Obter dados das duas iniciativas
    data1 = filtered_df[filtered_df['Nome'] == init1].iloc[0]
    data2 = filtered_df[filtered_df['Nome'] == init2].iloc[0]

    # Comparação em gráfico radar
    categories = ['Acurácia (%)', 'Resolução (m)', 'Classes']

    # Normalizar valores para o radar (invertendo resolução para que menor seja melhor)
    def normalize_for_radar(value, column, df):
        if column == 'Resolução (m)':
            # Para resolução, menor é melhor, então invertemos
            return (df[column].max() - value) / (df[column].max() - df[column].min()) * 100
        else:
            return (value - df[column].min()) / (df[column].max() - df[column].min()) * 100

    values1 = [normalize_for_radar(data1[cat], cat, filtered_df) for cat in categories]
    values2 = [normalize_for_radar(data2[cat], cat, filtered_df) for cat in categories]

    fig_radar = go.Figure()

    fig_radar.add_trace(go.Scatterpolar(
        r=values1 + [values1[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=init1,
        line_color='#ff6b6b'
    ))

    fig_radar.add_trace(go.Scatterpolar(
        r=values2 + [values2[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=init2,
        line_color='#4dabf7'
    ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Comparação em Gráfico Radar (Valores Normalizados)",
        height=500,
        font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig_radar, use_container_width=True)

    # Tabela comparativa
    st.markdown("#### 📋 Tabela Comparativa Detalhada")

    comparison_data = {
        'Característica': [
            'Acurácia (%)', 'Resolução (m)', 'Classes', 'Frequência', 
            'Metodologia', 'Escopo', 'Período'
        ],
        init1: [
            data1['Acurácia (%)'], data1['Resolução (m)'], data1['Classes'],
            data1['Frequência Temporal'], data1['Metodologia'], 
            data1['Escopo'], data1['Anos Disponíveis']
        ],
        init2: [
            data2['Acurácia (%)'], data2['Resolução (m)'], data2['Classes'],
            data2['Frequência Temporal'], data2['Metodologia'], 
            data2['Escopo'], data2['Anos Disponíveis']
        ]
    }

    comparison_df = pd.DataFrame(comparison_data)
    # Use safe HTML display to avoid PyArrow serialization issues
    st.markdown("### Comparação das Iniciativas Selecionadas")
    st.markdown(safe_dataframe_display(comparison_df), unsafe_allow_html=True)

# --- MELHORIA DE LEGENDA E SEÇÕES EM TEMA ESCURO ---
st.markdown("""
<style>
    .block-container { background: #18181b !important; }
    h1, h2, h3, h4, h5, h6 { color: #F3F4F6 !important; }
    .stTabs [data-baseweb="tab"] { background: #23232a !important; color: #F3F4F6 !important; }
    .stTabs [data-baseweb="tab"]:hover { background: #33334a !important; }
    .stTabs [aria-selected="true"] { background: #33334a !important; color: #FFD700 !important; }
    .stMetric, .stInfo, .stWarning, .stSuccess { color: #F3F4F6 !important; }
    .stSidebar { background: #23232a !important; color: #F3F4F6 !important; }
    .stButton>button { background: #23232a !important; color: #FFD700 !important; }
    .stSelectbox>div>div { background: #23232a !important; color: #F3F4F6 !important; }
    .streamlit-table thead tr { background-color: #23232a !important; color: #FFD700 !important; }
    .streamlit-table tbody tr { background-color: #23232a !important; color: #F3F4F6 !important; }
    .streamlit-table tbody tr:nth-of-type(even) { background-color: #18181b !important; }
</style>
""", unsafe_allow_html=True)

# --- SUGESTÕES DE NOVAS FUNCIONALIDADES ---
st.markdown("""
### 💡 Sugestões de novas funcionalidades:
- **Download dos gráficos e tabelas** em PNG, SVG ou CSV.
- **Comparação multi-iniciativas**: selecione mais de duas para radar ou tabela.
- **Filtro por região geográfica** (ex: estados, biomas, países).
- **Mapa interativo** mostrando a área de cobertura de cada iniciativa.
- **Exportação de relatório customizado** em PDF.
- **Integração com APIs externas** para atualização automática dos dados.
- **Análise temporal animada** (slider de ano para ver evolução).
- **Dashboard responsivo para mobile**.
- **Sugestão automática de iniciativas similares**.
""")
