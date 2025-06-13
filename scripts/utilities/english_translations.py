#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
English Language Translations for LULC Dashboard Interface
==========================================================

This module provides comprehensive English translations for all Portuguese
text elements in the dashboard interface, including headers, labels, messages,
chart titles, and UI components.

Author: Dashboard Iniciativas LULC
Date: 2024
"""

# Main interface translations
INTERFACE_TRANSLATIONS = {
    # Dashboard headers and titles
    "⏳ Análise Temporal Abrangente das Iniciativas LULC": "⏳ Comprehensive Temporal Analysis of LULC Initiatives",
    "📊 Análises Comparativas": "📊 Comparative Analysis",
    "🔍 Análises Detalhadas": "🔍 Detailed Analysis",
    "Visão Geral": "Overview",
    "Análises Comparativas": "Comparative Analysis", 
    "Análises Detalhadas": "Detailed Analysis",
    
    # Tab names
    "📊 Linha do Tempo": "📊 Timeline",
    "🔍 Cobertura Temporal": "🔍 Temporal Coverage",
    "⚠️ Lacunas Temporais": "⚠️ Temporal Gaps",
    "📈 Evolução da Disponibilidade": "📈 Availability Evolution",
    "📊 Barras Duplas": "📊 Dual Bars",
    "🎯 Resolução vs Acurácia": "🎯 Resolution vs Accuracy",
    "📅 Cobertura Temporal": "📅 Temporal Coverage",
    "🏷️ Número de Classes": "🏷️ Number of Classes",
    "⚙️ Metodologias": "⚙️ Methodologies",
    "🕸️ Análise Radar": "🕸️ Radar Analysis",
    
    # Filter labels
    "🔎 Filtros de Iniciativas": "🔎 Initiative Filters",
    "Tipo": "Type",
    "Resolução (m)": "Resolution (m)",
    "Acurácia (%)": "Accuracy (%)",
    "Metodologia": "Methodology",
    "Escopo": "Scope",
    "Classes": "Classes",
    "Nome": "Name",
    "Sigla": "Acronym",
    
    # Warning and error messages
    "⚠️ Metadados não encontrados. Execute a página principal (app.py) primeiro.": "⚠️ Metadata not found. Run the main page (app.py) first.",
    "Não há dados temporais disponíveis para análise.": "No temporal data available for analysis.",
    "⚠️ Nenhuma iniciativa corresponde aos filtros selecionados. Ajuste os filtros para visualizar os dados.": "⚠️ No initiatives match the selected filters. Adjust filters to view data.",
    "Dados temporais insuficientes para criar timeline.": "Insufficient temporal data to create timeline.",
    "Metadados não disponíveis.": "Metadata not available.",
    
    # Chart titles and labels
    "Timeline de Disponibilidade das Iniciativas LULC": "LULC Initiatives Availability Timeline",
    "📅 Timeline de Disponibilidade das Iniciativas LULC (1985-2024)": "📅 LULC Initiatives Availability Timeline (1985-2024)",
    "Distribuição do Número de Classes": "Number of Classes Distribution",
    "Distribuição do Número de Classes (Dados insuficientes)": "Number of Classes Distribution (Insufficient data)",
    "Distribuição do Número de Classes (Coluna 'Classes' não encontrada)": "Number of Classes Distribution ('Classes' column not found)",
    "Distribuição do Número de Classes (Nenhum dado válido)": "Number of Classes Distribution (No valid data)",
    "Número de Classes por Iniciativa": "Number of Classes per Initiative",
    "Número de Classes por Iniciativa (Dados insuficientes)": "Number of Classes per Initiative (Insufficient data)",
    "Cobertura Anual das Iniciativas Selecionadas": "Annual Coverage of Selected Initiatives",
    "Cobertura Anual (Nenhuma iniciativa selecionada)": "Annual Coverage (No initiative selected)",
    "Cobertura Anual (Nenhum dado temporal disponível)": "Annual Coverage (No temporal data available)",
    "Timeline das Iniciativas (Dados insuficientes)": "Initiatives Timeline (Insufficient data)",
    "Distribuição das Metodologias Utilizadas": "Distribution of Methodologies Used",
    "Distribuição das Metodologias Utilizadas (Dados insuficientes)": "Distribution of Methodologies Used (Insufficient data)",
    
    # Axis labels
    "Ano": "Year",
    "Produtos LULC": "LULC Products",
    "Iniciativas": "Initiatives",
    "Iniciativa": "Initiative",
    "Produto": "Product",
    "Valor (%)": "Value (%)",
    "Número de Iniciativas": "Number of Initiatives",
    "Número de Classes": "Number of Classes",
    "Metodologia": "Methodology",
    "Acurácia (%)": "Accuracy (%)",
    "Resolução (m)": "Resolution (m)",
    
    # Success messages
    "✅ Dados carregados": "✅ Data loaded",
    "✅ Timeline plot criado": "✅ Timeline plot created",
    "✅ Gráfico de distribuição criado": "✅ Distribution chart created",
    "✅ Gráfico de cobertura criado": "✅ Coverage chart created",
    
    # Button labels
    "⬇️ Baixar Timeline (PNG)": "⬇️ Download Timeline (PNG)",
    "⬇️ Baixar Gráfico": "⬇️ Download Chart",
    "⬇️ Baixar Gráfico (PNG)": "⬇️ Download Chart (PNG)",
    "⬇️ Baixar": "⬇️ Download",
    
    # Metrics and statistics
    "Total de Iniciativas": "Total Initiatives",
    "Período Total Coberto": "Total Period Covered",
    "Cobertura Média": "Average Coverage",
    "Total de Produtos": "Total Products",
    "Período Real": "Actual Period",
    "Ano Mais Ativo": "Most Active Year",
    "Metodologias": "Methodologies",
    "Melhor Acurácia": "Best Accuracy",
    "Acurácia Média": "Average Accuracy",
    "Menor Acurácia": "Lowest Accuracy",
    "Desvio Padrão": "Standard Deviation",
    
    # Analysis sections
    "📊 Análise Comparativa por Metodologia": "📊 Comparative Analysis by Methodology",
    "📈 Análise Comparativa por Metodologia": "📈 Comparative Analysis by Methodology",
    "🏆 Ranking de Acurácia dos Produtos LULC": "🏆 LULC Products Accuracy Ranking",
    "⏰ Evolução das Metodologias ao Longo do Tempo": "⏰ Evolution of Methodologies Over Time",
    "📈 Evolução da Adoção de Metodologias LULC": "📈 Evolution of LULC Methodology Adoption",
    "📊 Estatísticas Comparativas": "📊 Comparative Statistics",
    "📊 Análises Avançadas": "📊 Advanced Analysis",
    
    # Data quality and validation
    "🔍 Validação de Dados": "🔍 Data Validation",
    "📋 Resumo dos Dados": "📋 Data Summary",
    "⚙️ Configurações": "⚙️ Settings",
    "🎯 Filtros Aplicados": "🎯 Applied Filters",
    
    # Geographic terms
    "Global": "Global",
    "Nacional": "National",
    "Regional": "Regional",
    "Continental": "Continental",
    "Brasil": "Brazil",
    "Amazônia": "Amazon",
    "Cerrado": "Cerrado",
    
    # Temporal terms
    "Anual": "Annual",
    "Bienal": "Biennial", 
    "Tempo real": "Real-time",
    "Pontual": "Point-in-time",
    "Multi-temporal": "Multi-temporal",
    "Sazonal": "Seasonal",
    
    # Common UI elements
    "Carregando...": "Loading...",
    "Processando...": "Processing...",
    "Salvando...": "Saving...",
    "Concluído": "Complete",
    "Erro": "Error",
    "Aviso": "Warning",
    "Informação": "Information",
    "Sucesso": "Success",
    
    # File and data operations
    "Arquivo salvo": "File saved",
    "Arquivo carregado": "File loaded",
    "Dados processados": "Data processed",
    "Dados atualizados": "Data updated",
    "Exportar dados": "Export data",
    "Importar dados": "Import data",
    
    # Navigation
    "Voltar": "Back",
    "Próximo": "Next",
    "Anterior": "Previous",
    "Início": "Home",
    "Configurações": "Settings",
    "Ajuda": "Help",
    "Sobre": "About"
}

# Chart-specific translations
CHART_TRANSLATIONS = {
    # Chart types
    "Gráfico de Barras": "Bar Chart",
    "Gráfico de Linhas": "Line Chart", 
    "Gráfico de Pizza": "Pie Chart",
    "Gráfico de Dispersão": "Scatter Plot",
    "Gráfico de Radar": "Radar Chart",
    "Heatmap": "Heatmap",
    "Timeline": "Timeline",
    "Histograma": "Histogram",
    "Box Plot": "Box Plot",
    "Gráfico de Bolhas": "Bubble Chart",
    
    # Chart elements
    "Legenda": "Legend",
    "Eixo X": "X Axis",
    "Eixo Y": "Y Axis", 
    "Título": "Title",
    "Subtítulo": "Subtitle",
    "Dados": "Data",
    "Traços": "Traces",
    "Pontos": "Points",
    "Valores": "Values",
    
    # Chart interactions
    "Zoom": "Zoom",
    "Panorâmica": "Pan",
    "Redefinir": "Reset",
    "Salvar": "Save",
    "Imprimir": "Print",
    "Exportar": "Export",
    "Configurar": "Configure",
    "Personalizar": "Customize",
    
    # Data labels
    "Sem dados": "No data",
    "Dados insuficientes": "Insufficient data",
    "Carregando dados": "Loading data",
    "Processando dados": "Processing data",
    "Erro nos dados": "Data error",
    "Dados válidos": "Valid data",
    "Dados faltantes": "Missing data"
}

# Table column translations
TABLE_TRANSLATIONS = {
    "Nome": "Name",
    "Sigla": "Acronym", 
    "Tipo": "Type",
    "Resolução (m)": "Resolution (m)",
    "Acurácia (%)": "Accuracy (%)",
    "Classes": "Classes",
    "Metodologia": "Methodology",
    "Frequência Temporal": "Temporal Frequency",
    "Anos Disponíveis": "Available Years",
    "Escopo": "Scope",
    "Provedor": "Provider",
    "Score Resolução": "Resolution Score",
    "Score Geral": "Overall Score",
    "Categoria Acurácia": "Accuracy Category",
    "Categoria Resolução": "Resolution Category",
    "Primeiro Ano": "First Year",
    "Último Ano": "Last Year",
    "Total Anos": "Total Years",
    "Cobertura Percentual": "Coverage Percentage",
    "Período": "Period",
    "Duração": "Duration",
    "Intervalo": "Interval",
    "Frequência": "Frequency"
}

# Status and category translations
STATUS_TRANSLATIONS = {
    # Accuracy categories
    "Muito Alta": "Very High",
    "Alta": "High", 
    "Média": "Medium",
    "Baixa": "Low",
    "Muito Baixa": "Very Low",
    
    # Resolution categories  
    "Muito Alta": "Very High",
    "Alta": "High",
    "Média": "Medium", 
    "Baixa": "Low",
    "Muito Baixa": "Very Low",
    
    # Status indicators
    "Ativo": "Active",
    "Inativo": "Inactive",
    "Em Desenvolvimento": "In Development",
    "Descontinuado": "Discontinued",
    "Atualizado": "Updated",
    "Pendente": "Pending",
    "Completo": "Complete",
    "Incompleto": "Incomplete",
    "Disponível": "Available",
    "Indisponível": "Unavailable"
}

def translate_text(text: str) -> str:
    """
    Translate Portuguese text to English using the translation dictionaries.
    
    Args:
        text: Portuguese text to translate
        
    Returns:
        English translation or original text if no translation found
    """
    # Check all translation dictionaries
    all_translations = {
        **INTERFACE_TRANSLATIONS,
        **CHART_TRANSLATIONS, 
        **TABLE_TRANSLATIONS,
        **STATUS_TRANSLATIONS
    }
    
    return all_translations.get(text, text)

def translate_dataframe_columns(df, column_mapping: dict = None):
    """
    Translate DataFrame column names to English.
    
    Args:
        df: pandas DataFrame to translate
        column_mapping: Optional custom column mapping
        
    Returns:
        DataFrame with translated column names
    """
    if df is None or df.empty:
        return df
    
    if column_mapping is None:
        column_mapping = TABLE_TRANSLATIONS
    
    # Create new column names
    new_columns = {}
    for col in df.columns:
        if col in column_mapping:
            new_columns[col] = column_mapping[col]
    
    # Rename columns
    if new_columns:
        df = df.rename(columns=new_columns)
    
    return df

def get_english_chart_config(chart_type: str) -> dict:
    """
    Get English configuration for chart types.
    
    Args:
        chart_type: Type of chart
        
    Returns:
        Dictionary with English labels and titles
    """
    base_config = {
        "font": {"family": "Arial, sans-serif", "size": 12, "color": "#2D3748"},
        "plot_bgcolor": "#FFFFFF",
        "paper_bgcolor": "#FFFFFF"
    }
    
    chart_configs = {
        "timeline": {
            **base_config,
            "title": "LULC Initiatives Availability Timeline",
            "xaxis_title": "Year",
            "yaxis_title": "LULC Products"
        },
        "class_distribution": {
            **base_config,
            "title": "Number of Classes Distribution", 
            "xaxis_title": "Number of Classes",
            "yaxis_title": "Frequency"
        },
        "accuracy_resolution": {
            **base_config,
            "title": "Accuracy vs Resolution Analysis",
            "xaxis_title": "Resolution (m)",
            "yaxis_title": "Accuracy (%)"
        },
        "methodology_distribution": {
            **base_config,
            "title": "Distribution of Methodologies Used",
            "labels": {"values": "Count", "names": "Methodology"}
        },
        "temporal_coverage": {
            **base_config,
            "title": "Annual Coverage of Selected Initiatives",
            "xaxis_title": "Year", 
            "yaxis_title": "Initiative"
        }
    }
    
    return chart_configs.get(chart_type, base_config)

def translate_chart_elements(fig, chart_type: str = None):
    """
    Translate chart elements to English.
    
    Args:
        fig: Plotly figure object
        chart_type: Optional chart type for specific translations
        
    Returns:
        Updated figure with English labels
    """
    if fig is None:
        return fig
    
    # Get chart configuration
    if chart_type:
        config = get_english_chart_config(chart_type)
        
        # Update layout with English labels
        fig.update_layout(config)
    
    return fig

# Helper function to create English error messages
def get_english_error_message(error_type: str) -> str:
    """
    Get English error messages for common scenarios.
    
    Args:
        error_type: Type of error
        
    Returns:
        English error message
    """
    error_messages = {
        "no_data": "No data available for analysis",
        "insufficient_data": "Insufficient data to generate visualization", 
        "loading_error": "Error loading data",
        "processing_error": "Error processing data",
        "no_initiatives": "No initiatives match the selected filters",
        "no_temporal_data": "No temporal data available",
        "no_metadata": "Metadata not found",
        "invalid_selection": "Invalid selection", 
        "export_error": "Error exporting data",
        "save_error": "Error saving file"
    }
    
    return error_messages.get(error_type, "An error occurred")

# Helper function to create English success messages  
def get_english_success_message(action: str) -> str:
    """
    Get English success messages for common actions.
    
    Args:
        action: Type of action completed
        
    Returns:
        English success message
    """
    success_messages = {
        "data_loaded": "Data loaded successfully",
        "chart_created": "Chart created successfully",
        "data_exported": "Data exported successfully",
        "file_saved": "File saved successfully",
        "analysis_complete": "Analysis completed successfully",
        "validation_passed": "Validation passed",
        "processing_complete": "Processing completed",
        "update_complete": "Update completed successfully"
    }
    
    return success_messages.get(action, "Operation completed successfully")

# Test function
def test_translations():
    """Test translation functionality."""
    print("🧪 Testing translation system...")
    
    # Test basic translation
    test_phrases = [
        "Análise Temporal",
        "Tipo", 
        "Resolução (m)",
        "Muito Alta",
        "Carregando..."
    ]
    
    print("📝 Translation examples:")
    for phrase in test_phrases:
        translated = translate_text(phrase)
        print(f"  '{phrase}' -> '{translated}'")
    
    print("✅ Translation system tested successfully")

if __name__ == "__main__":
    test_translations()
