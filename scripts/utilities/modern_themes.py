"""
Sistema moderno de temas e estilos para visualizações Plotly
Configuração global para dashboards profissionais e responsivos
"""

import plotly.graph_objects as go
import plotly.io as pio


class ModernThemes:
    """Classe para configurar temas modernos do Plotly"""

    @staticmethod
    def setup_modern_theme():
        """Configura tema moderno padrão para todo o projeto"""

        # Define tema moderno global
        modern_template = go.layout.Template()

        # Configurações de layout modernas
        modern_template.layout = go.Layout(
            # Tipografia moderna e consistente
            font=dict(
                family="Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                size=14,
                color="#1f2937",
            ),
            # Título principal
            title=dict(
                font=dict(
                    family="Inter, system-ui, sans-serif", size=24, color="#111827"
                ),
                x=0.5,
                xanchor="center",
                pad=dict(t=20, b=20),
            ),
            # Configurações dos eixos
            xaxis=dict(
                title=dict(
                    font=dict(
                        family="Inter, system-ui, sans-serif", size=14, color="#374151"
                    )
                ),
                tickfont=dict(
                    family="Inter, system-ui, sans-serif", size=12, color="#6b7280"
                ),
                gridcolor="#f3f4f6",
                gridwidth=1,
                showgrid=True,
                zeroline=False,
                showline=True,
                linecolor="#e5e7eb",
                linewidth=1,
            ),
            yaxis=dict(
                title=dict(
                    font=dict(
                        family="Inter, system-ui, sans-serif", size=14, color="#374151"
                    )
                ),
                tickfont=dict(
                    family="Inter, system-ui, sans-serif", size=12, color="#6b7280"
                ),
                gridcolor="#f3f4f6",
                gridwidth=1,
                showgrid=True,
                zeroline=False,
                showline=True,
                linecolor="#e5e7eb",
                linewidth=1,
            ),
            # Legenda moderna
            legend=dict(
                font=dict(
                    family="Inter, system-ui, sans-serif", size=12, color="#374151"
                ),
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="#e5e7eb",
                borderwidth=1,
                orientation="v",
                x=1.02,
                xanchor="left",
            ),
            # Background moderno
            plot_bgcolor="white",
            paper_bgcolor="white",
            # Margens otimizadas
            margin=dict(t=60, r=80, b=60, l=80),
            # Hover moderno
            hoverlabel=dict(
                bgcolor="rgba(17, 24, 39, 0.95)",
                bordercolor="rgba(75, 85, 99, 0.3)",
                font=dict(
                    family="Inter, system-ui, sans-serif", size=12, color="white"
                ),
            ),
            # Responsividade
            autosize=True,
            # Configurações de anotações
            annotationdefaults=dict(
                font=dict(
                    family="Inter, system-ui, sans-serif", size=12, color="#374151"
                )
            ),
        )

        # Cores modernas para gráficos
        modern_template.layout.colorway = [
            "#3b82f6",  # Blue
            "#10b981",  # Emerald
            "#f59e0b",  # Amber
            "#ef4444",  # Red
            "#8b5cf6",  # Violet
            "#06b6d4",  # Cyan
            "#84cc16",  # Lime
            "#f97316",  # Orange
            "#ec4899",  # Pink
            "#6366f1",  # Indigo
        ]

        # Registra o tema
        pio.templates["modern"] = modern_template
        pio.templates.default = "modern"

        return modern_template

    @staticmethod
    def get_professional_colors():
        """Retorna paleta de cores profissionais"""
        return {
            "primary": "#3b82f6",
            "secondary": "#10b981",
            "accent": "#f59e0b",
            "danger": "#ef4444",
            "warning": "#f97316",
            "info": "#06b6d4",
            "success": "#22c55e",
            "purple": "#8b5cf6",
            "pink": "#ec4899",
            "indigo": "#6366f1",
            "text_primary": "#111827",
            "text_secondary": "#374151",
            "text_muted": "#6b7280",
            "border": "#e5e7eb",
            "background": "#ffffff",
            "surface": "#f9fafb",
        }

    @staticmethod
    def apply_to_figure(fig, title=None, height=None, width=None):
        """Aplica estilo moderno a uma figura específica"""
        colors = ModernThemes.get_professional_colors()

        fig.update_layout(
            template="modern",
            title=(
                dict(
                    text=title,
                    font=dict(
                        family="Inter, system-ui, sans-serif",
                        size=20,
                        color=colors["text_primary"],
                    ),
                    x=0.5,
                    xanchor="center",
                )
                if title
                else None
            ),
            height=height,
            width=width,
            showlegend=True,
            hovermode="closest",
        )

        return fig

    @staticmethod
    def create_modern_table_config():
        """Configuração moderna para tabelas"""
        colors = ModernThemes.get_professional_colors()

        return {
            "header": {
                "fill_color": colors["primary"],
                "font": {
                    "color": "white",
                    "size": 14,
                    "family": "Inter, system-ui, sans-serif",
                    "weight": "600",
                },
                "align": "center",
                "height": 40,
            },
            "cells": {
                "fill_color": ["white", colors["surface"]],
                "font": {
                    "color": colors["text_primary"],
                    "size": 12,
                    "family": "Inter, system-ui, sans-serif",
                },
                "align": "left",
                "height": 35,
            },
            "layout": {
                "title": {
                    "font": {
                        "size": 18,
                        "family": "Inter, system-ui, sans-serif",
                        "color": colors["text_primary"],
                    }
                },
                "margin": {"t": 50, "r": 30, "b": 30, "l": 30},
            },
        }


# Inicializa o tema moderno automaticamente
ModernThemes.setup_modern_theme()

# Exporta para uso fácil
modern_colors = ModernThemes.get_professional_colors()
modern_table_config = ModernThemes.create_modern_table_config()
