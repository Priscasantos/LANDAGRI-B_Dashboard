#!/usr/bin/env python3
import re

# Read the file
with open('scripts/plotting/charts/resolution_comparison_charts.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace font=dict(size=14) with get_font_config('annotation')
content = re.sub(r'font=dict\(size=14\)', 'font=get_font_config("annotation")', content)

# Replace font=dict(size=12) with get_font_config('annotation_small')  
content = re.sub(r'font=dict\(size=12\)', 'font=get_font_config("annotation_small")', content)

# Write back
with open('scripts/plotting/charts/resolution_comparison_charts.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Replacements completed successfully')
