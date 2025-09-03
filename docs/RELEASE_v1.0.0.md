# LANDAGRI-B Dashboard v1.0.0: Interactive Dashboard for Land Use and Land Cover Monitoring in Brazil

This stable release marks the production-ready version of the LANDAGRI-B Dashboard, an open-source tool designed for analyzing land use and land cover (LULC) monitoring initiatives in Brazil. Developed as part of doctoral research at INPE (National Institute for Space Research), this dashboard facilitates data-driven insights into agricultural and environmental monitoring using Brazilian datasets.

## Key Features

- **Comprehensive Analyses**: Includes overview metrics, temporal evolution tracking, detailed initiative comparisons, CONAB-specific data analysis, and advanced multi-dimensional comparisons.
- **Interactive Visualizations**: Built with Plotly for responsive charts, geospatial maps, and real-time metrics, supporting both desktop and mobile interfaces.
- **Modular Architecture**: Organized into components for agricultural analysis, IBGE data integration, CONAB data processing, and initiative evaluations.
- **Performance Optimizations**: Features caching, memory profiling, and quality assurance tools for efficient data handling.

## Technologies and Dependencies

- **Core**: Python 3.12, Streamlit 1.47.0
- **Data Processing**: Pandas, GeoPandas
- **Visualization**: Plotly
- **Quality Tools**: Ruff 0.12.4 (linting), Pre-commit hooks
- **Data Sources**: Integrates Brazilian IBGE agricultural data, CONAB datasets (including Excel files for safra 2023-24 and 2024-25), and JSON mappings for comprehensive analysis.

## Usage

Run the dashboard locally with:

```bash
python -m streamlit run app.py
```

Or use the custom script:

```bash
python run_app.py --port 8501
```

Access at <http://localhost:8501> for tabbed navigation and responsive design.

## Data and Documentation

- Includes processed datasets in `data/` (e.g., Brazilian agricultural JSON files, CONAB Excel files, vector data).
- Full documentation available in `docs/` folder, including optimization reports and technical details.
- Licensed under MIT for open access and reuse.

## Citation and DOI

This release is archived on Zenodo for long-term preservation and citation. DOI: <https://doi.org/10.5281/zenodo.17042299>

For citation formats, see the main README.md.

## Changelog

- Initial stable release with all core features implemented.
- Resolved issues from previous versions (see `docs/` for detailed reports).
- Optimized for performance and user experience.

This release contributes to open science by providing accessible tools for LULC monitoring, supporting research in environmental science and agriculture. Feedback and contributions are welcome via GitHub issues.
