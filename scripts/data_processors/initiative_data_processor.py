#!/usr/bin/env python3
"""
Processador de Dados das Iniciativas LULC
==========================================

Módulo responsável por processar e traduzir os metadados JSON das iniciativas
para formatos consistentes usados nos gráficos.

Author: Dashboard Iniciativas LULC
Date: 2025-07-29
"""

import logging
from typing import Any

import pandas as pd

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def translate_coverage_type(coverage: str) -> str:
    """
    Traduz o tipo de coverage para português.

    Args:
        coverage: Tipo de coverage em inglês

    Returns:
        str: Tipo traduzido em português
    """
    coverage_map = {
        "Global": "Global",
        "Regional": "Regional",
        "National": "Nacional",
        "Local": "Local",
        "Continental": "Continental",
        "Amazon": "Amazônia",
        "Cerrado": "Cerrado",
        "Brazil": "Brasil",
        "South America": "América do Sul",
    }
    return coverage_map.get(coverage, coverage)


def translate_methodology(methodology: str) -> str:
    """
    Traduz metodologia para português.

    Args:
        methodology: Metodologia em inglês

    Returns:
        str: Metodologia traduzida
    """
    methodology_map = {
        "Machine Learning": "Aprendizado de Máquina",
        "Deep Learning": "Aprendizado Profundo",
        "Random Forest": "Floresta Aleatória",
        "Neural Networks": "Redes Neurais",
        "Supervised Classification": "Classificação Supervisionada",
        "Unsupervised Classification": "Classificação Não Supervisionada",
        "Object-based": "Baseada em Objetos",
        "Pixel-based": "Baseada em Pixels",
        "Time Series Analysis": "Análise de Séries Temporais",
        "Spectral Analysis": "Análise Espectral",
        "Visual Interpretation": "Interpretação Visual",
        "Statistical Analysis": "Análise Estatística",
        "N/A": "N/A",
        "Not Available": "Não Disponível",
        "Unknown": "Desconhecido",
    }
    return methodology_map.get(methodology, methodology)


def process_initiative_metadata(raw_metadata: dict[str, Any]) -> dict[str, Any]:
    """
    Processa e padroniza os metadados de uma iniciativa.

    Args:
        raw_metadata: Metadados brutos do JSON

    Returns:
        Dict[str, Any]: Metadados processados e padronizados
    """
    if not isinstance(raw_metadata, dict):
        logger.warning(f"Metadados não são um dicionário: {type(raw_metadata)}")
        return {}

    # Extrair anos disponíveis
    available_years = []
    years_key = (
        "available_years" if "available_years" in raw_metadata else "anos_disponiveis"
    )

    if years_key in raw_metadata:
        years_raw = raw_metadata[years_key]
        if isinstance(years_raw, list):
            available_years = [
                int(year)
                for year in years_raw
                if pd.notna(year) and str(year).strip().isdigit()
            ]
        elif isinstance(years_raw, str):
            # Tentar parsear string com anos separados por vírgula
            try:
                available_years = [
                    int(year.strip())
                    for year in years_raw.split(",")
                    if year.strip().isdigit()
                ]
            except (ValueError, AttributeError):
                available_years = []

    # Processar dados básicos
    processed_data = {
        "acronym": raw_metadata.get("acronym", "Unknown"),
        "full_name": raw_metadata.get("full_name", "Unknown"),
        "available_years": sorted(available_years) if available_years else [],
        "coverage": translate_coverage_type(raw_metadata.get("coverage", "Unknown")),
        "methodology": translate_methodology(raw_metadata.get("methodology", "N/A")),
        "organization": raw_metadata.get("organization", "Unknown"),
        "sensor": raw_metadata.get("sensor", "Unknown"),
        "resolution": raw_metadata.get("resolution", "Unknown"),
        "start_year": min(available_years) if available_years else None,
        "end_year": max(available_years) if available_years else None,
        "total_years": len(available_years) if available_years else 0,
        "data_frequency": raw_metadata.get("data_frequency", "Unknown"),
        "update_frequency": raw_metadata.get("update_frequency", "Unknown"),
    }

    # Calcular período ativo
    if processed_data["start_year"] and processed_data["end_year"]:
        processed_data["active_period"] = (
            f"{processed_data['start_year']}-{processed_data['end_year']}"
        )
        processed_data["period_duration"] = (
            processed_data["end_year"] - processed_data["start_year"] + 1
        )
    else:
        processed_data["active_period"] = "N/A"
        processed_data["period_duration"] = 0

    logger.info(
        f"Processado: {processed_data['acronym']} - {len(available_years)} anos"
    )

    return processed_data


