import Expandable from '../ui/Expandable';
import { Satellite, Search, Rainbow } from 'lucide-react';
import type { SensorMap, SensorMetadata } from '../../types/sensor';
import { useT } from '../../i18n/LanguageContext';

interface SensorInfoProps {
  sensorKeys: string[];
  sensors: SensorMap;
}

function SensorCard({ sensorKey, sensor }: { sensorKey: string; sensor: SensorMetadata }) {
  const { t } = useT('overview');
  const resolutions = sensor.spatial_resolutions_m || [];
  const resStr = resolutions.length > 0
    ? `${Math.min(...resolutions.map(Number))} - ${Math.max(...resolutions.map(Number))}m`
    : '-';

  return (
    <div className="mb-4 p-3 bg-surface rounded-lg border border-border">
      <div className="font-semibold text-fg mb-2 flex items-center gap-1.5">
        <Satellite size={15} aria-hidden="true" className="shrink-0" />
        <span>{sensor.display_name || sensorKey}</span>
      </div>

      <Expandable title={t('expSpecs')} icon={<Search size={16} aria-hidden="true" />} defaultExpanded={true}>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <div><span className="font-medium">{t('fPlatform')}</span>{' '}
              <span
                className="inline-block max-w-64 truncate align-bottom"
                title={sensor.platform_name || undefined}
              >
                {sensor.platform_name || '-'}
              </span>
            </div>
            <div><span className="font-medium">{t('fFamily')}</span> {sensor.sensor_family || '-'}</div>
            <div><span className="font-medium">{t('fType')}</span> {sensor.sensor_type_description || '-'}</div>
          </div>
          <div>
            <div><span className="font-medium">{t('fSpatialRes')}</span> {resStr}</div>
            <div><span className="font-medium">{t('fRevisit')}</span> {sensor.revisit_time_days ? t('daysUnit', { days: sensor.revisit_time_days }) : '-'}</div>
            <div><span className="font-medium">{t('fStatus')}</span> {sensor.status || '-'}</div>
          </div>
        </div>
      </Expandable>

      {sensor.spectral_bands && Array.isArray(sensor.spectral_bands) && sensor.spectral_bands.length > 0 && (
        <Expandable title={t('expBands')} icon={<Rainbow size={16} aria-hidden="true" />}>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left px-2 py-1 text-fg-secondary">{t('thBand')}</th>
                  <th className="text-left px-2 py-1 text-fg-secondary">{t('thWavelength')}</th>
                  <th className="text-left px-2 py-1 text-fg-secondary">{t('thResolution')}</th>
                </tr>
              </thead>
              <tbody>
                {sensor.spectral_bands.map((band, idx) => (
                  <tr key={idx} className="border-b border-border">
                    <td className="px-2 py-1">{band.band_name || t('bandN', { n: idx + 1 })}</td>
                    <td className="px-2 py-1">{band.wavelength_nm || '-'}</td>
                    <td className="px-2 py-1">{band.resolution_m ?? '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Expandable>
      )}
    </div>
  );
}

export default function SensorInfo({ sensorKeys, sensors }: SensorInfoProps) {
  const { t } = useT('overview');
  if (sensorKeys.length === 0) {
    return (
      <p className="text-sm text-fg-muted italic">
        {t('noSensor')}
      </p>
    );
  }
  const matchedSensors = sensorKeys
    .map((key) => ({ key, sensor: sensors[key] }))
    .filter((s): s is { key: string; sensor: SensorMetadata } => s.sensor !== undefined);

  if (matchedSensors.length === 0) {
    return (
      <p className="text-sm text-fg-muted italic">
        {t('noMetadata')}
      </p>
    );
  }

  return (
    <div>
      {matchedSensors.map(({ key, sensor }) => (
        <SensorCard key={key} sensorKey={key} sensor={sensor} />
      ))}
    </div>
  );
}
