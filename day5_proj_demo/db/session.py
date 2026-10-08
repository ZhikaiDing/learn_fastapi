from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.settings import settings

def get_engine():
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite"):
        # SQLite 才加这个参数
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False}
        )
    else:
        # Postgres / MySQL 生产库，带连接池
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
    return engine

engine = get_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
