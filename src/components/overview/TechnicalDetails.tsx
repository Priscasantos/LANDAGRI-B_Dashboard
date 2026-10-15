import type { InitiativeRow } from '../../types/initiative';
import Expandable from '../ui/Expandable';
import { Building2, Microscope, History } from 'lucide-react';
import { parseAvailableYears } from '../../lib/dataParser';

interface TechnicalDetailsProps {
  data: InitiativeRow;
}

export default function TechnicalDetails({ data }: TechnicalDetailsProps) {
  const years = parseAvailableYears(data.Available_Years);

  return (
    <div className="space-y-3">
      <Expandable title="Basic Information" icon={<Building2 size={16} aria-hidden="true" />} defaultExpanded={true}>
        <div className="space-y-2">
          <div><span className="font-medium text-fg">Provider:</span> {data.Provider || '-'}</div>
          <div><span className="font-medium text-fg">Source:</span> {data.Source || '-'}</div>
          <div><span className="font-medium text-fg">Coverage:</span> {data.Coverage || '-'}</div>
        </div>
      </Expandable>

      <Expandable title="Technical Specifications" icon={<Microscope size={16} aria-hidden="true" />}>
        <div className="space-y-2">
          <div><span className="font-medium text-fg">Methodology:</span> {data.Methodology || '-'}</div>
          <div><span className="font-medium text-fg">Algorithm:</span> {data.Algorithm || '-'}</div>
          <div><span className="font-medium text-fg">Spatial Resolution:</span> {data.Resolution > 0 ? `${data.Resolution}m` : '-'}</div>
          <div><span className="font-medium text-fg">Reference System:</span> {data.Reference_System || '-'}</div>
        </div>
      </Expandable>

      <Expandable title="Temporal Information" icon={<History size={16} aria-hidden="true" />}>
        <div className="space-y-2">
          {years.length > 0 ? (
            <>
              <div><span className="font-medium text-fg">First Year:</span> {Math.min(...years)}</div>
              <div><span className="font-medium text-fg">Last Year:</span> {Math.max(...years)}</div>
              <div><span className="font-medium text-fg">Total Years:</span> {years.length}</div>
            </>
          ) : (
            <div className="text-fg-muted italic">Temporal coverage not available</div>
          )}
        </div>
      </Expandable>
    </div>
  );
}
