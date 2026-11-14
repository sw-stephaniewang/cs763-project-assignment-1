# Stack: Python, SQLAlchemy, psycopg, PostgreSQL
# Tool: GitHub Copilot Agent mode
# Prompt summary: Set up the PostgreSQL connection, database sessions,
# and schema initialization for the discussion board.
# Estimated AI contribution: 80%
# Human verification: I started PostgreSQL with Docker Compose and ran
# the integration suite against it. All 7 tests passed.


import os
from collections.abc import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@127.0.0.1:55432/discussion_board"
)


class Base(DeclarativeBase):
    pass


engine = create_engine(
    os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE discussion_posts "
                "ALTER COLUMN project_id DROP NOT NULL, "
                "ADD COLUMN IF NOT EXISTS category VARCHAR(50) NOT NULL "
                "DEFAULT 'Project Update Blogs', "
                "ADD COLUMN IF NOT EXISTS scope_type VARCHAR(20) NOT NULL "
                "DEFAULT 'project', "
                "ADD COLUMN IF NOT EXISTS scope_id UUID, "
                "ADD COLUMN IF NOT EXISTS author_handle VARCHAR(100), "
                "ADD COLUMN IF NOT EXISTS moderation_state VARCHAR(30) "
                "NOT NULL DEFAULT 'active'"
            )
        )
        connection.execute(
            text(
                "UPDATE discussion_posts SET scope_id = project_id "
                "WHERE scope_id IS NULL"
            )
        )
        connection.execute(
            text("ALTER TABLE discussion_posts ALTER COLUMN scope_id SET NOT NULL")
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_discussion_posts_scope_id "
                "ON discussion_posts (scope_id)"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE discussion_comments "
                "ADD COLUMN IF NOT EXISTS moderation_state VARCHAR(30) "
                "NOT NULL DEFAULT 'active'"
            )
        )


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
