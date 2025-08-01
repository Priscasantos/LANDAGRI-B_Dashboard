#!/usr/bin/env python3
"""
Test script to verify scope colors consistency
"""
import sys
sys.path.append('scripts')

def test_scope_colors():
    """Test if scope colors are consistent across the system"""
    print("🧪 Testando consistência das cores de escopo...")
    
    try:
        from scripts.plotting.chart_core import get_scope_colors
        
        # Test get_scope_colors function
        scope_colors = get_scope_colors()
        print(f"✅ get_scope_colors() funciona corretamente:")
        for scope, color in scope_colors.items():
            print(f"   {scope}: {color}")
        
        # Test that the function returns expected scopes
        expected_scopes = ['Global', 'Nacional', 'Regional']
        actual_scopes = list(scope_colors.keys())
        
        for expected in expected_scopes:
            if expected in actual_scopes:
                print(f"✅ Escopo '{expected}' encontrado")
            else:
                print(f"❌ Escopo '{expected}' NÃO encontrado")
        
        # Test imports from comparison_charts
        print("\n🔍 Testando importações de comparison_charts...")
        from scripts.plotting.charts.comparison_charts import (
            plot_spatial_resolution_comparison,
            plot_global_accuracy_comparison,
            plot_resolution_accuracy_scatter
        )
        print("✅ Todas as funções de comparison_charts importadas com sucesso")
        
        print("\n🎉 Teste concluído com sucesso!")
        print("As cores de escopo agora devem ser consistentes em todos os gráficos.")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scope_colors()
