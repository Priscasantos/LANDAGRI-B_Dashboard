/**
 * ECharts availability screenshots {pt,en}x{light,dark} (Fase 2 fatia 2a).
 * Seeds `landagri-lang` + `landagri-theme` via init script (mesmo padrão
 * do p2-visual) e captura a rota `availability` (ECharts promovido).
 */
import { test, expect } from '@playwright/test';

const ROUTE = '/LANDAGRI-B_Dashboard/agricultural-analysis/availability';
const LOCALES = [
  { seed: 'pt-BR', tag: 'pt' },
  { seed: 'en', tag: 'en' },
] as const;
const THEMES = ['light', 'dark'] as const;

test.describe('ECharts availability shots {pt,en}x{light,dark}', () => {
  for (const { seed, tag } of LOCALES) {
    for (const theme of THEMES) {
      test(`availability echarts ${tag}/${theme}`, async ({ page }) => {
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
        // Mesmo heading do original Plotly (spatial coverage card).
        await expect(page.getByRole('heading').first()).toBeVisible({
          timeout: 15000,
        });
        // ECharts SVG renderer presente.
        await expect(page.locator('figure div svg').first()).toBeVisible({
          timeout: 15000,
        });
        await page.waitForTimeout(800);
        await page.screenshot({
          path: `test-results/echarts-availability-${tag}-${theme}.png`,
          fullPage: true,
          animations: 'disabled',
        });
      });
    }
  }
});
