import streamlit as st
import warnings
import os
from data import load_data, prepare_plot_data, safe_dataframe_display
from plots import (
    plot_timeline,
    plot_ano_overlap,
    plot_heatmap,
    gap_analysis,
    plot_resolucao_acuracia,
    plot_classes_por_iniciativa,
    plot_distribuicao_classes,
    plot_distribuicao_metodologias,
    plot_acuracia_por_metodologia,
    plot_heatmap_tecnico,
    plot_radar_comparacao,
)

# Set environment variable to disable PyArrow optimization
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

# Suppress warnings to clean up output
warnings.filterwarnings("ignore")

# Configuração da página
st.set_page_config(
    page_title="Comparador de Iniciativas LULC",
    layout="wide",
    page_icon="🌍",
    initial_sidebar_state="expanded",
)

if st.sidebar.button("🔄 Limpar Cache", help="Clique se houver problemas de carregamento"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

# Carregar dados
csv_path = "initiatives_comparison.csv"
json_path = "initiatives_metadata.json"
df, metadata = load_data(csv_path, json_path)

df = prepare_plot_data(df)

# CSS customizado para fontes e layout
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# Título principal
st.title("🌍 Análise Comparativa de Iniciativas de Mapeamento LULC")
st.markdown(
    """
<div style='background-color: #e8f4fd; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;'>
<h4>🎯 Objetivo</h4>
<p>Explore e compare as principais características das iniciativas globais e brasileiras de mapeamento de cobertura e uso da terra (Land Use Land Cover - LULC).</p>
</div>
""",
    unsafe_allow_html=True,
)

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros de Análise")
st.sidebar.markdown("---")

# Filtro por tipo
selected_types = st.sidebar.multiselect(
    "📍 Tipo de Iniciativa:",
    options=df["Tipo"].unique(),
    default=df["Tipo"].unique(),
    help="Selecione os tipos de iniciativas para comparar",
)

# Filtro por resolução
min_res, max_res = int(df["Resolução (m)"].min()), int(df["Resolução (m)"].max())
selected_res = st.sidebar.slider(
    "🔬 Resolução Espacial (metros):",
    min_value=min_res,
    max_value=max_res,
    value=(min_res, max_res),
    help="Filtre por intervalo de resolução espacial",
)

# Filtro por acurácia
min_acc, max_acc = int(df["Acurácia (%)"].min()), int(df["Acurácia (%)"].max())
selected_acc = st.sidebar.slider(
    "🎯 Acurácia (%):",
    min_value=min_acc,
    max_value=max_acc,
    value=(min_acc, max_acc),
    help="Filtre por intervalo de acurácia",
)

# Filtro por metodologia
selected_methods = st.sidebar.multiselect(
    "⚙️ Metodologia:",
    options=df["Metodologia"].unique(),
    default=df["Metodologia"].unique(),
    help="Selecione as metodologias de interesse",
)

# Aplicar filtros
filtered_df = df[
    (df["Tipo"].isin(selected_types))
    & (df["Resolução (m)"].between(selected_res[0], selected_res[1]))
    & (df["Acurácia (%)"].between(selected_acc[0], selected_acc[1]))
    & (df["Metodologia"].isin(selected_methods))
]

# Prepare the filtered dataframe for safe display
filtered_df = prepare_plot_data(filtered_df)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**📊 Iniciativas selecionadas:** {len(filtered_df)}/{len(df)}")

# Verificar se há dados filtrados
if filtered_df.empty:
    st.warning(
        "⚠️ Nenhuma iniciativa corresponde aos filtros selecionados. Ajuste os filtros para visualizar os dados."
    )
    st.stop()

# Seção 1: Métricas Principais
st.header("📈 Métricas Principais")
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_accuracy = filtered_df["Acurácia (%)"].mean()
    st.metric("🎯 Acurácia Média", f"{avg_accuracy:.1f}%")

with col2:
    avg_resolution = filtered_df["Resolução (m)"].mean()
    st.metric("🔬 Resolução Média", f"{avg_resolution:.0f}m")

with col3:
    total_classes = filtered_df["Classes"].sum()
    st.metric("🏷️ Total de Classes", f"{total_classes}")

with col4:
    global_initiatives = len(filtered_df[filtered_df["Tipo"] == "Global"])
    st.metric("🌍 Iniciativas Globais", f"{global_initiatives}")

st.markdown("---")

# Seção 2: Gráficos Comparativos
st.header("📊 Análises Comparativas")

# Aba para diferentes visualizações
tab1, tab2, tab3, tab4 = st.tabs(
    ["🎯 Resolução vs Acurácia", "📅 Cobertura Temporal", "🏷️ Número de Classes", "⚙️ Metodologias"]
)

with tab1:
    st.subheader("Resolução Espacial vs Acurácia")
    fig = plot_resolucao_acuracia(filtered_df)
    st.plotly_chart(fig, use_container_width=True)
    best_accuracy = filtered_df.loc[filtered_df["Acurácia (%)"].idxmax()]
    best_resolution = filtered_df.loc[filtered_df["Resolução (m)"].idxmin()]
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"🏆 **Maior Acurácia:** {best_accuracy['Nome']} ({best_accuracy['Acurácia (%)']}%)")
    with col2:
        st.info(f"🔍 **Melhor Resolução:** {best_resolution['Nome']} ({best_resolution['Resolução (m)']}m)")

