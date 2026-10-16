/**
 * ECharts CropCalendar screenshots {pt,en}x{light,dark} (Fase 2 fatia 2b).
 * Seeds `landagri-lang` + `landagri-theme` via init script (mesmo padrão
 * do echarts-availability-shots) e captura a rota `crop-calendar`
 * (100% ECharts: Heatmap/Line/Gantt/Polar/GroupedBar/HorizontalBar).
 */
import { test, expect } from '@playwright/test';

const ROUTE = '/LANDAGRI-B_Dashboard/agricultural-analysis/crop-calendar';
const LOCALES = [
  { seed: 'pt-BR', tag: 'pt' },
  { seed: 'en', tag: 'en' },
] as const;
const THEMES = ['light', 'dark'] as const;

test.describe('ECharts crop-calendar shots {pt,en}x{light,dark}', () => {
  for (const { seed, tag } of LOCALES) {
    for (const theme of THEMES) {
      test(`crop-calendar echarts ${tag}/${theme}`, async ({ page }) => {
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
        await page.goto(ROUTE, { waitUntil: 'networkidle' });
        // Página carregou (filtros + primeira aba heatmap).
        await expect(page.getByRole('heading').first()).toBeVisible({
          timeout: 15000,
        });
        // ECharts SVG renderer presente, nenhum Plotly na rota.
        await expect(page.locator('figure div svg').first()).toBeVisible({
          timeout: 15000,
        });
        expect(await page.locator('.js-plotly-plot').count()).toBe(0);
        await page.waitForTimeout(800);
        await page.screenshot({
          path: `test-results/echarts-cropcalendar-${tag}-${theme}.png`,
          fullPage: true,
          animations: 'disabled',
        });
      });
    }
  }
});
