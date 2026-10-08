export type EmploymentType = "REGULAR" | "PAKYAW" | "MIXED";
export type EmploymentStatus = "REGULAR" | "PROBATIONARY" | "ON_CALL";
export type DeductionType = "SSS_LOAN" | "PAGIBIG_LOAN" | "MP2" | "CALAMITY_LOAN" | "PETTY_CASH";
export type HolidayType = "REGULAR" | "SPECIAL_NON_WORKING";

export interface Shift {
  id: number;
  name: string;
  start_time: string; // "HH:MM:SS"
  end_time: string;
  grace_period_minutes: number;
}

export interface Employee {
  id: number;
  employee_code: string;
  first_name: string;
  last_name: string;
  department: string | null;
  employment_type: EmploymentType;
  employment_status: EmploymentStatus;
  daily_rate: string;
  rest_day_of_week: number | null;
  default_shift_id: number | null;
  is_active: boolean;
}

export interface EmployeeInput {
  employee_code: string;
  first_name: string;
  last_name: string;
  department: string | null;
  employment_type: EmploymentType;
  employment_status: EmploymentStatus;
  daily_rate: string;
  rest_day_of_week: number | null;
  default_shift_id: number | null;
  is_active: boolean;
}

export interface Attendance {
  id: number;
  employee_id: number;
  date: string;
  time_in: string | null;
  time_out: string | null;
  actual_ot_minutes: number;
  approved_ot_minutes: number;
  nsd_minutes: number;
  late_minutes: number;
  undertime_minutes: number;
  is_rest_day_worked: boolean;
  holiday_id: number | null;
}

export interface AttendanceInput {
  employee_id: number;
  date: string;
  time_in: string | null;
  time_out: string | null;
  is_rest_day_worked: boolean;
  holiday_id: number | null;
}

export interface PakyawCatalogItem {
  id: number;
  task_name: string;
  unit_of_measure: string;
  rate_per_unit: string;
}

export interface PakyawLog {
  id: number;
  employee_id: number;
  pakyaw_catalog_id: number;
  date: string;
  units_completed: string;
  group_batch_id: string | null;
  computed_pay: string;
}

export interface Holiday {
  id: number;
  name: string;
  date: string;
  holiday_type: HolidayType;
}

export interface PayslipBreakdown {
  days_worked: number;
  base_pay: string;
  holiday_premium_pay: string;
  lateness_undertime_deduction: string;
  regular_pay: string;
  ot_pay: string;
  nsd_pay: string;
  pakyaw_pay: string;
  gross_pay: string;
}

export interface Payslip {
  id: number;
  payroll_run_id: number;
  employee_id: number;
  employee_name: string;
  gross_pay: string;
  sss_deduction: string;
  philhealth_deduction: string;
  pagibig_deduction: string;
  other_deductions: string;
  deductions: AppliedDeduction[];
  total_deductions: string;
  net_pay: string;
  breakdown: PayslipBreakdown;
}

export interface PayrollRun {
  id: number;
  cutoff_start: string;
  cutoff_end: string;
  apply_statutory_deductions: boolean;
  generated_at: string | null;
  status: string;
  payslips: Payslip[];
}

export interface EmployeeCounts {
  total: number;
  active: number;
  inactive: number;
  by_type: Record<EmploymentType, number>;
}

export interface LatestPayrollRunSummary {
  id: number;
  cutoff_start: string;
  cutoff_end: string;
  gross_pay: number;
  total_deductions: number;
  net_pay: number;
}

export interface PayrollTrendPoint {
  run_id: number;
  cutoff_end: string;
  gross_pay: number;
  net_pay: number;
}

export interface AttendanceSummaryThisMonth {
  late_minutes: number;
  approved_ot_minutes: number;
  nsd_minutes: number;
  days_logged: number;
}

export interface PakyawSummaryThisMonth {
  total_units: number;
  total_pay: number;
}

export interface UpcomingHoliday {
  id: number;
  name: string;
  date: string;
  holiday_type: HolidayType;
}

export interface DashboardSummary {
  employee_counts: EmployeeCounts;
  latest_payroll_run: LatestPayrollRunSummary | null;
  payroll_trend: PayrollTrendPoint[];
  attendance_summary_this_month: AttendanceSummaryThisMonth;
  pakyaw_summary_this_month: PakyawSummaryThisMonth;
  upcoming_holidays: UpcomingHoliday[];
}

export interface AppliedDeduction {
  deduction_type: DeductionType;
  label: string;
  amount: string;
}

export interface EmployeeDeduction {
  id: number;
  employee_id: number;
  deduction_type: DeductionType;
  total_amount: string | null;
  amount_per_cutoff: string;
  remaining_balance: string | null;
  start_date: string;
  is_active: boolean;
}

export interface EmployeeDeductionInput {
  employee_id: number;
  deduction_type: DeductionType;
  total_amount: string | null;
  amount_per_cutoff: string;
  start_date: string;
  is_active: boolean;
}
