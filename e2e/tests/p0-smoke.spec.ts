import { test, expect } from '@playwright/test';
import { BasePage } from '../pages/BasePage';
import { ROUTES, NAV_MENU_ITEMS, TIMEOUTS } from '../fixtures/testData';

test.describe('P0 - Smoke Tests (Critical Path)', () => {
  test('App loads with no console errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error' && !msg.text().includes('favicon')) {
        errors.push(msg.text());
      }
    });
    page.on('pageerror', (err) => errors.push(err.message));

    const bp = new BasePage(page);
    await bp.navigate(ROUTES.overview);

    expect(errors).toHaveLength(0);
  });

  test('Overview page loads and shows content', async ({ page }) => {
    const bp = new BasePage(page);
    await bp.navigate(ROUTES.overview);

    await expect(page.locator('main')).toBeVisible({ timeout: TIMEOUTS.pageLoad });
    await expect(page).toHaveURL(ROUTES.overview);
  });

  for (const item of NAV_MENU_ITEMS) {
    test(`Navigation to ${item.route} works`, async ({ page }) => {
      const bp = new BasePage(page);
      await bp.navigate(ROUTES.overview);

      await page.getByRole('link', { name: item.label }).first().click();
      await bp.waitForNavigationComplete();
      await expect(page).toHaveURL(item.route);
    });
  }

  test('No broken routes', async ({ page }) => {
    const routes = Object.values(ROUTES);

    for (const route of routes) {
      await page.goto(route, { waitUntil: 'networkidle', timeout: TIMEOUTS.pageLoad });
      await expect(page).toHaveURL(route);
      await expect(page.locator('main')).toBeVisible({ timeout: TIMEOUTS.pageLoad });
      const bodyText = await page.locator('body').textContent();
      expect(bodyText?.includes('404')).toBeFalsy();
    }
  });

  test('Overview renders map without the plotly bundle', async ({ page }) => {
    // Fase 2 fatia 2c: Overview uses ECharts (SVG); the plotly runtime is
    // gone from package.json, so no plotly request can exist.
    // P2a remodel (8195eea): overview is LULC-only — AgriculturalCharts was
    // intentionally removed, so assert the Leaflet island instead of ECharts
    // SVG here. ECharts coverage lives on initiative/agricultural routes.
    const plotlyRequests: string[] = [];
    page.on('request', (req) => {
      if (req.url().toLowerCase().includes('plotly')) plotlyRequests.push(req.url());
    });
    const bp = new BasePage(page);
    await bp.navigate(ROUTES.overview);
    await page.waitForTimeout(3000);

    const mapCount = await page.locator('.leaflet-container').count();
    expect(mapCount).toBeGreaterThan(0);
    await expect(page.locator('.leaflet-container').first()).toBeVisible();
    expect(plotlyRequests).toEqual([]);
  });

  test('Page has a title', async ({ page }) => {
    const bp = new BasePage(page);
    await bp.navigate(ROUTES.overview);

    const title = await bp.getPageTitle();
    expect(title.length).toBeGreaterThan(0);
  });
});
