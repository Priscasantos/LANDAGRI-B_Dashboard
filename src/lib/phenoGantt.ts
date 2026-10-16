/**
 * Gantt fenológico real (Gaia — UI + agregação em código, reversível).
 *
 * Troca a barra única first→last por duas lanes (P/H) por cultura-região
 * com segmentos disjuntos: meses ativos contíguos viram um segmento; um
 * mês vazio (hiato) SEMPRE quebra o segmento — nunca colapsa o intervalo.
 *
 * `PH` (plantio e colheita simultâneos — possível 2º ciclo) vira faixa
 * própria (`ph: true`, hachura no render) dentro da lane do tipo.
 * Agrega por cultura×região (união de UFs; tooltip lista top UFs).
 * Não toca dados brutos: só lê `months[]` + mapa UF→região.
 */
import { activityFromCode } from '../types/calendar';
import { escapeHtml } from './escapeHtml';

export interface ConabPhenoRow {
  crop: string;
  uf: string;
  months: string[];
}

export type PhenoKind = 'P' | 'H';

export interface PhenoLane {
  /** `${crop}¦${region}¦${kind}` — estável para chaves React/ECharts. */
  id: string;
  crop: string;
  region: string;
  kind: PhenoKind;
}

export interface PhenoSegment {
  laneId: string;
  /** Slot do boletim (0 = Out … 11 = Set), início inclusivo. */
  start: number;
  /** Slot do boletim, fim exclusivo (desenha até a borda do mês). */
  end: number;
  /** Mês(s) com código `PH` — render com hachura + tooltip de 2º ciclo. */
  ph: boolean;
  /** Siglas UF ativas na lane em algum slot do segmento (ordenadas). */
  activeUfs: string[];
  /** Siglas UF com `PH` no segmento (ordenadas, pode ser vazio). */
  phUfs: string[];
  /** UFs distintas do grupo cultura-região (denominador honesto). */
  totalUfs: number;
}

/** Teto de faixas renderizadas (caller fatia + rotula o overflow). */
export const MAX_PHENO_LANES = 60;

interface SlotState {
  active: Set<string>;
  ph: Set<string>;
}

function emptySlots(): SlotState[] {
  return Array.from({ length: 12 }, () => ({ active: new Set<string>(), ph: new Set<string>() }));
}

export interface PhenoModel {
  lanes: PhenoLane[];
  segments: PhenoSegment[];
}

/**
 * Constrói lanes P/H por cultura-região e segmentos disjuntos.
 * `stateRegions`: sigla UF → região; UF ausente cai na própria sigla.
 */
