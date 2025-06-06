# 🧪 Testes de Visualizações LULC

Este diretório contém o sistema de testes para avaliação de novas visualizações gráficas para o dashboard LULC.

## Arquivo Principal

- `teste_graficos.py` - Sistema interativo de testes de visualizações

## Como Executar

### Opção 1: Executar direto da pasta tests
```bash
cd tests
streamlit run teste_graficos.py --server.port 8504
```

### Opção 2: Executar do diretório principal
```bash
streamlit run tests/teste_graficos.py --server.port 8504
```

## Visualizações Disponíveis para Teste

1. **Barras Horizontais Duplas** - Comparação lado a lado de acurácia e resolução
2. **Gráfico de Radar (Spider Chart)** - Visualização multidimensional
3. **Heatmap de Comparação** - Matriz de valores normalizados
4. **Pizza - Distribuição por Metodologia** - Proporções das metodologias
5. **Pizza - Distribuição por Escopo** - Proporções dos escopos geográficos
6. **Análise de Acurácia Aprimorada** - Múltiplas visualizações especializadas
   - 6A. Ranking de Acurácia (Barras)
   - 6B. Scatter Plot Melhorado
   - 6C. Heatmap de Performance
   - 6D. Gráfico de Bolhas Interativo
   - 6E. Comparação Categórica
7. **Gráfico de Bolhas - 3 Dimensões** - Acurácia vs Resolução vs Classes
8. **Disponibilidade Temporal** - Matriz de disponibilidade ao longo do tempo
9. **Box Plot - Distribuição por Metodologia** - Estatísticas por metodologia
10. **Sunburst - Hierarquia de Categorias** - Visualização hierárquica

## Funcionalidades

- ✅ Filtros interativos por tipo, resolução, acurácia e metodologia
- ✅ Configurações de performance (limite de registros, indicadores de carregamento)
- ✅ Download de gráficos em PNG
- ✅ Interface limpa e organizada por teste
- ✅ Carregamento otimizado com spinners

## Objetivo

Avaliar quais visualizações são mais efetivas para:
- Análise comparativa de iniciativas LULC
- Identificação de padrões nos dados
- Facilidade de interpretação pelos usuários
- Performance de renderização

## Próximos Passos

Após testar as visualizações, as melhores serão integradas ao dashboard principal substituindo as visualizações atuais menos efetivas.
