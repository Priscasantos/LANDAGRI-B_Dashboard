#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug acronyms do JSON"""

import json

# Carregar o JSON para verificar
with open('data/raw/initiatives_metadata.jsonc', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove comments from JSONC
lines = content.split('\n')
cleaned_lines = []
for line in lines:
    if '//' in line:
        comment_pos = line.find('//')
        line = line[:comment_pos]
    cleaned_lines.append(line)

cleaned_content = '\n'.join(cleaned_lines)
metadata = json.loads(cleaned_content)

print('🔍 Verificando acronyms no JSON:')
print('-' * 50)

for name, data in list(metadata.items())[:5]:
    acronym = data.get('acronym', 'NÃO ENCONTRADO')
    print(f'Nome: {name}')
    print(f'Acronym: {acronym}')
    print('-' * 30)

# Verificar especificamente Dynamic World V1
if 'Dynamic World V1' in metadata:
    dw_data = metadata['Dynamic World V1']
    print(f'🎯 Dynamic World V1:')
    print(f'   Acronym no JSON: {dw_data.get("acronym", "NÃO ENCONTRADO")}')
else:
    print('❌ Dynamic World V1 não encontrado no JSON')
