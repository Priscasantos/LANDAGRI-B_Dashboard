# 🌍 LANDAGRI-B Dashboard

**Interactive Dashboard for Analyzing Land Use and Land Cover (LULC) Monitoring Initiatives in Brazil**

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.47.0-red.svg)](https://streamlit.io/)
[![Status](https://img.shields.io/badge/status-production--ready-green.svg)](https://github.com/Priscasantos/LANDAGRI-B_Dashboard)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.17042299-blue.svg)](https://doi.org/10.5281/zenodo.17042299)

> **Repository**: [https://github.com/Priscasantos/LANDAGRI-B_Dashboard](https://github.com/Priscasantos/LANDAGRI-B_Dashboard)  
> **Version**: 1.0.0 (Stable Release)  
> **Last Updated**: September 2, 2025

---

## Abstract

The LANDAGRI-B Dashboard is an open-source, interactive web application developed to facilitate the analysis of land use and land cover (LULC) monitoring initiatives in Brazil. This tool integrates geospatial data from Brazilian sources, including the Instituto Brasileiro de Geografia e Estatística (IBGE) and the Companhia Nacional de Abastecimento (CONAB), to provide researchers, policymakers, and stakeholders with comprehensive insights into agricultural and environmental dynamics. Built using Python and Streamlit, the dashboard employs advanced visualization techniques with Plotly to enable temporal, spatial, and comparative analyses of LULC data.

This software contributes to the field of remote sensing and geospatial analysis by offering an accessible platform for data exploration, supporting evidence-based decision-making in sustainable agriculture and environmental monitoring.

---

## � Quick Start

### Prerequisites
- Python 3.12 or higher
- Internet connection for data fetching

### Installation and Execution
```bash
# Clone the repository
git clone https://github.com/Priscasantos/LANDAGRI-B_Dashboard.git
cd LANDAGRI-B_Dashboard

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
python -m streamlit run app.py --server.port 8501
```

### Alternative Methods
- **Custom Script**: `python run_app.py --port 8501`
- **Debug Mode**: `python run_app.py --no-cache`

Access the application at <http://localhost:8501>.

---

## 📊 Features

### � Analytical Modules
- **Overview**: Aggregated metrics and key performance indicators for LULC initiatives.
- **Temporal Analysis**: Time-series visualization of land cover changes.
- **Detailed Comparisons**: Initiative-specific evaluations and benchmarking.
- **CONAB Integration**: Specialized analysis of agricultural supply data.
- **Multi-dimensional Comparisons**: Advanced cross-sectional analyses.

### � Visualization Capabilities
- Interactive Plotly charts for dynamic data exploration.
- Geospatial mapping with GeoPandas integration.
- Responsive design optimized for desktop and mobile devices.
- Real-time data processing and caching for performance.

### �️ Architecture
- Modular design for extensibility and maintainability.
- Integration with Brazilian geospatial datasets (IBGE, CONAB).
- Quality assurance with automated linting and testing frameworks.

---

## 🛠️ Technical Specifications

### Core Technologies
- **Programming Language**: Python 3.12
- **Web Framework**: Streamlit 1.47.0
- **Data Processing**: Pandas, GeoPandas
- **Visualization**: Plotly
- **Quality Assurance**: Ruff 0.12.4, Pre-commit hooks
- **Caching**: CacheTools, Memory-profiler

### Data Sources
- Brazilian Institute of Geography and Statistics (IBGE) agricultural datasets.
- National Supply Company (CONAB) crop monitoring data (e.g., safra 2023-24, 2024-25).
- Vector and raster geospatial data for mapping applications.

---

## � Documentation

Comprehensive documentation is available in the [`docs/`](./docs/) folder:
- [`docs/README.md`](./docs/README.md): Documentation overview
- [`docs/RELEASE_v1.0.0.md`](./docs/RELEASE_v1.0.0.md): Release notes

For technical details, refer to configuration files: `pyproject.toml`, `.pre-commit-config.yaml`.

---

## � Version History

### v1.0.0 (September 2, 2025)
- ✅ Production-ready stable release
- ✅ Complete feature implementation
- ✅ Zenodo DOI assignment: <https://doi.org/10.5281/zenodo.17042299>
- ✅ Documentation reorganization and cleanup
- ✅ Performance optimizations with caching and profiling

---

## 🤝 Contributing

We welcome contributions from the academic and developer community. To contribute:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Implement changes with adherence to code standards.
4. Submit a pull request with detailed description.

### Development Guidelines
- **Code Quality**: Use Ruff for linting; maintain type hints and docstrings.
- **Testing**: Implement unit tests for new features.
- **Documentation**: Update relevant docs for changes.

---

## 📖 Citation

If you use this software in your research, please cite as follows:

### APA (7th Edition)
Santos, P. A. (2025). *LANDAGRI-B Dashboard: Interactive Dashboard for Land Use and Land Cover Monitoring in Brazil* (Version 1.0.0) [Computer software]. Zenodo. <https://doi.org/10.5281/zenodo.17042299>

### BibTeX
```bibtex
@software{santos_landagri_b_2025,
  author = {Santos, Priscilla Azevedo dos},
  title = {LANDAGRI-B Dashboard: Interactive Dashboard for Land Use and Land Cover Monitoring in Brazil},
  year = {2025},
  version = {1.0.0},
  doi = {10.5281/zenodo.17042299},
  url = {https://github.com/Priscasantos/LANDAGRI-B_Dashboard}
}
```

**Author ORCID**: [0000-0001-5987-9222](https://orcid.org/0000-0001-5987-9222)

---

## 📞 Contact

- **Developer**: Priscilla Azevedo dos Santos
- **Affiliation**: Instituto Nacional de Pesquisas Espaciais (INPE), Brazil
- **Email**: [priscilla.santos@inpe.br](mailto:priscilla.santos@inpe.br) (placeholder)
- **Issues**: [GitHub Issues](https://github.com/Priscasantos/LANDAGRI-B_Dashboard/issues)

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**LANDAGRI-B Dashboard** - Advancing geospatial analysis for sustainable land management in Brazil 🇧🇷

*Developed as part of doctoral research at INPE*
