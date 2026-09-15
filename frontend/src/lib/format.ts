export const formatPeso = (value: string | number): string => {
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (Number.isNaN(num)) return "₱0.00";
  return `₱${num.toLocaleString("en-PH", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

export const DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
