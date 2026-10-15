import { test, expect } from '@playwright/test';
import { BasePage } from '../pages/BasePage';
import { ROUTES, TIMEOUTS } from '../fixtures/testData';

/**
 * Fase 3 theme system — mode-toggle + customizer persistence.
 * Validates that theme choices survive a full page reload via localStorage.
 */
test.describe('P4 - Theme System (mode + customizer persistence)', () => {
  test('Mode toggle switches dark class and persists landagri-theme', async ({
    page,
  }) => {
    const bp = new BasePage(page);
    await bp.navigate(ROUTES.overview);

    const toggle = page.getByTestId('theme-toggle');
    await expect(toggle).toBeVisible({ timeout: TIMEOUTS.pageLoad });

    const stored = (): Promise<string | null> =>
      page.evaluate(() => localStorage.getItem('landagri-theme'));
    const isDark = (): Promise<boolean> =>
      page.evaluate(() =>
        document.documentElement.classList.contains('dark'),
      );
    // Avança até um modo explícito (≤3 cliques a partir de qualquer estado).
    const advanceTo = async (mode: string): Promise<void> => {
      for (let i = 0; i < 4; i++) {
        if ((await stored()) === mode) return;
        await toggle.click();
        await page.waitForTimeout(300);
      }
      expect(await stored()).toBe(mode);
    };

    await advanceTo('dark');
    expect(await isDark()).toBe(true);

    await page.reload({ waitUntil: 'networkidle' });
    await expect(page.locator('main')).toBeVisible({
      timeout: TIMEOUTS.pageLoad,
    });
    expect(await stored()).toBe('dark');
    expect(await isDark()).toBe(true);

    await advanceTo('light');
    expect(await isDark()).toBe(false);
  });

  test('Theme customizer persists density + radius + preset across reload', async ({
    page,
  }) => {
    const bp = new BasePage(page);
    await bp.navigate(ROUTES.overview);

    await page
      .getByRole('button', { name: /personalizar tema/i })
      .click();
    const dialog = page.getByRole('dialog', { name: /personalizar tema/i });
    await expect(dialog).toBeVisible({ timeout: TIMEOUTS.pageLoad });

    await dialog.getByRole('radio', { name: /compacta/i }).click();
    await dialog.getByRole('radio', { name: /grande/i }).click();
    await dialog.getByRole('radio', { name: 'Verde Agro', exact: true }).click();

    expect(await page.evaluate(() => localStorage.getItem('landagri-density'))).toBe(
      'compact',
    );
    expect(
      await page.evaluate(() => localStorage.getItem('landagri-preset')),
    ).toBe('agro');

    await page.reload({ waitUntil: 'networkidle' });
    await expect(page.locator('main')).toBeVisible({
      timeout: TIMEOUTS.pageLoad,
    });
    expect(await page.evaluate(() => localStorage.getItem('landagri-density'))).toBe(
      'compact',
    );
    expect(
      await page.evaluate(() => localStorage.getItem('landagri-preset')),
    ).toBe('agro');
    expect(
      await page.evaluate(() => document.documentElement.dataset.density),
    ).toBe('compact');
  });

  test('Theme customizer swaps computed vars per preset + applies font + reset restores defaults', async ({
    page,
  }) => {
    const bp = new BasePage(page);
    await bp.navigate(ROUTES.overview);

    await page
      .getByRole('button', { name: /personalizar tema/i })
      .click();
    const dialog = page.getByRole('dialog', { name: /personalizar tema/i });
    await expect(dialog).toBeVisible({ timeout: TIMEOUTS.pageLoad });

    const computed = (token: string): Promise<string> =>
      page.evaluate(
        (t) =>
          getComputedStyle(document.documentElement)
            .getPropertyValue(t)
            .trim(),
        token,
      );

    // Terra aplica o primary terroso como var computada…
    await dialog.getByRole('radio', { name: 'Terra', exact: true }).click();
    expect(
      await page.evaluate(() => localStorage.getItem('landagri-preset')),
    ).toBe('terra');
    const terraPrimary = await computed('--color-primary');
    expect(terraPrimary).not.toBe('');

    // …e Âmbar troca visivelmente (var computada difere da Terra).
    await dialog.getByRole('radio', { name: 'Âmbar', exact: true }).click();
    const ambarPrimary = await computed('--color-primary');
    expect(ambarPrimary).not.toBe('');
    expect(ambarPrimary).not.toBe(terraPrimary);
    expect(await computed('--color-chart-1')).not.toBe('');

    // Fonte Mono propaga o stack monoespaçado para --font-sans.
    await dialog.getByRole('radio', { name: /mono/i }).click();
    expect(
      await page.evaluate(() => localStorage.getItem('landagri-font')),
    ).toBe('mono');
    expect(await computed('--font-sans')).toContain('JetBrains Mono');

    // Reset restaura os defaults do app (agro-v2 + confortável + md).
    await dialog.getByRole('radio', { name: /compacta/i }).click();
    await dialog
      .getByRole('button', { name: /restaurar padrão/i })
      .click();
    expect(
      await page.evaluate(() => localStorage.getItem('landagri-preset')),
    ).toBe('agro-v2');
    expect(
      await page.evaluate(() => localStorage.getItem('landagri-density')),
    ).toBe('comfortable');
    expect(
      await page.evaluate(() => localStorage.getItem('landagri-font')),
    ).toBe('default');
    expect(
      await page.evaluate(() => document.documentElement.dataset.density),
    ).toBe('comfortable');
    // Reset restaura o primary do Verde Agro v2 (light #2e7d32 / dark #9ccc65).
    const resetPrimary = (await computed('--color-primary')).toLowerCase();
    expect(['#2e7d32', '#9ccc65']).toContain(resetPrimary);
    expect(await computed('--font-sans')).toContain('Inter');
  });
});