def process_all_initiatives_metadata(
    raw_initiatives_metadata: dict[str, Any],
) -> dict[str, Any]:
    """
    Processa todos os metadados das iniciativas.

    Args:
        raw_initiatives_metadata: Dicionário com metadados brutos

    Returns:
        Dict[str, Any]: Dicionário com metadados processados
    """
    if not raw_initiatives_metadata:
        logger.warning("Nenhum metadado fornecido")
        return {}

    processed_initiatives = {}

    logger.info(f"Processando {len(raw_initiatives_metadata)} iniciativas...")

    for initiative_name, raw_metadata in raw_initiatives_metadata.items():
        try:
            processed_data = process_initiative_metadata(raw_metadata)
            if processed_data and processed_data.get("available_years"):
                processed_initiatives[initiative_name] = processed_data
            else:
                logger.warning(f"Iniciativa {initiative_name} não tem dados válidos")
        except Exception as e:
            logger.error(f"Erro ao processar {initiative_name}: {str(e)}")
            continue

    logger.info(
        f"Processamento concluído: {len(processed_initiatives)} iniciativas válidas"
    )

    return processed_initiatives


def generate_timeline_data(
    processed_metadata: dict[str, Any], filtered_df: pd.DataFrame = None
) -> list[dict[str, Any]]:
    """
    Gera dados estruturados para o gráfico timeline.

    Args:
        processed_metadata: Metadados processados das iniciativas
        filtered_df: DataFrame filtrado (opcional)

    Returns:
        List[Dict[str, Any]]: Lista de dados estruturados para timeline
    """
    timeline_data = []

    # Criar mapeamento nome->acronym do DataFrame se disponível
    name_to_acronym = {}
    if (
        filtered_df is not None
        and not filtered_df.empty
        and "Name" in filtered_df.columns
        and "Acronym" in filtered_df.columns
    ):
        for _, row in filtered_df.iterrows():
            if pd.notna(row["Name"]) and pd.notna(row["Acronym"]):
                name_to_acronym[row["Name"]] = row["Acronym"]

    for initiative_name, metadata in processed_metadata.items():
        if not metadata.get("available_years"):
            continue

        # Usar acronym do DataFrame se disponível, senão usar dos metadados
        display_acronym = name_to_acronym.get(initiative_name, metadata["acronym"])

        timeline_item = {
            "name": initiative_name,
            "acronym": display_acronym,
            "display_name": display_acronym,
            "full_name": metadata["full_name"],
            "start_year": metadata["start_year"],
            "end_year": metadata["end_year"],
            "years": metadata["available_years"],
            "type": metadata["coverage"],
            "methodology": metadata["methodology"],
            "organization": metadata["organization"],
            "sensor": metadata["sensor"],
            "resolution": metadata["resolution"],
            "period_duration": metadata["period_duration"],
            "total_years_available": metadata["total_years"],
            "data_frequency": metadata["data_frequency"],
            "update_frequency": metadata["update_frequency"],
        }

        timeline_data.append(timeline_item)

    # Ordenar por ano de início
    timeline_data.sort(key=lambda x: x["start_year"] if x["start_year"] else 9999)

    logger.info(f"Gerados dados de timeline para {len(timeline_data)} iniciativas")

    return timeline_data


def get_timeline_summary_stats(timeline_data: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Calcula estatísticas resumidas dos dados do timeline.

    Args:
        timeline_data: Dados do timeline

    Returns:
        Dict[str, Any]: Estatísticas resumidas
    """
    if not timeline_data:
        return {
            "total_initiatives": 0,
            "earliest_year": None,
            "latest_year": None,
            "total_period": "N/A",
            "total_years_available": 0,
            "coverage_types": [],
            "methodologies": [],
        }

    all_years = []
    coverage_types = set()
    methodologies = set()
    total_years_available = 0

    for item in timeline_data:
        if item["years"]:
            all_years.extend(item["years"])
        if item["type"]:
            coverage_types.add(item["type"])
        if item["methodology"]:
            methodologies.add(item["methodology"])
        total_years_available += item["total_years_available"]

    earliest_year = min(all_years) if all_years else None
    latest_year = max(all_years) if all_years else None

    return {
        "total_initiatives": len(timeline_data),
        "earliest_year": earliest_year,
        "latest_year": latest_year,
        "total_period": (
            f"{earliest_year}-{latest_year}" if earliest_year and latest_year else "N/A"
        ),
        "total_years_available": total_years_available,
        "coverage_types": sorted(coverage_types),
        "methodologies": sorted(methodologies),
        "period_span_years": (
            (latest_year - earliest_year + 1) if earliest_year and latest_year else 0
        ),
    }
