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
}

export default function Tabs({ tabs, defaultTab, onChange }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id || '');

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    onChange?.(tabId);
  };

  return (
    <div>
      {/* Tab headers */}
      <div
        className="flex mb-4 overflow-x-auto border-b border-border"
      >
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => handleTabChange(tab.id)}
            className={`inline-flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium whitespace-nowrap transition-all duration-200
              border-b-2 -mb-px`}
            style={{
              borderBottomColor: activeTab === tab.id ? 'var(--color-primary)' : 'transparent',
              color: activeTab === tab.id ? 'var(--color-primary)' : 'var(--color-fg-muted)',
              fontWeight: activeTab === tab.id ? 600 : 400,
            }}
            onMouseEnter={(e) => {
              if (activeTab !== tab.id) {
                e.currentTarget.style.color = 'var(--color-fg)';
                e.currentTarget.style.borderBottomColor = 'var(--color-border)';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== tab.id) {
                e.currentTarget.style.color = 'var(--color-fg-muted)';
                e.currentTarget.style.borderBottomColor = 'transparent';
              }
            }}
          >
            {tab.icon ? (
              <tab.icon size={15} aria-hidden="true" className="shrink-0" />
            ) : null}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div>
        {tabs.find((t) => t.id === activeTab)?.content}
      </div>
    </div>
  );
}
