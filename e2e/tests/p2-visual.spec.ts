import { test, expect } from '@playwright/test';
import { BasePage } from '../pages/BasePage';
import { ROUTES, TIMEOUTS } from '../fixtures/testData';

test.describe('P2 - Visual Tests', () => {
  test('Dashboard layout matches expected structure', async ({ page }) => {
    const bp = new BasePage(page);
    await bp.navigate(ROUTES.overview);
    await page.waitForTimeout(2000);

    const header = page.locator('header').first();
    const main = page.locator('main');

    await expect(header).toBeVisible();
    await expect(main).toBeVisible();

    const mainChildren = await main.locator('> *').count();
    expect(mainChildren).toBeGreaterThan(0);
  });

  test('Dark mode toggle works', async ({ page }) => {
    const bp = new BasePage(page);
    await bp.navigate(ROUTES.overview);

    const toggle = page.getByTestId('theme-toggle');
    if (await toggle.isVisible().catch(() => false)) {
      await toggle.click();
      await page.waitForTimeout(500);
      await toggle.click();
    }
  });

  test('Charts have proper dimensions on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    const bp = new BasePage(page);
    await bp.navigate(ROUTES.overview);
    await page.waitForTimeout(3000);

    const charts = page.locator('.js-plotly-plot');
    const chartCount = await charts.count();

    for (let i = 0; i < Math.min(chartCount, 3); i++) {
      const box = await charts.nth(i).boundingBox();
      expect(box).not.toBeNull();
      if (box) {
        expect(box.width).toBeGreaterThan(200);
        expect(box.height).toBeGreaterThan(200);
      }
    }
  });
});

/**
 * Fase 4 — matriz visual {pt,en}×{light,dark} nos charts e no mapa.
 * Tiles de rede são mascarados (`.leaflet-tile-pane`) para a comparação
 * ser determinística; tolerância via `maxDiffPixelRatio`.
 */
test.describe('P2 - Visual matrix {pt,en}x{light,dark} (charts + mapa)', () => {
  const LOCALES = [
    { seed: 'pt-BR', tag: 'pt' },
    { seed: 'en', tag: 'en' },
  ] as const;
  const THEMES = ['light', 'dark'] as const;

  for (const { seed, tag } of LOCALES) {
    for (const theme of THEMES) {
      test(`overview charts+mapa ${tag}/${theme}`, async ({ page }) => {
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
        const bp = new BasePage(page);
        await bp.navigate(ROUTES.overview);
        await expect(
          page.locator('.recharts-wrapper svg').first(),
        ).toBeVisible({ timeout: TIMEOUTS.pageLoad });
        await expect(page.locator('.leaflet-container')).toBeVisible({
          timeout: TIMEOUTS.pageLoad,
        });
        await page.waitForTimeout(1200);

        await expect(page).toHaveScreenshot(
          `p2-overview-charts-map-${tag}-${theme}.png`,
          {
            fullPage: true,
            animations: 'disabled',
            maxDiffPixelRatio: 0.05,
            mask: [page.locator('.leaflet-tile-pane')],
          },
        );
      });

      test(`initiative plotly ${tag}/${theme}`, async ({ page }) => {
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
        const bp = new BasePage(page);
        await bp.navigate(ROUTES.initiativeAnalysis);
        const count = await bp.getPlotlyChartCount();
        expect(count).toBeGreaterThan(0);
        await page.waitForTimeout(1200);

        await expect(page).toHaveScreenshot(
          `p2-initiative-plotly-${tag}-${theme}.png`,
          {
            fullPage: true,
            animations: 'disabled',
            maxDiffPixelRatio: 0.05,
          },
        );
      });
    }
  }
});
