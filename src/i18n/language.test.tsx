import { describe, expect, it, beforeEach } from 'vitest';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { getBasename, appRoutes } from '../config/routes';
import { en } from './dictionaries/en';
import { translate } from './index';
import { LanguageProvider, useLanguage, useT } from './LanguageContext';
import { DEFAULT_LOCALE, detectLocale } from './types';

function makeStorage(initial: Record<string, string> = {}): Storage {
  const store = new Map<string, string>(Object.entries(initial));
  return {
    getItem: (key: string) => store.get(key) ?? null,
    setItem: (key: string, value: string) => void store.set(key, String(value)),
    removeItem: (key: string) => void store.delete(key),
    clear: () => store.clear(),
    get length() {
      return store.size;
    },
    key: (index: number) => Array.from(store.keys())[index] ?? null,
  } as Storage;
}

describe('detectLocale (localStorage > navigator > fallback)', () => {
  it('stored locale wins over navigator', () => {
    expect(detectLocale(makeStorage({ 'landagri-lang': 'en' }), 'pt-BR')).toBe('en');
    expect(detectLocale(makeStorage({ 'landagri-lang': 'pt-BR' }), 'en-US')).toBe('pt-BR');
  });

  it('resolves pt* navigator to pt-BR and en* to en', () => {
    expect(detectLocale(makeStorage(), 'pt-PT')).toBe('pt-BR');
    expect(detectLocale(makeStorage(), 'en-GB')).toBe('en');
  });

  it('ignores invalid stored values and unknown navigators (fallback pt-BR)', () => {
    expect(detectLocale(makeStorage({ 'landagri-lang': 'fr' }), 'en-US')).toBe('en');
    expect(detectLocale(makeStorage(), 'fr-FR')).toBe(DEFAULT_LOCALE);
    expect(detectLocale(makeStorage(), undefined)).toBe(DEFAULT_LOCALE);
    expect(detectLocale(makeStorage(), '')).toBe(DEFAULT_LOCALE);
  });
});

describe('translate (fallback pt-BR por chave)', () => {
  it('resolves EN keys when present', () => {
    expect(translate('en', 'nav', 'overview')).toBe('Overview');
    expect(translate('pt-BR', 'nav', 'overview')).toBe('Visão Geral');
  });

  it('falls back to PT when the EN key is missing', () => {
    const table = en.nav as Record<string, string>;
    const backup = table.overview;
    delete table.overview;
    try {
      expect(translate('en', 'nav', 'overview')).toBe('Visão Geral');
    } finally {
      table.overview = backup;
    }
  });

  it('returns the key itself when missing everywhere', () => {
    expect(translate('en', 'nav', 'missing-key' as never)).toBe('missing-key');
  });

  it('interpolates {vars}', () => {
    expect(translate('pt-BR', 'common', 'searchEmpty', { query: 'solo' })).toContain('solo');
  });
});

describe('LanguageProvider (persistência + <html lang>)', () => {
  const KEY = 'landagri-lang';

  beforeEach(() => {
    localStorage.clear();
    document.documentElement.lang = 'pt-BR';
  });

  function Probe(): React.JSX.Element {
    const { locale, toggleLocale } = useLanguage();
    const { t } = useT('nav');
    return (
      <div>
        <span data-testid="locale">{locale}</span>
        <span data-testid="label">{t('overview')}</span>
        <button type="button" onClick={toggleLocale}>
          toggle
        </button>
      </div>
    );
  }

  it('initialises from localStorage and applies <html lang>', () => {
    localStorage.setItem(KEY, 'en');
    render(
      <LanguageProvider>
        <Probe />
      </LanguageProvider>,
    );
    expect(screen.getByTestId('locale')).toHaveTextContent('en');
    expect(screen.getByTestId('label')).toHaveTextContent('Overview');
    expect(document.documentElement.lang).toBe('en');
  });

  it('toggle flips locale, persists and updates <html lang>', () => {
    localStorage.setItem(KEY, 'pt-BR');
    render(
      <LanguageProvider>
        <Probe />
      </LanguageProvider>,
    );
    expect(screen.getByTestId('label')).toHaveTextContent('Visão Geral');

    act(() => {
      fireEvent.click(screen.getByRole('button', { name: 'toggle' }));
    });

    expect(screen.getByTestId('locale')).toHaveTextContent('en');
    expect(localStorage.getItem(KEY)).toBe('en');
    expect(document.documentElement.lang).toBe('en');
    expect(screen.getByTestId('label')).toHaveTextContent('Overview');
  });

  it('defaults to pt-BR outside the provider (testes legados seguem PT)', () => {
    render(<Probe />);
    expect(screen.getByTestId('locale')).toHaveTextContent('pt-BR');
    expect(screen.getByTestId('label')).toHaveTextContent('Visão Geral');
  });
});

describe('Fase 1 guards (basename + chaves de rota)', () => {
  it('getBasename intacto (gh-pages default)', () => {
    expect(getBasename({ VITE_BASENAME: '', DEV: false })).toBe('/LANDAGRI-B_Dashboard');
  });

  it('toda rota tem titleKey/descriptionKey que resolvem ao PT estático', () => {
    for (const route of appRoutes) {
      expect(translate('pt-BR', 'nav', route.titleKey)).toBe(route.title);
      expect(translate('pt-BR', 'nav', route.descriptionKey)).toBe(route.description);
    }
  });
});
