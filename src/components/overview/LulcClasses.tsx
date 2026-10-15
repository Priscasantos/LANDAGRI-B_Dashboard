import { LULC_CLASS_COLORS } from '../../types/theme';
import type { DetailedProduct } from '../../types/initiative';

interface LulcClassesProps {
  classification: string | DetailedProduct[];
}

function getColorForClass(className: string): string {
  // Match by keyword
  const lower = className.toLowerCase();
  for (const [key, color] of Object.entries(LULC_CLASS_COLORS)) {
    if (lower.includes(key.toLowerCase())) return color;
  }
  return '#94a3b8'; // default gray
}

/**
 * Classification badges nos tokens canônicos (`bg-muted`/`border-border`):
 * a cor da classe vira um dot decorativo (`aria-hidden`), não fundo
 * chapado — legível em light/dark e com wrap limpo (`flex-wrap`).
 */
function ClassBadge({ name }: { name: string }): React.JSX.Element {
  return (
    <span className="inline-flex min-w-0 items-center gap-1.5 rounded-full border border-border bg-muted px-2.5 py-0.5 text-xs font-medium text-foreground">
      <span
        aria-hidden="true"
        className="size-2 shrink-0 rounded-full"
        style={{ backgroundColor: getColorForClass(name) }}
      />
      <span className="truncate">{name}</span>
    </span>
  );
}
function parseClassLegend(legend: string): string[] {
  try {
    const parsed = JSON.parse(legend);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    // Fallback: split by comma
    return legend.split(',').map((s) => s.trim()).filter(Boolean);
  }
}

export default function LulcClasses({ classification }: LulcClassesProps) {
  // Handle detailed products
  if (Array.isArray(classification) && classification.length > 0) {
    return (
      <div className="space-y-4">
        {classification.map((product, idx) => (
          <div key={idx} className="p-3 bg-surface-alt rounded-lg border border-border">
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold text-fg">{product.product_name}</span>
              <span className="text-xs px-2 py-0.5 rounded-full border border-border bg-muted text-muted-foreground">
                {product.product_type}
              </span>
            </div>
            {product.accuracy > 0 && (
              <div className="text-xs text-fg-secondary mb-2">Accuracy: {product.accuracy}%</div>
            )}
            <div className="flex flex-wrap gap-1.5">
              {parseClassLegend(product.class_legend).map((cls, i) => (
                <ClassBadge key={i} name={cls} />
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Handle simple class legend string
  if (typeof classification === 'string' && classification) {
    const classes = parseClassLegend(classification);
    if (classes.length === 0) {
      return <p className="text-sm text-fg-muted italic">No classification data available</p>;
    }
    return (
      <div className="flex flex-wrap gap-2">
        {classes.map((cls, idx) => (
          <span
            key={idx}
            className="inline-flex min-w-0 items-center gap-1.5 rounded-full border border-border bg-muted px-3 py-1 text-sm font-medium text-foreground"
          >
            <span
              aria-hidden="true"
              className="size-2.5 shrink-0 rounded-full"
              style={{ backgroundColor: getColorForClass(cls) }}
            />
            <span className="truncate">{cls}</span>
          </span>
        ))}
      </div>
    );
  }

  return <p className="text-sm text-fg-muted italic">No classification data available</p>;
}
