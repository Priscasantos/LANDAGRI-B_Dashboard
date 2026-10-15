import { useState, useMemo } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import {
  Settings2,
  RefreshCw,
  Zap,
  Info,
} from 'lucide-react';
import AnimatedPage from '../components/AnimatedPage';
import PlotlyLazyChart from '../components/charts/PlotlyLazyChart';
import { themeDataColor } from '../lib/theme-data';
import type { Data } from 'plotly.js';
import { simulateProjections, getDefaultParams, BASELINE_2025 } from '../lib/landCoverSimulation';

export default function PredictivePage() {
  const [reforestationRate, setReforestationRate] = useState(getDefaultParams().reforestationRate);
  const [agriExpansion, setAgriExpansion] = useState(getDefaultParams().agriExpansion);
  const [sustainableAdoption, setSustainableAdoption] = useState(getDefaultParams().sustainableAdoption);

  const simulatedData = useMemo(
    () => simulateProjections({ reforestationRate, agriExpansion, sustainableAdoption }),
    [reforestationRate, agriExpansion, sustainableAdoption]
  );

  const result2035 = simulatedData[simulatedData.length - 1];
  const forestDelta = Math.round((result2035.forestryArea - BASELINE_2025.forestryArea) * 10) / 10;
  const agriDelta = Math.round((result2035.agricultureArea - BASELINE_2025.agricultureArea) * 10) / 10;
  const carbonDelta = Math.round(result2035.carbonEmissionIndex - 100);

  const plotlyYears = simulatedData.map((d) => d.year);
  const plotlyTraces: Data[] = [
    {
      type: 'scatter',
      mode: 'lines',
      name: 'Floresta (Mha)',
      x: plotlyYears,
      y: simulatedData.map((d) => d.forestryArea),
    },
    {
      type: 'scatter',
      mode: 'lines',
      name: 'Agricultura (Mha)',
      x: plotlyYears,
      y: simulatedData.map((d) => d.agricultureArea),
    },
    {
      type: 'scatter',
      mode: 'lines',
      name: 'Índice de Emissão',
      x: plotlyYears,
      y: simulatedData.map((d) => d.carbonEmissionIndex),
    },
  ];

  const handleReset = () => {
    const def = getDefaultParams();
    setReforestationRate(def.reforestationRate);
    setAgriExpansion(def.agriExpansion);
    setSustainableAdoption(def.sustainableAdoption);
  };

  return (
    <AnimatedPage>
      <div className="space-y-6">
        <div
          className="rounded-2xl p-6 border relative overflow-hidden bg-surface border-border"
        >
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div
                className="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold font-mono w-fit border mb-2"
                style={{
                  backgroundColor: 'var(--color-primary-light)',
                  borderColor: 'var(--color-primary)',
                  color: 'var(--color-primary)',
                }}
              >
                <Zap size={11} />
                <span>Simulador de Cenários</span>
              </div>
              <h2
                className="text-xl font-bold tracking-tight text-fg"
              >
                Simulador de Políticas de Uso do Solo
              </h2>
              <p className="text-sm mt-1 text-fg-secondary">
                Ajuste os parâmetros abaixo e veja as projeções até <strong>2035</strong>
              </p>
            </div>

            <button
              onClick={handleReset}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold cursor-pointer transition-all border w-fit"
              style={{
                backgroundColor: 'var(--color-canvas)',
                borderColor: 'var(--color-border)',
                color: 'var(--color-fg-secondary)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--color-primary)';
                e.currentTarget.style.color = 'var(--color-primary)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--color-border)';
                e.currentTarget.style.color = 'var(--color-fg-secondary)';
              }}
            >
              <RefreshCw size={14} />
              Resetar Padrão
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-w-0">
          <div className="lg:col-span-4 space-y-6 min-w-0">
            <div
              className="rounded-2xl p-6 border space-y-6 bg-surface border-border"
            >
              <h4
                className="text-xs font-bold uppercase tracking-wider flex items-center gap-2 text-fg-muted"
              >
                <Settings2 size={14} />
                Parâmetros de Política
              </h4>

              <div className="space-y-2">
                <div className="flex justify-between text-sm text-fg">
                  <label htmlFor="reforestation-rate" className="font-semibold">
                    Reflorestamento
                  </label>
                  <span className="font-bold" style={{ color: 'var(--color-primary)' }}>
                    +{reforestationRate}% / ano
                  </span>
                </div>
                <input
                  id="reforestation-rate"
                  type="range"
                  min="0"
                  max="4"
                  step="0.1"
                  value={reforestationRate}
                  aria-valuetext={`+${reforestationRate}% por ano`}
                  onChange={(e) => setReforestationRate(parseFloat(e.target.value))}
                  className="w-full h-1.5 rounded-lg appearance-none cursor-pointer accent-blue-500 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                  style={{ backgroundColor: 'var(--color-border)' }}
                />
                <p className="text-xs text-fg-muted">
                  Taxa de recuperação de áreas degradadas e reflorestamento de reservas legais.
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm text-fg">
                  <label htmlFor="agri-expansion" className="font-semibold">
                    Expansão Agrícola
                  </label>
                  <span className="font-bold text-amber-500">+{agriExpansion}% / ano</span>
                </div>
                <input
                  id="agri-expansion"
                  type="range"
                  min="0"
                  max="3"
                  step="0.1"
                  value={agriExpansion}
                  aria-valuetext={`+${agriExpansion}% por ano`}
                  onChange={(e) => setAgriExpansion(parseFloat(e.target.value))}
                  className="w-full h-1.5 rounded-lg appearance-none cursor-pointer accent-amber-500 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none"
                  style={{ backgroundColor: 'var(--color-border)' }}
                />
                <p className="text-xs text-fg-muted">
                  Conversão de pastagens degradadas para agricultura intensiva.
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm text-fg">
                  <label htmlFor="sustainable-adoption" className="font-semibold">
                    Adoção Sustentável
                  </label>
                  <span className="font-bold text-emerald-500">{sustainableAdoption}%</span>
                </div>
                <input
                  id="sustainable-adoption"
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={sustainableAdoption}
                  aria-valuetext={`${sustainableAdoption}%`}
                  onChange={(e) => setSustainableAdoption(parseInt(e.target.value))}
                  className="w-full h-1.5 rounded-lg appearance-none cursor-pointer accent-emerald-500 focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:outline-none"
                  style={{ backgroundColor: 'var(--color-border)' }}
                />
                <p className="text-xs text-fg-muted">
                  Integração lavoura-pecuária-floresta (ILPF), plantio direto e bioinsumos.
                </p>
              </div>
            </div>

            <div
              className="rounded-2xl p-5 border space-y-3"
              style={{
                backgroundColor: 'var(--color-primary-light)',
                borderColor: 'var(--color-primary)',
                opacity: 0.9,
              }}
            >
              <h5
                className="text-xs font-bold flex items-center gap-1"
                style={{ color: 'var(--color-primary)' }}
              >
                <Info size={14} />
                Sobre o Modelo
              </h5>
              <p className="text-xs leading-relaxed text-fg-secondary">
                O simulador projeta cenários baseados em parâmetros do <strong>Plano ABC+</strong> e dados do
                MapBiomas. Pastagens atuam como amortecedor: recuperando pastagens degradadas,
                o Brasil pode expandir agricultura e floresta simultaneamente.
              </p>
            </div>
          </div>

          <div className="lg:col-span-8 space-y-6 min-w-0">
            <div
              className="rounded-2xl p-6 border bg-surface border-border min-w-0"
            >
              <h3
                className="text-xs font-bold uppercase tracking-wider mb-1 text-fg-muted"
              >
                Projeção Anual (2025 - 2035)
              </h3>
              <p className="text-sm mb-4 text-fg-secondary">
                Interação entre reflorestamento, expansão agrícola e emissões
              </p>

              <div
                className="h-80 min-w-0 w-full rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                role="img"
                tabIndex={0}
                aria-label={`Projeção anual 2025–2035. Floresta ${result2035.forestryArea} Mha, agricultura ${result2035.agricultureArea} Mha, índice de emissão ${result2035.carbonEmissionIndex}.`}
                style={{ minWidth: 0 }}
              >
                <ResponsiveContainer width="100%" height="100%" minWidth={0}>
                  <LineChart data={simulatedData} margin={{ top: 10, right: 24, left: 8, bottom: 8 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                    <XAxis
                      dataKey="year"
                      tick={{ fontSize: 11, fill: 'var(--color-fg-muted)' }}
                      tickLine={false}
                      tickMargin={4}
                    />
                    <YAxis
                      tick={{ fontSize: 11, fill: 'var(--color-fg-muted)' }}
                      tickLine={false}
                      axisLine={false}
                      width={52}
                      tickMargin={4}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--color-canvas)',
                        border: '1px solid var(--color-border)',
                        borderRadius: '12px',
                        fontSize: '12px',
                      }}
                      labelStyle={{ color: 'var(--color-fg)', fontWeight: 'bold' }}
                    />
                    <Legend
                      iconType="circle"
                      align="center"
                      verticalAlign="bottom"
                      wrapperStyle={{ fontSize: '11px', paddingTop: '10px', maxWidth: '100%', lineHeight: '16px' }}
                    />
                    <Line
                      type="monotone"
                      name="Floresta (Mha)"
                      dataKey="forestryArea"
                      stroke={themeDataColor(0)}
                      strokeWidth={3}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      name="Pastagem (Mha)"
                      dataKey="pastureArea"
                      stroke={themeDataColor(1)}
                      strokeWidth={2}
                      dot={false}
                      strokeDasharray="4 4"
                    />
                    <Line
                      type="monotone"
                      name="Agricultura (Mha)"
                      dataKey="agricultureArea"
                      stroke={themeDataColor(2)}
                      strokeWidth={3}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      name="Índice de Emissão"
                      dataKey="carbonEmissionIndex"
                      stroke={themeDataColor(3)}
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div
              className="grid grid-cols-1 sm:grid-cols-3 gap-4 min-w-0"
            >
              <div
                className="rounded-2xl p-5 border text-center bg-surface border-border"
              >
                <p className="text-[10px] font-bold uppercase tracking-wider mb-1 text-fg-muted">
                  Variação Florestal
                </p>
                <h3
                  className="text-2xl font-black"
                  style={{ color: forestDelta >= 0 ? '#10b981' : '#ef4444' }}
                >
                  {forestDelta >= 0 ? '+' : ''}{forestDelta} Mha
                </h3>
                <p className="text-xs mt-1 text-fg-muted">
                  {forestDelta >= 0 ? 'Ganho de cobertura' : 'Perda florestal'}
                </p>
              </div>

              <div
                className="rounded-2xl p-5 border text-center bg-surface border-border"
              >
                <p className="text-[10px] font-bold uppercase tracking-wider mb-1 text-fg-muted">
                  Expansão Agrícola
                </p>
                <h3 className="text-2xl font-black text-amber-500">
                  +{agriDelta} Mha
                </h3>
                <p className="text-xs mt-1 text-fg-muted">
                  Nova área cultivada
                </p>
              </div>

              <div
                className="rounded-2xl p-5 border text-center bg-surface border-border"
              >
                <p className="text-[10px] font-bold uppercase tracking-wider mb-1 text-fg-muted">
                  Status de Emissão
                </p>
                <h3
                  className="text-2xl font-black"
                  style={{ color: carbonDelta <= 0 ? '#10b981' : '#ef4444' }}
                >
                  {carbonDelta <= 0 ? '' : '+'}{carbonDelta}%
                </h3>
                <p className="text-xs mt-1 text-fg-muted">
                  {carbonDelta <= 0 ? 'Redução de emissões' : 'Aumento de emissões'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Plotly island (lazy, chunk separado) — projeção detalhada */}
        <div className="rounded-2xl p-6 border bg-surface border-border">
          <h3 className="text-xs font-bold uppercase tracking-wider mb-1 text-fg-muted">
            Projeção Detalhada (2025 - 2035)
          </h3>
          <p className="text-sm mb-4 text-fg-secondary">
            Mesma simulação em gráfico interativo (zoom, exportação PNG)
          </p>
          <PlotlyLazyChart
            data={plotlyTraces}
            layout={{
              title: { text: 'Projeção detalhada 2025–2035' },
              xaxis: { title: { text: 'Ano' } },
              yaxis: { title: { text: 'Mha / Índice' } },
            }}
          />
        </div>
      </div>
    </AnimatedPage>
  );
}
