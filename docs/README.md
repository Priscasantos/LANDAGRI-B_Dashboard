# 📚 Documentation - LANDAGRI-B Dashboard

**Last updated:** July 23, 2025  
**Version:** 3.1  
**Status:** Actively in development

---

## 📋 Documentation Index

### 🏗️ Development Reports

- [`RELATORIO_OTIMIZACOES_FINAL.md`](./RELATORIO_OTIMIZACOES_FINAL.md) - Complete report of implemented optimizations
- [`OTIMIZACOES_FASE3.md`](./OTIMIZACOES_FASE3.md) - Details of Phase 3 optimizations
- [`FASE3_OTIMIZACOES_FINAIS.md`](./FASE3_OTIMIZACOES_FINAIS.md) - Final optimizations for Phase 3
- [`MODERNIZATION_REPORT.md`](./MODERNIZATION_REPORT.md) - Dashboard modernization report
- [`REORGANIZACAO_CODEBASE.md`](./REORGANIZACAO_CODEBASE.md) - Documentation reorganization report

### 🐛 Fixes and Migration

- [`FONT_WEIGHT_FIX.md`](./FONT_WEIGHT_FIX.md) - Plotly Font Weight bug fix
- [`SENSOR_METADATA_FIX.md`](./SENSOR_METADATA_FIX.md) - Sensor metadata system fix
- [`MIGRATION_REPORT.md`](./MIGRATION_REPORT.md) - Agricultural data migration report

### 🔧 Agricultural System

- [`SISTEMA_PROCESSADORES_AGRICOLAS.md`](./SISTEMA_PROCESSADORES_AGRICOLAS.md) - Agricultural data processors system
- [`relatorio-limpeza-validacao.md`](./relatorio-limpeza-validacao.md) - Data cleaning and validation report

### 📊 Data and Resources

- [`README_brazil-vector.md`](./README_brazil-vector.md) - Documentation for Brazil vector data
- [`ORGANIZACAO_DOCUMENTACAO.md`](./ORGANIZACAO_DOCUMENTACAO.md) - Documentation organization

### 🔧 Configuration Files

- [`../pyproject.toml`](../pyproject.toml) - Ruff (linter) configuration
- [`../.pre-commit-config.yaml`](../.pre-commit-config.yaml) - Git hooks configuration
- [`../.streamlit/config.toml`](../.streamlit/config.toml) - Streamlit settings

---

## 🚀 How to Use this Documentation

### For Developers

1. **Quick Start**: Read `RELATORIO_OTIMIZACOES_FINAL.md`
2. **Technical Details**: See `OTIMIZACOES_FASE3.md`
3. **Data**: Check `README_brazil-vector.md` for data understanding
4. **Agricultural System**: See `SISTEMA_PROCESSADORES_AGRICOLAS.md`

### For Users

1. **Run Dashboard**: `python -m streamlit run app.py`
2. **Check Quality**: `python -m ruff check .`
3. **Apply Formatting**: `python -m ruff format .`

---

## 📈 Version History

### v3.1 (07/23/2025)

- ✅ Complete documentation reorganization
- ✅ All documentation files moved to `docs/`
- ✅ Removal of temporary test and validation files
- ✅ Agricultural processors system implemented
- ✅ Documentation index updated

### v3.0 (07/22/2025)

- ✅ Complete code quality optimizations
- ✅ 95% quality improvement (283 → 14 issues)
- ✅ Modern tools configured (Ruff, Pre-commit)
- ✅ Performance optimized
- ✅ Documentation organized

### v2.x (Previous)

- Core features implemented
- Modern interface with streamlit-option-menu
- Optimized cache system

---

## 🛠️ Technology Stack

### Core

- **Python 3.12** - Main language
- **Streamlit 1.47.0** - Dashboard framework
- **Pandas** - Data manipulation
- **Plotly** - Interactive visualizations

### Quality & Tools

- **Ruff 0.12.4** - Modern, fast linter
- **Pre-commit 4.2.0** - Automated Git hooks
- **Black-compatible** - Consistent formatting

### Performance

- **CacheTools** - Advanced caching system
- **Memory-profiler** - Memory monitoring
- **DiskCache** - Persistent cache

---

## 📞 Contact and Support

For development questions:

- Check the optimization reports
- Review settings in `.toml` and `.yaml` files
- Run the quality check commands

---

## 🔄 Next Steps

### Planned

- [ ] Unit tests implementation
- [ ] Production deployment
- [ ] API documentation
- [ ] Performance benchmarks

### Under Evaluation

- [ ] Migration to FastAPI backend
- [ ] WebSockets implementation
- [ ] Advanced dashboard analytics

---

*Documentation maintained automatically - LANDAGRI-B Dashboard*
