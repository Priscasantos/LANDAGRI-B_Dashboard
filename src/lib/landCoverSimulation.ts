export interface PolicyParams {
  reforestationRate: number;
  agriExpansion: number;
  sustainableAdoption: number;
}

export interface ProjectionPoint {
  year: number;
  forestryArea: number;
  pastureArea: number;
  agricultureArea: number;
  carbonEmissionIndex: number;
}

export const BASELINE_2025 = {
  forestryArea: 472.9,
  pastureArea: 159.2,
  agricultureArea: 81.3,
  totalArea: 851.6,
};

export function simulateProjections(params: PolicyParams): ProjectionPoint[] {
  const results: ProjectionPoint[] = [];
  const { reforestationRate, agriExpansion, sustainableAdoption } = params;

  let forest = BASELINE_2025.forestryArea;
  let pasture = BASELINE_2025.pastureArea;
  let agriculture = BASELINE_2025.agricultureArea;
  let carbonIndex;

  for (let year = 2025; year <= 2035; year++) {
    const reforestGain = pasture * (reforestationRate / 100);
    forest += reforestGain;
    pasture -= reforestGain;

    const agriGain = pasture * (agriExpansion / 100);
    agriculture += agriGain;
    pasture -= agriGain;

    const carbonReduction = sustainableAdoption * 0.15;
    carbonIndex = 100 - (year - 2025) * (carbonReduction / 10);

    const naturalRegen = pasture * 0.005;
    pasture -= naturalRegen;
    forest += naturalRegen;

    forest = Math.max(forest, 300);
    pasture = Math.max(pasture, 50);
    agriculture = Math.max(agriculture, 60);

    results.push({
      year,
      forestryArea: Math.round(forest * 10) / 10,
      pastureArea: Math.round(pasture * 10) / 10,
      agricultureArea: Math.round(agriculture * 10) / 10,
      carbonEmissionIndex: Math.round(carbonIndex * 10) / 10,
    });
  }

  return results;
}

export function getDefaultParams(): PolicyParams {
  return {
    reforestationRate: 1.2,
    agriExpansion: 0.8,
    sustainableAdoption: 65,
  };
}
