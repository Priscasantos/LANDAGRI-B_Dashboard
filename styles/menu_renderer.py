"""
Menu Renderer para LANDAGRI-B Dashboard

Este módulo contém as funções de renderização dos menus,
separadas da lógica de estilos para melhor organização.
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, Any, List, Optional
from .menu_styles import MenuStyles


def generate_css_vars(config: Dict[str, Any]) -> str:
    """
    Gera variáveis CSS baseadas na configuração atual.
    
    Args:
        config (Dict[str, Any]): Configurações de layout e tipografia
        
    Returns:
        str: String CSS com variáveis personalizadas
    """
    return f"""
    :root {{
        --menu-width: {config.get('menu_width', 250)}px;
        --header-height: {config.get('header_height', 60)}px;
        --spacing: {config.get('spacing', 12)}px;
        --border-radius: {config.get('border_radius', 8)}px;
        --font-size: {config.get('font_size', 14)}px;
        --font-family: {config.get('font_family', 'Arial, sans-serif')};
    }}
    """


class MenuRenderer:
    """Classe responsável pela renderização dos menus do dashboard."""
    
    @staticmethod
    def render_styled_menu(palette: List[str], config: Dict[str, Any], MENU_STRUCTURE: Dict[str, Any], key_prefix: str = "styled_menu", *, css_only: bool = False) -> None:
        """
        Render a modern sidebar menu using streamlit-option-menu with optional CSS-only styling.
        """
        try:
            from streamlit_option_menu import option_menu
        except Exception:
            st.error("streamlit-option-menu package is required for styled menu")
            return

        categories = list(MENU_STRUCTURE.keys())

        # Main menu styles (only used when css_only=False)
        modern_menu_styles = {
            "container": {
                "padding": "0.8rem",
                "background": "linear-gradient(135deg, #f8fdf8 0%, #f1faf1 50%, #e8f5e8 100%)",
                "border-radius": "16px",
                "box-shadow": "0 10px 40px rgba(102, 122, 0, 0.15)",
                "backdrop-filter": "blur(10px)",
                "border": "1px solid rgba(102, 122, 0, 0.2)",
            },
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0.4rem 0",
                "padding": "1.2rem 1.4rem",
                "border-radius": "12px",
                "transition": "all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
                "background": "rgba(255, 255, 255, 0.8)",
                "border-left": "4px solid transparent",
                "backdrop-filter": "blur(5px)",
                "color": "#667A00",
                "font-weight": "500",
                "box-shadow": "0 2px 8px rgba(102, 122, 0, 0.08)",
                "border": "1px solid rgba(102, 122, 0, 0.1)",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #667A00 0%, #4a5a00 100%)",
                "color": "#ffffff",
                "font-weight": "600",
                "transform": "translateX(8px) scale(1.02)",
                "box-shadow": "0 8px 25px rgba(102, 122, 0, 0.4)",
                "border-left": "4px solid #8ba300",
                "border": "1px solid rgba(102, 122, 0, 0.3)",
            },
            "nav-link:hover": {
                "background": "rgba(102, 122, 0, 0.05)",
                "transform": "translateX(4px)",
                "box-shadow": "0 4px 15px rgba(102, 122, 0, 0.15)",
            },
            "icon": {"display": "none"},
            "menu-title": {
                "color": "#667A00",
                "font-weight": "700",
                "font-size": "20px",
                "text-align": "center",
                "margin-bottom": "1rem",
                "padding": "0.8rem",
                "text-shadow": "0 1px 2px rgba(102, 122, 0, 0.1)",
            },
        }

        # Sub menu styles (only used when css_only=False)
        sub_menu_styles = {
            "container": {
                "padding": "0.6rem",
                "background": "linear-gradient(135deg, rgba(102, 122, 0, 0.08) 0%, rgba(102, 122, 0, 0.05) 100%)",
                "border-radius": "12px",
                "border": "1px solid rgba(102, 122, 0, 0.15)",
                "box-shadow": "0 4px 15px rgba(102, 122, 0, 0.1)",
            },
            "nav-link": {
                "font-size": "14px",
                "text-align": "left",
                "margin": "0.3rem 0",
                "padding": "1rem 1.2rem",
                "border-radius": "8px",
                "transition": "all 0.3s ease",
                "color": "#4a5a00",
                "background": "rgba(255, 255, 255, 0.7)",
                "font-weight": "500",
                "box-shadow": "0 1px 4px rgba(102, 122, 0, 0.05)",
                "border": "1px solid rgba(102, 122, 0, 0.08)",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, rgba(102, 122, 0, 0.2) 0%, rgba(102, 122, 0, 0.15) 100%)",
                "color": "#667A00",
                "font-weight": "600",
                "transform": "translateX(4px)",
                "box-shadow": "0 3px 12px rgba(102, 122, 0, 0.25)",
                "border": "1px solid rgba(102, 122, 0, 0.2)",
            },
            "nav-link:hover": {
                "background": "rgba(102, 122, 0, 0.1)",
                "color": "#667A00",
                "transform": "translateX(2px)",
            },
            "icon": {"display": "none"},
        }

        # Render main category menu inside sidebar
        with st.sidebar:
            selected_cat = option_menu(
                menu_title="LANDAGRI-B Dashboard",
                options=categories,
                icons=None,
                menu_icon=None,
                default_index=0,
                styles=(None if css_only else modern_menu_styles),
                key=f"{key_prefix}_cat",
            )

            st.markdown("---")

            data = MENU_STRUCTURE.get(selected_cat, {})
            pages: List[str] = []
            page_icons: List[str] = []
            if isinstance(data, dict) and 'pages' in data:
                pages = data['pages']
                page_icons = data.get('page_icons', None) or []
            elif isinstance(data, list):
                pages = data

            selected_page = None
            if pages:
                clean_category_name = selected_cat
                try:
                    if len(selected_cat) > 1 and (not selected_cat[0].isalnum()) and selected_cat[1] == ' ':
                        clean_category_name = selected_cat.split(' ', 1)[1]
                except Exception:
                    pass

                selected_page = option_menu(
                    menu_title=f"{clean_category_name}",
                    options=pages,
                    icons=(page_icons if page_icons else None),
                    menu_icon=None,
                    default_index=0,
                    styles=(None if css_only else sub_menu_styles),
                    key=f"{key_prefix}_sub_{selected_cat.replace(' ', '_')}",
                )

            st.session_state.current_category = selected_cat
            st.session_state.current_page = selected_page or ""

    @staticmethod
    def _update_query_params(category: str, page: str) -> None:
        """
        Update the browser URL query params to reflect the current menu selection.
        """
        try:
            from urllib.parse import quote_plus

            safe_cat = quote_plus(category) if category else ""
            safe_page = quote_plus(page) if page else ""
            try:
                qp = st.query_params
                qp.update({
                    'category': [safe_cat],
                    'page': [safe_page],
                })
            except Exception:
                try:
                    st.query_params.from_dict({'category': [safe_cat], 'page': [safe_page]})
                except Exception:
                    pass
        except Exception:
            pass

    @staticmethod
    def render_menu(palette: List[str], config: Dict[str, Any], MENU_STRUCTURE: Dict[str, Any], *, sync_url: bool = True, show_breadcrumb: bool = True, key_prefix: str = "styled_menu", css_only: bool = False) -> None:
        """
        Unified public entrypoint to render the sidebar menu and breadcrumb.
        """
        # Centralize menu-related styles so app.py doesn't inject HTML/styles
        # Inject menu styles only once per session to avoid duplicate <style> blocks.
        try:
            if not st.session_state.get("_menu_styles_injected", False):
                st.markdown(MenuStyles.get_option_menu_styles(), unsafe_allow_html=True)
                st.markdown(MenuStyles.get_breadcrumb_styles(), unsafe_allow_html=True)
                st.session_state["_menu_styles_injected"] = True
        except Exception:
            pass

        # Render the styled menu
        MenuRenderer.render_styled_menu(palette, config, MENU_STRUCTURE, key_prefix, css_only=css_only)
        
        # Sync URL if requested
        if sync_url:
            try:
                cat = st.session_state.get('current_category', '')
                page = st.session_state.get('current_page', '')
                if cat and page:
                    MenuRenderer._update_query_params(cat, page)
            except Exception:
                pass

        # Optionally render breadcrumb
        if show_breadcrumb:
            try:
                cat = st.session_state.get('current_category', '')
                page = st.session_state.get('current_page', '')
                if page:
                    MenuRenderer.render_breadcrumb(page, category=cat, home_label="Dashboard")
            except Exception:
                pass
    
    @staticmethod
    def render_breadcrumb(current_page: str, 
                         category: Optional[str] = None, 
                         home_label: str = "Home") -> None:
        """
        Renderiza breadcrumb de navegação.
        
        Args:
            current_page (str): Página atual
            category (str, optional): Categoria atual
            home_label (str): Label para a página inicial
        """
        breadcrumb_styles = MenuStyles.get_breadcrumb_styles()
        st.markdown(breadcrumb_styles, unsafe_allow_html=True)
        
        breadcrumb_html = '<div class="breadcrumb">'
        
        # Home
        breadcrumb_html += f'<span class="breadcrumb-item">{home_label}</span>'
        
        # Categoria (se existir)
        if category:
            breadcrumb_html += '<span class="breadcrumb-separator">›</span>'
            breadcrumb_html += f'<span class="breadcrumb-item">{category}</span>'
        
        # Página atual
        breadcrumb_html += '<span class="breadcrumb-separator">›</span>'
        breadcrumb_html += f'<span class="breadcrumb-item active">{current_page}</span>'
        
        breadcrumb_html += '</div>'
        
        st.markdown(breadcrumb_html, unsafe_allow_html=True)
