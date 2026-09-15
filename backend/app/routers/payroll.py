import json
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee import Employee
from app.models.payroll import PayrollPayslip, PayrollRun
from app.pdf.payslip_generator import generate_payslip_pdf
from app.schemas.payroll import PayrollGenerateRequest, PayrollRunRead, PayslipRead
from app.services.payroll_service import calculate_payroll_for_cutoff

router = APIRouter(prefix="/payroll", tags=["payroll"])


def _decimal_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    return str(obj)


def _to_payslip_read(payslip: PayrollPayslip, employee: Employee) -> PayslipRead:
    return PayslipRead(
        id=payslip.id,
        payroll_run_id=payslip.payroll_run_id,
        employee_id=payslip.employee_id,
        employee_name=f"{employee.first_name} {employee.last_name}",
        gross_pay=payslip.gross_pay,
        sss_deduction=payslip.sss_deduction,
        philhealth_deduction=payslip.philhealth_deduction,
        pagibig_deduction=payslip.pagibig_deduction,
        total_deductions=payslip.total_deductions,
        net_pay=payslip.net_pay,
        breakdown=json.loads(payslip.breakdown) if payslip.breakdown else {},
    )


@router.post("/generate", response_model=PayrollRunRead, status_code=201)
def generate_payroll(payload: PayrollGenerateRequest, db: Session = Depends(get_db)):
    query = db.query(Employee).filter(Employee.is_active == True)  # noqa: E712
    if payload.employee_ids:
        query = query.filter(Employee.id.in_(payload.employee_ids))
    employees = query.all()
    if not employees:
        raise HTTPException(status_code=400, detail="No matching active employees found")

    run = PayrollRun(
        cutoff_start=payload.cutoff_start,
        cutoff_end=payload.cutoff_end,
        apply_statutory_deductions=payload.apply_statutory_deductions,
        status="COMPLETED",
    )
    db.add(run)
    db.flush()

    payslips_read = []
    for employee in employees:
        result = calculate_payroll_for_cutoff(
            db,
            employee.id,
            payload.cutoff_start,
            payload.cutoff_end,
            apply_statutory=payload.apply_statutory_deductions,
        )
        breakdown_json = json.dumps(result["breakdown"], default=_decimal_default)
        payslip = PayrollPayslip(
            payroll_run_id=run.id,
            employee_id=employee.id,
            gross_pay=result["gross_pay"],
            sss_deduction=result["sss_deduction"],
            philhealth_deduction=result["philhealth_deduction"],
            pagibig_deduction=result["pagibig_deduction"],
            total_deductions=result["total_deductions"],
            net_pay=result["net_pay"],
            breakdown=breakdown_json,
        )
        db.add(payslip)
        db.flush()
        payslips_read.append(_to_payslip_read(payslip, employee))

    db.commit()

    return PayrollRunRead(
        id=run.id,
        cutoff_start=run.cutoff_start,
        cutoff_end=run.cutoff_end,
        apply_statutory_deductions=run.apply_statutory_deductions,
        generated_at=run.generated_at,
        status=run.status,
        payslips=payslips_read,
    )


@router.get("/runs", response_model=list[PayrollRunRead])
def list_payroll_runs(db: Session = Depends(get_db)):
    runs = db.query(PayrollRun).order_by(PayrollRun.generated_at.desc()).all()
    result = []
    for run in runs:
        payslips_read = [_to_payslip_read(p, p.employee) for p in run.payslips]
        result.append(
            PayrollRunRead(
                id=run.id,
                cutoff_start=run.cutoff_start,
                cutoff_end=run.cutoff_end,
                apply_statutory_deductions=run.apply_statutory_deductions,
                generated_at=run.generated_at,
                status=run.status,
                payslips=payslips_read,
            )
        )
    return result


@router.get("/runs/{run_id}", response_model=PayrollRunRead)
def get_payroll_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(PayrollRun).filter(PayrollRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")
    payslips_read = [_to_payslip_read(p, p.employee) for p in run.payslips]
    return PayrollRunRead(
        id=run.id,
        cutoff_start=run.cutoff_start,
        cutoff_end=run.cutoff_end,
        apply_statutory_deductions=run.apply_statutory_deductions,
        generated_at=run.generated_at,
        status=run.status,
        payslips=payslips_read,
    )


@router.get("/payslips/{payslip_id}/pdf")
def download_payslip_pdf(payslip_id: int, db: Session = Depends(get_db)):
    payslip = db.query(PayrollPayslip).filter(PayrollPayslip.id == payslip_id).first()
    if not payslip:
        raise HTTPException(status_code=404, detail="Payslip not found")

    employee = payslip.employee
    run = payslip.payroll_run
    breakdown = json.loads(payslip.breakdown) if payslip.breakdown else {}

    pdf_buffer = generate_payslip_pdf(employee, run, payslip, breakdown)
    filename = f"payslip_{employee.employee_code}_{run.cutoff_start}_{run.cutoff_end}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
