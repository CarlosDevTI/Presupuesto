import { useMemo, useState } from "react";

import { HierarchyNode } from "types/budget";
import { formatCompactMoney, formatPercent, statusClasses } from "utils/format";

import { SectionCard } from "./SectionCard";

interface HierarchyTableProps {
  nodes: HierarchyNode[];
}

interface FlatRow {
  node: HierarchyNode;
  depth: number;
}

export function HierarchyTable({ nodes }: HierarchyTableProps) {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const rows = useMemo(() => flattenNodes(nodes, expandedRows), [nodes, expandedRows]);

  const toggleRow = (id: string) => {
    setExpandedRows((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <SectionCard title="Detalle por cuenta" subtitle="Todos los nodos inician colapsados para facilitar el drill-down" className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-xs uppercase tracking-[0.2em] text-slate-500">
              <th className="pb-3">Cuenta</th>
              <th className="pb-3">Concepto</th>
              <th className="pb-3 text-right">Proyectado</th>
              <th className="pb-3 text-right">Ejecutado</th>
              <th className="pb-3 text-right">Variacion</th>
              <th className="pb-3 text-right">% ejec.</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(({ node, depth }) => {
              const hasChildren = node.children.length > 0;
              const isExpanded = expandedRows.has(node.id);
              return (
                <tr key={node.id} className="border-b border-slate-100 last:border-b-0">
                  <td className="py-4 text-slate-600">
                    <button
                      type="button"
                      onClick={() => hasChildren && toggleRow(node.id)}
                      className="flex items-center gap-2"
                      style={{ paddingLeft: `${depth * 16}px` }}
                    >
                      <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-slate-100 text-slate-500">
                        {hasChildren ? (isExpanded ? "-" : "+") : "•"}
                      </span>
                      {node.account_code}
                    </button>
                  </td>
                  <td className="py-4 font-medium text-ink">{node.account_name}</td>
                  <td className="py-4 text-right text-slate-600">{formatCompactMoney(node.projected)}</td>
                  <td className="py-4 text-right text-slate-600">{formatCompactMoney(node.executed)}</td>
                  <td className={`py-4 text-right font-semibold ${node.variance_value > 0 ? "text-rose-600" : "text-emerald-600"}`}>
                    {formatCompactMoney(node.variance_value)}
                  </td>
                  <td className="py-4 text-right">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusClasses(node.status)}`}>
                      {formatPercent(node.execution_pct)}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </SectionCard>
  );
}

function flattenNodes(nodes: HierarchyNode[], expandedRows: Set<string>, depth = 0): FlatRow[] {
  return nodes.flatMap((node) => {
    const current: FlatRow = { node, depth };
    if (!node.children.length || !expandedRows.has(node.id)) {
      return [current];
    }
    return [current, ...flattenNodes(node.children, expandedRows, depth + 1)];
  });
}
