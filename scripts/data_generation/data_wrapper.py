#!/usr/bin/env python3
"""
Data Wrapper for Dashboard Components
====================================

This module provides a clean interface for dashboard components to access
processed LULC initiative data. It acts as a wrapper around the UnifiedDataProcessor
to provide specific functions that dashboards need.

Key Features:
- Simple data loading functions
- Plot-ready data preparation
- Dashboard-specific data formatting
- Error handling and validation
- Caching for performance

Author: Dashboard Iniciativas LULC
Date: 2025
"""

import json
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

try:
    from scripts.data_generation.lulc_data_engine import UnifiedDataProcessor
except ImportError:
    from lulc_data_engine import UnifiedDataProcessor


class DataWrapper:
    """Wrapper class that provides dashboard-friendly data access."""

    def __init__(self):
        """Initialize the data wrapper."""
        self.processor = UnifiedDataProcessor()
        self._cached_data = {}
        self._data_loaded = False

    def _load_processed_data(self) -> bool:
        """Load processed data from files if not already loaded."""
        if self._data_loaded:
            return True

        try:
            # Load processed CSV
            csv_path = PROJECT_ROOT / "data/processed/initiatives_processed.csv"
            if csv_path.exists():
                self._cached_data["dataframe"] = pd.read_csv(csv_path)
            else:
                print("⚠️ Processed CSV not found. Generating data...")
                df, metadata = self.processor.load_data_from_jsonc()
                auxiliary_data = self.processor.create_comprehensive_auxiliary_data(
                    df, metadata
                )
                self._cached_data["dataframe"] = df
                self._cached_data["metadata"] = metadata
                self._cached_data["auxiliary"] = auxiliary_data

            # Load processed metadata
            metadata_path = PROJECT_ROOT / "data/processed/metadata_processed.json"
            if metadata_path.exists() and "metadata" not in self._cached_data:
                with open(metadata_path, encoding="utf-8") as f:
                    self._cached_data["metadata"] = json.load(f)

            # Load auxiliary data
            aux_path = PROJECT_ROOT / "data/processed/auxiliary_data.json"
            if aux_path.exists() and "auxiliary" not in self._cached_data:
                with open(aux_path, encoding="utf-8") as f:
                    self._cached_data["auxiliary"] = json.load(f)

            self._data_loaded = True
            return True

        except Exception as e:
            print(f"❌ Error loading processed data: {e}")
            # If loading fails, attempt to generate data on the fly as a fallback
            try:
                print(
                    "🔄 Attempting to generate data on the fly due to loading error..."
                )
                df, metadata = self.processor.load_data_from_jsonc()
                auxiliary_data = self.processor.create_comprehensive_auxiliary_data(
                    df, metadata
                )
                self._cached_data["dataframe"] = df
                self._cached_data["metadata"] = metadata
                self._cached_data["auxiliary"] = auxiliary_data
                self._data_loaded = True  # Mark as loaded even if generated
                return True
            except Exception as gen_e:
                print(f"❌❌ Critical Error: Failed to load and generate data: {gen_e}")
                return False

    def load_data(self) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any]]:
        """
        Load all processed data for dashboard use.

        Returns:
            Tuple containing (dataframe, metadata, auxiliary_data)
        """
        if not self._load_processed_data():
            # Fallback: generate data on the fly
            print("🔄 Generating data on the fly...")
            df, metadata = self.processor.load_data_from_jsonc()
            auxiliary_data = self.processor.create_comprehensive_auxiliary_data(
                df, metadata
            )
            return df, metadata, auxiliary_data

        return (
            self._cached_data.get("dataframe", pd.DataFrame()),
            self._cached_data.get("metadata", {}),
            self._cached_data.get("auxiliary", {}),
        )

    def prepare_plot_data(
        self,
        df: pd.DataFrame,
        plot_type: str = "comparison",
        filter_params: dict | None = None,
    ) -> dict[str, Any]:
        """
        Prepare data specifically formatted for different types of plots.

        Args:
            df: The DataFrame containing the data to be plotted.
            plot_type: Type of plot ('comparison', 'temporal', 'detailed', 'overview')
            filter_params: Optional filtering parameters

        Returns:
            Dictionary with plot-ready data.
        """
        df_loaded, metadata, auxiliary = self.load_data()

        current_df = df if df is not None and not df.empty else df_loaded

        if current_df.empty:
            return {
                "error": "No data available",
                "data": pd.DataFrame(),
            }  # Ensure a DataFrame is always in 'data' key

        plot_data = {
            "plot_type": plot_type,
            "data": pd.DataFrame(),
        }  # Initialize with an empty DataFrame

        try:
            if plot_type == "comparison":
                plot_data.update(self._prepare_comparison_data(current_df, auxiliary))
                plot_data["data"] = current_df  # Keep original df for flexibility
            elif plot_type == "temporal":
                plot_data.update(self._prepare_temporal_data(current_df, auxiliary))
                plot_data["data"] = current_df
            elif plot_type == "detailed":
                plot_data.update(self._prepare_detailed_data(current_df, metadata))
                plot_data["data"] = current_df
            elif plot_type == "overview":
                plot_data.update(self._prepare_overview_data(current_df, auxiliary))
                plot_data["data"] = current_df
            elif plot_type == "default":
                plot_data["data"] = current_df  # Store the DataFrame in the 'data' key
            else:
                plot_data["warning"] = (
                    f"Unknown plot_type: {plot_type}. Returning general data."
                )
                plot_data.update(self._prepare_general_data(current_df))
                plot_data["data"] = current_df

        except Exception as e:
            plot_data["error"] = f"Error preparing {plot_type} data: {e}"

        return plot_data

    def _prepare_comparison_data(
        self, df: pd.DataFrame, auxiliary: dict
    ) -> dict[str, Any]:
        """Prepare data for comparison plots."""
        comparison_matrix = auxiliary.get("comparison_matrix", [])

        if not comparison_matrix:
            # Generate basic comparison data from dataframe
            comparison_data = []
            for _, row in df.iterrows():
                comparison_data.append(
                    {
                        "Name": row.get("Name", ""),
                        "Acronym": row.get("Acronym", ""),
                        "Accuracy (%)": row.get("Overall Accuracy (%)", 0),
                        "Resolution (m)": row.get("Spatial Resolution (m)", 0),
                        "Classes": row.get("Classes", 0),
                    }
                )
            comparison_matrix = comparison_data

        return {
            "comparison_matrix": comparison_matrix,
            "metrics": ["Accuracy (%)", "Resolution (m)", "Classes"],
            "initiatives_count": len(comparison_matrix),
        }

    def _prepare_temporal_data(
        self, df: pd.DataFrame, auxiliary: dict
    ) -> dict[str, Any]:
        """Prepare data for temporal analysis plots."""
        temporal_analysis = auxiliary.get("temporal_analysis", {})

        if not temporal_analysis:
            # Generate basic temporal data
            temporal_data = {"initiatives": []}
            for _, row in df.iterrows():
                if "Available Years" in row and row["Available Years"]:
                    years_str = str(row["Available Years"])
                    years = []
                    try:
                        # Parse years from string format
                        years = [
                            int(y.strip())
                            for y in years_str.split(",")
                            if y.strip().isdigit()
                        ]
                    except (ValueError, AttributeError):
                        years = []

                    if years:
                        temporal_data["initiatives"].append(
                            {
                                "name": row.get("Name", ""),
                                "acronym": row.get("Acronym", ""),
                                "years": years,
                                "start_year": min(years),
                                "end_year": max(years),
                                "total_years": len(years),
                            }
                        )
            temporal_analysis = temporal_data

        return {
            "temporal_analysis": temporal_analysis,
            "year_range": self._get_year_range(temporal_analysis),
            "initiatives_with_temporal": len(temporal_analysis.get("initiatives", [])),
        }

    def _prepare_detailed_data(
        self, df: pd.DataFrame, metadata: dict
    ) -> dict[str, Any]:
        """Prepare data for detailed analysis."""
        return {
            "dataframe": df,
            "metadata": metadata,
            "summary_stats": {
                "total_initiatives": len(df),
                "providers": (
                    df["Provider"].nunique() if "Provider" in df.columns else 0
                ),
                "coverage_types": (
                    df["Coverage"].unique().tolist() if "Coverage" in df.columns else []
                ),
                "resolution_stats": self._get_resolution_stats(df),
                "accuracy_stats": self._get_accuracy_stats(df),
            },
        }

    def _prepare_overview_data(
        self, df: pd.DataFrame, auxiliary: dict
    ) -> dict[str, Any]:
        """Prepare data for overview dashboard."""
        return {
            "summary": {
                "total_initiatives": len(df),
                "global_initiatives": (
                    len(df[df["Coverage"] == "Global"])
                    if "Coverage" in df.columns
                    else 0
                ),
                "national_initiatives": (
                    len(df[df["Coverage"] == "National"])
                    if "Coverage" in df.columns
                    else 0
                ),
                "regional_initiatives": (
                    len(df[df["Coverage"] == "Regional"])
                    if "Coverage" in df.columns
                    else 0
                ),
            },
            "top_providers": self._get_top_providers(df),
            "resolution_distribution": self._get_resolution_distribution(df),
            "accuracy_distribution": self._get_accuracy_distribution(df),
        }

    def _prepare_general_data(self, df: pd.DataFrame) -> dict[str, Any]:
        """Prepare general data for any plot type."""
        return {
            "dataframe": df,
            "basic_stats": {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.to_dict(),
            },
        }

    def _get_year_range(self, temporal_analysis: dict) -> tuple[int, int]:
        """Get the overall year range from temporal analysis."""
        all_years = []
        for initiative in temporal_analysis.get("initiatives", []):
            all_years.extend(initiative.get("years", []))

        if all_years:
            return (min(all_years), max(all_years))
        return (2000, 2024)  # Default range

    def _get_resolution_stats(self, df: pd.DataFrame) -> dict:
        """Get resolution statistics."""
        if "Spatial Resolution (m)" in df.columns:
            res_col = df["Spatial Resolution (m)"]
            return {
                "min": float(res_col.min()),
                "max": float(res_col.max()),
                "mean": float(res_col.mean()),
                "median": float(res_col.median()),
            }
        return {}

    def _get_accuracy_stats(self, df: pd.DataFrame) -> dict:
        """Get accuracy statistics."""
        if "Overall Accuracy (%)" in df.columns:
            acc_col = df["Overall Accuracy (%)"].replace(0, np.nan)  # Remove 0 values
            acc_col = acc_col.dropna()
            if not acc_col.empty:
                return {
                    "min": float(acc_col.min()),
                    "max": float(acc_col.max()),
                    "mean": float(acc_col.mean()),
                    "median": float(acc_col.median()),
                }
        return {}

    def _get_top_providers(self, df: pd.DataFrame, top_n: int = 5) -> list[dict]:
        """Get top providers by number of initiatives."""
        if "Provider" not in df.columns:
            return []

        provider_counts = df["Provider"].value_counts().head(top_n)
        return [
            {"provider": provider, "count": int(count)}
            for provider, count in provider_counts.items()
        ]

    def _get_resolution_distribution(self, df: pd.DataFrame) -> list[dict]:
        """Get distribution of spatial resolutions."""
        if "Spatial Resolution (m)" not in df.columns:
            return []

        # Create resolution categories
        df_copy = df.copy()
        df_copy["Resolution Category"] = pd.cut(
            df_copy["Spatial Resolution (m)"],
            bins=[0, 15, 35, 65, 200],
            labels=[
                "Very High (≤15m)",
                "High (16-35m)",
                "Medium (36-65m)",
                "Low (>65m)",
            ],
            include_lowest=True,
        )

        dist = df_copy["Resolution Category"].value_counts()
        return [
            {"category": str(cat), "count": int(count)} for cat, count in dist.items()
        ]

    def _get_accuracy_distribution(self, df: pd.DataFrame) -> list[dict]:
        """Get distribution of accuracy values."""
        if "Overall Accuracy (%)" not in df.columns:
            return []

        # Filter out 0 values and create categories
        df_filtered = df[df["Overall Accuracy (%)"] > 0].copy()
        if df_filtered.empty:
            return []

        df_filtered["Accuracy Category"] = pd.cut(
            df_filtered["Overall Accuracy (%)"],
            bins=[0, 70, 80, 90, 100],
            labels=[
                "Fair (≤70%)",
                "Good (71-80%)",
                "Very Good (81-90%)",
                "Excellent (>90%)",
            ],
            include_lowest=True,
        )

        dist = df_filtered["Accuracy Category"].value_counts()
        return [
            {"category": str(cat), "count": int(count)} for cat, count in dist.items()
        ]


# Global instance for easy access
_data_wrapper = DataWrapper()


def load_data() -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any]]:
    """Global helper to load all processed data."""
    return _data_wrapper.load_data()


def prepare_plot_data(
    df: pd.DataFrame, plot_type: str = "default", filter_params: dict | None = None
) -> dict[str, Any]:
    """Global helper to prepare plot-specific data."""
    return _data_wrapper.prepare_plot_data(df, plot_type, filter_params)


def get_summary_stats() -> dict[str, Any]:
    """Get summary statistics."""
    df, metadata, auxiliary = load_data()
    return _data_wrapper._prepare_overview_data(df, auxiliary)


def refresh_data():
    """Refresh cached data."""
    _data_wrapper._data_loaded = False
    _data_wrapper._cached_data.clear()
