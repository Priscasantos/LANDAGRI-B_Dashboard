import { Moon, Sun, Monitor } from 'lucide-react';
import { useTheme, useEffectiveTheme } from '../../hooks/use-theme';

/** Ciclo do toggle: fixa a aparência atual, depois alterna, depois sistema. */
const NEXT: Record<'light' | 'dark' | 'system', 'light' | 'dark' | 'system'> = {
  system: 'light',
  light: 'dark',
  dark: 'system',
};

/**
 * Mode toggle com `system` (adaptado do `mode-toggle.tsx` da referência).
 * Sem Button/circular-transition da referência: <button> nativo + lucide.
 * Rótulo segue a aparência efetiva (claro → "escuro", escuro → "claro"),
 * com sufixo `(sistema)` quando o modo é automático. Reversível.
 */
export default function ThemeToggle(): React.JSX.Element {
  const { theme, setTheme } = useTheme();
  const effective = useEffectiveTheme();

  const current: 'light' | 'dark' | 'system' =
    theme === 'light' || theme === 'dark' || theme === 'system'
      ? theme
      : 'system';

  const baseLabel =
    effective === 'dark' ? 'Ativar modo claro' : 'Ativar modo escuro';
  const label = current === 'system' ? `${baseLabel} (sistema)` : baseLabel;
  const Icon = current === 'system' ? Monitor : effective === 'dark' ? Sun : Moon;

  return (
    <button
      type="button"
      data-testid="theme-toggle"
      onClick={() => setTheme(NEXT[current])}
      aria-label={label}
      title={`Tema atual: ${current} (${effective}) — ${baseLabel}`}
      className="flex items-center justify-center w-9 h-9 rounded-lg
        bg-transparent hover:bg-surface-hover
        text-fg-secondary
        transition-all duration-200
        focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      <Icon
        size={18}
        aria-hidden="true"
        className="transition-transform duration-300 hover:scale-110"
      />
    </button>
  );
}

/** Alias compatível com o nome da referência (`mode-toggle.tsx`). */
export const ModeToggle = ThemeToggle;
