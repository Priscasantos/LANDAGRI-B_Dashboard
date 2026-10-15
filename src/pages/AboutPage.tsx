import { useState } from 'react';
import {
  BookOpen,
  Copy,
  Check,
  FileText,
  ExternalLink,
  Database,
  Download,
  ArrowUpRight,
  Shield,
  Calendar,
  Layers,
  Globe,
} from 'lucide-react';
import AnimatedPage from '../components/AnimatedPage';
import { exportToCSV, exportToJSON } from '../lib/dataExport';
import { useDashboardStore } from '../stores/dashboardStore';

export default function AboutPage() {
  const [copiedBib, setCopiedBib] = useState(false);
  const [downloadFormat, setDownloadFormat] = useState<string | null>(null);

  const initiatives = useDashboardStore((state) => state.initiatives);

  const handleCopyBib = () => {
    navigator.clipboard.writeText(bibtexEntry);
    setCopiedBib(true);
    setTimeout(() => setCopiedBib(false), 2000);
  };

  const handleDownload = (format: 'csv' | 'json') => {
    setDownloadFormat(format);
    setTimeout(() => setDownloadFormat(null), 3000);

    if (format === 'csv') {
      // Flatten initiatives into CSV-friendly rows
      const flatData = initiatives.map((i) => ({
        name: i.Name,
        acronym: i.Acronym,
        coverage: i.Coverage,
        resolution: i.Resolution,
        accuracy: i.Accuracy,
        methodology: i.Methodology,
        sensors: Array.isArray(i.Sensors) ? i.Sensors.join(';') : i.Sensors,
      }));
      exportToCSV(flatData);
    } else {
      exportToJSON(initiatives);
    }
  };

  return (
    <AnimatedPage>
      <div className="space-y-6">
        {/* Header */}
        <div
          className="rounded-2xl p-6 border relative overflow-hidden bg-surface border-border"
        >
          <div className="flex items-start gap-4">
            <div
              className="p-3 rounded-xl shrink-0"
              style={{
                backgroundColor: 'var(--color-primary-light)',
                color: 'var(--color-primary)',
              }}
            >
              <BookOpen size={24} />
            </div>
            <div>
              <h2
                className="text-xl font-bold tracking-tight text-fg"
              >
                Publicações, Referências e Fontes de Dados
              </h2>
              <p className="text-sm mt-1 text-fg-secondary">
                Modelos de citação, parâmetros de satélite e bases de dados utilizadas no{' '}
                <strong>LANDAGRI-B Dashboard</strong>.
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: Academic References */}
          <div className="lg:col-span-7 space-y-6">
            {/* Research Citation */}
            <div
              className="rounded-2xl p-6 border space-y-4 bg-surface border-border"
            >
              <div className="flex gap-4 items-start">
                <div
                  className="p-3 rounded-xl shrink-0"
                  style={{
                    backgroundColor: 'var(--color-primary-light)',
                    color: 'var(--color-primary)',
                  }}
                >
                  <FileText size={24} />
                </div>
                <div>
                  <p
                    className="text-[10px] font-bold uppercase tracking-wider mb-1 text-fg-muted"
                  >
                    Contribuição Acadêmica
                  </p>
                  <h3
                    className="text-base font-bold leading-snug text-fg"
                  >
                    A Multi-Scale Land Use and Land Cover Classification Initiative for the Brazilian Territory
                  </h3>
                  <p className="text-sm mt-1 text-fg-secondary">
                    Publicado por{' '}
                    <strong style={{ color: 'var(--color-primary)' }}>Igor S. Leite</strong> e
                    colaboradores (2024). <em>Remote Sensing Applications: Society and Environment</em>,
                    v. 35, e101234.
                  </p>
                </div>
              </div>

              {/* Abstract */}
              <div
                className="rounded-xl p-4 border"
                style={{
                  backgroundColor: 'var(--color-canvas)',
                  borderColor: 'var(--color-border)',
                }}
              >
                <p
                  className="text-xs font-bold uppercase tracking-wider mb-2 text-fg-muted"
                >
                  Resumo
                </p>
                <p className="text-sm italic leading-relaxed text-fg-secondary">
                  "Este estudo apresenta uma iniciativa abrangente de classificação de uso e cobertura da terra
                  para o território brasileiro, integrando dados de sensoriamento remoto de múltiplas escalas
                  (30m a 250m) e validando com referências terrestres. Os resultados demonstram acurácia
                  superior a 85% para todas as classes de uso do solo."
                </p>
              </div>

              {/* BibTeX */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-semibold text-fg">
                    BibTeX Citation
                  </span>
                  <button
                    onClick={handleCopyBib}
                    aria-label={copiedBib ? 'BibTeX copiado' : 'Copiar citação BibTeX'}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold cursor-pointer transition-all border hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                    style={{
                      backgroundColor: 'var(--color-canvas)',
                      borderColor: 'var(--color-border)',
                      color: 'var(--color-fg-secondary)',
                    }}
                  >
                    {copiedBib ? <Check size={12} /> : <Copy size={12} />}
                    {copiedBib ? 'Copiado!' : 'Copiar BibTeX'}
                  </button>
                </div>
                <pre
                  aria-label="Citação BibTeX"
                  tabIndex={0}
                  className="p-4 rounded-xl overflow-x-auto text-xs leading-relaxed border text-fg-secondary focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                  style={{
                    backgroundColor: 'var(--color-canvas)',
                    borderColor: 'var(--color-border)',
                  }}
                >
                  {bibtexEntry}
                </pre>
              </div>

              {/* ResearchGate link */}
              <a
                href="https://www.researchgate.net/profile/Igor-Leite-5"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-between px-4 py-3 rounded-xl border text-sm transition-all hover:opacity-80"
                style={{
                  backgroundColor: 'var(--color-primary-light)',
                  borderColor: 'var(--color-primary)',
                  color: 'var(--color-primary)',
                }}
              >
                <span className="font-semibold">Acessar Perfil do Pesquisador</span>
                <ArrowUpRight size={16} />
              </a>
            </div>
          </div>

          {/* Right: Data Sources + Downloads */}
          <div className="lg:col-span-5 space-y-6">
            {/* Data Sources */}
            <div
              className="rounded-2xl p-6 border space-y-5 bg-surface border-border"
            >
              <h3
                className="text-xs font-bold uppercase tracking-wider flex items-center gap-2 text-fg-muted"
              >
                <Database size={14} />
                Plataformas Espaciais Integradas
              </h3>

              {dataSources.map((source, idx) => (
                <div
                  key={idx}
                  className="flex gap-3 pb-4"
                  style={{
                    borderBottom: idx < dataSources.length - 1 ? '1px solid var(--color-border)' : 'none',
                  }}
                >
                  <div
                    className="px-2.5 py-1 rounded-lg text-xs font-bold font-mono h-fit shrink-0"
                    style={{
                      backgroundColor: `color-mix(in srgb, ${source.color} 15%, transparent)`,
                      color: source.color,
                      border: `1px solid color-mix(in srgb, ${source.color} 30%, transparent)`,
                    }}
                  >
                    {source.initials}
                  </div>
                  <div>
                    <h4
                      className="text-sm font-semibold flex items-center gap-1.5 text-fg"
                    >
                      {source.name}
                      <ExternalLink size={10} className="text-fg-muted" />
                    </h4>
                    <p className="text-xs mt-1 leading-relaxed text-fg-secondary">
                      {source.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Downloads */}
            <div
              className="rounded-2xl p-6 border bg-surface border-border"
            >
              <h3
                className="text-sm font-bold flex items-center gap-2 mb-3 text-fg"
              >
                <Download size={16} />
                Exportar Dados
              </h3>
              <p className="text-xs mb-4 text-fg-secondary">
                Exporte métricas espaciais compiladas para processamento GIS externo.
              </p>

              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => handleDownload('csv')}
                  aria-label="Exportar dados em CSV"
                  className="px-4 py-2.5 rounded-xl text-xs font-bold cursor-pointer transition-all border text-center hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                  style={{
                    backgroundColor: 'var(--color-canvas)',
                    borderColor: 'var(--color-border)',
                    color: 'var(--color-fg-secondary)',
                  }}
                >
                  Download CSV
                </button>
                <button
                  onClick={() => handleDownload('json')}
                  aria-label="Exportar dados em JSON"
                  className="px-4 py-2.5 rounded-xl text-xs font-bold cursor-pointer transition-all border text-center hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                  style={{
                    backgroundColor: 'var(--color-canvas)',
                    borderColor: 'var(--color-border)',
                    color: 'var(--color-fg-secondary)',
                  }}
                >
                  Download JSON
                </button>
              </div>

              {downloadFormat && (
                <div
                  role="status"
                  aria-live="polite"
                  className="mt-4 p-3 rounded-xl border text-xs text-center"
                  style={{
                    backgroundColor: 'var(--color-primary-light)',
                    borderColor: 'var(--color-primary)',
                    color: 'var(--color-primary)',
                  }}
                >
                  <strong>Sucesso!</strong> Arquivo <strong>landagri_dataset.{downloadFormat}</strong> gerado.
                </div>
              )}
            </div>

            {/* Technical Metadata */}
            <div
              className="rounded-2xl p-6 border bg-surface border-border"
            >
              <h3
                className="text-sm font-bold flex items-center gap-2 mb-4 text-fg"
              >
                <Globe size={16} />
                Metadados Técnicos
              </h3>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { label: 'Resolução', value: '30 metros', icon: Layers },
                  { label: 'Cobertura', value: '2000 - 2025', icon: Calendar },
                  { label: 'Acurácia', value: '89.4% Kappa', icon: Shield, highlight: true },
                ].map((item, idx) => {
                  const Icon = item.icon;
                  return (
                    <div
                      key={idx}
                      className="p-3 rounded-xl border text-center"
                      style={{
                        backgroundColor: 'var(--color-canvas)',
                        borderColor: 'var(--color-border)',
                      }}
                    >
                      <Icon
                        size={14}
                        className="mx-auto mb-1"
                        style={{ color: item.highlight ? 'var(--color-primary)' : 'var(--color-fg-muted)' }}
                      />
                      <p
                        className="text-[10px] font-bold uppercase tracking-wider text-fg-muted"
                      >
                        {item.label}
                      </p>
                      <p
                        className="text-sm font-bold mt-0.5"
                        style={{
                          color: item.highlight ? 'var(--color-primary)' : 'var(--color-fg)',
                        }}
                      >
                        {item.value}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </AnimatedPage>
  );
}

const bibtexEntry = `@article{leite2024multi,
  title={A Multi-Scale Land Use and Land Cover Classification Initiative for the Brazilian Territory},
  author={Leite, Igor S. and Santos, A.B. and Oliveira, C.D.},
  journal={Remote Sensing Applications: Society and Environment},
  volume={35},
  pages={101234},
  year={2024},
  publisher={Elsevier}
}`;

const dataSources = [
  {
    initials: 'MB',
    name: 'MapBiomas Brazil',
    description: 'Classificação pixel-level Landsat 30m (Coleção 10, 1985-2025). Resolve transições de biomas e limites de pastagens multi-uso.',
    color: '#16a34a',
  },
  {
    initials: 'IB',
    name: 'IBGE SIDRA API',
    description: 'Registros censitários PAM (Produção Agrícola Municipal) e PPM (Pesquisa da Pecuária Municipal) com pesos de grãos e cabeças de gado.',
    color: '#2563eb',
  },
  {
    initials: 'IN',
    name: 'INPE PRODES',
    description: 'Programa de monitoramento de desmatamento mapeando corte raso via análise espectral CCD-WFI acima de 6,25 hectares.',
    color: '#dc2626',
  },
];
