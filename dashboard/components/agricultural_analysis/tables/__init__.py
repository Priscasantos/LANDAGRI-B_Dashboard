"""
Tables Module
=============

Module for creating enhanced table displays for agricultural data analysis.
Provides formatted tables with improved styling and interactivity.
"""

from .summary_tables import (
    create_crop_summary_table,
    create_regional_summary_table,
    create_activities_summary_table,
    format_dataframe_display
)

__all__ = [
    'create_crop_summary_table',
    'create_regional_summary_table', 
    'create_activities_summary_table',
    'format_dataframe_display'
]
