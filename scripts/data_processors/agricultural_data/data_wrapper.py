#!/usr/bin/env python3
"""
Agricultural Data Wrapper
==========================

Wrapper que conecta os processadores de dados agrícolas ao sistema existente
do dashboard. Fornece interface unificada para acesso aos dados processados
por diferentes fontes (CONAB, IBGE, etc.).

Características:
- Interface unificada para múltiplas fontes de dados agrícolas
- Cache automático e otimização de performance
- Compatibilidade com sistema existente do dashboard
- Suporte a filtros e agregações

Author: Dashboard Iniciativas LULC
Date: 2025
"""

import warnings
from pathlib import Path
from typing import Any

import pandas as pd

from .conab_processor import create_conab_processor

warnings.filterwarnings("ignore")


class AgriculturalDataWrapper:
    """
    Wrapper unificado para acesso a dados agrícolas processados.

    Centraliza o acesso a diferentes fontes de dados agrícolas
    e fornece interface consistente para o dashboard.
    """

    def __init__(self, data_directory: str | Path = None):
        """
        Inicializa wrapper de dados agrícolas.

        Args:
            data_directory: Diretório com dados agrícolas
        """
        self.data_directory = Path(data_directory) if data_directory else Path("data")
        self.processors: dict[str, Any] = {}
        self._initialize_processors()

    def _initialize_processors(self) -> None:
        """Inicializa processadores disponíveis."""
        # Inicializar processador CONAB
        conab_data_path = self.data_directory / "conab_crop_calendar.jsonc"
        if conab_data_path.exists():
            try:
                self.processors["CONAB"] = create_conab_processor(conab_data_path)
                print(
                    f"✅ Processador CONAB inicializado com dados de {conab_data_path}"
                )
            except Exception as e:
                print(f"⚠️ Erro ao inicializar processador CONAB: {e}")

        # Adicionar outros processadores no futuro (IBGE, etc.)

    def get_available_sources(self) -> list[str]:
        """Retorna fontes de dados disponíveis."""
        return list(self.processors.keys())

    def get_crop_calendar(self, source: str = "CONAB") -> pd.DataFrame:
        """
        Retorna calendário agrícola de uma fonte específica.

        Args:
            source: Fonte de dados (padrão: CONAB)

        Returns:
            DataFrame com calendário agrícola
        """
        if source not in self.processors:
            raise ValueError(
                f"Fonte {source} não disponível. Fontes: {self.get_available_sources()}"
            )

        return self.processors[source].get_crop_calendar()

    def get_production_data(self, source: str = "CONAB") -> pd.DataFrame:
        """
        Retorna dados de produção de uma fonte específica.

        Args:
            source: Fonte de dados (padrão: CONAB)

        Returns:
            DataFrame com dados de produção
        """
        if source not in self.processors:
            raise ValueError(
                f"Fonte {source} não disponível. Fontes: {self.get_available_sources()}"
            )

        try:
            return self.processors[source].get_production_data()
        except ValueError:
            # Retornar DataFrame vazio se dados não disponíveis
            return pd.DataFrame()

    def get_crop_calendar_summary(self, source: str = "CONAB") -> pd.DataFrame:
        """
        Retorna resumo do calendário agrícola.

        Args:
            source: Fonte de dados (padrão: CONAB)

        Returns:
            DataFrame com resumo por região e cultura
        """
        if source not in self.processors:
            raise ValueError(
                f"Fonte {source} não disponível. Fontes: {self.get_available_sources()}"
            )

        processor = self.processors[source]
        if hasattr(processor, "get_calendar_summary"):
            return processor.get_calendar_summary()

        # Fallback para processadores sem método específico
        calendar_df = processor.get_crop_calendar()
        return self._generate_basic_summary(calendar_df)

    def _generate_basic_summary(self, calendar_df: pd.DataFrame) -> pd.DataFrame:
        """Gera resumo básico do calendário."""
        summary_data = []

        if "crop" in calendar_df.columns and "region" in calendar_df.columns:
            for crop in calendar_df["crop"].unique():
                for region in calendar_df["region"].unique():
                    crop_region_data = calendar_df[
                        (calendar_df["crop"] == crop)
                        & (calendar_df["region"] == region)
                    ]

                    if not crop_region_data.empty:
                        summary_data.append(
                            {
                                "crop": crop,
                                "region": region,
                                "states_count": len(crop_region_data),
                                "data_source": "Multiple",
                            }
                        )

        return pd.DataFrame(summary_data)

    def get_filtered_calendar(
        self,
        crops: list[str] = None,
        regions: list[str] = None,
        states: list[str] = None,
        source: str = "CONAB",
    ) -> pd.DataFrame:
        """
        Retorna calendário agrícola filtrado.

        Args:
            crops: Lista de culturas para filtrar
            regions: Lista de regiões para filtrar
            states: Lista de estados para filtrar
            source: Fonte de dados

        Returns:
            DataFrame filtrado
        """
        calendar_df = self.get_crop_calendar(source)

        # Aplicar filtros
        if crops:
            calendar_df = calendar_df[calendar_df["crop"].isin(crops)]

        if regions:
            calendar_df = calendar_df[calendar_df["region"].isin(regions)]

        if states:
            if "state_code" in calendar_df.columns:
                calendar_df = calendar_df[calendar_df["state_code"].isin(states)]
            elif "state_name" in calendar_df.columns:
                calendar_df = calendar_df[calendar_df["state_name"].isin(states)]

        return calendar_df

    def get_planting_harvest_info(self, source: str = "CONAB") -> dict[str, dict]:
        """
        Retorna informações sobre épocas de plantio e colheita.

        Args:
            source: Fonte de dados

        Returns:
            Dicionário com informações sazonais
        """
        if source not in self.processors:
            raise ValueError(
                f"Fonte {source} não disponível. Fontes: {self.get_available_sources()}"
            )

        processor = self.processors[source]
        if hasattr(processor, "get_planting_harvest_seasons"):
            return processor.get_planting_harvest_seasons()

        return {}

    def export_calendar_data(
        self, output_path: str | Path, format_type: str = "csv", source: str = "CONAB"
    ) -> None:
        """
        Exporta dados de calendário para arquivo.

        Args:
            output_path: Caminho de saída
            format_type: Formato (csv, excel, json)
            source: Fonte de dados
        """
        calendar_df = self.get_crop_calendar(source)
        output_path = Path(output_path)

        if format_type.lower() == "csv":
            calendar_df.to_csv(output_path, index=False, encoding="utf-8")
        elif format_type.lower() == "excel":
            calendar_df.to_excel(output_path, index=False)
        elif format_type.lower() == "json":
            calendar_df.to_json(output_path, orient="records", indent=2)
        else:
            raise ValueError(f"Formato não suportado: {format_type}")

    def get_metadata(self, source: str = "CONAB") -> dict[str, Any]:
        """
        Retorna metadados da fonte de dados.

        Args:
            source: Fonte de dados

        Returns:
            Dicionário com metadados
        """
        if source not in self.processors:
            raise ValueError(
                f"Fonte {source} não disponível. Fontes: {self.get_available_sources()}"
            )

        return self.processors[source].get_metadata()

    def get_available_crops(self, source: str = "CONAB") -> list[str]:
        """Retorna culturas disponíveis para uma fonte."""
        if source not in self.processors:
            return []

        return self.processors[source].get_available_crops()

    def get_available_regions(self, source: str = "CONAB") -> list[str]:
        """Retorna regiões disponíveis para uma fonte."""
        if source not in self.processors:
            return []

        return self.processors[source].get_available_regions()

    def reload_data(self, source: str = None) -> None:
        """
        Recarrega dados de uma fonte específica ou todas.

        Args:
            source: Fonte específica ou None para todas
        """
        if source:
            if source in self.processors:
                # Recarregar fonte específica
                if source == "CONAB":
                    conab_data_path = self.data_directory / "conab_crop_calendar.jsonc"
                    if conab_data_path.exists():
                        self.processors["CONAB"] = create_conab_processor(
                            conab_data_path
                        )
        else:
            # Recarregar todas as fontes
            self.processors.clear()
            self._initialize_processors()

    def get_dashboard_compatible_data(
        self, source: str = "CONAB"
    ) -> dict[str, pd.DataFrame]:
        """
        Retorna dados em formato compatível com o dashboard existente.

        Args:
            source: Fonte de dados

        Returns:
            Dicionário com DataFrames formatados para o dashboard
        """
        data = {}

        try:
            # Calendário agrícola
            calendar_df = self.get_crop_calendar(source)
            data["calendar"] = calendar_df

            # Resumo do calendário
            summary_df = self.get_crop_calendar_summary(source)
            data["calendar_summary"] = summary_df

            # Dados de produção se disponíveis
            production_df = self.get_production_data(source)
            if not production_df.empty:
                data["production"] = production_df

            # Metadados
            metadata = self.get_metadata(source)
            data["metadata"] = pd.DataFrame([metadata])

        except Exception as e:
            print(f"⚠️ Erro ao obter dados compatíveis do dashboard: {e}")

        return data


# Factory function para criar wrapper global
def create_agricultural_data_wrapper(
    data_directory: str | Path = None,
) -> AgriculturalDataWrapper:
    """
    Cria wrapper de dados agrícolas configurado.

    Args:
        data_directory: Diretório com dados agrícolas

    Returns:
        Instância configurada do wrapper
    """
    return AgriculturalDataWrapper(data_directory)


# Instância global para uso no dashboard
agricultural_data = None


def initialize_agricultural_data(
    data_directory: str | Path = None,
) -> AgriculturalDataWrapper:
    """
    Inicializa dados agrícolas globais.

    Args:
        data_directory: Diretório com dados

    Returns:
        Wrapper inicializado
    """
    global agricultural_data
    agricultural_data = create_agricultural_data_wrapper(data_directory)
    return agricultural_data


def get_agricultural_data() -> AgriculturalDataWrapper:
    """
    Retorna instância global de dados agrícolas.

    Returns:
        Wrapper de dados agrícolas
    """
    global agricultural_data
    if agricultural_data is None:
        agricultural_data = initialize_agricultural_data()

    return agricultural_data
