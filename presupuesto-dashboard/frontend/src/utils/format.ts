import { StatusTone } from "types/budget";

const moneyFormatter = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

const compactFormatter = new Intl.NumberFormat("es-CO", {
  notation: "compact",
  maximumFractionDigits: 1,
});

export function formatMoney(value: number): string {
  return moneyFormatter.format(value);
}

export function formatCompactMoney(value: number): string {
  return `$${compactFormatter.format(value)}`;
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function statusLabel(status: StatusTone): string {
  if (status === "green") return "Controlado";
  if (status === "yellow") return "Atencion";
  return "Alerta";
}

export function statusClasses(status: StatusTone): string {
  if (status === "green") return "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200";
  if (status === "yellow") return "bg-amber-50 text-amber-700 ring-1 ring-amber-200";
  return "bg-rose-50 text-rose-700 ring-1 ring-rose-200";
}
