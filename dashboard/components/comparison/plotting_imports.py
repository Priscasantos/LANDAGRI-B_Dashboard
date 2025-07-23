"""
Componente para importações de funções de plotting
=================================================

Este módulo gerencia a importação das funções de plotting e fornece
fallbacks caso as importações falhem.
"""

import plotly.graph_objects as go
import streamlit as st


def import_plotting_functions() -> tuple[bool, dict]:
    """
    Importa as funções de plotting necessárias para a comparação.

    Returns:
        Tuple contendo (success_flag, functions_dict)
    """
    plotting_functions = {}

    try:
        from scripts.plotting.generate_graphics import (  # Distribution charts for new tabs; Additional function that might be needed; New resolution chart imports
            plot_acuracia_por_metodologia,
            plot_class_diversity_focus,
            plot_classes_frequency_boxplot,
            plot_classification_methodology,
            plot_distribuicao_classes,
            plot_distribuicao_metodologias,
            plot_global_accuracy_comparison,
            plot_initiativas_by_resolution_category,
            plot_normalized_performance_heatmap,
            plot_resolution_accuracy_scatter,
            plot_resolution_by_sensor_family,
            plot_resolution_coverage_heatmap,
            plot_resolution_slopegraph,
            plot_resolution_vs_launch_year,
            plot_spatial_resolution_comparison,
            plot_temporal_evolution_frequency,
        )

        # Store all functions in dict
        plotting_functions = {
            "plot_resolution_accuracy_scatter": plot_resolution_accuracy_scatter,
            "plot_classes_frequency_boxplot": plot_classes_frequency_boxplot,
            "plot_spatial_resolution_comparison": plot_spatial_resolution_comparison,
            "plot_global_accuracy_comparison": plot_global_accuracy_comparison,
            "plot_temporal_evolution_frequency": plot_temporal_evolution_frequency,
            "plot_class_diversity_focus": plot_class_diversity_focus,
            "plot_classification_methodology": plot_classification_methodology,
            "plot_resolution_vs_launch_year": plot_resolution_vs_launch_year,
            "plot_resolution_coverage_heatmap": plot_resolution_coverage_heatmap,
            "plot_resolution_by_sensor_family": plot_resolution_by_sensor_family,
            "plot_resolution_slopegraph": plot_resolution_slopegraph,
            "plot_distribuicao_classes": plot_distribuicao_classes,
            "plot_distribuicao_metodologias": plot_distribuicao_metodologias,
            "plot_acuracia_por_metodologia": plot_acuracia_por_metodologia,
            "plot_normalized_performance_heatmap": plot_normalized_performance_heatmap,
            "plot_initiativas_by_resolution_category": plot_initiativas_by_resolution_category,
        }

        st.success("✅ All plotting functions imported successfully!")
        return True, plotting_functions

    except ImportError as e:
        st.error(f"❌ Failed to import plotting functions: {e}")
        return False, {}


def get_plotting_placeholders() -> dict:
    """
    Retorna funções placeholder para quando as importações falham.

    Returns:
        Dict com funções placeholder
    """

    def create_placeholder(function_name: str):
        """Cria uma função placeholder para uma função específica."""

        def placeholder(*args, **kwargs):
            st.warning(
                f"Placeholder: {function_name} not available due to import error."
            )
            return go.Figure().add_annotation(
                text=f"{function_name} not available",
                showarrow=False,
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                font={"size": 16, "color": "red"},
            )

        return placeholder

    # List of all plotting functions needed
    function_names = [
        "plot_resolution_accuracy_scatter",
        "plot_classes_frequency_boxplot",
        "plot_spatial_resolution_comparison",
        "plot_global_accuracy_comparison",
        "plot_temporal_evolution_frequency",
        "plot_class_diversity_focus",
        "plot_classification_methodology",
        "plot_resolution_vs_launch_year",
        "plot_resolution_coverage_heatmap",
        "plot_resolution_by_sensor_family",
        "plot_resolution_slopegraph",
        "plot_distribuicao_classes",
        "plot_distribuicao_metodologias",
        "plot_acuracia_por_metodologia",
        "plot_normalized_performance_heatmap",
        "plot_initiativas_by_resolution_category",
    ]

    return {name: create_placeholder(name) for name in function_names}


def setup_plotting_functions() -> tuple[bool, dict]:
    """
    Configura as funções de plotting, usando placeholders se necessário.

    Returns:
        Tuple contendo (success_flag, functions_dict)
    """
    # Try to import real functions first
    success, functions = import_plotting_functions()

    if not success:
        st.warning("Using placeholder functions for plotting")
        functions = get_plotting_placeholders()

    return success, functions
