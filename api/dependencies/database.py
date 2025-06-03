from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
from api.config.settings import config
from api.utils.db import db_utils

# Create database engine
engine = create_engine(config.DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    Usage with FastAPI:
    
    @app.get("/items/")
    def read_items(db: Session = Depends(get_db)):
        ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_sqlite_connection():
    """
    Get raw SQLite connection from utils.
    For operations that need direct SQLite access.
    """
    return db_utils.get_connection()