import plotly.graph_objects as go
import pandas as pd

def plot_radar_comparacao(data1, data2, filtered_df, init1, init2):
    categories = ['Acurácia (%)', 'Resolução (m)', 'Classes']
    def normalize_for_radar(value, column, df):
        if column == 'Resolução (m)':
            return (df[column].max() - value) / (df[column].max() - df[column].min()) * 100
        else:
            return (value - df[column].min()) / (df[column].max() - df[column].min()) * 100
    values1 = [normalize_for_radar(data1[cat], cat, filtered_df) for cat in categories]
    values2 = [normalize_for_radar(data2[cat], cat, filtered_df) for cat in categories]
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values1 + [values1[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=init1,
        line_color='#ff6b6b'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=values2 + [values2[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=init2,
        line_color='#4dabf7'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title="Comparação em Gráfico Radar (Valores Normalizados)",
        height=500,
        font=dict(size=12, family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig_radar
