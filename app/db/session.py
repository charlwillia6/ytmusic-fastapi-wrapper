from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.db.models import Base
from alembic import command
from alembic.config import Config
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Handle special case for SQLite
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine: Engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine: Engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables() -> None:
    """Create database and tables."""
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 

def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
