import type { DeductionType, EmploymentStatus } from "../api/types";

export const formatPeso = (value: string | number): string => {
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (Number.isNaN(num)) return "₱0.00";
  return `₱${num.toLocaleString("en-PH", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

export const DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

export const EMPLOYMENT_STATUS_LABELS: Record<EmploymentStatus, string> = {
  REGULAR: "Regular",
  PROBATIONARY: "Probationary",
  ON_CALL: "On-call",
};

export const EMPLOYMENT_STATUSES = Object.keys(EMPLOYMENT_STATUS_LABELS) as EmploymentStatus[];

export const DEDUCTION_LABELS: Record<DeductionType, string> = {
  SSS_LOAN: "SSS Loan",
  PAGIBIG_LOAN: "Pag-IBIG Loan",
  MP2: "MP2",
  CALAMITY_LOAN: "Calamity Loan",
  PETTY_CASH: "Petty Cash",
};

export const DEDUCTION_TYPES = Object.keys(DEDUCTION_LABELS) as DeductionType[];
