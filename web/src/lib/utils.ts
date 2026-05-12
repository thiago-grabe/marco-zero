import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Formata valor monetário em BRL. Ex: 429629.87 → "R$ 429.629,87" */
export function formatBRL(value: number): string {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
  }).format(value);
}

/** Formata data em pt-BR. Ex: 2029-04-21 → "21/04/2029" */
export function formatDate(dateStr: string | Date): string {
  const d = typeof dateStr === "string" ? new Date(dateStr + "T00:00:00") : dateStr;
  return new Intl.DateTimeFormat("pt-BR").format(d);
}

/** Formata mês e ano. Ex: 2029-04-21 → "abril/2029" */
export function formatMonthYear(dateStr: string | Date): string {
  const d = typeof dateStr === "string" ? new Date(dateStr + "T00:00:00") : dateStr;
  return new Intl.DateTimeFormat("pt-BR", { month: "long", year: "numeric" }).format(d);
}

/** Formata taxa percentual. Ex: 0.009631393 → "0,9631%" */
export function formatRate(rate: number, decimals = 4): string {
  return (rate * 100).toFixed(decimals).replace(".", ",") + "%";
}

/**
 * Gera e faz download de um arquivo CSV.
 * Útil para exportar planilhas de amortização.
 */
export function downloadCSV(filename: string, headers: string[], rows: (string | number)[][]): void {
  const bom = "\uFEFF"; // BOM para Excel abrir com encoding correto
  const sep = ";"; // separador ponto-e-vírgula para locale BR
  const headerLine = headers.join(sep);
  const dataLines = rows.map((row) =>
    row.map((cell) => {
      if (typeof cell === "number") {
        return cell.toFixed(2).replace(".", ","); // formato BR
      }
      return `"${String(cell).replace(/"/g, '""')}"`;
    }).join(sep)
  );
  const csv = bom + [headerLine, ...dataLines].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

/** Usa debounce para reduzir chamadas ao motor nos sliders. */
export function debounce<T extends (...args: Parameters<T>) => ReturnType<T>>(
  fn: T,
  ms: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout>;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}
