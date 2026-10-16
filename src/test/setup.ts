import '@testing-library/jest-dom';

// Trivial, test-only, reversible: some jsdom versions in this toolchain
// expose no `localStorage`. Provide a minimal in-memory stub so theme
// tests (ThemeContext/ThemeToggle) can run. Guarded — never overrides a
// real implementation.
if (typeof globalThis.localStorage === 'undefined') {
  const store = new Map<string, string>();
  Object.defineProperty(globalThis, 'localStorage', {
    value: {
      getItem: (key: string) => (store.has(key) ? store.get(key)! : null),
      setItem: (key: string, value: string) => void store.set(key, String(value)),
      removeItem: (key: string) => void store.delete(key),
      clear: () => store.clear(),
      get length() {
        return store.size;
      },
      key: (index: number) => Array.from(store.keys())[index] ?? null,
    } satisfies Storage,
    configurable: true,
    writable: true,
  });
}
