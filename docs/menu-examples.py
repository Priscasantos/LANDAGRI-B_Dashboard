"""
Exemplo de implementação de menu hierárquico melhorado para o Dashboard LULC
Baseado no seu código atual com melhorias de UX e organização
"""

import streamlit as st
from streamlit_option_menu import option_menu

def create_modern_menu():
    """
    Cria um menu moderno hierárquico com categorias organizadas
    """
    
    # Estrutura hierárquica do menu
    menu_structure = {
        "📊 Dashboards": {
            "icon": "speedometer2",
            "pages": ["Overview", "Summary Dashboard"],
            "page_icons": ["house", "bar-chart-line"]
        },
        "📈 Análises": {
            "icon": "graph-up",
            "pages": ["Comparative Analysis", "Temporal Analysis", "Detailed Analysis"],
            "page_icons": ["bar-chart", "calendar-event", "zoom-in"]
        },
        "🌾 Dados Externos": {
            "icon": "map",
            "pages": ["CONAB Analysis", "External Sources"],
            "page_icons": ["map", "database"]
        },
        "⚙️ Configurações": {
            "icon": "gear",
            "pages": ["Data Management", "Export Options"],
            "page_icons": ["folder", "download"]
        }
    }
    
    # CSS personalizado para o menu moderno
    modern_menu_styles = {
        "container": {
            "padding": "0.5rem",
            "background": "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)",
            "border-radius": "12px",
            "box-shadow": "0 8px 32px rgba(0,0,0,0.3)",
            "backdrop-filter": "blur(10px)",
            "border": "1px solid rgba(255,255,255,0.1)"
        },
        "nav-link": {
            "font-size": "16px",
            "text-align": "left",
            "margin": "0.3rem 0",
            "padding": "1rem 1.2rem",
            "border-radius": "10px",
            "transition": "all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
            "background": "rgba(255,255,255,0.05)",
            "border-left": "4px solid transparent",
            "backdrop-filter": "blur(5px)"
        },
        "nav-link-selected": {
            "background": "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
            "color": "#ffffff",
            "font-weight": "600",
            "transform": "translateX(8px) scale(1.02)",
            "box-shadow": "0 6px 20px rgba(59, 130, 246, 0.4)",
            "border-left": "4px solid #60a5fa"
        },
        "icon": {
            "color": "#60a5fa",
            "font-size": "18px",
            "margin-right": "12px"
        },
        "menu-title": {
            "color": "#60a5fa",
            "font-weight": "700",
            "font-size": "22px",
            "text-align": "center",
            "margin-bottom": "1.5rem",
            "padding": "1rem",
            "background": "linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(29, 78, 216, 0.1) 100%)",
            "border-radius": "10px",
            "border": "1px solid rgba(59, 130, 246, 0.2)"
        }
    }
    
    # Selecionar categoria principal
    with st.sidebar:
        # Título principal com animação
        st.markdown("""
        <style>
        .main-title {
            animation: glow 2s ease-in-out infinite alternate;
        }
        @keyframes glow {
            from { text-shadow: 0 0 5px #60a5fa; }
            to { text-shadow: 0 0 20px #60a5fa, 0 0 30px #60a5fa; }
        }
        </style>
        """, unsafe_allow_html=True)
        
        selected_category = option_menu(
            menu_title="🛰️ LULC Dashboard",
            options=list(menu_structure.keys()),
            icons=[menu_structure[cat]["icon"] for cat in menu_structure.keys()],
            default_index=0,
            styles=modern_menu_styles,
            key="main_menu"
        )
        
        # Sub-menu para categoria selecionada
        if selected_category in menu_structure:
            st.markdown("---")
            
            # Estilo para sub-menu
            sub_menu_styles = {
                "container": {
                    "padding": "0.3rem",
                    "background": "rgba(59, 130, 246, 0.1)",
                    "border-radius": "8px"
                },
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "left",
                    "margin": "0.2rem 0",
                    "padding": "0.8rem 1rem",
                    "border-radius": "6px",
                    "transition": "all 0.3s ease"
                },
                "nav-link-selected": {
                    "background": "rgba(59, 130, 246, 0.3)",
                    "color": "#ffffff",
                    "font-weight": "500"
                }
            }
            
            selected_page = option_menu(
                menu_title=f"📋 {selected_category.split(' ', 1)[1]}",
                options=menu_structure[selected_category]["pages"],
                icons=menu_structure[selected_category]["page_icons"],
                default_index=0,
                styles=sub_menu_styles,
                key=f"sub_menu_{selected_category}"
            )
            
            # Breadcrumb navigation
            st.markdown(f"""
            <div style="
                margin-top: 1rem;
                padding: 0.5rem;
                background: rgba(255,255,255,0.05);
                border-radius: 6px;
                font-size: 12px;
                color: #94a3b8;
            ">
                🏠 Dashboard → {selected_category.split(' ', 1)[1]} → {selected_page}
            </div>
            """, unsafe_allow_html=True)
            
            return selected_category, selected_page
    
    return None, None

