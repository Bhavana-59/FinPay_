import os
from pathlib import Path
from sqlalchemy.engine import make_url
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
database_url = make_url(os.getenv("DATABASE_URL", "sqlite:///./finpay.db"))
if database_url.get_backend_name() == "sqlite":
    database_path = database_url.database
    if database_path and database_path != ":memory:" and not Path(database_path).is_absolute():
        database_url = database_url.set(
            database=str((Path(__file__).resolve().parents[2] / database_path).resolve())
        )
DATABASE_URL = database_url.render_as_string(hide_password=False)
JWT_SECRET = os.getenv("JWT_SECRET", "development-only-change-me")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))
