# 🌍 Dashboard Iniciativas LULC

**Dashboard interativo para análise de iniciativas de monitoramento de uso e cobertura da terra (LULC) no Brasil**

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.47.0-red.svg)
![Status](https://img.shields.io/badge/status-production--ready-green.svg)

---

## 🚀 Início Rápido

### Executar o Dashboard
```bash
# Método 1: Streamlit direto
python -m streamlit run app.py

# Método 2: Script personalizado com auto-reload
python run_app.py --port 8501

# Método 3: Com cache desabilitado
python run_app.py --no-cache
```

### Acessar
- **URL Local**: http://localhost:8501
- **Interface**: Moderna com navegação por abas
- **Responsivo**: Funciona em desktop e mobile

---

## 📊 Funcionalidades

### 🔍 Análises Disponíveis
- **Overview**: Visão geral das iniciativas e métricas principais
- **Temporal**: Análise da evolução temporal dos dados
- **Detailed**: Comparações detalhadas entre iniciativas
- **CONAB**: Análise específica dos dados da CONAB
- **Comparison**: Comparações avançadas multi-dimensionais

### 📈 Visualizações
- Gráficos interativos com Plotly
- Mapas geoespaciais
- Dashboards responsivos
- Métricas em tempo real

---

## 🛠️ Tecnologias

### Core Stack
- **Python 3.12** - Linguagem principal
- **Streamlit 1.47.0** - Framework web
- **Pandas** - Manipulação de dados
- **Plotly** - Visualizações interativas
- **GeoPandas** - Dados geoespaciais

### Qualidade & Performance
- **Ruff 0.12.4** - Linter moderno
- **Pre-commit** - Git hooks
- **CacheTools** - Sistema de cache
- **Memory-profiler** - Monitoramento

---

## 📚 Documentação

> **Toda a documentação detalhada está organizada na pasta [`docs/`](./docs/)**

### 📋 Principais Documentos
- [`docs/README.md`](./docs/README.md) - Índice completo da documentação
- [`docs/RELATORIO_OTIMIZACOES_FINAL.md`](./docs/RELATORIO_OTIMIZACOES_FINAL.md) - Relatório de otimizações
- [`docs/OTIMIZACOES_FASE3.md`](./docs/OTIMIZACOES_FASE3.md) - Detalhes técnicos das melhorias

---

## ⚡ Comandos Úteis

### Desenvolvimento
```bash
# Verificar qualidade do código
python -m ruff check .

# Aplicar formatação automática
python -m ruff format .

# Executar hooks de qualidade
pre-commit run --all-files

# Instalar hooks no git
pre-commit install
```

### Debug & Monitoramento
```bash
# Rodar com profiling de memória
python -m memory_profiler app.py

# Debug sem cache
python run_app.py --no-cache

# Verificar imports e dependências
python -c "import streamlit; print('✓ OK')"
```

---

## 🏗️ Estrutura do Projeto

```
📂 dashboard-iniciativas/
├── 📱 app.py                 # Entry point principal
├── 🔧 run_app.py            # Script de execução com opções
├── 📋 requirements.txt      # Dependências
├── ⚙️ pyproject.toml        # Configuração ruff
├── 🪝 .pre-commit-config.yaml # Git hooks
│
├── 📊 dashboard/            # Módulos do dashboard
│   ├── overview.py          # Visão geral
│   ├── temporal.py          # Análise temporal
│   ├── detailed.py          # Comparações detalhadas
│   ├── conab.py            # Análise CONAB
│   └── comparison.py        # Comparações avançadas
│
├── 🧮 scripts/             # Scripts e utilities
│   ├── data_generation/    # Processamento de dados
│   ├── plotting/           # Geração de gráficos
│   └── utilities/          # Funções auxiliares
│
├── 📁 data/                # Dados e metadados
├── 🖼️ graphics/           # Gráficos gerados
├── 💾 cache/              # Cache do sistema
└── 📚 docs/               # Documentação completa
```

---

## 📈 Status do Projeto

### ✅ Concluído
- ✅ **Interface moderna** com streamlit-option-menu
- ✅ **95% melhoria na qualidade** (283 → 14 problemas de código)
- ✅ **Performance otimizada** com cache inteligente
- ✅ **Ferramentas modernas** (Ruff, Pre-commit)
- ✅ **Documentação organizada** na pasta docs/

### 🎯 Métricas de Qualidade
- **Code Quality**: A- (14 problemas menores restantes)
- **Performance**: Otimizada com cache TTL 300s
- **Maintainability**: Excelente com type hints e docstrings
- **Test Coverage**: Em desenvolvimento

---

## 🤝 Contribuição

### Para Desenvolvedores
1. **Fork** o projeto
2. **Clone** localmente
3. **Instale** dependências: `pip install -r requirements.txt`
4. **Configure** hooks: `pre-commit install`
5. **Desenvolva** com qualidade: `python -m ruff check .`

### Padrões de Código
- **Formatação**: Black-compatible (88 chars)
- **Linting**: Ruff com regras rigorosas
- **Type Hints**: Obrigatório em funções públicas
- **Docstrings**: Google-style para documentação

---

## 📞 Suporte

### Documentação
- 📖 **Documentação completa**: [`docs/README.md`](./docs/README.md)
- 🔧 **Configurações**: Arquivos `.toml` e `.yaml`
- 📊 **Relatórios**: Pasta `docs/` com todos os detalhes

### Execução
- 🚀 **Dashboard**: `python -m streamlit run app.py`
- 🔍 **Debug**: `python run_app.py --no-cache`
- ✅ **Qualidade**: `python -m ruff check .`

---

**Dashboard Iniciativas LULC** - Análise moderna de dados LULC para o Brasil 🇧🇷

*Desenvolvido com ❤️ usando Python e Streamlit*
