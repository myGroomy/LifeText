"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    connect_args={"timeout": 10}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from src.models import Base
    Base.metadata.create_all(bind=engine)
