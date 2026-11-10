from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import DATABASE_URL
args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def sqlite_settings(conn, record):
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.execute("PRAGMA journal_mode=WAL")
        cur.close()
class Base(DeclarativeBase):
    pass

def ensure_transaction_cashback_status_column(bind=engine):
    if "transactions" not in inspect(bind).get_table_names():
        return
    columns = {column["name"] for column in inspect(bind).get_columns("transactions")}
    if "cashback_status" not in columns:
        with bind.begin() as connection:
            connection.execute(
                text("ALTER TABLE transactions ADD COLUMN cashback_status VARCHAR(64)")
            )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
