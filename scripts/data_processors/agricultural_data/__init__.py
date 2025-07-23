#!/usr/bin/env python3
"""
Agricultural Data Processor Base
================================

Este módulo fornece a interface base e padrões para processadores de dados agrícolas.
Todos os processadores específicos (CONAB, IBGE, etc.) devem implementar esta interface.

Características principais:
- Interface padronizada para processamento de dados agrícolas
- Validação de dados consistente
- Cache e otimização automática
- Formatação padronizada para o dashboard
- Suporte a dados temporais e geoespaciais

Author: Dashboard Iniciativas LULC
Date: 2025
"""

import warnings
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Union

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


class AgriculturalDataProcessor(ABC):
    """
    Interface base para processadores de dados agrícolas.

    Todos os processadores específicos devem herdar desta classe
    e implementar os métodos abstratos.
    """

    def __init__(self, data_source: str, cache_enabled: bool = True):
        """
        Inicializa o processador de dados agrícolas.

        Args:
            data_source: Nome da fonte de dados (ex: 'CONAB', 'IBGE')
            cache_enabled: Se deve usar cache para otimização
        """
        self.data_source = data_source
        self.cache_enabled = cache_enabled
        self.last_update: datetime | None = None
        self._data_cache: dict[str, Any] = {}

    @abstractmethod
    def load_raw_data(self, data_path: Path) -> dict[str, Any]:
        """
        Carrega dados brutos da fonte específica.

        Args:
            data_path: Caminho para os dados

        Returns:
            Dicionário com os dados brutos carregados
        """
        pass

    @abstractmethod
    def validate_data(self, data: dict[str, Any]) -> bool:
        """
        Valida a integridade e consistência dos dados.

        Args:
            data: Dados a serem validados

        Returns:
            True se os dados são válidos, False caso contrário
        """
        pass

    @abstractmethod
    def process_data(self, raw_data: dict[str, Any]) -> dict[str, pd.DataFrame]:
        """
        Processa os dados brutos para formato padronizado.

        Args:
            raw_data: Dados brutos da fonte

        Returns:
            Dicionário com DataFrames processados por categoria
        """
        pass

    @abstractmethod
    def get_crop_calendar(self) -> pd.DataFrame:
        """
        Retorna o calendário agrícola formatado para o dashboard.

        Returns:
            DataFrame com informações de plantio e colheita
        """
        pass

    @abstractmethod
    def get_production_data(self) -> pd.DataFrame:
        """
        Retorna dados de produção agrícola formatados.

        Returns:
            DataFrame com dados de produção por região/período
        """
        pass

    def get_metadata(self) -> dict[str, Any]:
        """
        Retorna metadados sobre a fonte de dados.

        Returns:
            Dicionário com informações sobre a fonte
        """
        return {
            "data_source": self.data_source,
            "last_update": self.last_update,
            "cache_enabled": self.cache_enabled,
            "available_crops": self.get_available_crops(),
            "available_regions": self.get_available_regions(),
            "data_period": self.get_data_period(),
        }

    @abstractmethod
    def get_available_crops(self) -> list[str]:
        """Retorna lista de culturas disponíveis."""
        pass

    @abstractmethod
    def get_available_regions(self) -> list[str]:
        """Retorna lista de regiões disponíveis."""
        pass

    @abstractmethod
    def get_data_period(self) -> dict[str, str]:
        """Retorna período dos dados disponíveis."""
        pass

    def standardize_state_codes(
        self, df: pd.DataFrame, state_column: str = "state"
    ) -> pd.DataFrame:
        """
        Padroniza códigos de estados para o formato usado no dashboard.

        Args:
            df: DataFrame com dados
            state_column: Nome da coluna com códigos de estados

        Returns:
            DataFrame com códigos padronizados
        """
        state_mapping = {
            # Norte
            "RO": "RO",
            "Rondônia": "RO",
            "AC": "AC",
            "Acre": "AC",
            "AM": "AM",
            "Amazonas": "AM",
            "RR": "RR",
            "Roraima": "RR",
            "PA": "PA",
            "Pará": "PA",
            "AP": "AP",
            "Amapá": "AP",
            "TO": "TO",
            "Tocantins": "TO",
            # Nordeste
            "MA": "MA",
            "Maranhão": "MA",
            "PI": "PI",
            "Piauí": "PI",
            "CE": "CE",
            "Ceará": "CE",
            "RN": "RN",
            "Rio Grande do Norte": "RN",
            "PB": "PB",
            "Paraíba": "PB",
            "PE": "PE",
            "Pernambuco": "PE",
            "AL": "AL",
            "Alagoas": "AL",
            "SE": "SE",
            "Sergipe": "SE",
            "BA": "BA",
            "Bahia": "BA",
            # Centro-Oeste
            "MT": "MT",
            "Mato Grosso": "MT",
            "MS": "MS",
            "Mato Grosso do Sul": "MS",
            "GO": "GO",
            "Goiás": "GO",
            "DF": "DF",
            "Distrito Federal": "DF",
            # Sudeste
            "MG": "MG",
            "Minas Gerais": "MG",
            "ES": "ES",
            "Espírito Santo": "ES",
            "RJ": "RJ",
            "Rio de Janeiro": "RJ",
            "SP": "SP",
            "São Paulo": "SP",
            # Sul
            "PR": "PR",
            "Paraná": "PR",
            "SC": "SC",
            "Santa Catarina": "SC",
            "RS": "RS",
            "Rio Grande do Sul": "RS",
        }

        df_copy = df.copy()
        if state_column in df_copy.columns:
            df_copy[state_column] = (
                df_copy[state_column].map(state_mapping).fillna(df_copy[state_column])
            )

        return df_copy

    def add_region_info(
        self, df: pd.DataFrame, state_column: str = "state"
    ) -> pd.DataFrame:
        """
        Adiciona informações de região baseadas no código do estado.

        Args:
            df: DataFrame com dados
            state_column: Nome da coluna com códigos de estados

        Returns:
            DataFrame com coluna de região adicionada
        """
        region_mapping = {
            # North
            "RO": "North",
            "AC": "North",
            "AM": "North",
            "RR": "North",
            "PA": "North",
            "AP": "North",
            "TO": "North",
            # Northeast
            "MA": "Northeast",
            "PI": "Northeast",
            "CE": "Northeast",
            "RN": "Northeast",
            "PB": "Northeast",
            "PE": "Northeast",
            "AL": "Northeast",
            "SE": "Northeast",
            "BA": "Northeast",
            # Central-West
            "MT": "Central-West",
            "MS": "Central-West",
            "GO": "Central-West",
            "DF": "Central-West",
            # Southeast
            "MG": "Southeast",
            "ES": "Southeast",
            "RJ": "Southeast",
            "SP": "Southeast",
            # South
            "PR": "South",
            "SC": "South",
            "RS": "South",
        }

        df_copy = df.copy()
        if state_column in df_copy.columns:
            df_copy["region"] = df_copy[state_column].map(region_mapping)

        return df_copy

    def format_for_dashboard(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """
        Formata dados para uso no dashboard com padrões consistentes.

        Args:
            df: DataFrame a ser formatado
            data_type: Tipo de dados ('calendar', 'production', 'area', etc.)

        Returns:
            DataFrame formatado para o dashboard
        """
        df_formatted = df.copy()

        # Padronizar nomes de colunas
        column_standardization = {
            "federation_unit": "state",
            "uf": "state",
            "estado": "state",
            "crop_type": "crop",
            "cultura": "crop",
            "ano": "year",
            "mes": "month",
            "valor": "value",
            "area": "area_ha",
            "producao": "production_ton",
            "produtividade": "productivity_kg_ha",
        }

        # Renomear colunas se existirem
        for old_name, new_name in column_standardization.items():
            if old_name in df_formatted.columns:
                df_formatted = df_formatted.rename(columns={old_name: new_name})

        # Padronizar códigos de estados
        if "state" in df_formatted.columns:
            df_formatted = self.standardize_state_codes(df_formatted, "state")
            df_formatted = self.add_region_info(df_formatted, "state")

        # Adicionar metadados
        df_formatted.attrs["data_source"] = self.data_source
        df_formatted.attrs["data_type"] = data_type
        df_formatted.attrs["last_update"] = datetime.now().isoformat()

        return df_formatted


class SeasonalDataMixin:
    """Mixin para processamento de dados sazonais agrícolas."""

    def get_season_from_month(self, month: str | int) -> str:
        """
        Determina a estação do ano baseada no mês.

        Args:
            month: Mês (nome ou número)

        Returns:
            Nome da estação em inglês
        """
        month_to_season = {
            # Spring (Sep 22 - Dec 21): Oct, Nov, Dec
            "October": "Spring",
            "November": "Spring",
            "December": "Spring",
            10: "Spring",
            11: "Spring",
            12: "Spring",
            # Summer (Dec 21 - Mar 20): Jan, Feb, Mar
            "January": "Summer",
            "February": "Summer",
            "March": "Summer",
            1: "Summer",
            2: "Summer",
            3: "Summer",
            # Autumn (Mar 20 - Jun 21): Apr, May, Jun
            "April": "Autumn",
            "May": "Autumn",
            "June": "Autumn",
            4: "Autumn",
            5: "Autumn",
            6: "Autumn",
            # Winter (Jun 21 - Sep 22): Jul, Aug, Sep
            "July": "Winter",
            "August": "Winter",
            "September": "Winter",
            7: "Winter",
            8: "Winter",
            9: "Winter",
        }

        return month_to_season.get(month, "Unknown")

    def group_by_season(
        self, df: pd.DataFrame, month_column: str = "month"
    ) -> pd.DataFrame:
        """
        Agrupa dados por estação do ano.

        Args:
            df: DataFrame com dados mensais
            month_column: Nome da coluna com meses

        Returns:
            DataFrame agrupado por estação
        """
        df_copy = df.copy()
        if month_column in df_copy.columns:
            df_copy["season"] = df_copy[month_column].apply(self.get_season_from_month)

        return df_copy


class CropCalendarFormatter:
    """Formatador específico para calendários agrícolas."""

    @staticmethod
    def format_calendar_data(calendar_data: dict[str, Any]) -> pd.DataFrame:
        """
        Formata dados de calendário agrícola para o padrão do dashboard.

        Args:
            calendar_data: Dados do calendário em formato dict/json

        Returns:
            DataFrame formatado com calendário agrícola
        """
        records = []

        if "crop_calendar" in calendar_data:
            for crop, states_data in calendar_data["crop_calendar"].items():
                for state_data in states_data:
                    record = {
                        "crop": crop,
                        "state_code": state_data["state_code"],
                        "state_name": state_data["state_name"],
                        "region": state_data.get("region", "Unknown"),
                    }

                    # Adicionar dados mensais
                    if "calendar" in state_data:
                        for month, activity in state_data["calendar"].items():
                            record[month.lower()] = activity

                    # Adicionar dados sazonais se disponíveis
                    if "seasons" in state_data:
                        for season, months_data in state_data["seasons"].items():
                            for month, activity in months_data.items():
                                season_column = f"{season}_{month.lower()}"
                                record[season_column] = activity

                    records.append(record)

        return pd.DataFrame(records)


# Constantes para padronização
AGRICULTURAL_DATA_STANDARDS = {
    "crop_calendar_columns": [
        "crop",
        "state_code",
        "state_name",
        "region",
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ],
    "production_columns": [
        "crop",
        "state_code",
        "state_name",
        "region",
        "year",
        "area_ha",
        "production_ton",
        "productivity_kg_ha",
    ],
    "activity_codes": {
        "P": "Planting",
        "H": "Harvest",
        "PH": "Planting and Harvest",
        "": "No Activity",
    },
}
