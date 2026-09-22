# MIGRAÇÃO AUTOMÁTICA - 2025-07-23
# Este arquivo foi atualizado para usar os novos processadores de dados agrícolas
# Processadores disponíveis em: scripts/data_processors/agricultural_data/

#!/usr/bin/env python3
"""
Data Processing Pipeline
=======================

Main script that coordinates all data processing tasks for LULC initiatives.
This script provides a single entry point for all data generation tasks.

Features:
- Complete data loading and processing
- Comprehensive auxiliary data generation
- Validation and error handling
- Optimized performance
- English standardization
- Visualization-ready outputs

Author: LANDAGRI-B Project Team 
Date: 2025
"""

import sys
from pathlib import Path
from typing import Any

import pandas as pd

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from .lulc_data_engine import UnifiedDataProcessor
except ImportError:
    from lulc_data_engine import UnifiedDataProcessor


def setup_environment() -> None:
    """Set up required directories and environment."""
    print("🔧 Setting up environment...")

    directories = [
        "data/processed",
        "data/raw",
        "graphics/comparisons",
        "graphics/detailed",
        "graphics/temporal",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print("✅ Environment setup complete")


def run_full_processing_pipeline() -> tuple[
    pd.DataFrame | None,
    dict[str, Any] | None,
    dict[str, Any] | None,
    dict[str, Any] | None,
]:
    """Run the complete data processing pipeline.

    Returns:
        Tuple of (dataframe, metadata, auxiliary_data, validation_results) or None values on error.
    """
    print("🚀 Starting Unified Data Processing Pipeline")
    print("=" * 60)

    setup_environment()

    # Initialize unified processor
    processor = UnifiedDataProcessor()

    try:
        # Step 1: Load data from JSONC
        print("\n📥 Step 1: Loading data from JSONC...")
        df, metadata = processor.load_data_from_jsonc()

        # Step 2: Generate auxiliary data
        print("\n🔄 Step 2: Generating comprehensive auxiliary data...")
        auxiliary_data = processor.create_comprehensive_auxiliary_data(df, metadata)

        # Step 3: Validate data
        print("\n✅ Step 3: Validating processed data...")
        validation_results = processor.validate_data(df, metadata)

        # Step 4: Save all processed data
        print("\n💾 Step 4: Saving processed data...")

        # Save main dataset
        processor.save_data(df, "data/processed/initiatives_processed.csv", "CSV")

        # Save enhanced metadata
        processor.save_data(metadata, "data/processed/metadata_processed.json", "JSON")

        # Save auxiliary data
        processor.save_data(
            auxiliary_data, "data/processed/auxiliary_data.json", "JSON"
        )

        # Save validation report
        processor.save_data(
            validation_results, "data/processed/validation_report.json", "JSON"
        )

        # Step 5: Generate summary report
        print("\n📊 Step 5: Generating processing summary...")
        generate_processing_summary(df, metadata, auxiliary_data, validation_results)

        print("\n🎉 Unified processing pipeline completed successfully!")

        return df, metadata, auxiliary_data, validation_results

    except Exception as e:
        print(f"\n❌ Error in processing pipeline: {e}")
        import traceback

        traceback.print_exc()
        return None, None, None, None


def generate_processing_summary(
    df: pd.DataFrame,
    metadata: dict[str, Any],
    auxiliary_data: dict[str, Any],
    validation: dict[str, Any],
):
    """Generate a comprehensive processing summary."""

    summary = {
        "processing_timestamp": auxiliary_data.get("generation_timestamp", ""),
        "data_statistics": {
            "total_initiatives": len(df),
            "initiatives_with_temporal_data": len(
                [name for name in metadata if metadata[name].get("available_years", [])]
            ),
            "column_count": len(df.columns),
            "unique_providers": (
                df["Provider"].nunique() if "Provider" in df.columns else 0
            ),
            "coverage_types": (
                df["Coverage"].unique().tolist() if "Coverage" in df.columns else []
            ),  # Changed 'Type' to 'Coverage'
            "resolution_range": {
                "min": (
                    float(df["Spatial Resolution (m)"].min())
                    if "Spatial Resolution (m)" in df.columns
                    else 0
                ),  # Changed 'Resolution (m)' to 'Spatial Resolution (m)'
                "max": (
                    float(df["Spatial Resolution (m)"].max())
                    if "Spatial Resolution (m)" in df.columns
                    else 0
                ),  # Changed 'Resolution (m)' to 'Spatial Resolution (m)'
                "mean": (
                    float(df["Spatial Resolution (m)"].mean())
                    if "Spatial Resolution (m)" in df.columns
                    else 0
                ),  # Changed 'Resolution (m)' to 'Spatial Resolution (m)'
            },
            "accuracy_range": {
                "min": (
                    float(df["Overall Accuracy (%)"].min())
                    if "Overall Accuracy (%)" in df.columns
                    else 0
                ),  # Changed 'Accuracy (%)' to 'Overall Accuracy (%)'
                "max": (
                    float(df["Overall Accuracy (%)"].max())
                    if "Overall Accuracy (%)" in df.columns
                    else 0
                ),  # Changed 'Accuracy (%)' to 'Overall Accuracy (%)'
                "mean": (
                    float(df["Overall Accuracy (%)"].mean())
                    if "Overall Accuracy (%)" in df.columns
                    else 0
                ),  # Changed 'Accuracy (%)' to 'Overall Accuracy (%)'
            },
        },
        "auxiliary_data_status": {
            "comparison_matrix_generated": "comparison_matrix" in auxiliary_data,
            "temporal_analysis_generated": "temporal_analysis" in auxiliary_data,
            "comparison_matrix_size": len(auxiliary_data.get("comparison_matrix", {})),
            "temporal_initiatives_count": len(
                auxiliary_data.get("temporal_analysis", {}).get("initiatives", [])
            ),
        },
        "validation_status": {
            "dataframe_valid": validation.get("dataframe_valid", False),
            "metadata_valid": validation.get("metadata_valid", False),
            "total_issues": validation.get("summary", {}).get("total_issues", 0),
            "validation_passed": validation.get("summary", {}).get(
                "validation_passed", False
            ),
        },
        "files_generated": [
            "data/processed/initiatives_processed.csv",
            "data/processed/metadata_processed.json",
            "data/processed/auxiliary_data.json",
            "data/processed/validation_report.json",
        ],
    }

    # Save summary
    processor = UnifiedDataProcessor()
    processor.save_data(summary, "data/processed/processing_summary.json", "JSON")

    # Print summary to console
    print("\n📋 Processing Summary:")
    print(f"   • Total initiatives: {summary['data_statistics']['total_initiatives']}")
    print(f"   • Data columns: {summary['data_statistics']['column_count']}")
    print(f"   • Unique providers: {summary['data_statistics']['unique_providers']}")
    print(
        f"   • Validation passed: {summary['validation_status']['validation_passed']}"
    )
    print(f"   • Issues found: {summary['validation_status']['total_issues']}")
    print(f"   • Files generated: {len(summary['files_generated'])}")

    if summary["validation_status"]["total_issues"] > 0:
        print("   ⚠️ Please check validation_report.json for details")


def quick_test():
    """Quick test to verify the unified processor is working."""
    print("🧪 Running quick test of unified processor...")

    try:
        processor = UnifiedDataProcessor()
        df, metadata = processor.load_data_from_jsonc()

        print(f"✅ Test passed: {len(df)} initiatives loaded")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main entry point for the unified processing pipeline."""
    print("🌍 Unified Data Processing Pipeline for LULC Initiatives")
    print("🚀 Optimized, consolidated, and future-ready architecture")

    # Run quick test first
    if not quick_test():
        print("❌ Quick test failed. Please check your setup.")
        return

    # Run full pipeline
    results = run_full_processing_pipeline()

    if results[0] is not None:
        print("\n✨ All processing completed successfully!")
        print("📁 Check data/processed/ for generated files")
        print("📋 See processing_summary.json for detailed report")
    else:
        print("\n❌ Processing failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
