#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para sincronizar e atualizar todos os dados do dashboard
"""

import pandas as pd
import json

def process_years_data(metadata_dict):
    """Processa os anos disponíveis dos metadados para o formato do dashboard."""
    processed_metadata = {}
    
    for name, meta in metadata_dict.items():
        processed_meta = meta.copy()
        
        # Garantir que anos_disponiveis seja uma lista
        if 'anos_disponiveis' in processed_meta:
            if isinstance(processed_meta['anos_disponiveis'], list):
                # Já é uma lista, manter como está
                pass
            elif isinstance(processed_meta['anos_disponiveis'], str):
                # Converter string para lista
                try:
                    anos_str = processed_meta['anos_disponiveis']
                    if '-' in anos_str and ',' not in anos_str:
                        # Formato "2015-2019"
                        start, end = map(int, anos_str.split('-'))
                        processed_meta['anos_disponiveis'] = list(range(start, end + 1))
                    else:
                        # Formato "2015,2016,2017" ou similar
                        processed_meta['anos_disponiveis'] = [int(x.strip()) for x in anos_str.split(',')]
                except:
                    processed_meta['anos_disponiveis'] = []
        else:
            processed_meta['anos_disponiveis'] = []
            
        processed_metadata[name] = processed_meta
    
    return processed_metadata

def create_csv_from_metadata(metadata_dict):
    """Cria um CSV atualizado baseado nos metadados."""
    data_rows = []
    
    for name, meta in metadata_dict.items():
        # Determinar o tipo baseado no escopo
        escopo = meta.get('escopo', 'Global')
        if 'Global' in escopo:
            tipo = 'Global'
        elif 'Nacional' in escopo or 'Brasil' in escopo:
            tipo = 'Nacional'
        elif 'Regional' in escopo:
            tipo = 'Regional'
        else:
            tipo = 'Global'
        
        # Extrair resolução numérica
        resolucao_str = meta.get('resolucao_espacial', '30m')
        try:
            resolucao = float(resolucao_str.replace('m', '').replace('-', '').split()[0])
        except:
            resolucao = 30.0
            
        # Extrair acurácia numérica
        acuracia_str = meta.get('acuracia', '0%')
        try:
            if acuracia_str == 'Not informed' or acuracia_str == 'Incomplete':
                acuracia = 0.0
            else:
                acuracia = float(acuracia_str.replace('%', '').replace('≥', '').replace('>', '').strip())
        except:
            acuracia = 0.0
        
        # Extrair número de classes
        classes_str = meta.get('classes', '1 classe')
        try:
            classes = int(classes_str.split()[0])
        except:
            classes = 1
            
        # Criar string de anos disponíveis
        anos_list = meta.get('anos_disponiveis', [])
        anos_str = ','.join(map(str, anos_list)) if anos_list else ''
        
        # Determinar primeiro e último ano
        primeiro_ano = min(anos_list) if anos_list else 0
        ultimo_ano = max(anos_list) if anos_list else 0
        numero_anos = len(anos_list)
        
        # Calcular lacunas
        maior_lacuna = 0
        anos_com_lacuna = 0
        if numero_anos > 1:
            anos_sorted = sorted(anos_list)
            gaps = []
            for i in range(1, len(anos_sorted)):
                gap = anos_sorted[i] - anos_sorted[i-1] - 1
                if gap > 0:
                    gaps.append(gap)
            maior_lacuna = max(gaps) if gaps else 0
            anos_com_lacuna = sum(gaps)
        
        data_rows.append({
            'Nome': name,
            'Tipo': tipo,
            'Resolução (m)': resolucao,
            'Acurácia (%)': acuracia,
            'Classes': classes,
            'Metodologia': meta.get('tipo_metodologia', 'Não informado'),
            'Frequência Temporal': meta.get('frequencia_temporal', 'Não informado'),
            'Anos Disponíveis': anos_str,
            'Escopo': escopo,
            'Provedor': meta.get('provedor', 'Não informado'),
            'Primeiro Ano': primeiro_ano,
            'Último Ano': ultimo_ano,
            'Número de Anos': numero_anos,
            'Maior Lacuna (anos)': maior_lacuna,
            'Anos com Lacuna': anos_com_lacuna
        })
    
    return pd.DataFrame(data_rows)

def main():
    print("🔄 Sincronizando todos os dados do dashboard...")
    print("=" * 50)
    
    # 1. Processar metadados atualizados
    print("📋 1. Processando metadados...")
    with open('initiative_data/initiative_meta.json', 'r', encoding='utf-8') as f:
        raw_metadata = json.load(f)
    
    processed_metadata = process_years_data(raw_metadata)
    
    # Salvar metadados processados
    with open('initiative_data/metadata_processed.json', 'w', encoding='utf-8') as f:
        json.dump(processed_metadata, f, ensure_ascii=False, indent=2)
    print("   ✅ Metadados processados salvos em metadata_processed.json")
    
    # 2. Criar CSV atualizado baseado nos metadados
    print("📊 2. Criando CSV atualizado...")
    df_updated = create_csv_from_metadata(processed_metadata)
    
    # Salvar CSV processado
    df_updated.to_csv('initiative_data/initiatives_processed.csv', index=False, encoding='utf-8')
    print("   ✅ CSV atualizado salvo em initiatives_processed.csv")
    
    # 3. Estatísticas finais
    print("📈 3. Estatísticas dos dados atualizados:")
    print(f"   - Total de iniciativas: {len(df_updated)}")
    print(f"   - Iniciativas globais: {len(df_updated[df_updated['Tipo'] == 'Global'])}")
    print(f"   - Iniciativas nacionais: {len(df_updated[df_updated['Tipo'] == 'Nacional'])}")
    print(f"   - Iniciativas regionais: {len(df_updated[df_updated['Tipo'] == 'Regional'])}")
    print(f"   - Acurácia média: {df_updated[df_updated['Acurácia (%)'] > 0]['Acurácia (%)'].mean():.1f}%")
    print(f"   - Resolução média: {df_updated['Resolução (m)'].mean():.1f}m")
    
    print("\n✨ Sincronização concluída com sucesso!")
    print("🚀 O dashboard está pronto para uso com os dados atualizados.")

if __name__ == "__main__":
    main()
