from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, DeclarativeBase
import os

class Base(DeclarativeBase):
    pass

def _get_db_url():
    url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL") or os.getenv("SQLITE_PATH")
    if url:
        return url
    
    # 优先使用 /data 目录作为数据库存储位置（Docker环境）
    # 在Windows系统上，直接使用 /data 目录需要管理员权限，且路径语义不同
    import platform
    
    # 检查当前系统是否为Windows
    is_windows = platform.system() == "Windows"
    data_dir = "/data"
    
    try:
        # 对于Windows系统，默认回退到项目根目录的data目录
        if is_windows:
            project_root = os.path.dirname(os.path.dirname(__file__))
            data_dir = os.path.join(project_root, "data")
        else:
            # 非Windows系统（如Linux/Docker），检查/data目录是否存在且可写
            if not os.path.exists(data_dir) or not os.access(data_dir, os.W_OK):
                project_root = os.path.dirname(os.path.dirname(__file__))
                data_dir = os.path.join(project_root, "data")
    except (PermissionError, OSError, AttributeError):
        # 捕获任何可能出现的错误，回退到项目根目录的data目录
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
