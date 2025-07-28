"""
Test Suite for Agricultural Charts Module
========================================

Comprehensive testing for CONAB agricultural data visualization.
"""

import unittest
import sys
import os
from pathlib import Path
import pandas as pd
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from scripts.plotting.charts.agricultural_charts import (
        load_conab_data,
        plot_crop_calendar_heatmap,
        plot_regional_crop_coverage,
        plot_temporal_crop_trends,
        plot_crop_diversity_by_region,
        plot_agricultural_performance_metrics,
        create_agricultural_summary_stats
    )
    AGRICULTURAL_CHARTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Agricultural charts module not available: {e}")
    AGRICULTURAL_CHARTS_AVAILABLE = False


class TestAgriculturalCharts(unittest.TestCase):
    """Test cases for agricultural charts functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Fix path construction for Windows
        cls.data_dir = project_root / "data" / "json"
        cls.detailed_file = cls.data_dir / "conab_detailed_initiative.jsonc"
        cls.calendar_file = cls.data_dir / "conab_crop_calendar_complete.jsonc"
        
        # Print debug info
        print(f"Project root: {project_root}")
        print(f"Data dir: {cls.data_dir}")
        print(f"Detailed file: {cls.detailed_file}")
        print(f"Calendar file: {cls.calendar_file}")
        
    def setUp(self):
        """Set up each test."""
        if not AGRICULTURAL_CHARTS_AVAILABLE:
            self.skipTest("Agricultural charts module not available")
    
    def test_data_files_exist(self):
        """Test that required CONAB data files exist."""
        self.assertTrue(
            self.detailed_file.exists(),
            f"CONAB detailed initiative file not found: {self.detailed_file}"
        )
        self.assertTrue(
            self.calendar_file.exists(),
            f"CONAB crop calendar file not found: {self.calendar_file}"
        )
    
    def test_load_conab_data(self):
        """Test CONAB data loading function."""
        detailed_data, calendar_data = load_conab_data()
        
        # Test that data is loaded
        self.assertIsNotNone(detailed_data, "Detailed data should not be None")
        self.assertIsNotNone(calendar_data, "Calendar data should not be None")
        
        # Test data structure
        if detailed_data:
            self.assertIsInstance(detailed_data, dict, "Detailed data should be a dictionary")
        
        if calendar_data:
            self.assertIsInstance(calendar_data, dict, "Calendar data should be a dictionary")
    
    def test_create_agricultural_summary_stats(self):
        """Test agricultural summary statistics creation."""
        detailed_data, calendar_data = load_conab_data()
        stats = create_agricultural_summary_stats(detailed_data, calendar_data)
        
        # Test that stats is a dictionary
        self.assertIsInstance(stats, dict, "Stats should be a dictionary")
        
        # Test required keys
        required_keys = ['total_crops', 'total_regions', 'year_span', 'accuracy', 'main_crops']
        for key in required_keys:
            self.assertIn(key, stats, f"Stats should contain key: {key}")
        
        # Test data types
        self.assertIsInstance(stats['total_crops'], int, "Total crops should be integer")
        self.assertIsInstance(stats['total_regions'], int, "Total regions should be integer")
        self.assertIsInstance(stats['accuracy'], (int, float), "Accuracy should be numeric")
        self.assertIsInstance(stats['main_crops'], list, "Main crops should be a list")
    
    def test_plot_crop_calendar_heatmap(self):
        """Test crop calendar heatmap generation."""
        detailed_data, calendar_data = load_conab_data()
        
        if calendar_data:
            try:
                fig = plot_crop_calendar_heatmap(calendar_data)
                
                # Test that figure is created
                self.assertIsNotNone(fig, "Figure should not be None")
                
                # Test figure properties
                self.assertTrue(hasattr(fig, 'data'), "Figure should have data attribute")
                self.assertTrue(hasattr(fig, 'layout'), "Figure should have layout attribute")
                
                # Test that figure has data
                self.assertGreater(len(fig.data), 0, "Figure should contain plot data")
                
            except Exception as e:
                self.fail(f"Crop calendar heatmap generation failed: {e}")
        else:
            self.skipTest("Calendar data not available")
    
    def test_plot_regional_crop_coverage(self):
        """Test regional crop coverage chart generation."""
        detailed_data, calendar_data = load_conab_data()
        
        if detailed_data:
            try:
                fig = plot_regional_crop_coverage(detailed_data)
                
                # Test that figure is created
                self.assertIsNotNone(fig, "Figure should not be None")
                self.assertTrue(hasattr(fig, 'data'), "Figure should have data attribute")
                self.assertGreater(len(fig.data), 0, "Figure should contain plot data")
                
            except Exception as e:
                self.fail(f"Regional coverage chart generation failed: {e}")
        else:
            self.skipTest("Detailed data not available")
    
    def test_plot_temporal_crop_trends(self):
        """Test temporal crop trends chart generation."""
        detailed_data, calendar_data = load_conab_data()
        
        if detailed_data:
            try:
                fig = plot_temporal_crop_trends(detailed_data)
                
                # Test that figure is created
                self.assertIsNotNone(fig, "Figure should not be None")
                self.assertTrue(hasattr(fig, 'data'), "Figure should have data attribute")
                self.assertGreater(len(fig.data), 0, "Figure should contain plot data")
                
            except Exception as e:
                self.fail(f"Temporal trends chart generation failed: {e}")
        else:
            self.skipTest("Detailed data not available")
    
    def test_plot_crop_diversity_by_region(self):
        """Test crop diversity sunburst chart generation."""
        detailed_data, calendar_data = load_conab_data()
        
        if detailed_data:
            try:
                fig = plot_crop_diversity_by_region(detailed_data)
                
                # Test that figure is created
                self.assertIsNotNone(fig, "Figure should not be None")
                self.assertTrue(hasattr(fig, 'data'), "Figure should have data attribute")
                self.assertGreater(len(fig.data), 0, "Figure should contain plot data")
                
            except Exception as e:
                self.fail(f"Diversity sunburst chart generation failed: {e}")
        else:
            self.skipTest("Detailed data not available")
    
    def test_plot_agricultural_performance_metrics(self):
        """Test agricultural performance metrics chart generation."""
        detailed_data, calendar_data = load_conab_data()
        
        if detailed_data:
            try:
                fig = plot_agricultural_performance_metrics(detailed_data)
                
                # Test that figure is created
                self.assertIsNotNone(fig, "Figure should not be None")
                self.assertTrue(hasattr(fig, 'data'), "Figure should have data attribute")
                self.assertGreater(len(fig.data), 0, "Figure should contain plot data")
                
            except Exception as e:
                self.fail(f"Performance metrics chart generation failed: {e}")
        else:
            self.skipTest("Detailed data not available")
    
    def test_data_integration(self):
        """Test integration between different chart functions."""
        detailed_data, calendar_data = load_conab_data()
        
        if detailed_data and calendar_data:
            try:
                # Test that all charts can be generated in sequence
                chart_functions = [
                    plot_crop_calendar_heatmap,
                    plot_regional_crop_coverage,
                    plot_temporal_crop_trends,
                    plot_crop_diversity_by_region,
                    plot_agricultural_performance_metrics
                ]
                
                for i, func in enumerate(chart_functions):
                    if func == plot_crop_calendar_heatmap:
                        fig = func(calendar_data)
                    else:
                        fig = func(detailed_data)
                    
                    self.assertIsNotNone(fig, f"Chart function {i+1} should return a figure")
                
            except Exception as e:
                self.fail(f"Chart integration test failed: {e}")
        else:
            self.skipTest("Required data not available for integration test")


class TestAgriculturalDashboard(unittest.TestCase):
    """Test cases for agricultural dashboard components."""
    
    def setUp(self):
        """Set up each test."""
        if not AGRICULTURAL_CHARTS_AVAILABLE:
            self.skipTest("Agricultural charts module not available")
    
    def test_dashboard_imports(self):
        """Test that dashboard components can be imported."""
        try:
            from dashboard.components.agricultural.agricultural_dashboard import (
                render_agricultural_dashboard,
                render_agricultural_summary_widget
            )
            
            # Test that functions are callable
            self.assertTrue(callable(render_agricultural_dashboard))
            self.assertTrue(callable(render_agricultural_summary_widget))
            
        except ImportError as e:
            self.fail(f"Failed to import dashboard components: {e}")
    
    def test_page_imports(self):
        """Test that agricultural analysis page can be imported."""
        try:
            # Test that the page file exists
            page_file = project_root / "pages" / "🌾_Agricultural_Analysis.py"
            self.assertTrue(page_file.exists(), "Agricultural analysis page should exist")
            
        except Exception as e:
            self.fail(f"Failed to test page imports: {e}")


def run_tests():
    """Run all agricultural tests."""
    print("=" * 60)
    print("RUNNING AGRICULTURAL CHARTS TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestAgriculturalCharts))
    suite.addTest(unittest.makeSuite(TestAgriculturalDashboard))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
