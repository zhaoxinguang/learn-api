from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    # --- 下面是连接池扩容 ---
    pool_size=20,        # 平时保持 20 个连接
    max_overflow=30,     # 高峰期允许额外开出 30 个（最多 50 个）
    pool_timeout=10,     # 拿不到连接最多等 10 秒
    pool_recycle=1800,   # 连接 30 分钟回收一次
)

def sqlite_pragmas(dbapi_connection, connection_record):
    cur = dbapi_connection.cursor()
    cur.execute("PRAGMA journal_mode=WAL")
    cur.execute("PRAGMA busy_timeout=5000")
    cur.execute("PRAGMA foreign_keys=ON")
    cur.close()
    
event.listen(engine, "connect", sqlite_pragmas)
# 开启 WAL 模式（提升读写并发）
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=5000") # 遇到写锁最多等 5 秒
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()