def create_horizontal_menu():
    """
    Versão horizontal do menu para telas grandes
    """
    horizontal_styles = {
        "container": {
            "padding": "0!important",
            "background-color": "#0f172a",
            "border-bottom": "3px solid #3b82f6"
        },
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "margin": "0px",
            "padding": "1rem 2rem",
            "color": "#e2e8f0",
            "transition": "all 0.3s ease"
        },
        "nav-link-selected": {
            "background-color": "#3b82f6",
            "color": "#ffffff"
        }
    }
    
    return option_menu(
        menu_title=None,
        options=["Overview", "Analysis", "External Data", "Settings"],
        icons=["house", "graph-up", "database", "gear"],
        orientation="horizontal",
        styles=horizontal_styles
    )

def create_mobile_optimized_menu():
    """
    Menu otimizado para dispositivos móveis
    """
    # Detectar se é mobile (simplificado)
    is_mobile = st.session_state.get("mobile_view", False)
    
    if is_mobile:
        # Menu compacto para mobile
        compact_styles = {
            "container": {"padding": "0.3rem"},
            "nav-link": {
                "font-size": "14px",
                "padding": "0.6rem 0.8rem",
                "margin": "0.1rem 0"
            }
        }
        
        return option_menu(
            menu_title="📱 LULC",
            options=["Home", "Analysis", "Data"],
            icons=["house", "graph-up", "database"],
            styles=compact_styles
        )
    else:
        return create_modern_menu()

def create_tabs_alternative():
    """
    Alternativa usando tabs nativas do Streamlit
    """
    # Criar tabs principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔎 Overview", 
        "📈 Analysis", 
        "🌾 External Data", 
        "⚙️ Settings"
    ])
    
    with tab1:
        # Sub-tabs para overview
        subtab1, subtab2 = st.tabs(["Dashboard", "Summary"])
        with subtab1:
            return "Overview", "Dashboard"
        with subtab2:
            return "Overview", "Summary"
    
    with tab2:
        # Sub-tabs para análises
        subtab1, subtab2, subtab3 = st.tabs([
            "Comparative", 
            "Temporal", 
            "Detailed"
        ])
        with subtab1:
            return "Analysis", "Comparative"
        with subtab2:
            return "Analysis", "Temporal"
        with subtab3:
            return "Analysis", "Detailed"
    
    with tab3:
        return "External Data", "CONAB"
    
    with tab4:
        return "Settings", "Config"

def create_search_menu():
    """
    Menu com funcionalidade de busca
    """
    with st.sidebar:
        # Barra de busca
        search_term = st.text_input(
            "🔍 Buscar página...", 
            placeholder="Digite para buscar..."
        )
        
        # Lista de todas as páginas disponíveis
        all_pages = [
            "Overview", "Summary Dashboard", 
            "Comparative Analysis", "Temporal Analysis", "Detailed Analysis",
            "CONAB Analysis", "External Sources",
            "Data Management", "Export Options"
        ]
        
        # Filtrar páginas baseado na busca
        if search_term:
            filtered_pages = [
                page for page in all_pages 
                if search_term.lower() in page.lower()
            ]
        else:
            filtered_pages = all_pages
        
        # Mostrar resultados
        if filtered_pages:
            selected = st.radio(
                "📄 Páginas encontradas:",
                filtered_pages
            )
            return selected
        else:
            st.warning("Nenhuma página encontrada!")
            return None

# Exemplo de uso
if __name__ == "__main__":
    st.set_page_config(
        page_title="Menu Examples",
        layout="wide",
        page_icon="🛰️"
    )
    
    # Escolher tipo de menu
    menu_type = st.selectbox(
        "Escolha o tipo de menu:",
        [
            "Menu Hierárquico Moderno",
            "Menu Horizontal", 
            "Menu Mobile",
            "Tabs Nativas",
            "Menu com Busca"
        ]
    )
    
    if menu_type == "Menu Hierárquico Moderno":
        category, page = create_modern_menu()
        if category and page:
            st.title(f"{category} - {page}")
            st.write("Conteúdo da página selecionada...")
    
    elif menu_type == "Menu Horizontal":
        selected = create_horizontal_menu()
        st.title(f"Página: {selected}")
    
    elif menu_type == "Menu Mobile":
        selected = create_mobile_optimized_menu()
        st.title(f"Mobile: {selected}")
    
    elif menu_type == "Tabs Nativas":
        category, page = create_tabs_alternative()
        st.title(f"{category} - {page}")
    
    elif menu_type == "Menu com Busca":
        selected = create_search_menu()
        if selected:
            st.title(f"Página: {selected}")
