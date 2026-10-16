import { MODULE_ACCENT, type ModuleName } from '../types/theme';

interface ModuleHeaderProps {
  moduleName: ModuleName;
  title: string;
  subtitle: string;
}

/**
 * @deprecated Fase 1 shell SaaS: page titles moved to `BaseLayout`
 * (`App.tsx` passes `title`/`description` from the route table).
 * This component is kept for backward compatibility and renders a
 * plain card — `MODULE_ACCENT` is used as a section accent only
 * (border/text), never a full-bleed gradient background.
 */
export default function ModuleHeader({ moduleName, title, subtitle }: ModuleHeaderProps) {
  const accent = MODULE_ACCENT[moduleName];

  return (
    <div
      className="rounded-xl border border-border bg-card p-5 mb-6 border-l-4"
      style={{ borderLeftColor: accent }}
    >
      <h1 className="text-3xl md:text-4xl font-bold m-0 text-foreground">{title}</h1>
      <p className="mt-2 text-base md:text-lg italic text-muted-foreground">{subtitle}</p>
    </div>
  );
}
