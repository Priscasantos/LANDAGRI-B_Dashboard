import { test, expect } from '@playwright/test';
import { BasePage } from '../pages/BasePage';
import { ROUTES, NAV_MENU_ITEMS, TIMEOUTS } from '../fixtures/testData';

/**
 * Fase 1 shell SaaS — sidebar nav smoke.
 * Validates the BaseLayout shell: sidebar links, breadcrumb,
 * command palette (Ctrl+K) and per-module titles.
 */
test.describe('P0 - Shell SaaS (sidebar nav smoke)', () => {
  test('Sidebar is visible with the 5 module links', async ({ page }) => {
    const bp = new BasePage(page);
    await bp.navigate(ROUTES.overview);

    const sidebar = page.getByTestId('app-sidebar');
    await expect(sidebar).toBeVisible({ timeout: TIMEOUTS.pageLoad });
    for (const item of NAV_MENU_ITEMS) {
      await expect(
        sidebar.getByRole('link', { name: item.label }).first(),
      ).toBeVisible();
    }
  });

  test('Sidebar links navigate to each module', async ({ page }) => {
    const bp = new BasePage(page);
    await bp.navigate(ROUTES.overview);

    for (const item of NAV_MENU_ITEMS) {
      await page
        .getByTestId('app-sidebar')
        .getByRole('link', { name: item.label })
        .first()
        .click();
      await bp.waitForNavigationComplete();
      await expect(page).toHaveURL(item.route);
      await expect(page.locator('main')).toBeVisible({
        timeout: TIMEOUTS.pageLoad,
      });
    }
  });

  test('Breadcrumb + module title render per page', async ({ page }) => {
    const bp = new BasePage(page);
    await bp.navigate(ROUTES.predictive);

    await expect(page.getByLabel('breadcrumb')).toBeVisible();
    await expect(
      page.locator('main h1', { hasText: /Simulador Preditivo/ }),
    ).toBeVisible({ timeout: TIMEOUTS.pageLoad });
  });

  test('Command palette opens with Ctrl+K and navigates', async ({ page }) => {
    const bp = new BasePage(page);
    await bp.navigate(ROUTES.overview);

    await page.keyboard.press('Control+k');
    const dialog = page.getByRole('dialog', {
      name: /Buscar páginas do dashboard/,
    });
    await expect(dialog).toBeVisible({ timeout: TIMEOUTS.pageLoad });

    await page.getByRole('combobox', { name: 'Buscar páginas' }).fill('temporal');
    await page
      .getByRole('option', { name: /Temporal Analysis/ })
      .first()
      .click();
    await bp.waitForNavigationComplete();
    await expect(page).toHaveURL(ROUTES.initiativeAnalysis);
  });

  test('Unknown path redirects home (catch-all 404)', async ({ page }) => {
    await page.goto('/LANDAGRI-B_Dashboard/definitely-not-a-page', {
      waitUntil: 'networkidle',
      timeout: TIMEOUTS.pageLoad,
    });
    await expect(page).toHaveURL(/\/LANDAGRI-B_Dashboard\/?$/);
    await expect(page.locator('main')).toBeVisible({
      timeout: TIMEOUTS.pageLoad,
    });
  });
});
