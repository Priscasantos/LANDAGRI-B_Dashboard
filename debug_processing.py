#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug processamento dos acronyms"""

from scripts.data_generation.lulc_data_engine import UnifiedDataProcessor

processor = UnifiedDataProcessor()
df, metadata = processor.load_data_from_jsonc()

print('🔍 Verificando se os acronyms do JSON estão no DataFrame:')
print('-' * 50)

# Verificar Dynamic World V1
dynamic_world = df[df['Name'] == 'Dynamic World V1']
if not dynamic_world.empty:
    acronym = dynamic_world['Acronym'].iloc[0]
    print(f'Dynamic World V1 -> {acronym}')
    
    # Verificar o que está acontecendo no código
    name = 'Dynamic World V1'
    metadata_acronym = metadata[name].get('acronym', 'NÃO ENCONTRADO')
    hardcoded_acronym = processor.name_to_acronym.get(name, name[:8])
    
    print(f'Acronym do JSON: {metadata_acronym}')
    print(f'Acronym hardcoded: {hardcoded_acronym}')
    print(f'Acronym no DataFrame: {acronym}')
else:
    print('❌ Dynamic World V1 não encontrado no DataFrame')

# Verificar Copernicus 
cgls = df[df['Name'].str.contains('Copernicus', na=False)]
if not cgls.empty:
    name = cgls['Name'].iloc[0]
    acronym = cgls['Acronym'].iloc[0]
    print(f'\\n{name} -> {acronym}')
    
    metadata_acronym = metadata[name].get('acronym', 'NÃO ENCONTRADO')
    hardcoded_acronym = processor.name_to_acronym.get(name, name[:8])
    
    print(f'Acronym do JSON: {metadata_acronym}')
    print(f'Acronym hardcoded: {hardcoded_acronym}')
    print(f'Acronym no DataFrame: {acronym}')
