/**
 * ECharts initiative-analysis + predictive screenshots {pt,en}x{light,dark}
 * (Fase 2 fatia 2c). Seeds `landagri-lang` + `landagri-theme` via init
 * script (mesmo padrão do echarts-cropcalendar-shots) e captura as rotas
 * `temporal` / `comparative` / `detailed` / `predictive` (100% ECharts nos
 * charts migrados: Timeline/Line/Heatmap/GroupedBar/Scatter/Radar/Gantt).
 */
import { test, expect } from '@playwright/test';

const BASE = '/LANDAGRI-B_Dashboard';
const PAGES = [
  { slug: 'temporal', route: `${BASE}/initiative-analysis/temporal`, rechartsFree: true },
  { slug: 'comparative', route: `${BASE}/initiative-analysis/comparative`, rechartsFree: true },
  { slug: 'detailed', route: `${BASE}/initiative-analysis/detailed`, rechartsFree: true },
  // Predictive mantém o chart principal em recharts (fora do escopo 2c);
  // só a ilha de detalhe migrou para ECharts.
  { slug: 'predictive', route: `${BASE}/predictive`, rechartsFree: false },
] as const;
const LOCALES = [
  { seed: 'pt-BR', tag: 'pt' },
  { seed: 'en', tag: 'en' },
] as const;
const THEMES = ['light', 'dark'] as const;

test.describe('ECharts initiative+predictive shots {pt,en}x{light,dark}', () => {
  for (const { slug, route, rechartsFree } of PAGES) {
    for (const { seed, tag } of LOCALES) {
      for (const theme of THEMES) {
        test(`${slug} echarts ${tag}/${theme}`, async ({ page }) => {
          await page.setViewportSize({ width: 1280, height: 800 });
          await page.addInitScript(
            ({ lang, th }) => {
              try {
                localStorage.setItem('landagri-lang', lang);
                localStorage.setItem('landagri-theme', th);
              } catch {
                /* private mode — segue defaults */
              }
            },
            { lang: seed, th: theme },
          );
          await page.goto(route, { waitUntil: 'networkidle' });
          // Página carregou (heading + primeira aba).
          await expect(page.getByRole('heading').first()).toBeVisible({
            timeout: 15000,
          });
          // ECharts SVG renderer presente, nenhum Plotly na rota.
          await expect(page.locator('figure div svg').first()).toBeVisible({
            timeout: 15000,
          });
          expect(await page.locator('.js-plotly-plot').count()).toBe(0);
          if (rechartsFree) {
            expect(await page.locator('.recharts-wrapper').count()).toBe(0);
          }
          await page.waitForTimeout(800);
          await page.screenshot({
            path: `test-results/echarts-${slug}-${tag}-${theme}.png`,
            fullPage: true,
            animations: 'disabled',
          });
        });
      }
    }
  }
});
