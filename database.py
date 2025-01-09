from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker, relationship, declarative_base, Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
import os
from typing import Optional, List, Iterable

# Use environment variable for database URL with a default fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sessions.db")

# Error handling for database connection
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except SQLAlchemyError as e:
    print(f"Database connection error: {e}")
    raise

Base = declarative_base()

class Credentials(Base):
    __tablename__ = "credentials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_uri: Mapped[str] = mapped_column(Text, nullable=False)
    client_id: Mapped[str] = mapped_column(Text, nullable=False)
    client_secret: Mapped[str] = mapped_column(Text, nullable=False)
    scopes: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    sessions: Mapped[List["Session"]] = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Credentials(id={self.id}, client_id={self.client_id})>"

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("credentials.id", ondelete="CASCADE"), nullable=False)
    session_token: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    user: Mapped["Credentials"] = relationship("Credentials", back_populates="sessions")

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id})>"

    @property
    def is_expired(self) -> bool:
        return bool(datetime.now(timezone.utc) > self.expires_at)

def create_db_and_tables():
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as e:
        print(f"Error creating database tables: {e}")
        raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility function for session cleanup
def cleanup_expired_sessions(db: SQLAlchemySession) -> int:
    try:
        result = db.query(Session).filter(Session.expires_at < datetime.utcnow()).delete()
        db.commit()
        return result
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error cleaning up expired sessions: {e}")
        raise
