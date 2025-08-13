# 🌍 LANDAGRI-B Dashboard

**Interactive dashboard for analyzing land use and land cover (LULC) monitoring initiatives in Brazil**

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.47.0-red.svg)](https://streamlit.io/)
[![Status](https://img.shields.io/badge/status-production--ready-green.svg)](https://github.com/Priscasantos/LANDAGRI-B_Dashboard)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> 🔗 **Repository**: [https://github.com/Priscasantos/LANDAGRI-B_Dashboard](https://github.com/Priscasantos/LANDAGRI-B_Dashboard)

---

## 🚀 Quick Start

### Run the Dashboard
```bash
# Method 1: Directly with Streamlit
python -m streamlit run app.py

# Method 2: Custom script with auto-reload
python run_app.py --port 8501

# Method 3: With cache disabled
python run_app.py --no-cache
```

### Access
- **Local URL**: http://localhost:8501
- **Interface**: Modern tabbed navigation
- **Responsive**: Works on desktop and mobile

---

## 📊 Features

### 🔍 Available Analyses
- **Overview**: General view of initiatives and key metrics
- **Temporal**: Analysis of data evolution over time
- **Detailed**: Detailed comparisons between initiatives
- **CONAB**: Specific analysis of CONAB data
- **Comparison**: Advanced multi-dimensional comparisons

### 📈 Visualizations
- Interactive charts with Plotly
- Geospatial maps
- Responsive dashboards
- Real-time metrics

---

## 🛠️ Technologies

### Core Stack
- **Python 3.12** - Main language
- **Streamlit 1.47.0** - Web framework
- **Pandas** - Data manipulation
- **Plotly** - Interactive visualizations
- **GeoPandas** - Geospatial data

### Quality & Performance
- **Ruff 0.12.4** - Modern linter
- **Pre-commit** - Git hooks
- **CacheTools** - Caching system
- **Memory-profiler** - Monitoring

---

## 📚 Documentation

> **All detailed documentation is organized in the [`docs/`](./docs/) folder**

### 📋 Key Documents
- [`docs/README.md`](./docs/README.md) - Complete documentation index
- [`docs/RELATORIO_OTIMIZACOES_FINAL.md`](./docs/RELATORIO_OTIMIZACOES_FINAL.md) - Optimization report
- [`docs/OTIMIZACOES_FASE3.md`](./docs/OTIMIZACOES_FASE3.md) - Technical details of improvements

---

## ⚡ Useful Commands

### Development
```bash
# Check code quality
python -m ruff check .

# Apply automatic formatting
python -m ruff format .

# Run quality hooks
pre-commit run --all-files

# Install git hooks
pre-commit install
```

### Debug & Monitoring
```bash
# Run with memory profiling
python -m memory_profiler app.py

# Debug without cache
python run_app.py --no-cache

# Check imports and dependencies
python -c "import streamlit; print('✓ OK')"
```

---

## 🏗️ Project Structure

```
📂 dashboard-iniciatives/
├── 📱 app.py                 # Main entry point
├── 🔧 run_app.py            # Execution script with options
├── 📋 requirements.txt      # Dependencies
├── ⚙️ pyproject.toml        # Ruff configuration
├── 🪝 .pre-commit-config.yaml # Git hooks
│
├── 📊 dashboard/            # Dashboard modules
│   ├── overview.py          # Overview
│   ├── temporal.py          # Temporal analysis
│   ├── detailed.py          # Detailed comparisons
│   ├── conab.py             # CONAB analysis
│   └── comparison.py        # Advanced comparisons
│
├── 🧮 scripts/               # Scripts and utilities
│   ├── data_generation/     # Data processing
│   ├── plotting/            # Chart generation
│   └── utilities/           # Helper functions
│
├── 📁 data/                 # Data and metadata
├── 🖼️ graphics/             # Generated graphics
├── 💾 cache/                # System cache
└── 📚 docs/                 # Complete documentation
```

---

## 📈 Project Status

### ✅ Completed
- ✅ **Modern interface** with streamlit-option-menu
- ✅ **95% code quality improvement** (283 → 14 issues)
- ✅ **Optimized performance** with smart caching
- ✅ **Modern tools** (Ruff, Pre-commit)
- ✅ **Organized documentation** in the docs/ folder

### 🎯 Quality Metrics
- **Code Quality**: A- (14 minor issues remaining)
- **Performance**: Optimized with TTL 300s cache
- **Maintainability**: Excellent with type hints and docstrings
- **Test Coverage**: In development

---

## 🤝 Contributing

### For Developers
1. **Fork** the project
2. **Clone** locally
3. **Install** dependencies: `pip install -r requirements.txt`
4. **Set up** hooks: `pre-commit install`
5. **Develop** with quality: `python -m ruff check .`

### Code Standards
- **Formatting**: Black-compatible (88 chars)
- **Linting**: Ruff with strict rules
- **Type Hints**: Required in public functions
- **Docstrings**: Google-style for documentation

---

## 📞 Support

### Documentation
- 📖 **Full documentation**: [`docs/README.md`](./docs/README.md)
- 🔧 **Configurations**: `.toml` and `.yaml` files
- 📊 **Reports**: `docs/` folder with all details

### Running
- 🚀 **Dashboard**: `python -m streamlit run app.py`
- 🔍 **Debug**: `python run_app.py --no-cache`
- ✅ **Quality**: `python -m ruff check .`

---

## Running the Dashboard (Recommended Mode)

To always run the dashboard during development or production, use the standard command:

```sh
python -m streamlit run app.py --server.port 8501
```

This ensures Streamlit runs on the correct port with the recommended configuration. You can also use the VS Code task "Run Streamlit Dashboard (Standard)" for convenience.

---

**LANDAGRI-B Dashboard** - Modern LULC data analysis for Brazil 🇧🇷

*Developed with ❤️ using Python and Streamlit*
