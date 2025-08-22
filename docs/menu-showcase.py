"""
DEMONSTRAÇÃO VISUAL DAS OPÇÕES DE MENU PARA SEU DASHBOARD LULC
================================================================

Este arquivo mostra exemplos práticos de cada tipo de menu que você pode implementar.
Execute este arquivo para ver as opções em ação.
"""

import streamlit as st
from streamlit_option_menu import option_menu
# Configuração da página

def render():
    """Render the menu showcase UI. This function must be called explicitly to
    avoid rendering UI on import by other modules."""

    # Page configuration
    st.set_page_config(
        page_title="🛰️ Exemplos de Menu - LULC Dashboard",
        layout="wide",
        page_icon="🛰️"
    )

    st.title("🛰️ Opções de Menu para Dashboard LULC")
    st.markdown("**Explore diferentes estilos de navegação para seu dashboard**")

    # Sidebar para escolher o exemplo
    with st.sidebar:
        st.header("🎛️ Escolha um Exemplo")
        exemplo_selecionado = st.radio(
            "Tipo de Menu:",
            [
                "🔥 Menu Hierárquico Moderno (Recomendado)",
                "🏢 Menu Horizontal Corporativo", 
                "📱 Menu Mobile Responsivo",
                "📑 Tabs Nativas do Streamlit",
                "🔍 Menu com Busca Inteligente",
                "🎨 Menu com Temas Personalizados"
            ]
        )

    # Área principal para demonstração
    col1, col2 = st.columns([2, 1])

    with col1:
        # Menu Hierárquico Moderno
        if "🔥 Menu Hierárquico Moderno" in exemplo_selecionado:
            st.subheader("🔥 Menu Hierárquico Moderno")
            st.markdown("""
            **✨ Características:**
            - Categorias organizadas hierarquicamente
            - Sub-menus dinâmicos
            - Navegação breadcrumb
            - Animações suaves
            - Ideal para dashboards complexos
            """)

            # Demonstração do menu hierárquico
            st.markdown("### 📋 Estrutura Proposta:")

            menu_demo = {
                "📊 Dashboards": ["Overview", "Summary Dashboard"],
                "📈 Análises": ["Comparative Analysis", "Temporal Analysis", "Detailed Analysis"],
                "🌾 Dados Externos": ["CONAB Analysis", "External Sources"],
                "⚙️ Configurações": ["Data Management", "Export Options"]
            }

            # Simular o menu principal
            selected_cat = option_menu(
                menu_title="🛰️ LULC Dashboard",
                options=list(menu_demo.keys()),
                icons=["speedometer2", "graph-up", "map", "gear"],
                default_index=0,
                orientation="horizontal",
                styles={
                    "container": {"padding": "0.5rem", "background": "#f8fafc"},
                    "nav-link": {"font-size": "14px", "text-align": "center", "margin": "0px"},
                    "nav-link-selected": {"background-color": "#3b82f6"}
                }
            )

            # Mostrar sub-menu
            if selected_cat in menu_demo:
                st.markdown(f"**Sub-páginas de {selected_cat}:**")
                selected_page = st.selectbox(
                    "Selecione a página:",
                    menu_demo[selected_cat]
                )

                # Breadcrumb
                st.markdown(f"""
                <div style="
                    padding: 0.5rem 1rem;
                    background: #e2e8f0;
                    border-radius: 6px;
                    font-size: 14px;
                    color: #475569;
                    margin: 1rem 0;
                ">
                    🏠 Dashboard → {selected_cat.split(' ', 1)[1]} → {selected_page}
                </div>
                """, unsafe_allow_html=True)

        # Menu Horizontal Corporativo
        elif "🏢 Menu Horizontal Corporativo" in exemplo_selecionado:
            st.subheader("🏢 Menu Horizontal Corporativo")
            st.markdown("""
            **✨ Características:**
            - Layout horizontal moderno
            - Ideal para telas grandes
            - Visual corporativo limpo
            - Navegação rápida
            """)

            # Demonstração horizontal
            horizontal_menu = option_menu(
                menu_title=None,
                options=["Overview", "Análises", "Dados Externos", "Configurações"],
                icons=["house", "graph-up", "database", "gear"],
                orientation="horizontal",
                styles={
                    "container": {"padding": "0!important", "background-color": "#1e293b"},
                    "nav-link": {
                        "font-size": "16px",
                        "text-align": "center",
                        "margin": "0px",
                        "padding": "1rem 2rem",
                        "color": "#e2e8f0"
                    },
                    "nav-link-selected": {"background-color": "#3b82f6"}
                }
            )

            st.success(f"✅ Página selecionada: **{horizontal_menu}**")

        # Menu Mobile Responsivo
        elif "📱 Menu Mobile Responsivo" in exemplo_selecionado:
            st.subheader("📱 Menu Mobile Responsivo")
            st.markdown("""
            **✨ Características:**
            - Otimizado para dispositivos móveis
            - Ícones grandes e toque amigável
            - Menu compacto
            - Rápido carregamento
            """)

            # Simular menu mobile
            mobile_menu = option_menu(
                menu_title="📱 LULC",
                options=["Home", "Análises", "Dados"],
                icons=["house-fill", "bar-chart-fill", "database-fill"],
                default_index=0,
                styles={
                    "container": {"padding": "0.3rem", "background": "#0f172a"},
                    "nav-link": {
                        "font-size": "14px",
                        "padding": "0.8rem",
                        "margin": "0.2rem 0",
                        "border-radius": "8px"
                    },
                    "nav-link-selected": {
                        "background": "#3b82f6",
                        "font-weight": "bold"
                    },
                    "icon": {"font-size": "20px"}
                }
            )

            st.info(f"📱 Navegação mobile: **{mobile_menu}**")

        # Tabs Nativas do Streamlit
        elif "📑 Tabs Nativas do Streamlit" in exemplo_selecionado:
            st.subheader("📑 Tabs Nativas do Streamlit")
            st.markdown("""
            **✨ Características:**
            - Nativo do Streamlit (sem dependências)
            - Interface familiar
            - Boa para conteúdo relacionado
            - Simples de implementar
            """)

            # Demonstração com tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Overview", 
                "📈 Análises", 
                "🌾 Dados Externos", 
                "⚙️ Configurações"
            ])

            with tab1:
                st.markdown("### 🔎 Dashboard Overview")
                st.markdown("- Resumo geral dos dados")
                st.markdown("- Métricas principais")
                st.markdown("- Gráficos de tendência")

            with tab2:
                st.markdown("### 📈 Análises Avançadas")
                # Sub-tabs dentro de tab
                subtab1, subtab2, subtab3 = st.tabs(["Comparativa", "Temporal", "Detalhada"])
                with subtab1:
                    st.write("🔍 Análise Comparativa")
                with subtab2:
                    st.write("⏰ Análise Temporal")
                with subtab3:
                    st.write("🎯 Análise Detalhada")

            with tab3:
                st.markdown("### 🌾 Dados CONAB")
                st.markdown("- Calendário agrícola")
                st.markdown("- Disponibilidade de culturas")

            with tab4:
                st.markdown("### ⚙️ Configurações")
                st.markdown("- Gerenciamento de dados")
                st.markdown("- Opções de export")

        # Menu com Busca Inteligente
        elif "🔍 Menu com Busca Inteligente" in exemplo_selecionado:
            st.subheader("🔍 Menu com Busca Inteligente")
            st.markdown("""
            **✨ Características:**
            - Busca em tempo real
            - Filtros inteligentes
            - Navegação rápida
            - Ideal para muitas páginas
            """)

            # Demonstração de busca
            todas_paginas = [
                "Overview Dashboard", "Summary Report", 
                "Comparative Analysis", "Temporal Analysis", "Detailed Analysis",
                "CONAB Calendar", "CONAB Availability", "External Sources",
                "Data Management", "Export Options", "User Settings"
            ]

            busca = st.text_input(
                "🔍 Buscar página...", 
                placeholder="Digite para buscar (ex: 'temporal', 'conab', 'export')",
                key="search_demo"
            )

            if busca:
                paginas_filtradas = [
                    p for p in todas_paginas 
                    if busca.lower() in p.lower()
                ]

                if paginas_filtradas:
                    st.success(f"🎯 Encontradas {len(paginas_filtradas)} páginas:")
                    pagina_selecionada = st.selectbox(
                        "Selecione uma página:",
                        paginas_filtradas
                    )
                    st.info(f"📄 Navegando para: **{pagina_selecionada}**")
                else:
                    st.warning("❌ Nenhuma página encontrada para sua busca.")
            else:
                st.info("💡 Digite algo no campo de busca para filtrar as páginas")

        # Menu com Temas Personalizados
        elif "🎨 Menu com Temas Personalizados" in exemplo_selecionado:
            st.subheader("🎨 Menu com Temas Personalizados")
            st.markdown("""
            **✨ Características:**
            - Múltiplos temas visuais
            - Personalização avançada
            - Modo escuro/claro
            - Branding customizado
            """)

            # Seletor de tema
            tema_selecionado = st.selectbox(
                "🎨 Escolha um tema:",
                ["🌊 Oceano Azul", "🌲 Floresta Verde", "🔥 Fogo Laranja", "🌙 Noite Escura"]
            )

            # Definir estilos baseado no tema
            temas = {
                "🌊 Oceano Azul": {
                    "container": {"background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"},
                    "nav-link-selected": {"background": "#3b82f6"}
                },
                "🌲 Floresta Verde": {
                    "container": {"background": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"},
                    "nav-link-selected": {"background": "#10b981"}
                },
                "🔥 Fogo Laranja": {
                    "container": {"background": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"},
                    "nav-link-selected": {"background": "#f59e0b"}
                },
                "🌙 Noite Escura": {
                    "container": {"background": "linear-gradient(135deg, #2d3748 0%, #1a202c 100%)"},
                    "nav-link-selected": {"background": "#805ad5"}
                }
            }

            estilo_tema = temas[tema_selecionado]

            # Menu com tema aplicado
            menu_tematizado = option_menu(
                menu_title="🛰️ Dashboard Temático",
                options=["Overview", "Análises", "Dados", "Config"],
                icons=["house", "graph-up", "database", "gear"],
                styles={
                    "container": {
                        "padding": "1rem",
                        "border-radius": "12px",
                        **estilo_tema["container"]
                    },
                    "nav-link": {
                        "font-size": "16px",
                        "padding": "0.8rem 1rem",
                        "margin": "0.2rem 0",
                        "border-radius": "8px",
                        "color": "white"
                    },
                    "nav-link-selected": {
                        "font-weight": "bold",
                        **estilo_tema["nav-link-selected"]
                    }
                }
            )

            st.success(f"✨ Tema aplicado: **{tema_selecionado}** → Página: **{menu_tematizado}**")

    # Sidebar com informações adicionais
    with col2:
        st.markdown("### 💡 Dicas de Implementação")
        
        if "🔥 Menu Hierárquico Moderno" in exemplo_selecionado:
            st.markdown("""
            **📋 Para implementar:**
            1. Organize conteúdo em categorias
            2. Use sub-menus para páginas relacionadas
            3. Adicione breadcrumbs para navegação
            4. Implemente estado persistente
            """)
            
        elif "🏢 Menu Horizontal Corporativo" in exemplo_selecionado:
            st.markdown("""
            **📋 Para implementar:**
            1. Ideal para ≤ 6 itens principais
            2. Use ícones reconhecíveis
            3. Teste em diferentes resoluções
            4. Considere responsividade
            """)
            
        elif "📱 Menu Mobile Responsivo" in exemplo_selecionado:
            st.markdown("""
            **📋 Para implementar:**
            1. Detecte tamanho da tela
            2. Use ícones grandes e legíveis
            3. Minimize opções de menu
            4. Teste em dispositivos reais
            """)
            
        elif "📑 Tabs Nativas do Streamlit" in exemplo_selecionado:
            st.markdown("""
            **📋 Para implementar:**
            1. Agrupe conteúdo relacionado
            2. Use emojis para melhor UX
            3. Considere sub-tabs se necessário
            4. Mantenha labels curtos
            """)
            
        elif "🔍 Menu com Busca Inteligente" in exemplo_selecionado:
            st.markdown("""
            **📋 Para implementar:**
            1. Indexe todas as páginas
            2. Implemente busca fuzzy
            3. Adicione filtros por categoria
            4. Considere histórico de busca
            """)
            
        elif "🎨 Menu com Temas Personalizados" in exemplo_selecionado:
            st.markdown("""
            **📋 Para implementar:**
            1. Defina paleta de cores
            2. Crie sistema de temas
            3. Permita troca em tempo real
            4. Salve preferências do usuário
            """)

# Rodapé com próximos passos
    st.markdown("---")
    st.markdown("### 🚀 Próximos Passos")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **1️⃣ Escolher Estilo**
        - Analise cada opção
        - Considere seu público
        - Teste usabilidade
        """)

    with col2:
        st.markdown("""
        **2️⃣ Implementar**
        - Backup do código atual
        - Implementação gradual
        - Testes em staging
        """)

    with col3:
        st.markdown("""
        **3️⃣ Otimizar**
        - Feedback dos usuários
        - Métricas de uso
        - Melhorias contínuas
        """)


    if __name__ == "__main__":
        render()

    # Botão para ver código
    with st.expander("👨‍💻 Ver código de implementação"):
        st.code("""
# Exemplo de implementação do menu hierárquico
def create_hierarchical_menu():
    menu_structure = {
        "📊 Dashboards": ["Overview", "Summary"],
        "📈 Análises": ["Comparative", "Temporal", "Detailed"],
        "🌾 Dados Externos": ["CONAB", "External"],
        "⚙️ Configurações": ["Data Mgmt", "Export"]
    }
    
    selected_category = option_menu(
        menu_title="🛰️ LULC Dashboard",
        options=list(menu_structure.keys()),
        icons=["speedometer2", "graph-up", "map", "gear"]
    )
    
    if selected_category in menu_structure:
        selected_page = option_menu(
            menu_title=None,
            options=menu_structure[selected_category],
            orientation="horizontal"
        )
        
        return selected_category, selected_page
    """, language="python")
