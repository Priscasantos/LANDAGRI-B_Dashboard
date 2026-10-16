import { test, expect } from '@playwright/test';
import { BasePage } from '../pages/BasePage';
import { ROUTES, TIMEOUTS } from '../fixtures/testData';

/**
 * Fase 4 — e2e i18n toggle-only PT↔EN (verify only).
 *
 * Cobre as 5 rotas: toggle persiste após reload, shell traduzido,
 * `<html lang>` correto, sem `width(-1)` no console, screenshots {pt,en},
 * mapa OSM (role=application, aviso noCoords, tiles, dark sem watermark) e
 * pins `landagri-lang` / `landagri-theme`.
 *
 * Desvios pinados (não mexer): CARTO dark_matter descartado (API KEY
 * REQUIRED) — OSM+filter CSS é o estado final; legenda ECharts bottom.
 */

const FIVE_ROUTES = [
  { slug: 'overview', route: ROUTES.overview, ptH1: /Visão Geral/, enH1: /Overview/ },
  {
    slug: 'initiative',
    route: ROUTES.initiativeAnalysis,
    ptH1: /Iniciativas/,
    enH1: /Initiatives/,
  },
  {
    slug: 'agricultural',
    route: ROUTES.agriculturalAnalysis,
    ptH1: /Agricultura/,
    enH1: /Agriculture/,
  },
  {
    slug: 'predictive',
    route: ROUTES.predictive,
    ptH1: /Simulador/,
    enH1: /Simulator/,
  },
  {
    slug: 'about',
    route: ROUTES.about,
    ptH1: /Sobre o Dashboard/,
    enH1: /About the LANDAGRI/,
  },
] as const;

const PT_NO_COORDS =
  'Sem coordenadas disponíveis para as iniciativas — exibindo mapa base do Brasil.';
const EN_NO_COORDS =
  'No coordinates available for the initiatives — showing base map of Brazil.';

async function htmlLang(page: import('@playwright/test').Page): Promise<string> {
  return page.evaluate(() => document.documentElement.lang);
}

/** Troca o locale via storage + reload único (storage persiste nos `goto`s seguintes). */
async function switchLocale(
  page: import('@playwright/test').Page,
  locale: 'pt-BR' | 'en',
): Promise<void> {
  await page.evaluate((lang) => {
    try {
      localStorage.setItem('landagri-lang', lang);
    } catch {
      /* private mode — segue em memória */
    }
  }, locale);
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
}

