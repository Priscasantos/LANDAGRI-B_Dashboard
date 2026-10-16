import { useState, type ReactNode } from 'react';
import type { LucideIcon } from 'lucide-react';

interface Tab {
  id: string;
  label: string;
  /** Optional Lucide icon rendered before the label (decorative). */
  icon?: LucideIcon;
  content: ReactNode;
}

interface TabsProps {
  tabs: Tab[];
  defaultTab?: string;
  onChange?: (tabId: string) => void;
  /** Accessible label for the tab list (defaults to a generic label). */
  label?: string;
}

export default function Tabs({ tabs, defaultTab, onChange, label = 'Seções' }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id || '');

  const handleTabChange = (tabId: string): void => {
    setActiveTab(tabId);
    onChange?.(tabId);
  };

  return (
    <div>
      {/* Tab headers */}
      <div
        role="tablist"
        aria-label={label}
        className="mb-4 flex snap-x snap-mandatory gap-1 overflow-x-auto border-b border-border [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
      >
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={isActive}
              aria-controls={`tabpanel-${tab.id}`}
              id={`tab-${tab.id}`}
              tabIndex={isActive ? 0 : -1}
              onClick={() => handleTabChange(tab.id)}
              onKeyDown={(event) => {
                if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
                  event.preventDefault();
                  const index = tabs.findIndex((t) => t.id === activeTab);
                  const delta = event.key === 'ArrowRight' ? 1 : -1;
                  const next = tabs[(index + delta + tabs.length) % tabs.length];
                  if (next) handleTabChange(next.id);
                }
              }}
              className={`inline-flex min-h-[44px] shrink-0 snap-start items-center gap-1.5 border-b-2 -mb-px px-4 py-2.5 text-sm whitespace-nowrap transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary ${
                isActive
                  ? 'border-primary font-semibold text-primary'
                  : 'border-transparent font-normal text-fg-muted hover:border-border hover:text-fg'
              }`}
            >
              {tab.icon ? (
                <tab.icon size={15} aria-hidden="true" className="shrink-0" />
              ) : null}
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab content */}
      <div
        role="tabpanel"
        id={`tabpanel-${activeTab}`}
        aria-labelledby={`tab-${activeTab}`}
      >
        {tabs.find((t) => t.id === activeTab)?.content}
      </div>
    </div>
  );
}
