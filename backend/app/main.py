from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import attendance, employees, holidays, pakyaw, payroll, shifts

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bio Green HR & Payroll System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)
app.include_router(shifts.router)
app.include_router(attendance.router)
app.include_router(pakyaw.router)
app.include_router(holidays.router)
app.include_router(payroll.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "Bio Green HR & Payroll System"}
