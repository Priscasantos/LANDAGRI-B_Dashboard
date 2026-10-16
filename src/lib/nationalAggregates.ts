/**
 * Agregados nacionais (ex. `"BR"`) excluídos das visões "por estado".
 * Filtro só de exibição: o dado bruto segue intacto e o agregado continua
 * disponível onde fizer sentido (ex. KPIs nacionais). Reversível: esvazie o
 * set para reexibir o agregado nas listas de estados.
 */
const NATIONAL_AGGREGATE_UFS = new Set(['BR', 'BRAZIL', 'BRASIL']);

export function isNationalAggregateUf(uf: string): boolean {
  return NATIONAL_AGGREGATE_UFS.has(uf.trim().toUpperCase());
}
