import { test, expect } from '@playwright/test';
import { BasePage } from '../pages/BasePage';
import { ROUTES, TIMEOUTS } from '../fixtures/testData';

const BASENAME = '/LANDAGRI-B_Dashboard';

test.describe('P3 - Fase 4 hardening', () => {
  test('all 5 routes load under the basename', async ({ page }) => {
    const bp = new BasePage(page);
    for (const route of Object.values(ROUTES)) {
      await bp.navigate(route);
      await expect(page).toHaveURL(route);
      await expect(page.locator('main')).toBeVisible({
        timeout: TIMEOUTS.pageLoad,
      });
    }
  });

  test('deep link loads directly (client routing, no 404)', async ({
    page,
  }) => {
    const bp = new BasePage(page);
    await bp.navigate(ROUTES.initiativeAnalysis);
    await expect(page).toHaveURL(ROUTES.initiativeAnalysis);
    await expect(page.locator('main')).toBeVisible({
      timeout: TIMEOUTS.pageLoad,
    });
    const bodyText = await page.locator('body').textContent();
    expect(bodyText?.includes('404')).toBeFalsy();
  });

  test('404.html fallback preserves path + query + hash', async ({
    request,
  }) => {
    const res = await request.get(`${BASENAME}/404.html`);
    expect(res.ok()).toBeTruthy();
    const html = await res.text();
    // Session-storage handoff read by App.tsx.
    expect(html).toContain('redirectPath');
    // Query string and hash survive the redirect.
    expect(html).toContain('location.search');
    expect(html).toContain('location.hash');
    // No hardcoded sub-path outside the first-segment heuristic.
    expect(html).not.toContain('/LANDAGRI-B_Dashboard/');
  });

  test('mobile drawer: dialog semantics, Escape closes, aria-current set', async ({
    page,
  }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    const bp = new BasePage(page);
    await bp.navigate(ROUTES.overview);

    await page.getByRole('button', { name: 'Abrir menu' }).click();
    const dialog = page.getByRole('dialog', { name: 'Menu de navegação' });
    await expect(dialog).toBeVisible();
    await expect(dialog).toHaveAttribute('aria-modal', 'true');

    // Active link is announced.
    const current = dialog.getByRole('link', { current: 'page' });
    expect(await current.count()).toBeGreaterThan(0);

    // Escape closes and focus returns to the menu button.
    await page.keyboard.press('Escape');
    await expect(dialog).toBeHidden();
    await expect(
      page.getByRole('button', { name: 'Abrir menu' }),
    ).toBeFocused();
  });

  test('Overview downloads no plotly bundle (network assert)', async ({
    page,
  }) => {
    const plotlyRequests: string[] = [];
    page.on('request', (req) => {
      if (req.url().toLowerCase().includes('plotly')) {
        plotlyRequests.push(req.url());
      }
    });

    const bp = new BasePage(page);
    await bp.navigate(ROUTES.overview);
    await page.waitForTimeout(TIMEOUTS.dataLoad);

    expect(plotlyRequests).toEqual([]);
  });
});
