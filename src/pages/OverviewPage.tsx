import { useEffect } from 'react';
import { useDashboardStore } from '../stores/dashboardStore';
import SummaryCards from '../components/overview/SummaryCards';
import OverviewMap from '../components/overview/OverviewMap';
import InitiativesTable from '../components/initiatives/InitiativesTable';
import InitiativeSelector from '../components/overview/InitiativeSelector';
import KeyMetricsCards from '../components/overview/KeyMetricsCards';
import LulcClasses from '../components/overview/LulcClasses';
import TechnicalDetails from '../components/overview/TechnicalDetails';
import SensorInfo from '../components/overview/SensorInfo';
import AgriculturalCharts from '../components/overview/AgriculturalCharts';
import type { SensorMap } from '../types/sensor';

export default function OverviewPage() {
  const { initiatives, selection, sensors, setSelectedInitiative } = useDashboardStore();

  // Auto-select first initiative if none selected
  useEffect(() => {
    if (!selection.selectedInitiative && initiatives.length > 0) {
      setSelectedInitiative(initiatives[0].Name);
    }
  }, [initiatives, selection.selectedInitiative, setSelectedInitiative]);

  const selectedData = selection.selectedInitiative
    ? initiatives.find((i) => i.Name === selection.selectedInitiative)
    : null;

  // Extract classification data
  const classificationJson = selectedData
    ? (selectedData.Detailed_Products && selectedData.Detailed_Products.length > 0
        ? selectedData.Detailed_Products
        : selectedData.Class_Legend || '[]')
    : '[]';

  return (
    <div>
      {/* Summary metrics */}
      <SummaryCards />

      {/* Leaflet island (lazy, chunk separado) */}
      <OverviewMap />

      <hr className="my-6 border-border" />

      {/* Initiative Details */}
      <h2 className="text-xl font-bold text-fg mb-4">Initiative Details</h2>
      <InitiativeSelector />

      {selectedData && (
        <>
          {/* Initiative header — superfície canônica, sem faixa chapada */}
          <div className="rounded-xl border border-border bg-card px-5 py-4 mb-5 text-center text-card-foreground font-bold text-xl shadow-sm">
            {selectedData.Name} ({selectedData.Acronym})
          </div>

          {/* Key Metrics */}
          <div className="flex justify-center mb-4">
            <h2 className="text-2xl font-bold text-fg">KEY METRICS</h2>
          </div>
          <KeyMetricsCards data={selectedData} />

          {/* Two-column layout */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-bold text-fg mb-3">🏷️ Classification</h3>
              <LulcClasses classification={classificationJson} />
            </div>
            <div>
              <h3 className="text-lg font-bold text-fg mb-3">🔧 Technical Details</h3>
              <TechnicalDetails data={selectedData} />

              <h3 className="text-lg font-bold text-fg mb-3 mt-6">🛰️ Sensor Information</h3>
              <SensorInfo sensorKeys={selectedData.Sensors} sensors={sensors as SensorMap} />
            </div>
          </div>
        </>
      )}

      <hr className="my-6 border-border" />

      {/* Agricultural Data Charts */}
      <AgriculturalCharts />

      <hr className="my-6 border-border" />

      {/* Initiatives table (iniciativa/área/ano) */}
      <section aria-labelledby="initiatives-table-heading">
        <h2 id="initiatives-table-heading" className="text-xl font-bold text-fg mb-4">
          Iniciativas
        </h2>
        <InitiativesTable />
      </section>
    </div>
  );
}
