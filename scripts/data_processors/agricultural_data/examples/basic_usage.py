#!/usr/bin/env python3
"""
Exemplo Básico - Uso dos Processadores de Dados Agrícolas
=========================================================

Este exemplo mostra como usar os novos processadores de dados
agrícolas no dashboard.
"""

from pathlib import Path

# Importar o wrapper de dados agrícolas
from scripts.data_processors.agricultural_data import get_agricultural_data


def exemplo_basico():
    """Exemplo básico de uso dos processadores."""

    # Obter instância global dos dados agrícolas
    agri_data = get_agricultural_data()

    # Verificar fontes disponíveis
    print("Fontes disponíveis:", agri_data.get_available_sources())

    # Obter calendário agrícola
    calendar_df = agri_data.get_crop_calendar("CONAB")
    print(f"Calendário carregado: {len(calendar_df)} registros")

    # Obter resumo por região
    summary_df = agri_data.get_crop_calendar_summary("CONAB")
    print(f"Resumo: {len(summary_df)} combinações região-cultura")

    # Filtrar por cultura específica
    soybean_calendar = agri_data.get_filtered_calendar(
        crops=["Soybean"], regions=["Central-West"]
    )
    print(f"Calendário da soja no Centro-Oeste: {len(soybean_calendar)} registros")

    return calendar_df, summary_df, soybean_calendar


def exemplo_avancado():
    """Exemplo avançado com múltiplas operações."""

    # Inicializar com diretório específico
    from scripts.data_processors.agricultural_data import initialize_agricultural_data

    agri_data = initialize_agricultural_data("data")

    # Obter informações sazonais
    seasonal_info = agri_data.get_planting_harvest_info("CONAB")

    # Exportar dados filtrados
    filtered_data = agri_data.get_filtered_calendar(
        crops=["Cotton", "Corn"], regions=["North", "Northeast"]
    )

    # Exportar para CSV
    output_path = Path("exports/filtered_calendar.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    agri_data.export_calendar_data(output_path, "csv", "CONAB")

    print(f"Dados exportados para: {output_path}")

    return seasonal_info, filtered_data


if __name__ == "__main__":
    print("=== Exemplo Básico ===")
    exemplo_basico()

    print("\n=== Exemplo Avançado ===")
    exemplo_avancado()
