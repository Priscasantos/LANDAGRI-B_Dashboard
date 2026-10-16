# 🌍 LANDAGRI-B Dashboard

**Interactive Dashboard for Analyzing Land Use and Land Cover (LULC) Monitoring Initiatives in Brazil**

[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6-646CFF.svg)](https://vitejs.dev/)
[![Status](https://img.shields.io/badge/status-production--ready-green.svg)](https://github.com/Priscasantos/LANDAGRI-B_Dashboard)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.17042299-blue.svg)](https://doi.org/10.5281/zenodo.17042299)

> **Repository**: [https://github.com/Priscasantos/LANDAGRI-B_Dashboard](https://github.com/Priscasantos/LANDAGRI-B_Dashboard)  
> **Version**: 2.0.0 (React/TypeScript SPA)  
> **Last Updated**: May 2026

---

## Abstract

The LANDAGRI-B Dashboard is an open-source, interactive web application developed to facilitate the analysis of land use and land cover (LULC) monitoring initiatives in Brazil. This tool integrates geospatial data from Brazilian sources, including the Instituto Brasileiro de Geografia e Estatística (IBGE) and the Companhia Nacional de Abastecimento (CONAB), to provide researchers, policymakers, and stakeholders with comprehensive insights into agricultural and environmental dynamics. Built as a static single-page application using React and TypeScript, the dashboard employs advanced visualization techniques with Plotly to enable temporal, spatial, and comparative analyses of LULC data.

This software contributes to the field of remote sensing and geospatial analysis by offering an accessible platform for data exploration, supporting evidence-based decision-making in sustainable agriculture and environmental monitoring.

---

## Quick Start

### Prerequisites

- Node.js 18+
- npm 9+

### Installation and Execution

```bash
# Clone the repository
git clone https://github.com/Priscasantos/LANDAGRI-B_Dashboard.git
cd LANDAGRI-B_Dashboard

# Install dependencies
npm install

# Start development server
npm run dev
```

Access the application at <http://localhost:5173>.

---

## Features

### Analytical Modules

- **Overview**: Aggregated metrics and key performance indicators for LULC initiatives.
- **Initiative Analysis**: Temporal, detailed, and comparative analysis of monitoring initiatives.
- **Agricultural Analysis**: CONAB/IBGE integration, crop calendar, and availability data.
- **About**: Project documentation, methodology, and citation information.

### Visualization Capabilities

- 14 interactive Plotly chart types for dynamic data exploration.
- Responsive design optimized for desktop and mobile devices.
- Client-side data processing with preprocessed static JSON datasets.

### Architecture

- Modular React/TypeScript component architecture.
- Zustand state management for predictable data flow.
- Zero backend dependency — fully static SPA deployable to GitHub Pages.
- 24 unit tests using Vitest + Testing Library.

---

## Technical Specifications

### Core Technologies

- **Framework**: React 19 with TypeScript 5.7
- **Build Tool**: Vite 6
- **Charts**: Plotly.js (react-plotly.js)
- **State Management**: Zustand
- **Styling**: Tailwind CSS v4
- **Testing**: Vitest + @testing-library/react
- **Linting**: ESLint with typescript-eslint

### Data Sources

- Brazilian Institute of Geography and Statistics (IBGE) agricultural datasets.
- National Supply Company (CONAB) crop monitoring data (safra 2023-24).
- Preprocessed static JSON datasets bundled with the SPA.

---

## Available Scripts

| Script            | Description                         |
| ----------------- | ----------------------------------- |
| `npm run dev`     | Start development server with HMR   |
| `npm run build`   | Type-check and build for production |
| `npm run preview` | Preview production build locally    |
| `npm test`        | Run test suite                      |
| `npm run lint`    | Lint all source files               |
| `npm run deploy`  | Deploy to GitHub Pages              |

---

## Documentation

Comprehensive documentation is available in the [`docs/`](./docs/) folder:

- [`docs/README.md`](./docs/README.md): Documentation overview
- [`docs/RELEASE_v1.0.0.md`](./docs/RELEASE_v1.0.0.md): Release notes
- [`docs/methodology_taxonomy.md`](./docs/methodology_taxonomy.md): Methodology taxonomy (upstream)

> **Note (dependency pins)**: frontend pins live in `package.json` / `package-lock.json`;
> legacy Python pins (e.g. Streamlit 1.47.0, Ruff 0.12.4) remain in `requirements.txt`
> for reference. The SPA is the current application; the Streamlit app is legacy.

---

## Version History

### v2.0.0 (May 2026)

- Complete rewrite from Python/Streamlit to React/TypeScript SPA
- 60+ React components across 4 modules
- 14 interactive Plotly chart types
- Zero backend dependency — fully static deployment
- 24 passing tests with Vitest

### v1.0.0 (September 2, 2025)

- Original Python/Streamlit release
- Zenodo DOI assignment: <https://doi.org/10.5281/zenodo.17042299>

---

## Contributing

We welcome contributions from the academic and developer community. To contribute:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Implement changes with adherence to code standards.
4. Submit a pull request with detailed description.

### Development Guidelines

- **Code Quality**: ESLint with TypeScript strict rules.
- **Testing**: Write Vitest tests for new features.
- **Documentation**: Update relevant docs for changes.

---

## Citation

If you use this software in your research, please cite as follows:

### APA (7th Edition)

Santos, P. A. (2025). _LANDAGRI-B Dashboard: Interactive Dashboard for Land Use and Land Cover Monitoring in Brazil_ (Version 2.0.0) [Computer software]. Zenodo. <https://doi.org/10.5281/zenodo.17042299>

### BibTeX

```bibtex
@software{santos_landagri_b_2025,
  author = {Santos, Priscilla Azevedo dos},
  title = {LANDAGRI-B Dashboard: Interactive Dashboard for Land Use and Land Cover Monitoring in Brazil},
  year = {2026},
  version = {2.0.0},
  doi = {10.5281/zenodo.17042299},
  url = {https://github.com/Priscasantos/LANDAGRI-B_Dashboard}
}
```

**Author ORCID**: [0000-0001-5987-9222](https://orcid.org/0000-0001-5987-9222)

---

## Contact

- **Developer**: Priscilla Azevedo dos Santos
- **Affiliation**: Instituto Nacional de Pesquisas Espaciais (INPE), Brazil
- **Email**: [priscilla.santos@inpe.br](mailto:priscilla.santos@inpe.br)
- **Issues**: [GitHub Issues](https://github.com/Priscasantos/LANDAGRI-B_Dashboard/issues)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**LANDAGRI-B Dashboard** - Advancing geospatial analysis for sustainable land management in Brazil 🇧🇷

_Developed as part of doctoral research at INPE_
