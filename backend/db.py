from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, DeclarativeBase
import os

class Base(DeclarativeBase):
    pass

def _get_db_url():
    url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL") or os.getenv("SQLITE_PATH")
    if url:
        return url
    project_root = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    db_file = os.path.join(data_dir, "redink.db")
    db_uri = "sqlite:///" + db_file.replace("\\", "/")
    return db_uri

_url = _get_db_url()
if _url.startswith("sqlite"):
    engine = create_engine(_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(_url, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))
