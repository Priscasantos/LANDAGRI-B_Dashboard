import { useEffect, useId, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import { commandIndex } from '../../config/routes';
import { useT } from '../../i18n/LanguageContext';
import { pt } from '../../i18n/dictionaries/pt';
import { en } from '../../i18n/dictionaries/en';
import {
  filterCommandEntries,
  loadRecents,
  orderWithRecents,
  recordRecent,
  type PaletteEntry,
} from '../../lib/commandSearch';

interface CommandSearchProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

/**
 * Command palette (adapted from the reference `command-search.tsx`).
 * Indexes the 5 module routes + initiative/agricultural sub-routes
 * (`commandIndex` in `src/config/routes.tsx`). Dependency-free:
 * a fixed dialog with listbox semantics and full keyboard support.
 * Fase 1 i18n: rótulos via chaves `nav`.
 * Fase 3 IA enxuta: busca casa PT + EN + url + sinônimos (`keywords`,
 * insensível a acentos) e sugere recentes primeiro com query vazia.
 */
export function CommandSearch({ open, onOpenChange }: CommandSearchProps): React.JSX.Element | null {
  const navigate = useNavigate();
  const [query, setQuery] = useState<string>('');
  const [activeIndex, setActiveIndex] = useState<number>(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const listId = useId();
  const recentHeadingId = useId();
  const { t: tNav } = useT('nav');
  const { t } = useT('common');

  const entries: PaletteEntry[] = useMemo(
    () =>
      commandIndex.map((entry) => ({
        url: entry.url,
        title: tNav(entry.titleKey),
        group: tNav(entry.groupKey),
        ptTitle: pt.nav[entry.titleKey] ?? entry.title,
        enTitle: en.nav[entry.titleKey] ?? entry.title,
        enGroup: en.nav[entry.groupKey] ?? entry.group,
        keywords: entry.keywords,
      })),
    [tNav],
  );

  const recentUrls = useMemo(() => {
    if (!open) return [];
    try {
      return loadRecents(localStorage);
    } catch {
      return [];
    }
  }, [open ]);

  const results = useMemo(() => {
    const filtered = filterCommandEntries(entries, query);
    if (query.trim()) return filtered;
    return orderWithRecents(filtered, recentUrls);
  }, [query, entries, recentUrls]);

  const showRecents = query.trim() === '' && recentUrls.length > 0 && results.length > 0;
  const recentCount = showRecents
    ? results.filter((entry) => recentUrls.includes(entry.url)).length
    : 0;

  useEffect(() => {
    // Focus after paint so the dialog exists in the DOM.
    const frame = requestAnimationFrame(() => inputRef.current?.focus());
    return () => cancelAnimationFrame(frame);
  }, []);

  const handleQueryChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setQuery(event.target.value);
    setActiveIndex(0);
  };

  if (!open) return null;

  const go = (url: string): void => {
    try {
      recordRecent(localStorage, url);
    } catch {
      /* private mode: segue sem persistir */
    }
    onOpenChange(false);
    navigate(url);
  };

  const handleKeyDown = (event: React.KeyboardEvent): void => {
    if (event.key === 'Escape') {
      onOpenChange(false);
    } else if (event.key === 'ArrowDown') {
      event.preventDefault();
      setActiveIndex((prev) => (results.length === 0 ? 0 : (prev + 1) % results.length));
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      setActiveIndex((prev) =>
        results.length === 0 ? 0 : (prev - 1 + results.length) % results.length,
      );
    } else if (event.key === 'Enter') {
      const target = results[activeIndex];
      if (target) go(target.url);
    }
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-start justify-center px-4 pt-[15vh]">
      <div
        className="absolute inset-0 bg-overlay"
        onClick={() => onOpenChange(false)}
        aria-hidden="true"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={t('searchTitle')}
        className="relative w-full max-w-lg overflow-hidden rounded-xl border border-border bg-surface shadow-lg"
      >
        <div className="flex items-center gap-2 border-b border-border px-3">
          <Search size={16} aria-hidden="true" className="shrink-0 text-fg-muted" />
          <input
            ref={inputRef}
            type="text"
            role="combobox"
            aria-expanded="true"
            aria-controls={listId}
            aria-autocomplete="list"
            aria-label={t('searchLabel')}
            placeholder={t('searchPlaceholder')}
            value={query}
            onChange={handleQueryChange}
            onKeyDown={handleKeyDown}
            className="h-12 w-full bg-transparent text-sm text-fg outline-none placeholder:text-fg-muted"
          />
          <kbd className="hidden shrink-0 rounded border border-border bg-surface-alt px-1.5 py-0.5 text-[11px] text-fg-muted sm:inline-block">
            esc
          </kbd>
        </div>
        {showRecents && (
          <p id={recentHeadingId} className="px-4 pt-3 pb-1 text-[11px] font-semibold tracking-wider text-fg-muted uppercase">
            {t('recentTitle')}
          </p>
        )}
        <ul
          id={listId}
          role="listbox"
          aria-label={t('searchResults')}
          className="max-h-72 overflow-y-auto p-1.5"
        >
          {results.length === 0 && (
            <li className="px-3 py-6 text-center text-sm text-fg-secondary">
              {t('searchEmpty', { query })}
            </li>
          )}
          {results.map((entry, index) => (
            <li key={entry.url} role="option" aria-selected={index === activeIndex}>
              <button
                type="button"
                onMouseEnter={() => setActiveIndex(index)}
                onClick={() => go(entry.url)}
                className={`flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary ${
                  index === activeIndex ? 'bg-surface-hover' : ''
                }`}
              >
                <span className="min-w-0 flex-1 truncate font-medium text-fg">
                  {entry.title}
                </span>
                {showRecents && index < recentCount && (
                  <span className="shrink-0 rounded-full bg-surface-alt px-2 py-0.5 text-[11px] text-fg-muted">
                    {t('recentTitle')}
                  </span>
                )}
                <span className="shrink-0 text-xs text-fg-muted">{entry.group}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

interface SearchTriggerProps {
  onClick: () => void;
}

export function SearchTrigger({ onClick }: SearchTriggerProps): React.JSX.Element {
  const { t } = useT('common');
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={t('searchShortcut')}
      className="relative flex h-9 w-9 items-center justify-center gap-2 rounded-full border border-border bg-surface px-0 text-sm font-normal text-fg-muted shadow-sm transition-colors hover:bg-surface-hover hover:text-fg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary sm:w-full sm:justify-start sm:px-3 md:w-44 lg:w-60"
    >
      <Search size={15} aria-hidden="true" />
      <span className="hidden sm:inline">{t('searchButton')}</span>
      <kbd className="absolute top-1/2 right-1.5 hidden -translate-y-1/2 rounded border border-border bg-surface-alt px-1.5 py-0.5 text-[11px] sm:inline-block">
        ⌘K
      </kbd>
    </button>
  );
}
