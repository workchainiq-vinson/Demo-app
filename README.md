# Bio Green HR & Payroll System

A hybrid HR and Payroll system for **Bio Green Processing and Manufacturing Inc.**, supporting daily-wage (REGULAR), piece-rate (PAKYAW), and MIXED employees. Handles attendance/lateness, overtime, night shift differential, holiday and rest-day premiums, 2026 Philippine statutory deductions (SSS, PhilHealth, Pag-IBIG), and PDF payslip generation.

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite
- **PDF Generation**: ReportLab
- **Frontend**: React (Vite), TypeScript, Tailwind CSS, Lucide React, React Router, Axios

## Project Structure

```
backend/
  app/
    models/       # SQLAlchemy models (Employee, Shift, Attendance, Pakyaw, Holiday, Payroll)
    schemas/       # Pydantic request/response schemas
    services/      # Payroll calculation engine (lateness, OT, NSD, holidays, statutory deductions)
    routers/       # FastAPI REST endpoints
    pdf/           # ReportLab payslip generator
    main.py        # FastAPI app entrypoint
  seeder.py        # Seeds Pakyaw task catalog + 2026 PH holidays
  requirements.txt
frontend/
  src/
    api/           # Axios client + typed API calls
    components/    # Layout / sidebar
    pages/         # Employee Directory, Attendance, Pakyaw Entry, Payroll Generation
```

## Prerequisites

- Python 3.11 (newer versions may lack prebuilt wheels for some pinned dependencies)
- Node.js 18+

## Backend Setup

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seeder.py                # creates bio_green.db and seeds Pakyaw tasks + 2026 holidays
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Interactive docs are available at `http://127.0.0.1:8000/docs`.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173` and expects the backend to be running at `http://127.0.0.1:8000` (CORS is already configured for this origin).

## Typical Workflow

1. **Employees** — create shifts (via API or `/docs`) and add employees, assigning employment type, daily rate, rest day, and default shift.
2. **Attendance** — log daily time in/out per employee; lateness, undertime, and night shift differential minutes are computed automatically from the assigned shift. Approve overtime separately (only approved OT is paid).
3. **Pakyaw Entry** — log piece-rate output individually, or use Group Entry to split a team's total output equally.
4. **Payroll** — pick a cutoff date range, choose whether to apply statutory deductions, and generate a payroll run. Download a PDF payslip per employee from the resulting table.

## Notes

- The PDF payslip generator uses the literal prefix `"PHP "` instead of the `₱` glyph to avoid Unicode font crashes in ReportLab's default fonts.
- Statutory deduction brackets (SSS, PhilHealth, Pag-IBIG) reflect the 2026 rates as specified; verify against official issuances before production use.
- 2026 special non-working holiday dates in `seeder.py` are best-effort placeholders pending the official Malacañang proclamation.
- SQLite is used for local development; models avoid SQLite-specific types so migrating to PostgreSQL only requires changing the `SQLALCHEMY_DATABASE_URL` in `backend/app/database.py`.
