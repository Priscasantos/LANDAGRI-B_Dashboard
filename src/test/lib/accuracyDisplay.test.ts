import { describe, it, expect } from 'vitest';
import {
  ACCURACY_UNAVAILABLE_LABEL,
  accuracyTooltipText,
  averageOverValid,
  countValid,
  formatAccuracyPct,
  formatAccuracyValue,
  hasAssessedAccuracy,
  sourceLinksFor,
} from '../../lib/accuracyDisplay';
import { parseInitiatives } from '../../lib/dataParser';
import type { InitiativeMetadata } from '../../types/initiative';

function row(
  name: string,
  acronym: string,
  accuracy?: InitiativeMetadata['overall_accuracy'],
): Record<string, InitiativeMetadata> {
  return {
    [name]: {
      acronym,
      provider: 'P',
      source: 'S',
      spatial_resolution: 30,
      available_years: [2020],
      temporal_frequency: '',
      update_frequency: '',
      reference_system: '',
      methodology: 'Machine Learning',
      classification_method: '',
      coverage: 'National',
      ...(accuracy !== undefined ? { overall_accuracy: accuracy } : {}),
      number_of_classes: 5,
      class_legend: '',
      number_of_agriculture_classes: 0,
      agricultural_capabilities: '',
      algorithm: '',
      sensors_referenced: [],
    },
  };
}

describe('council: display —/n.d. (nunca 0.0 cru)', () => {
  it('literal exato do council para ausente', () => {
    expect(ACCURACY_UNAVAILABLE_LABEL).toBe('—/n.d.');
  });

  it('formatadores exibem —/n.d. para 0 interno (IBGE/CONAB)', () => {
    expect(formatAccuracyPct(0)).toBe('—/n.d.');
    expect(formatAccuracyValue(0)).toBe('—/n.d.');
    expect(formatAccuracyPct(0, '—/n.d.')).toBe('—/n.d.');
  });

  it('formatadores preservam avaliados e nunca emitem 0.0', () => {
    expect(formatAccuracyPct(92.5)).toBe('92.5%');
    expect(formatAccuracyValue(92.5)).toBe('92.5');
    for (const v of [0, -1, Number.NaN]) {
      const n = Number.isNaN(v) ? 0 : v;
      expect(formatAccuracyPct(n)).not.toMatch(/0\.0/);
      expect(formatAccuracyValue(n)).not.toMatch(/0\.0/);
    }
  });

  it('hasAssessedAccuracy: 0 interno = ausente', () => {
    expect(hasAssessedAccuracy(0)).toBe(false);
    expect(hasAssessedAccuracy(90)).toBe(true);
  });

  it('parser: IBGE-MLCU e CONAB-AM com OA null viram —/n.d. + nota', () => {
    const rows = parseInitiatives({
      ...row('IBGE Monitoring Land Cover and Land Use', 'IBGE-MLCU', {
        status: 'not_available',
        overall: null as unknown as number,
        reason: 'No accuracy assessment conducted or reported',
      } as never),
      ...row('National Supply Company Agricultural Mapping', 'CONAB-AM', {
        status: 'incomplete',
        overall: null as unknown as number,
        reason: 'Accuracy assessment reported as incomplete',
      } as never),
      ...row('Avaliada', 'AVA', 91.04),
    });
    const byAcronym = Object.fromEntries(rows.map((r) => [r.Acronym, r]));
    for (const ac of ['IBGE-MLCU', 'CONAB-AM']) {
      expect(byAcronym[ac].Accuracy).toBe(0);
      expect(byAcronym[ac].Accuracy_Label).toBe('—/n.d.');
      expect(byAcronym[ac].Accuracy_Note).toBeTruthy();
    }
    expect(byAcronym['AVA'].Accuracy_Label).toBe('91.0');
    expect(byAcronym['AVA'].Accuracy_Note).toBe('');
  });
});

describe('council: tooltip cita fontes com links (PT/EN via phrase)', () => {
  it('IBGE-MLCU cita ibge.gov.br', () => {
    const tip = accuracyTooltipText('Fonte não publica overall_accuracy', 'IBGE-MLCU', 'motivo');
    expect(tip).toContain('Fonte não publica overall_accuracy');
    expect(tip).toContain('ibge.gov.br');
    expect(tip).toContain('motivo');
  });

  it('CONAB-AM cita gov.br/conab e csr.ufmg.br', () => {
    const tip = accuracyTooltipText('Source does not publish overall_accuracy', 'CONAB-AM');
    expect(tip).toContain('Source does not publish overall_accuracy');
    expect(tip).toContain('gov.br/conab');
    expect(tip).toContain('csr.ufmg.br');
  });

  it('sourceLinksFor resolve por sigla com fallback', () => {
    expect(sourceLinksFor('IBGE-MLCU').map((l) => l.url).join(' ')).toContain('ibge.gov.br');
    expect(sourceLinksFor('DESCONHECIDA').length).toBeGreaterThan(0);
  });
});

describe('council: Overall_Score exclui sem OA (N válido)', () => {
  it('média ignora zeros internos', () => {
    expect(averageOverValid([90, 0, 0])).toBe(90);
    expect(averageOverValid([80, 90, 0])).toBe(85);
    expect(countValid([80, 90, 0])).toBe(2);
  });

  it('sem N válido retorna 0 (chamador exibe —/n.d.)', () => {
    expect(averageOverValid([])).toBe(0);
    expect(averageOverValid([0, 0])).toBe(0);
    expect(countValid([0, 0])).toBe(0);
    expect(formatAccuracyPct(averageOverValid([0, 0]))).toBe('—/n.d.');
  });

  it('dicionários PT/EN trazem nota metodológica e literal', () => {
    // Import dinâmico evita custo no ciclo RED; chaves tipadas garantem paridade.
    return Promise.all([import('../../i18n/dictionaries/pt'), import('../../i18n/dictionaries/en')]).then(
      ([modPt, modEn]) => {
        const { pt } = modPt;
        const { en } = modEn;
        expect(pt.initiative.accuracyUnavailable).toBe('—/n.d.');
        expect(en.initiative.accuracyUnavailable).toBe('—/n.d.');
        expect(pt.initiative.accuracyNoOverall).toContain('overall_accuracy');
        expect(en.initiative.accuracyNoOverall).toContain('overall_accuracy');
        expect(pt.initiative.overallScoreNote).toContain('IBGE-MLCU');
        expect(en.initiative.overallScoreNote).toContain('CONAB-AM');
      },
    );
  });
});
