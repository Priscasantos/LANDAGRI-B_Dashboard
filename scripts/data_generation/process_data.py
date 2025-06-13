#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

Author: Dashboard Iniciativas LULC
Date: 2025
"""

import sys
from pathlib import Path
from typing import Dict, Any
import pandas as pd

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from .data_processor import UnifiedDataProcessor
except ImportError:
    from data_processor import UnifiedDataProcessor

def setup_environment():
    """Setup required directories and environment."""
    print("🔧 Setting up environment...")
    
    directories = [
        'data/processed',
        'data/raw',
        'graphics/comparisons',
        'graphics/detailed', 
        'graphics/temporal'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Environment setup complete")

def run_full_processing_pipeline():
    """Run the complete data processing pipeline."""
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
        processor.save_data(df, 'data/processed/initiatives_processed.csv', 'CSV')
        
        # Save enhanced metadata
        processor.save_data(metadata, 'data/processed/metadata_processed.json', 'JSON')
        
        # Save auxiliary data
        processor.save_data(auxiliary_data, 'data/processed/auxiliary_data.json', 'JSON')
        
        # Save validation report
        processor.save_data(validation_results, 'data/processed/validation_report.json', 'JSON')
        
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

def generate_processing_summary(df: pd.DataFrame, metadata: Dict[str, Any], 
                              auxiliary_data: Dict[str, Any], validation: Dict[str, Any]):
    """Generate a comprehensive processing summary."""
    
    summary = {
        'processing_timestamp': auxiliary_data.get('generation_timestamp', ''),
        'data_statistics': {
            'total_initiatives': len(df),
            'initiatives_with_temporal_data': len([name for name in metadata.keys() 
                                                 if metadata[name].get('available_years', [])]),
            'column_count': len(df.columns),
            'unique_providers': df['Provider'].nunique() if 'Provider' in df.columns else 0,
            'coverage_types': df['Type'].unique().tolist() if 'Type' in df.columns else [],
            'resolution_range': {
                'min': float(df['Resolution (m)'].min()) if 'Resolution (m)' in df.columns else 0,
                'max': float(df['Resolution (m)'].max()) if 'Resolution (m)' in df.columns else 0,
                'mean': float(df['Resolution (m)'].mean()) if 'Resolution (m)' in df.columns else 0
            },
            'accuracy_range': {
                'min': float(df['Accuracy (%)'].min()) if 'Accuracy (%)' in df.columns else 0,
                'max': float(df['Accuracy (%)'].max()) if 'Accuracy (%)' in df.columns else 0,
                'mean': float(df['Accuracy (%)'].mean()) if 'Accuracy (%)' in df.columns else 0
            }
        },
        'auxiliary_data_status': {
            'comparison_matrix_generated': 'comparison_matrix' in auxiliary_data,
            'temporal_analysis_generated': 'temporal_analysis' in auxiliary_data,
            'comparison_matrix_size': len(auxiliary_data.get('comparison_matrix', {})),
            'temporal_initiatives_count': len(auxiliary_data.get('temporal_analysis', {}).get('initiatives', []))
        },
        'validation_status': {
            'dataframe_valid': validation.get('dataframe_valid', False),
            'metadata_valid': validation.get('metadata_valid', False),
            'total_issues': validation.get('summary', {}).get('total_issues', 0),
            'validation_passed': validation.get('summary', {}).get('validation_passed', False)
        },
        'files_generated': [
            'data/processed/initiatives_processed.csv',
            'data/processed/metadata_processed.json',
            'data/processed/auxiliary_data.json',
            'data/processed/validation_report.json'
        ]
    }
    
    # Save summary
    processor = UnifiedDataProcessor()
    processor.save_data(summary, 'data/processed/processing_summary.json', 'JSON')
    
    # Print summary to console
    print("\n📋 Processing Summary:")
    print(f"   • Total initiatives: {summary['data_statistics']['total_initiatives']}")
    print(f"   • Data columns: {summary['data_statistics']['column_count']}")
    print(f"   • Unique providers: {summary['data_statistics']['unique_providers']}")
    print(f"   • Validation passed: {summary['validation_status']['validation_passed']}")
    print(f"   • Issues found: {summary['validation_status']['total_issues']}")
    print(f"   • Files generated: {len(summary['files_generated'])}")
    
    if summary['validation_status']['total_issues'] > 0:
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
