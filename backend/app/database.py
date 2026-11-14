"""SQLAlchemy engine, session factory, and declarative base.

Uses SQLite for the demo. Swap ``database_url`` for PostgreSQL in production.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # SQLite only
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Shared base for every ORM model."""


def init_db() -> None:
    """Create all tables that don't exist yet and run lightweight migrations."""
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        from sqlalchemy import inspect, text
        inspector = inspect(engine)
        if "scribe_sessions" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("scribe_sessions")]
            if "template_key" not in columns:
                conn.execute(text(
                    "ALTER TABLE scribe_sessions ADD COLUMN template_key VARCHAR(40) DEFAULT 'comprehensive_exam'"
                ))
                conn.commit()
