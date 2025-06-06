# Arquivos Processados - Dashboard LULC

## Arquivos Criados

### 1. `initiatives_processed.csv`
CSV simplificado com dados tabulares extraídos do `initiative_meta.json`:
- **Nome**: Nome da iniciativa
- **Tipo**: Global, Nacional, Regional
- **Resolução (m)**: Resolução espacial em metros (numérico)
- **Acurácia (%)**: Acurácia em porcentagem (numérico)  
- **Classes**: Número de classes (numérico)
- **Metodologia**: Tipo de metodologia utilizada
- **Frequência Temporal**: Frequência de atualização
- **Anos Disponíveis**: Lista de anos em formato string
- **Escopo**: Descrição do escopo geográfico
- **Provedor**: Instituição responsável
- **Primeiro Ano**: Primeiro ano de cobertura
- **Último Ano**: Último ano de cobertura
- **Número de Anos**: Total de anos com dados
- **Maior Lacuna (anos)**: Maior lacuna temporal em anos
- **Anos com Lacuna**: Número de anos com lacunas > 1

### 2. `metadata_processed.json`
Metadados estruturados para análise de lacunas temporais:
```json
{
  "nome_iniciativa": {
    "anos_disponiveis": [lista de anos],
    "primeiro_ano": ano,
    "ultimo_ano": ano,
    "numero_anos": total,
    "maior_lacuna": maior lacuna,
    "anos_com_lacuna": número de lacunas,
    "escopo": "Global/Nacional/Regional",
    "tipo": "Global/Nacional/Regional",
    "provedor": "nome",
    "metodologia": "tipo"
  }
}
```

### 3. `config_simple.json`
Configurações para facilitar processamentos:
- Mapeamentos de arquivos
- Estrutura de colunas
- Mapeamentos de tipos e metodologias
- Cores para visualizações
- Configurações de filtros e exibição

### 4. `simple_analysis.py`
Funções utilitárias para análise simples:
- `load_simple_data()`: Carrega dados processados
- `gap_analysis_simple()`: Análise de lacunas simplificada
- `get_summary_stats()`: Estatísticas resumidas
- `get_initiatives_by_filter()`: Filtrar iniciativas
- `get_temporal_coverage_summary()`: Resumo temporal

### 5. `tables_updated.py`
Versão teste das funções atualizadas para `tools/tables.py`

### 6. `dashboard_simple.json`
Estrutura simplificada para substituir `dashboard_comparison_complete.json`:
- Metadados básicos
- Produtos com anos disponíveis e lacunas calculadas
- Formato compatível com as funções existentes

## Funcionalidades Implementadas

### ✅ Análise de Lacunas Temporais
- Função `gap_analysis()` atualizada em `tools/tables.py`
- Usa dados pré-processados para melhor performance
- Retorna colunas na ordem solicitada:
  - Nome, Primeiro Ano, Último Ano, Número de anos com lacuna temporal, Maior lacuna temporal, Tipo

### ✅ Dados Simplificados
- Extração automática de números de strings (resolução, acurácia, classes)
- Cálculo automático de métricas temporais
- Classificação automática por tipo (Global/Nacional/Regional)

### ✅ Compatibilidade
- Mantém assinatura das funções existentes
- Funciona com filtros e DataFrame existentes
- Performance melhorada (sem cálculos complexos em tempo real)

### ✅ Correções Realizadas
- Sintaxe corrigida em `comparison.py`
- Botão de download atualizado para usar nome correto da coluna
- Tabela de lacunas temporais funcionando corretamente

## Como Usar

1. **Carregar dados simples**:
```python
from initiative_data.simple_analysis import load_simple_data
df, metadata, config = load_simple_data()
```

2. **Análise de lacunas atualizada**:
```python
from tools.tables import gap_analysis
gap_df = gap_analysis(metadata, filtered_df)
```

3. **Estatísticas resumidas**:
```python
from initiative_data.simple_analysis import get_summary_stats
stats = get_summary_stats()
```

## Resultados dos Testes

✅ **14 iniciativas** processadas com sucesso
✅ **4 iniciativas com lacunas temporais** identificadas:
- FROM-GLC: 5 anos de lacuna máxima
- PRODES Cerrado: 2 anos de lacuna máxima 
- TerraClass Amazônia: 4 anos de lacuna máxima
- IBGE Monitoramento: 2 anos de lacuna máxima

✅ **Estatísticas gerais**:
- Acurácia média: 79.6%
- Resolução média: 99m
- 8 iniciativas globais, 2 nacionais, 4 regionais

Todos os arquivos estão prontos para uso no dashboard e permitem processamento rápido e simples das tabelas e gráficos!
