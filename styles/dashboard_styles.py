"""
Dashboard Styles para LANDAGRI-B Dashboard

Este módulo contém todos os estilos CSS gerais do dashboard,
incluindo containers, cards, botões e elementos visuais.
"""

from typing import Dict, Any, List, Optional


class DashboardStyles:
    """Classe responsável pelos estilos CSS gerais do dashboard."""
    
    @staticmethod
    def get_main_container_styles() -> str:
        """
        Retorna os estilos CSS para o container principal do dashboard.
        
        Returns:
            str: String CSS para o container principal
        """
        return """
        <style>
        .main-container {
            padding: 20px;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            min-height: 100vh;
        }
        .content-wrapper {
            max-width: 1200px;
            margin: 0 auto;
        }
        </style>
        """
    
    @staticmethod
    def get_card_styles() -> str:
        """
        Retorna os estilos CSS para cards e métricas.
        
        Returns:
            str: String CSS para cards
        """
        return """
        <style>
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.1);
            border: 1px solid rgba(148, 163, 184, 0.1);
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(15, 23, 42, 0.15);
        }
        .metric-title {
            font-size: 14px;
            color: #64748b;
            font-weight: 500;
            margin-bottom: 8px;
        }
        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 4px;
        }
        .metric-delta {
            font-size: 12px;
            font-weight: 600;
        }
        .metric-delta.positive {
            color: #059669;
        }
        .metric-delta.negative {
            color: #dc2626;
        }
        </style>
        """
    
    @staticmethod
    def get_button_styles(palette: Optional[List[str]] = None) -> str:
        """
        Retorna os estilos CSS para botões personalizados.
        
        Args:
            palette (List[str], optional): Lista de cores da paleta
            
        Returns:
            str: String CSS para botões
        """
        primary_color = palette[0] if palette else "#3b82f6"
        secondary_color = palette[1] if palette and len(palette) > 1 else "#64748b"
        
        return f"""
        <style>
        .btn-primary {{
            background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
        }}
        .btn-secondary {{
            background: transparent;
            color: {primary_color};
            border: 2px solid {primary_color};
            padding: 10px 22px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        .btn-secondary:hover {{
            background: {primary_color};
            color: white;
            transform: translateY(-2px);
        }}
        </style>
        """
    
    @staticmethod
    def get_header_styles() -> str:
        """
        Retorna os estilos CSS para cabeçalhos e títulos.
        
        Returns:
            str: String CSS para headers
        """
        return """
        <style>
        .page-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.1);
            border: 1px solid rgba(148, 163, 184, 0.1);
        }

        /* Force-hide decorative icons/inline elements that may appear near headers */
        .page-header i, .page-header svg, .page-header .icon, .page-header [class*="bi-"],
        .page-header i::before, .page-header i::after, .page-header::before, .page-header::after {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
            visibility: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
            content: none !important;
        }

        .page-title {
            font-size: 28px;
            font-weight: 700;
            color: #1e293b;
            margin: 0;
        }
        .page-subtitle {
            font-size: 16px;
            color: #64748b;
            margin: 4px 0 0 0;
        }

        </style>
        """
    
    @staticmethod
    def get_chart_container_styles() -> str:
        """
        Retorna os estilos CSS para containers de gráficos.
        
        Returns:
            str: String CSS para containers de charts
        """
        return """
        <style>
        .chart-container {
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.1);
            border: 1px solid rgba(148, 163, 184, 0.1);
            margin-bottom: 20px;
        }
        .chart-title {
            font-size: 18px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .chart-subtitle {
            font-size: 14px;
            color: #64748b;
            margin-bottom: 20px;
        }
        </style>
        """
    
    @staticmethod
    def get_sidebar_styles() -> str:
        """
        Retorna os estilos CSS para a sidebar.
        
        Returns:
            str: String CSS para sidebar
        """
        return """
        <style>
        .sidebar-content {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.1);
            border: 1px solid rgba(148, 163, 184, 0.1);
            margin-bottom: 20px;
        }
        .sidebar-title {
            font-size: 16px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e2e8f0;
        }
        .sidebar-section {
            margin-bottom: 20px;
        }
        .sidebar-label {
            font-size: 14px;
            font-weight: 500;
            color: #374151;
            margin-bottom: 8px;
        }
        </style>
        """
    
    @staticmethod
    def get_responsive_styles() -> str:
        """
        Retorna os estilos CSS responsivos para diferentes tamanhos de tela.
        
        Returns:
            str: String CSS responsivo
        """
        return """
        <style>
        @media (max-width: 768px) {
            .main-container {
                padding: 10px;
            }
            .page-header {
                flex-direction: column;
                text-align: center;
                gap: 12px;
            }
            .metric-card {
                margin-bottom: 16px;
            }
            .chart-container {
                padding: 16px;
            }
        }
        @media (max-width: 480px) {
            .page-title {
                font-size: 24px;
            }
            .metric-value {
                font-size: 24px;
            }
            .btn-primary, .btn-secondary {
                width: 100%;
                justify-content: center;
                margin-bottom: 8px;
            }
        }
        </style>
        """
