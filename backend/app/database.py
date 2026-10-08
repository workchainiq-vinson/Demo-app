from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./bio_green.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# (table, column, DDL type/constraints). create_all() never alters an existing
# table, so a column added to a model after a database already exists must be
# added here or every query touching that table fails on the old schema.
ADDITIVE_COLUMNS = [
    ("employees", "employment_status", "VARCHAR(12) NOT NULL DEFAULT 'REGULAR'"),
]


def run_additive_migrations(bind=engine) -> None:
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())
    with bind.begin() as connection:
        for table, column, ddl in ADDITIVE_COLUMNS:
            if table not in existing_tables:
                continue
            existing_columns = {c["name"] for c in inspector.get_columns(table)}
            if column not in existing_columns:
                connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
