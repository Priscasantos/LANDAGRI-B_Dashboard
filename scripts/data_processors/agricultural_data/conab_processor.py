#!/usr/bin/env python3
"""
CONAB Agricultural Data Processor
=================================

Processador específico para dados da Companhia Nacional de Abastecimento (CONAB).
Implementa a interface base AgriculturalDataProcessor para processar dados
de calendário agrícola, produção e área plantada.

Características:
- Processamento de calendários de cultivo CONAB
- Formatação para padrões do dashboard
- Suporte a múltiplas culturas e regiões
- Validação específica de dados CONAB

Author: LANDAGRI-B Project Team 
Date: 2025
"""

from datetime import datetime
import json
from pathlib import Path
from typing import Any

import pandas as pd

from . import AgriculturalDataProcessor, SeasonalDataMixin


class CONABProcessor(AgriculturalDataProcessor, SeasonalDataMixin):
    """
    Processador específico para dados CONAB.

    Processa dados da Companhia Nacional de Abastecimento incluindo
    calendários agrícolas, produção e área plantada.
    """

    def __init__(self, cache_enabled: bool = True):
        """Inicializa o processador CONAB."""
        super().__init__("CONAB", cache_enabled)
        self.supported_crops = [
            "Cotton",
            "Rice",
            "Beans",
            "Corn",
            "Soybean",
            "Wheat",
            "Sorghum",
            "Sunflower",
        ]

        # Culturas detectadas dinamicamente dos dados
        self.detected_crops = []

    def load_raw_data(self, data_path: Path) -> dict[str, Any]:
        """
        Carrega dados CONAB de arquivo JSONC.

        Args:
            data_path: Caminho para arquivo JSONC do CONAB

        Returns:
            Dados CONAB carregados
        """
        try:
            with open(data_path, encoding="utf-8") as file:
                # Remove comentários JSONC
                content = file.read()
                lines = content.split("\n")
                cleaned_lines = []

                for line in lines:
                    # Remove comentários de linha
                    if "//" in line:
                        line = line.split("//")[0]
                    cleaned_lines.append(line)

                cleaned_content = "\n".join(cleaned_lines)
                data = json.loads(cleaned_content)

                self.last_update = datetime.now()
                return data

        except Exception as e:
            raise ValueError(f"Erro ao carregar dados CONAB: {e}") from e

    def validate_data(self, data: dict[str, Any]) -> bool:
        """
        Valida estrutura dos dados CONAB.

        Args:
            data: Dados CONAB a serem validados

        Returns:
            True se dados são válidos
        """
        required_fields = ["metadata", "crop_calendar"]

        # Verificar campos obrigatórios
        for field in required_fields:
            if field not in data:
                return False

        # Verificar estrutura do calendário
        if "crop_calendar" in data:
            for _crop, states_data in data["crop_calendar"].items():
                if not isinstance(states_data, list):
                    return False

                for state_data in states_data:
                    required_state_fields = ["state_code", "state_name"]
                    for field in required_state_fields:
                        if field not in state_data:
                            return False

        return True

    def process_data(self, raw_data: dict[str, Any]) -> dict[str, pd.DataFrame]:
        """
        Processa dados brutos CONAB.

        Args:
            raw_data: Dados CONAB brutos

        Returns:
            Dicionário com DataFrames processados
        """
        processed_data = {}

        # Detectar culturas disponíveis nos dados
        if "crop_calendar" in raw_data:
            self.detected_crops = list(raw_data["crop_calendar"].keys())

        # Processar calendário agrícola
        if "crop_calendar" in raw_data:
            calendar_df = self._process_crop_calendar(raw_data)
            processed_data["crop_calendar"] = calendar_df
            # Cache para acesso rápido
            self._data_cache["crop_calendar"] = calendar_df

        # Processar outros tipos de dados se disponíveis
        if "production_data" in raw_data:
            production_df = self._process_production_data(raw_data["production_data"])
            processed_data["production"] = production_df
            self._data_cache["production"] = production_df

        if "area_data" in raw_data:
            area_df = self._process_area_data(raw_data["area_data"])
            processed_data["area"] = area_df
            self._data_cache["area"] = area_df

        return processed_data

    def _process_crop_calendar(self, data: dict[str, Any]) -> pd.DataFrame:
        """Processa calendário agrícola CONAB."""
        records = []

        # Obter mapeamento de estados para regiões
        states_info = data.get("states", {})

        for crop, states_data in data["crop_calendar"].items():
            for state_data in states_data:
                state_code = state_data["state_code"]

                # Obter região do mapeamento de estados
                region = "Unknown"
                if state_code in states_info:
                    region = states_info[state_code].get("region", "Unknown")

                record = {
                    "crop": crop,
                    "state_code": state_code,
                    "state_name": state_data["state_name"],
                    "region": region,
                }

                # Processar calendário mensal
                if "calendar" in state_data:
                    for month, activity in state_data["calendar"].items():
                        record[month.lower()] = self._standardize_activity(activity)

                # Processar dados sazonais se disponíveis
                if "seasons" in state_data:
                    for season, months_data in state_data["seasons"].items():
                        for month, activity in months_data.items():
                            season_column = f"{season}_{month.lower()}"
                            record[season_column] = self._standardize_activity(activity)

                records.append(record)

        df = pd.DataFrame(records)
        return self.format_for_dashboard(df, "calendar")

    def _process_production_data(self, production_data: list[dict]) -> pd.DataFrame:
        """Processa dados de produção CONAB."""
        df = pd.DataFrame(production_data)
        return self.format_for_dashboard(df, "production")

    def _process_area_data(self, area_data: list[dict]) -> pd.DataFrame:
        """Processa dados de área CONAB."""
        df = pd.DataFrame(area_data)
        return self.format_for_dashboard(df, "area")

    def _standardize_activity(self, activity: str) -> str:
        """
        Padroniza códigos de atividade agrícola.

        Args:
            activity: Código de atividade original

        Returns:
            Atividade padronizada
        """
        activity_map = {
            "P": "Planting",
            "H": "Harvest",
            "PH": "Planting and Harvest",
            "P/H": "Planting and Harvest",
            "": "No Activity",
            None: "No Activity",
        }

        return activity_map.get(activity, activity if activity else "No Activity")

    def get_crop_calendar(self) -> pd.DataFrame:
        """
        Retorna calendário agrícola formatado.

        Returns:
            DataFrame com calendário agrícola
        """
        if "crop_calendar" in self._data_cache:
            return self._data_cache["crop_calendar"]

        raise ValueError(
            "Dados de calendário não carregados. Execute process_data primeiro."
        )

    def get_production_data(self) -> pd.DataFrame:
        """
        Retorna dados de produção formatados.

        Returns:
            DataFrame com dados de produção
        """
        if "production" in self._data_cache:
            return self._data_cache["production"]

        raise ValueError("Dados de produção não carregados.")

    def get_available_crops(self) -> list[str]:
        """Retorna culturas disponíveis."""
        # Usar culturas detectadas se disponíveis, senão usar lista padrão
        if self.detected_crops:
            return self.detected_crops.copy()
        return self.supported_crops.copy()

    def get_available_regions(self) -> list[str]:
        """Retorna regiões disponíveis."""
        return ["North", "Northeast", "Central-West", "Southeast", "South"]

    def get_dashboard_summary(self) -> dict:
        """
        Retorna um resumo dos dados CONAB para uso no dashboard.

        Returns:
            dict com contagem de iniciativas, culturas, regiões e listas detalhadas
        """
        # Certifique-se de que os dados estão carregados e válidos
        if "crop_calendar" not in self._data_cache:
            raise ValueError(
                "Dados de calendário não carregados. Execute process_data primeiro."
            )

        calendar_df = self._data_cache["crop_calendar"]

        # Contagem de iniciativas (estados), culturas e regiões
        initiatives = calendar_df["state_code"].unique().tolist()
        crops = calendar_df["crop"].unique().tolist()
        regions = calendar_df["region"].unique().tolist()

        summary = {
            "initiative_count": len(initiatives),
            "crop_count": len(crops),
            "region_count": len(regions),
            "initiatives": initiatives,
            "crops": crops,
            "regions": regions,
            "states": calendar_df[["state_code", "state_name", "region"]]
            .drop_duplicates()
            .to_dict(orient="records"),
        }

        return summary

    def get_data_period(self) -> dict[str, str]:
        """Retorna período dos dados."""
        return {
            "start_year": "2020",
            "end_year": "2024",
            "frequency": "annual",
            "last_update": self.last_update.isoformat() if self.last_update else None,
        }

    def get_calendar_summary(self) -> pd.DataFrame:
        """
        Retorna resumo do calendário agrícola por região.

        Returns:
            DataFrame com resumo por região e cultura
        """
        calendar_df = self.get_crop_calendar()

        summary_data = []
        for crop in calendar_df["crop"].unique():
            crop_data = calendar_df[calendar_df["crop"] == crop]

            for region in crop_data["region"].unique():
                region_data = crop_data[crop_data["region"] == region]

                # Contar atividades por mês
                planting_months = []
                harvest_months = []

                month_columns = [
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
                ]

                for month in month_columns:
                    if month in region_data.columns:
                        activities = region_data[month].unique()
                        if any("Planting" in str(act) for act in activities):
                            planting_months.append(month.capitalize())
                        if any("Harvest" in str(act) for act in activities):
                            harvest_months.append(month.capitalize())

                summary_data.append(
                    {
                        "crop": crop,
                        "region": region,
                        "planting_months": ", ".join(planting_months),
                        "harvest_months": ", ".join(harvest_months),
                        "states_count": len(region_data),
                    }
                )

        return pd.DataFrame(summary_data)

    def export_calendar_to_csv(self, output_path: Path) -> None:
        """
        Exporta calendário agrícola para CSV.

        Args:
            output_path: Caminho de saída para CSV
        """
        calendar_df = self.get_crop_calendar()
        calendar_df.to_csv(output_path, index=False, encoding="utf-8")

    def filter_by_crop(self, crops: list[str]) -> "CONABProcessor":
        """
        Filtra processador por culturas específicas.

        Args:
            crops: Lista de culturas para manter

        Returns:
            Nova instância filtrada
        """
        filtered_processor = CONABProcessor(self.cache_enabled)
        filtered_processor.supported_crops = [
            crop for crop in self.supported_crops if crop in crops
        ]
        filtered_processor._data_cache = self._data_cache.copy()
        filtered_processor.last_update = self.last_update

        return filtered_processor

    def get_planting_harvest_seasons(self) -> dict[str, dict]:
        """
        Retorna informações sobre épocas de plantio e colheita.

        Returns:
            Dicionário com épocas por cultura e região
        """
        calendar_df = self.get_crop_calendar()
        seasons_info = {}

        for crop in calendar_df["crop"].unique():
            crop_data = calendar_df[calendar_df["crop"] == crop]
            seasons_info[crop] = {}

            for region in crop_data["region"].unique():
                region_data = crop_data[crop_data["region"] == region]

                # Identificar épocas predominantes
                month_columns = [
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
                ]

                planting_pattern = []
                harvest_pattern = []

                for month in month_columns:
                    if month in region_data.columns:
                        activities = region_data[month].tolist()
                        planting_count = sum(
                            1 for act in activities if "Planting" in str(act)
                        )
                        harvest_count = sum(
                            1 for act in activities if "Harvest" in str(act)
                        )

                        if planting_count > len(activities) * 0.5:
                            planting_pattern.append(month)
                        if harvest_count > len(activities) * 0.5:
                            harvest_pattern.append(month)

                seasons_info[crop][region] = {
                    "main_planting_season": self._get_season_range(planting_pattern),
                    "main_harvest_season": self._get_season_range(harvest_pattern),
                    "planting_months": planting_pattern,
                    "harvest_months": harvest_pattern,
                }

        return seasons_info

    def _get_season_range(self, months: list[str]) -> str:
        """Determina a estação predominante para uma lista de meses."""
        if not months:
            return "No defined season"

        seasons = [self.get_season_from_month(month) for month in months]
        most_common_season = (
            max(set(seasons), key=seasons.count) if seasons else "Unknown"
        )

        return most_common_season


def create_conab_processor(data_path: str | Path = None) -> CONABProcessor:
    """
    Factory function para criar processador CONAB.

    Args:
        data_path: Caminho opcional para dados CONAB

    Returns:
        Instância configurada do CONABProcessor
    """
    processor = CONABProcessor(cache_enabled=True)

    if data_path:
        data_path = Path(data_path)
        if data_path.exists():
            raw_data = processor.load_raw_data(data_path)
            if processor.validate_data(raw_data):
                processed_data = processor.process_data(raw_data)
                processor._data_cache.update(processed_data)
            else:
                raise ValueError(f"Dados CONAB inválidos em {data_path}")

    return processor
