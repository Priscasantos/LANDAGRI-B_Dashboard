"""
Menu Styles para LANDAGRI-B Dashboard

Este módulo contém todos os estilos CSS para os diferentes tipos de menu
utilizados no dashboard, incluindo o menu hierárquico principal.
"""

from typing import Dict, Any, List


class MenuStyles:
    """Classe responsável pelos estilos CSS dos menus do dashboard."""
    
    @staticmethod
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
    
    @staticmethod
    def get_hierarchical_menu_styles(palette: List[str], config: Dict[str, Any]) -> str:
        """
        Retorna os estilos CSS para o menu hierárquico principal seguindo o layout da imagem.
        
        Args:
            palette (List[str]): Lista de cores da paleta
            config (Dict[str, Any]): Configurações de layout
            
        Returns:
            str: String CSS completa para o menu hierárquico
        """
        css_vars = MenuStyles.generate_css_vars(config)
        
        return f"""
        <style>
        {css_vars}
        
        /* Container principal do sidebar */
        .sidebar-content {{
            background: #ffffff;
            padding: 0;
            margin: 0;
            font-family: Arial, sans-serif;
        }}
        
        /* Título do menu principal */
        .menu-title {{
            color: #2c3e50;
            font-weight: 600;
            font-size: 18px;
            text-align: center;
            margin-bottom: 16px;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 6px;
        }}


            /* Hide only the top decorative icon placed inside the menu title.
               Keep per-page icons (e.g. those rendered by option_menu) visible. */
            .menu-title > i.icon.bi-menu-up,
            .menu-title > i.icon,
            .menu-title > svg {{
                display: none !important;
                width: 0 !important;
                height: 0 !important;
                visibility: hidden !important;
                margin: 0 !important;
                padding: 0 !important;
                content: none !important;
            }}

        /* Base style for main category buttons (was accidentally orphaned before) */
        .main-category {{
            width: 100%;
            background: #1e88e5;
            color: white;
            border: none;
            padding: 12px 16px;
            margin: 0 0 2px 0;
            text-align: left;
            font-size: 14px;
            font-weight: 500;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .main-category:hover {{
            background: #1976d2;
            transform: translateX(2px);
        }}
        
        .main-category.selected {{
            background: #1565c0;
        }}
        
        /* Subcategorias - botões cinza claro indentados */
        .sub-page {{
            width: 100%;
            background: #f5f5f5;
            color: #424242;
            border: none;
            padding: 10px 16px 10px 32px;
            margin: 0 0 1px 0;
            text-align: left;
            font-size: 13px;
            font-weight: 400;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
        }}
        
        .sub-page:hover {{
            background: #e8f4fd;
            color: #1976d2;
            border-left-color: #1976d2;
            transform: translateX(4px);
        }}
        
        .sub-page.selected {{
            background: #e3f2fd;
            color: #1565c0;
            border-left-color: #1565c0;
            font-weight: 500;
        }}
        
        /* Espaçamento entre grupos */
        .menu-group {{
            margin-bottom: 8px;
        }}
        

        
        /* Reset de estilos do Streamlit */
        .stButton > button {{
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            background: none !important;
            box-shadow: none !important;
        }}
        
        .stButton > button > div {{
            width: 100% !important;
            text-align: left !important;
        }}
        
        /* Estilo específico para botões da categoria principal */
        .main-category-button > button {{
            background: #1e88e5 !important;
            color: white !important;
            padding: 12px 16px !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
        }}
        
        .main-category-button > button:hover {{
            background: #1976d2 !important;
        }}
        
        /* Estilo específico para botões de subcategoria */
        .sub-page-button > button {{
            background: #f5f5f5 !important;
            color: #424242 !important;
            padding: 10px 16px 10px 32px !important;
            border-radius: 4px !important;
            border-left: 3px solid transparent !important;
        }}
        
        .sub-page-button > button:hover {{
            background: #e8f4fd !important;
            color: #1976d2 !important;
            border-left: 3px solid #1976d2 !important;
        }}
        </style>
        """
    
    @staticmethod
    def get_option_menu_styles() -> str:
        """
        Retorna os estilos CSS para o streamlit-option-menu.
        
        Returns:
            str: String CSS para o option menu
        """
        return """
        <style>
        /* Hide default option_menu title icons (Bootstrap or SVG) */
        .menu-title i,
        .menu-title svg,
        .menu-title .icon {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .nav-link {
            font-size: 16px !important;
            font-weight: 500 !important;
            margin: 0px !important;
            padding: 12px 20px !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
        }
        .nav-link:hover {
            background-color: rgba(59, 130, 246, 0.1) !important;
            transform: translateX(4px) !important;
        }
        .nav-link-selected {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
        }

        </style>
        """
    
    @staticmethod
    def get_breadcrumb_styles() -> str:
        """
        Retorna os estilos CSS para breadcrumbs de navegação.
        
        Returns:
            str: String CSS para breadcrumbs
        """
        return """
        <style>
        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 20px;
            padding: 10px 16px;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 8px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            font-size: 14px;
            color: #64748b;
        }
        .breadcrumb-item {
            color: #64748b;
            text-decoration: none;
        }
        .breadcrumb-item.active {
            color: #1e40af;
            font-weight: 600;
        }
        .breadcrumb-separator {
            color: #cbd5e1;
            margin: 0 4px;
        }
        </style>
        """