with tab2:
    st.markdown('<div class="timeline-container"><h2 class="timeline-title">📅 Análise Temporal das Iniciativas</h2></div>', unsafe_allow_html=True)
    fig = plot_timeline(metadata, df)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('---')
    st.header('🆚 Comparação Temporal Avançada')
    fig_count = plot_ano_overlap(metadata, df)
    st.plotly_chart(fig_count, use_container_width=True)
    fig_heat = plot_heatmap(metadata, df)
    st.plotly_chart(fig_heat, use_container_width=True)
    gap_df = gap_analysis(metadata, df)
    if not gap_df.empty:
        st.markdown('#### Lacunas Temporais nas Séries')
        st.markdown(safe_dataframe_display(gap_df.sort_values('Maior Lacuna (anos)', ascending=False)), unsafe_allow_html=True)
    else:
        st.info('Todas as iniciativas possuem séries temporais contínuas ou apenas um ano disponível.')

with tab3:
    st.subheader("Distribuição do Número de Classes")
    col1, col2 = st.columns(2)
    with col1:
        fig_bar = plot_classes_por_iniciativa(filtered_df)
        st.plotly_chart(fig_bar, use_container_width=True)
    with col2:
        fig_hist = plot_distribuicao_classes(filtered_df)
        st.plotly_chart(fig_hist, use_container_width=True)

with tab4:
    st.subheader("Distribuição por Metodologias")
    col1, col2 = st.columns(2)
    with col1:
        method_counts = filtered_df["Metodologia"].value_counts()
        fig_pie = plot_distribuicao_metodologias(method_counts)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        fig_box = plot_acuracia_por_metodologia(filtered_df)
        st.plotly_chart(fig_box, use_container_width=True)

st.markdown("---")

# Seção 3: Heatmap de Características
st.header("🌡️ Matriz de Comparação Técnica")
fig_heatmap = plot_heatmap_tecnico(filtered_df)
st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")

# Seção 4: Detalhes da Iniciativa Selecionada
st.header("🔍 Exploração Detalhada")

selected_initiative = st.selectbox(
    "Selecione uma iniciativa para ver detalhes:",
    options=filtered_df["Nome"].tolist(),
    help="Escolha uma iniciativa para ver informações detalhadas",
)

if selected_initiative:
    # Dados da iniciativa selecionada
    init_data = filtered_df[filtered_df["Nome"] == selected_initiative].iloc[0]
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
            st.metric("🏷️ Classes", init_data["Classes"])

        with metrics_col2:
            st.metric("🔬 Resolução", f"{init_data['Resolução (m)']}m")
            st.metric("📅 Frequência", init_data["Frequência Temporal"])

        # Informações técnicas
        st.markdown("#### ⚙️ Informações Técnicas")
        st.info(f"**Tipo:** {init_data['Tipo']}")
        st.info(f"**Metodologia:** {init_data['Metodologia']}")
        st.info(f"**Escopo:** {init_data['Escopo']}")
        st.info(f"**Período:** {init_data['Anos Disponíveis']}")

    with col2:
        st.markdown("#### 📋 Detalhes Metodológicos")

        st.markdown("**🔬 Metodologia:**")
        st.write(init_metadata["metodologia"])

        st.markdown("**✅ Validação:**")
        st.success(init_metadata["validacao"])

        st.markdown("**🌍 Cobertura:**")
        st.warning(init_metadata["cobertura"])

        st.markdown("**📡 Fontes de Dados:**")
        st.info(init_metadata["fonte_dados"])

st.markdown("---")

# Seção 5: Comparação Direta
st.header("⚖️ Comparação Direta Entre Iniciativas")

col1, col2 = st.columns(2)

with col1:
    init1 = st.selectbox(
        "Primeira iniciativa:",
        options=filtered_df["Nome"].tolist(),
        key="comparison1",
    )

with col2:
    init2 = st.selectbox(
        "Segunda iniciativa:",
        options=filtered_df["Nome"].tolist(),
        index=1 if len(filtered_df) > 1 else 0,
        key="comparison2",
    )

if init1 and init2 and init1 != init2:
    # Obter dados das duas iniciativas
    data1 = filtered_df[filtered_df["Nome"] == init1].iloc[0]
    data2 = filtered_df[filtered_df["Nome"] == init2].iloc[0]

    # Comparação em gráfico radar
    categories = ["Acurácia (%)", "Resolução (m)", "Classes"]

    # Normalizar valores para o radar (invertendo resolução para que menor seja melhor)
    def normalize_for_radar(value, column, df):
        if column == "Resolução (m)":
            # Para resolução, menor é melhor, então invertemos
            return (
                df[column].max() - value
            ) / (df[column].max() - df[column].min()) * 100
        else:
            return (value - df[column].min()) / (df[column].max() - df[column].min()) * 100

    values1 = [normalize_for_radar(data1[cat], cat, filtered_df) for cat in categories]
    values2 = [normalize_for_radar(data2[cat], cat, filtered_df) for cat in categories]

    fig_radar = plot_radar_comparacao(data1, data2, filtered_df, init1, init2)
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
    # Cria tabela HTML manualmente para evitar dependência de pandas
    table_html = "<table class='streamlit-table'><thead><tr><th>Característica</th><th>{}</th><th>{}</th></tr></thead><tbody>".format(init1, init2)
    for i, cat in enumerate(comparison_data['Característica']):
        table_html += f"<tr><td>{cat}</td><td>{comparison_data[init1][i]}</td><td>{comparison_data[init2][i]}</td></tr>"
    table_html += "</tbody></table>"
    st.markdown("### Comparação das Iniciativas Selecionadas")
    st.markdown(table_html, unsafe_allow_html=True)

# --- MELHORIA DE LEGENDA E SEÇÕES EM TEMA ESCURO ---
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# --- SUGESTÕES DE NOVAS FUNCIONALIDADES ---
st.markdown(
    """
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
"""
)