export function buildPhenoModel(
  rows: ConabPhenoRow[],
  stateRegions: Record<string, string>,
): PhenoModel {
  const groups = new Map<string, { crop: string; region: string; ufs: Set<string>; p: SlotState[]; h: SlotState[] }>();

  for (const row of rows) {
    const crop = (row.crop || '').trim();
    const uf = (row.uf || '').trim();
    if (crop === '' || uf === '') continue;
    const region = stateRegions[uf] ?? uf;
    const key = `${crop}¦${region}`;
    let group = groups.get(key);
    if (group === undefined) {
      group = { crop, region, ufs: new Set(), p: emptySlots(), h: emptySlots() };
      groups.set(key, group);
    }
    group.ufs.add(uf);
    row.months.slice(0, 12).forEach((code, slot) => {
      const { plantingPct, harvestPct } = activityFromCode(code);
      const isPh = plantingPct > 0 && harvestPct > 0;
      if (plantingPct > 0) {
        group.p[slot].active.add(uf);
        if (isPh) group.p[slot].ph.add(uf);
      }
      if (harvestPct > 0) {
        group.h[slot].active.add(uf);
        if (isPh) group.h[slot].ph.add(uf);
      }
    });
  }

  const ordered = [...groups.values()].sort(
    (a, b) => a.crop.localeCompare(b.crop) || a.region.localeCompare(b.region),
  );
  const lanes: PhenoLane[] = [];
  const segments: PhenoSegment[] = [];

  for (const group of ordered) {
    const totalUfs = group.ufs.size;
    const kinds: { kind: PhenoKind; slots: SlotState[] }[] = [
      { kind: 'P', slots: group.p },
      { kind: 'H', slots: group.h },
    ];
    for (const { kind, slots } of kinds) {
      const laneId = `${group.crop}¦${group.region}¦${kind}`;
      lanes.push({ id: laneId, crop: group.crop, region: group.region, kind });
      // Runs maximais: hiato fecha o segmento; troca plain↔PH subdivide.
      let run: { start: number; ph: boolean; active: Set<string>; phUfs: Set<string> } | null = null;
      const flush = (end: number): void => {
        if (run === null) return;
        segments.push({
          laneId,
          start: run.start,
          end,
          ph: run.ph,
          activeUfs: [...run.active].sort(),
          phUfs: [...run.phUfs].sort(),
          totalUfs,
        });
        run = null;
      };
      slots.forEach((slotState, slot) => {
        const hasPh = slotState.ph.size > 0;
        if (slotState.active.size === 0) {
          flush(slot);
          return;
        }
        if (run === null) {
          run = { start: slot, ph: hasPh, active: new Set(), phUfs: new Set() };
        } else if (run.ph !== hasPh) {
          flush(slot);
          run = { start: slot, ph: hasPh, active: new Set(), phUfs: new Set() };
        }
        for (const uf of slotState.active) run.active.add(uf);
        for (const uf of slotState.ph) run.phUfs.add(uf);
      });
      flush(12);
    }
  }

  return { lanes, segments };
}

export interface PhenoTipLabels {
  planting: string;
  harvest: string;
  /** Linha de contagem honesta: `(ativas/total)`. */
  activeUfs: (active: number, total: number) => string;
  /** Nota PH: "plantio e colheita simultâneos — possível 2º ciclo". */
  simultaneous: string;
  more: (overflow: number) => string;
}

/**
 * Tooltip HTML do segmento: faixa + intervalo de meses + UFs (top-N) +
 * nota PH quando hachurado. Rótulos injetados (i18n no componente).
 */
export function formatPhenoTip(
  segment: PhenoSegment,
  laneLabel: string,
  months: string[],
  labels: PhenoTipLabels,
  topN = 5,
): string {
  const first = escapeHtml(months[segment.start] ?? '');
  const last = escapeHtml(months[Math.max(segment.end - 1, segment.start)] ?? '');
  const top = segment.activeUfs.slice(0, topN).map((uf) => escapeHtml(uf)).join(', ') || '–';
  const overflow = segment.activeUfs.length - Math.min(segment.activeUfs.length, topN);
  const more = overflow > 0 ? ` ${labels.more(overflow)}` : '';
  const kind = segment.laneId.endsWith('¦H') ? labels.harvest : labels.planting;
  // Root cause: laneLabel/UFs vêm de dados (crop/região/UF) — sem escape um
  // `<`/`&` quebra o tooltip HTML do ECharts.
  let tip = `<b>${escapeHtml(laneLabel)}</b><br>${kind}: ${first} – ${last}<br>${labels.activeUfs(segment.activeUfs.length, segment.totalUfs)}: ${top}${more}`;
  if (segment.ph) {
    const phTop = segment.phUfs.slice(0, topN).map((uf) => escapeHtml(uf)).join(', ');
    tip += `<br>⚠ ${labels.simultaneous}${phTop !== '' ? ` (${phTop})` : ''}`;
  }
  return tip;
}

/**
 * Rótulo da safra vigente no calendário Out→Set: outubro abre a safra
 * nova (`2025/26` a partir de out/2025); setembro ainda é da safra atual.
 */
export function seasonLabelForDate(now: Date): string {
  const year = now.getFullYear();
  const month = now.getMonth() + 1;
  const short = (y: number): string => String(y).slice(-2);
  return month >= 10 ? `${year}/${short(year + 1)}` : `${year - 1}/${short(year)}`;
}
