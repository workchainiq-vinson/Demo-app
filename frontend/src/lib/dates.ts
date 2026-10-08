// Date-only helpers built from LOCAL calendar parts. Never use
// `toISOString().slice(0, 10)` for these: it converts to UTC first, so the
// result is off by a day whenever the local date differs from the UTC date
// (every evening west of UTC, every early morning east of it, e.g. Manila).
// `now` is injectable so the behavior can be tested with a fixed clock.

const pad = (n: number): string => String(n).padStart(2, "0");

export const toLocalIso = (d: Date): string => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

export const todayIso = (now: Date = new Date()): string => toLocalIso(now);

export const firstOfMonthIso = (now: Date = new Date()): string =>
  toLocalIso(new Date(now.getFullYear(), now.getMonth(), 1));

// Parses "YYYY-MM-DD" as a local date (the Date constructor handles month and
// year overflow), so there is no UTC round trip to shift the day.
export const addDays = (iso: string, days: number): string => {
  const [year, month, day] = iso.split("-").map(Number);
  return toLocalIso(new Date(year, month - 1, day + days));
};
