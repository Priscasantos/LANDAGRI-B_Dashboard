/**
 * Fase A — fallback deep-link: refresh direto nas sub-rotas rende a página
 * (sem 404 silencioso) e sub-rota desconhecida mostra retorno local.
 */
import { test, expect } from '@playwright/test';

const BASE = '/LANDAGRI-B_Dashboard';
const CROP_CALENDAR = `${BASE}/agricultural-analysis/crop-calendar`;
const TEMPORAL = `${BASE}/initiative-analysis/temporal`;

async function gotoSeeded(
  page: import('@playwright/test').Page,
  route: string,
): Promise<void> {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.addInitScript(() => {
    try {
      localStorage.setItem('landagri-lang', 'pt-BR');
      localStorage.setItem('landagri-theme', 'light');
    } catch {
      /* private mode — segue defaults */
    }
  });
  await page.goto(route, { waitUntil: 'networkidle' });
}

test.describe('deep-link refresh direto', () => {
  test('crop-calendar: acesso direto + reload rende conteúdo', async ({ page }) => {
    await gotoSeeded(page, CROP_CALENDAR);
    await expect(page.getByRole('heading').first()).toBeVisible({ timeout: 15000 });
    await expect(page.locator('figure div svg').first()).toBeVisible({ timeout: 15000 });
    await page.reload({ waitUntil: 'networkidle' });
    await expect(page.getByRole('heading').first()).toBeVisible({ timeout: 15000 });
    await expect(page.locator('figure div svg').first()).toBeVisible({ timeout: 15000 });
  });

  test('temporal: acesso direto + reload rende conteúdo', async ({ page }) => {
    await gotoSeeded(page, TEMPORAL);
    await expect(page.getByRole('heading').first()).toBeVisible({ timeout: 15000 });
    await expect(page.locator('figure div svg').first()).toBeVisible({ timeout: 15000 });
    await page.reload({ waitUntil: 'networkidle' });
    await expect(page.getByRole('heading').first()).toBeVisible({ timeout: 15000 });
    await expect(page.locator('figure div svg').first()).toBeVisible({ timeout: 15000 });
  });

  test('sub-rota desconhecida mostra retorno em vez de 404 silencioso', async ({ page }) => {
    await gotoSeeded(page, `${BASE}/agricultural-analysis/rota-inexistente`);
    await expect(page.getByText(/Subpágina não encontrada/)).toBeVisible({ timeout: 15000 });
    await expect(page.getByRole('link', { name: /Voltar para a seção/ })).toBeVisible();
  });
});
