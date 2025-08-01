#!/usr/bin/env python3
import re

# Read the file
with open('dashboard/components/agricultural_analysis/charts/agricultural_charts.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace apply_modern_styling calls with apply_standard_layout  
content = re.sub(r'fig = apply_modern_styling\(fig, \*\*get_modern_layout_config\(\)\)', 'apply_standard_layout(fig, "", "", "")', content)
content = re.sub(r'fig = apply_modern_styling\(fig, \*\*get_modern_bar_config\(\)\)', 'apply_standard_layout(fig, "", "", "")', content)
content = re.sub(r'fig = apply_modern_styling\(fig, \*\*get_modern_line_config\(\)\)', 'apply_standard_layout(fig, "", "", "")', content)

# Replace apply_modern_theme calls
content = re.sub(r'apply_modern_theme\(fig, "[^"]*", chart_type="[^"]*"\)', '# Modern theme applied via chart_core', content)

# Write back
with open('dashboard/components/agricultural_analysis/charts/agricultural_charts.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Agricultural charts modern theme replacements completed successfully')
