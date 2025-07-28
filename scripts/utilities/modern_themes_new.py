"""
Sistema moderno de temas e estilos para visualizações Plotly
Configuração global para dashboards profissionais e responsivos
"""

import plotly.graph_objects as go
import plotly.io as pio
import plotly.colors as colors
from typing import Dict, List, Optional, Any


class ModernColorPalettes:
    """Paletas de cores modernas e acessíveis"""
    
    # Cores primárias modernas
    PRIMARY = {
        'blue': '#3b82f6',
        'indigo': '#6366f1', 
        'purple': '#8b5cf6',
        'pink': '#ec4899',
        'red': '#ef4444',
        'orange': '#f97316',
        'amber': '#f59e0b',
        'yellow': '#eab308',
        'lime': '#84cc16',
        'green': '#22c55e',
        'emerald': '#10b981',
        'teal': '#14b8a6',
        'cyan': '#06b6d4',
        'sky': '#0ea5e9'
    }
    
    # Paleta categórica moderna
    CATEGORICAL = [
        '#3b82f6',  # blue
        '#10b981',  # emerald  
        '#f59e0b',  # amber
        '#ef4444',  # red
        '#8b5cf6',  # purple
        '#06b6d4',  # cyan
        '#84cc16',  # lime
        '#ec4899',  # pink
        '#f97316',  # orange
        '#6366f1',  # indigo
        '#22c55e',  # green
        '#14b8a6'   # teal
    ]
    
    # Colorscales modernos para heatmaps
    COLORSCALES = {
        'modern_blue': [
            [0, '#f8fafc'], [0.2, '#e2e8f0'], [0.4, '#cbd5e1'],
            [0.6, '#64748b'], [0.8, '#3b82f6'], [1, '#1e40af']
        ],
        'modern_green': [
            [0, '#f0fdf4'], [0.2, '#dcfce7'], [0.4, '#bbf7d0'],
            [0.6, '#4ade80'], [0.8, '#16a34a'], [1, '#15803d']
        ],
        'modern_diverging': [
            [0, '#dc2626'], [0.25, '#f87171'], [0.5, '#f3f4f6'],
            [0.75, '#60a5fa'], [1, '#2563eb']
        ],
        'performance': [
            [0, '#fef2f2'], [0.25, '#fecaca'], [0.5, '#fde047'],
            [0.75, '#86efac'], [1, '#22c55e']
        ]
    }
    
    # Cores semânticas
    SEMANTIC = {
        'success': '#22c55e',
        'warning': '#f59e0b', 
        'error': '#ef4444',
        'info': '#3b82f6',
        'neutral': '#6b7280'
    }


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
                    family="Inter, system-ui, sans-serif", size=20, color="#111827"
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
                linecolor="#e5e7eb",
                linewidth=1,
            ),
            # Configurações de legenda modernas
            legend=dict(
                font=dict(
                    family="Inter, system-ui, sans-serif", size=12, color="#374151"
                ),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#e5e7eb",
                borderwidth=1,
            ),
            # Cor de fundo limpa
            plot_bgcolor="white",
            paper_bgcolor="white",
            # Margens responsivas
            margin=dict(l=80, r=40, t=60, b=80),
        )

        # Cores padrão para traces
        modern_template.data.scatter = [
            go.Scatter(marker_color="#3b82f6"),
            go.Scatter(marker_color="#10b981"),
            go.Scatter(marker_color="#f59e0b"),
            go.Scatter(marker_color="#ef4444"),
            go.Scatter(marker_color="#8b5cf6"),
            go.Scatter(marker_color="#06b6d4"),
        ]

        modern_template.data.bar = [
            go.Bar(
                marker_color="#3b82f6",
                marker_line=dict(width=0.5, color="rgba(255,255,255,0.8)"),
            )
        ]

        modern_template.data.heatmap = [
            go.Heatmap(
                colorscale="Blues",
                showscale=True,
                colorbar=dict(
                    thickness=15,
                    len=0.7,
                    bgcolor="rgba(255,255,255,0)",
                    borderwidth=0,
                    tickfont=dict(
                        family="Inter, system-ui, sans-serif", size=12, color="#374151"
                    ),
                ),
            )
        ]

        # Registra o tema no Plotly
        pio.templates["modern"] = modern_template
        pio.templates.default = "modern"

    @staticmethod
    def get_responsive_height(
        chart_type: str, num_items: int = 10, base_height: int = 400
    ) -> int:
        """
        Calcula altura responsiva baseada no tipo de gráfico e número de itens

        Args:
            chart_type: Tipo do gráfico ('bar', 'heatmap', 'timeline', etc.)
            num_items: Número de itens/categorias
            base_height: Altura base mínima

        Returns:
            Altura calculada em pixels
        """
        height_configs = {
            "bar_horizontal": max(base_height, num_items * 40 + 100),
            "bar_vertical": base_height,
            "heatmap": max(base_height, num_items * 30 + 150),
            "timeline": max(base_height, num_items * 25 + 100),
            "scatter": base_height,
            "line": base_height,
            "pie": base_height,
            "radar": base_height,
        }

        return height_configs.get(chart_type, base_height)

    @staticmethod
    def get_color_sequence(num_colors: int = 12) -> List[str]:
        """
        Retorna sequência de cores categóricas modernas

        Args:
            num_colors: Número de cores necessárias

        Returns:
            Lista de cores hex
        """
        base_colors = ModernColorPalettes.CATEGORICAL
        if num_colors <= len(base_colors):
            return base_colors[:num_colors]

        # Se precisar de mais cores, repete o padrão com variações
        extended_colors = []
        for i in range(num_colors):
            base_idx = i % len(base_colors)
            extended_colors.append(base_colors[base_idx])

        return extended_colors

    @staticmethod
    def get_colorscale(scale_name: str = 'modern_blue') -> List:
        """
        Retorna colorscale moderno para heatmaps

        Args:
            scale_name: Nome do colorscale

        Returns:
            Lista de colorscale
        """
        return ModernColorPalettes.COLORSCALES.get(scale_name, ModernColorPalettes.COLORSCALES['modern_blue'])

    @staticmethod
    def apply_modern_layout(
        fig: go.Figure,
        title: str = "",
        xaxis_title: str = "",
        yaxis_title: str = "",
        chart_type: str = "default",
        num_items: Optional[int] = None,
        **kwargs
    ) -> go.Figure:
        """
        Aplica layout moderno a uma figura Plotly

        Args:
            fig: Figura Plotly
            title: Título do gráfico
            xaxis_title: Título do eixo X
            yaxis_title: Título do eixo Y
            chart_type: Tipo do gráfico para otimizações específicas
            num_items: Número de itens para altura responsiva
            **kwargs: Configurações adicionais

        Returns:
            Figura com layout moderno aplicado
        """
        # Calcula altura responsiva se num_items foi fornecido
        height = kwargs.get('height')
        if num_items and not height:
            height = ModernThemes.get_responsive_height(chart_type, num_items)

        # Configurações base do layout moderno
        layout_updates = {
            "font": {
                "family": "Inter, system-ui, sans-serif",
                "size": 14,
                "color": "#1f2937"
            },
            "plot_bgcolor": "white",
            "paper_bgcolor": "white",
            "margin": {"l": 80, "r": 40, "t": 80 if title else 40, "b": 80},
        }

        if height:
            layout_updates["height"] = height

        # Adiciona título se fornecido
        if title:
            layout_updates["title"] = {
                "text": f"<b>{title}</b>",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 18, "color": "#111827"}
            }

        # Configurações dos eixos
        xaxis_config = {
            "title": {"text": xaxis_title, "font": {"size": 14, "color": "#374151"}},
            "tickfont": {"size": 12, "color": "#6b7280"},
            "gridcolor": "#f3f4f6",
            "gridwidth": 1,
            "showgrid": True,
            "zeroline": False,
            "linecolor": "#e5e7eb",
            "linewidth": 1,
        }

        yaxis_config = {
            "title": {"text": yaxis_title, "font": {"size": 14, "color": "#374151"}},
            "tickfont": {"size": 12, "color": "#6b7280"},
            "gridcolor": "#f3f4f6",
            "gridwidth": 1,
            "showgrid": True,
            "zeroline": False,
            "linecolor": "#e5e7eb",
            "linewidth": 1,
        }

        # Otimizações específicas por tipo de gráfico
        if chart_type == "heatmap":
            xaxis_config["tickangle"] = 0
            yaxis_config["autorange"] = "reversed"
        elif chart_type == "bar_horizontal":
            xaxis_config["showgrid"] = True
            yaxis_config["showgrid"] = False
        elif chart_type == "timeline":
            yaxis_config["type"] = "category"

        layout_updates["xaxis"] = xaxis_config
        layout_updates["yaxis"] = yaxis_config

        # Configuração de legenda moderna
        layout_updates["legend"] = {
            "font": {"size": 12, "color": "#374151"},
            "bgcolor": "rgba(255,255,255,0.9)",
            "bordercolor": "#e5e7eb",
            "borderwidth": 1,
            "yanchor": "top",
            "y": 1,
            "xanchor": "left",
            "x": 1.02
        }

        # Aplica configurações adicionais do kwargs
        layout_updates.update(kwargs)

        fig.update_layout(**layout_updates)
        return fig


# Funções utilitárias globais
def get_modern_colors(num_colors: int = 12) -> List[str]:
    """Função global para obter cores modernas"""
    return ModernThemes.get_color_sequence(num_colors)


def get_modern_colorscale(scale_name: str = 'modern_blue') -> List:
    """Função global para obter colorscale moderno"""
    return ModernThemes.get_colorscale(scale_name)


def apply_modern_theme(
    fig: go.Figure,
    title: str = "",
    xaxis_title: str = "",
    yaxis_title: str = "",
    chart_type: str = "default",
    num_items: Optional[int] = None,
    **kwargs
) -> go.Figure:
    """Função global para aplicar tema moderno"""
    return ModernThemes.apply_modern_layout(
        fig, title, xaxis_title, yaxis_title, chart_type, num_items, **kwargs
    )


# Inicializa tema moderno automaticamente quando o módulo é importado
ModernThemes.setup_modern_theme()