test.describe('P5 - i18n toggle PT↔EN nas 5 rotas', () => {
  test('toggle persiste após reload nas 5 rotas, html[lang] correto', async ({
    page,
  }) => {
    const bp = new BasePage(page);
    // Contexto fresco: detectLocale usa navigator (playwright fixa pt-BR).
    await bp.navigate(ROUTES.overview);
    expect(await htmlLang(page)).toBe('pt-BR');

    const toggle = page.getByTestId('language-toggle');
    await expect(toggle).toBeVisible({ timeout: TIMEOUTS.pageLoad });

    // PT → EN via toggle real (caminho UX).
    await toggle.click();
    await expect
      .poll(() => page.evaluate(() => localStorage.getItem('landagri-lang')))
      .toBe('en');
    expect(await htmlLang(page)).toBe('en');

    // EN sobrevive ao reload + navegação nas 5 rotas.
    for (const { route } of FIVE_ROUTES) {
      await page.goto(route, {
        waitUntil: 'networkidle',
        timeout: TIMEOUTS.pageLoad,
      });
      await expect(page.locator('main')).toBeVisible({
        timeout: TIMEOUTS.pageLoad,
      });
      expect(
        await page.evaluate(() => localStorage.getItem('landagri-lang')),
      ).toBe('en');
      expect(await htmlLang(page)).toBe('en');
    }

    await page.reload({ waitUntil: 'networkidle' });
    expect(
      await page.evaluate(() => localStorage.getItem('landagri-lang')),
    ).toBe('en');
    expect(await htmlLang(page)).toBe('en');

    // EN → PT volta e persiste.
    await page.getByTestId('language-toggle').click();
    await expect
      .poll(() => page.evaluate(() => localStorage.getItem('landagri-lang')))
      .toBe('pt-BR');
    expect(await htmlLang(page)).toBe('pt-BR');
    await page.reload({ waitUntil: 'networkidle' });
    expect(
      await page.evaluate(() => localStorage.getItem('landagri-lang')),
    ).toBe('pt-BR');
    expect(await htmlLang(page)).toBe('pt-BR');
  });

  test('shell 100% traduzido por rota (EN sem resto PT, PT sem resto EN)', async ({
    page,
  }) => {
    test.setTimeout(120000);
    const bp = new BasePage(page);
    // Contexto fresco = PT (detectLocale cai no navigator pt-BR do projeto).
    for (const { route, ptH1 } of FIVE_ROUTES) {
      await bp.navigate(route);
      await expect(page.locator('main h1').first()).toContainText(ptH1, {
        timeout: TIMEOUTS.pageLoad,
      });
      const sidebar = page.getByTestId('app-sidebar');
      await expect(
        sidebar.getByRole('link', { name: 'Visão Geral' }).first(),
      ).toBeVisible();
      await expect(page.locator('footer').first()).toContainText(
        /Dados: MapBiomas & IBGE/,
      );
      expect(await htmlLang(page)).toBe('pt-BR');
    }

    // EN aplicado uma vez; storage persiste nos gotos seguintes.
    await switchLocale(page, 'en');
    for (const { route, enH1 } of FIVE_ROUTES) {
      await page.goto(route, {
        waitUntil: 'networkidle',
        timeout: TIMEOUTS.pageLoad,
      });
      await expect(page.locator('main')).toBeVisible({
        timeout: TIMEOUTS.pageLoad,
      });
      await expect(page.locator('main h1').first()).toContainText(enH1, {
        timeout: TIMEOUTS.pageLoad,
      });
      const sidebar = page.getByTestId('app-sidebar');
      await expect(sidebar.getByRole('link', { name: /Overview/ }).first())
        .toBeVisible();
      await expect(
        sidebar.getByRole('link', { name: 'Visão Geral' }),
      ).toHaveCount(0);
      await expect(page.locator('footer').first()).toContainText(
        /Data: MapBiomas & IBGE/,
      );
      expect(await htmlLang(page)).toBe('en');
    }
  });

  test('sem width(-1) no console em {pt,en} × 5 rotas', async ({ page }) => {
    test.setTimeout(120000);
    const hits: string[] = [];
    page.on('console', (msg) => {
      const text = msg.text();
      if (/width\s*\(\s*-1/i.test(text)) hits.push(`[${msg.type()}] ${text}`);
    });
    page.on('pageerror', (err) => {
      if (/width\s*\(\s*-1/i.test(err.message)) hits.push(`[pageerror] ${err.message}`);
    });

    const bp = new BasePage(page);
    for (const { route } of FIVE_ROUTES) {
      await bp.navigate(route);
      // Dá tempo dos charts (ECharts SVG) medirem o container.
      await page.waitForTimeout(1000);
    }
    await switchLocale(page, 'en');
    for (const { route } of FIVE_ROUTES) {
      await page.goto(route, {
        waitUntil: 'networkidle',
        timeout: TIMEOUTS.pageLoad,
      });
      await expect(page.locator('main')).toBeVisible({
        timeout: TIMEOUTS.pageLoad,
      });
      await page.waitForTimeout(1000);
    }
    expect(hits).toEqual([]);
  });

  test('screenshots {pt,en} por rota (artefatos p5-i18n)', async ({ page }) => {
    test.setTimeout(120000);
    const phases = [
      { locale: 'pt-BR', tag: 'pt' },
      { locale: 'en', tag: 'en' },
    ] as const;
    let first = true;
    for (const { locale, tag } of phases) {
      if (first) {
        first = false; // contexto fresco já é PT
      } else {
        await switchLocale(page, locale);
      }
      for (const { slug, route } of FIVE_ROUTES) {
        await page.goto(route, {
          waitUntil: 'networkidle',
          timeout: TIMEOUTS.pageLoad,
        });
        await expect(page.locator('main')).toBeVisible({
          timeout: TIMEOUTS.pageLoad,
        });
        await page.waitForTimeout(1000);
        await page.screenshot({
          path: `test-results/p5-i18n/${slug}-${tag}.png`,
          fullPage: true,
        });
      }
    }
  });

  test('mapa overview: role=application, noCoords, tiles OSM, dark sem watermark', async ({
    page,
  }) => {
    const bp = new BasePage(page);
    const osmRequests: string[] = [];
    page.on('request', (req) => {
      if (req.url().includes('tile.openstreetmap.org')) {
        osmRequests.push(req.url());
      }
    });

    for (const locale of ['pt-BR', 'en'] as const) {
      const expectedNoCoords = locale === 'pt-BR' ? PT_NO_COORDS : EN_NO_COORDS;
      const expectedAria =
        locale === 'pt-BR'
          ? 'Mapa das iniciativas LANDAGRI-B (Brasil)'
          : 'LANDAGRI-B initiatives map (Brazil)';
      if (locale === 'en') await switchLocale(page, locale);
      else await bp.navigate(ROUTES.overview);

      const map = page.getByRole('application', { name: expectedAria });
      await expect(map).toBeVisible({ timeout: TIMEOUTS.pageLoad });
      await expect(
        map.getByRole('status').filter({ hasText: expectedNoCoords }),
      ).toBeVisible();
      await expect(page.locator('.leaflet-container')).toBeVisible();

      // Tiles OSM: <img> com src OSM ou request emitido (offline ainda tenta).
      await page.waitForTimeout(2500);
      const tileSrcs = await page
        .locator('.leaflet-tile-pane img.leaflet-tile')
        .evaluateAll((imgs) =>
          imgs.map((img) => (img as HTMLImageElement).src),
        );
      const hasOsmTile = tileSrcs.some((src) =>
        src.includes('tile.openstreetmap.org'),
      );
      expect(hasOsmTile || osmRequests.length > 0).toBe(true);
    }

    // Dark: filtro CSS no tile pane, nenhum watermark CARTO/API KEY.
    await page.evaluate(() => {
      try {
        localStorage.setItem('landagri-lang', 'en');
        localStorage.setItem('landagri-theme', 'dark');
      } catch {
        /* noop */
      }
    });
    await bp.navigate(ROUTES.overview);
    const darkMap = page.getByRole('application').first();
    await expect(darkMap).toBeVisible({ timeout: TIMEOUTS.pageLoad });
    await expect(darkMap).toHaveClass(/leaflet-tiles-dark/);
    await expect(page.locator('.leaflet-tile-pane')).toBeAttached();
    expect(
      await page.evaluate(() =>
        document.documentElement.classList.contains('dark'),
      ),
    ).toBe(true);
    const bodyText = (await page.locator('body').textContent()) ?? '';
    expect(bodyText).not.toContain('API KEY REQUIRED');
    const cartoImgs = await page
      .locator('img[src*="carto"], img[src*="cartodb"]')
      .count();
    expect(cartoImgs).toBe(0);
  });

  test('pins landagri-lang + landagri-theme sobrevivem ao reload', async ({
    page,
  }) => {
    const bp = new BasePage(page);
    await bp.navigate(ROUTES.overview);

    // Fixa EN + dark (dark via storage — toggle tem ciclo light/dark/system).
    await page.getByTestId('language-toggle').click();
    await expect
      .poll(() => page.evaluate(() => localStorage.getItem('landagri-lang')))
      .toBe('en');
    await page.evaluate(() => {
      try {
        localStorage.setItem('landagri-theme', 'dark');
      } catch {
        /* noop */
      }
    });
    await page.reload({ waitUntil: 'networkidle' });
    await expect(page.locator('main')).toBeVisible({
      timeout: TIMEOUTS.pageLoad,
    });

    expect(await page.evaluate(() => localStorage.getItem('landagri-lang'))).toBe(
      'en',
    );
    expect(
      await page.evaluate(() => localStorage.getItem('landagri-theme')),
    ).toBe('dark');
    expect(await htmlLang(page)).toBe('en');
    expect(
      await page.evaluate(() =>
        document.documentElement.classList.contains('dark'),
      ),
    ).toBe(true);
  });
});
