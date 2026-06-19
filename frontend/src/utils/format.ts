const currency = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

export function formatCurrency(value: string | number): string {
  const num = typeof value === "string" ? Number(value) : value;
  return currency.format(Number.isFinite(num) ? num : 0);
}

export function formatDate(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}
