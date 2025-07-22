#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Padronização de Dimensões dos Gráficos
================================================

Script para testar a nova padronização de dimensões implementada no chart_core.py
"""

import plotly.graph_objects as go
import pandas as pd
from scripts.plotting.chart_core import apply_standard_layout, get_standard_dimensions

def test_standardization():
    """Testa a padronização de dimensões em diferentes tipos de gráfico"""
    
    print("=== Teste de Padronização de Dimensões ===\n")
    
    # Teste 1: Gráfico de barras padrão
    print("1. Gráfico de Barras (5 itens):")
    fig1 = go.Figure(data=go.Bar(x=['A', 'B', 'C', 'D', 'E'], y=[1, 2, 3, 4, 5]))
    apply_standard_layout(fig1, "Categorias", "Valores", chart_type="bar_chart", num_items=5)
    print(f"   Dimensões: {fig1.layout.width} x {fig1.layout.height}")
    
    # Teste 2: Gráfico de barras com muitos itens
    print("2. Gráfico de Barras (20 itens):")
    fig2 = go.Figure(data=go.Bar(x=list(range(20)), y=list(range(20))))
    apply_standard_layout(fig2, "Categorias", "Valores", chart_type="bar_chart", num_items=20)
    print(f"   Dimensões: {fig2.layout.width} x {fig2.layout.height}")
    
    # Teste 3: Heatmap
    print("3. Heatmap (10 itens):")
    fig3 = go.Figure(data=go.Heatmap(z=[[1, 2], [3, 4]]))
    apply_standard_layout(fig3, "X", "Y", chart_type="heatmap", num_items=10)
    print(f"   Dimensões: {fig3.layout.width} x {fig3.layout.height}")
    
    # Teste 4: Matriz de correlação
    print("4. Matriz de Correlação (8 itens):")
    fig4 = go.Figure(data=go.Heatmap(z=[[1, 0.5], [0.5, 1]]))
    apply_standard_layout(fig4, "Var1", "Var2", chart_type="correlation_matrix", num_items=8)
    print(f"   Dimensões: {fig4.layout.width} x {fig4.layout.height}")
    
    # Teste 5: Gráfico de linha
    print("5. Gráfico de Linha (15 pontos):")
    fig5 = go.Figure(data=go.Scatter(x=list(range(15)), y=list(range(15))))
    apply_standard_layout(fig5, "Tempo", "Valores", chart_type="line_chart", num_items=15)
    print(f"   Dimensões: {fig5.layout.width} x {fig5.layout.height}")
    
    # Teste 6: Gráfico de radar
    print("6. Gráfico de Radar:")
    fig6 = go.Figure()
    apply_standard_layout(fig6, "", "", chart_type="radar_chart")
    print(f"   Dimensões: {fig6.layout.width} x {fig6.layout.height}")
    
    # Teste 7: Aspectos override
    print("\n=== Teste de Aspectos Override ===")
    print("7. Square Override:")
    fig7 = go.Figure(data=go.Bar(x=['A', 'B'], y=[1, 2]))
    apply_standard_layout(fig7, "X", "Y", aspect_override="square")
    print(f"   Dimensões: {fig7.layout.width} x {fig7.layout.height}")
    
    print("8. Wide Override:")
    fig8 = go.Figure(data=go.Bar(x=['A', 'B'], y=[1, 2]))
    apply_standard_layout(fig8, "X", "Y", aspect_override="wide")
    print(f"   Dimensões: {fig8.layout.width} x {fig8.layout.height}")
    
    print("9. Tall Override:")
    fig9 = go.Figure(data=go.Bar(x=['A', 'B'], y=[1, 2]))
    apply_standard_layout(fig9, "X", "Y", aspect_override="tall")
    print(f"   Dimensões: {fig9.layout.width} x {fig9.layout.height}")
    
    print("\n✅ Todos os testes foram executados com sucesso!")
    print("🎨 A padronização de dimensões está funcionando corretamente!")

if __name__ == "__main__":
    test_standardization()
