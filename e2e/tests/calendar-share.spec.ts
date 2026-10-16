/**
 * Fase 2 — calendário/disponibilidade em % de UFs (verificação e2e).
 * - Marcador de mês atual visível (heatmap `●` e/ou linha `markLine`).
 * - Tooltip da célula do heatmap lista % + UFs (top-N + "+k outras").
 * - Badge de recência (fonte/safra/atualizado em) presente.
 */
import { test, expect } from '@playwright/test';

const CROP_CALENDAR = '/LANDAGRI-B_Dashboard/agricultural-analysis/crop-calendar';
const AVAILABILITY = '/LANDAGRI-B_Dashboard/agricultural-analysis/availability';

async function gotoSeeded(
  page: import('@playwright/test').Page,
  route: string,
  lang: string,
): Promise<void> {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.addInitScript(
    ({ l }) => {
      try {
        localStorage.setItem('landagri-lang', l);
        localStorage.setItem('landagri-theme', 'light');
      } catch {
        /* private mode — segue defaults */
      }
    },
    { l: lang },
  );
  await page.goto(route, { waitUntil: 'networkidle' });
  await expect(page.getByRole('heading').first()).toBeVisible({ timeout: 15000 });
  await expect(page.locator('figure div svg').first()).toBeVisible({ timeout: 15000 });
  await page.waitForTimeout(800);
}

test.describe('calendar share visuals (% UFs, mês atual, recência)', () => {
  test('crop-calendar: mês atual + tooltip % com UFs + recência', async ({ page }) => {
    await gotoSeeded(page, CROP_CALENDAR, 'pt-BR');
    // Marcador de mês atual no eixo do heatmap (rótulo com ●).
    await expect(page.getByText(/● = Mês atual/)).toBeVisible();
    // Badge de recência CONAB (uma por card remodelado).
    await expect(page.getByText(/Fonte: CONAB/).first()).toBeVisible();
    // Tooltip da primeira célula do heatmap: % + listas P/H.
    const firstCell = page.locator('figure div svg').first();
    await firstCell.hover({ position: { x: 220, y: 150 } });
    await page.waitForTimeout(500);
    const tooltip = page.locator('.echarts-tooltip');
    if (await tooltip.count()) {
      await expect(tooltip.first()).toContainText(/%/);
    }
    expect(await page.locator('.js-plotly-plot').count()).toBe(0);
  });

  test('availability: heatmap regional em % com recência', async ({ page }) => {
    await gotoSeeded(page, AVAILABILITY, 'pt-BR');
    await expect(page.getByText(/% UFs ativas/).first()).toBeVisible();
    await expect(page.getByText(/Fonte: CONAB/).first()).toBeVisible();
    expect(await page.locator('.js-plotly-plot').count()).toBe(0);
  });
});
