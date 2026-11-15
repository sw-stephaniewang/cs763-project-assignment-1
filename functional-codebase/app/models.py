# Stack: Python, SQLAlchemy, PostgreSQL
# Tool: GitHub Copilot Agent mode
# Prompt summary: Define the database models for posts, comments,
# and the associations that link projects to courses and labs.
# Estimated AI contribution: 80%
# Human verification: I ran the integration tests covering saved posts,
# nested replies, and timelines that include associated projects.


from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DiscussionPost(Base):
    __tablename__ = "discussion_posts"

    post_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    project_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True, index=True)
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Project Update Blogs",
    )
    scope_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="project",
    )
    scope_id: Mapped[UUID] = mapped_column(Uuid, nullable=False, index=True)
    author_handle: Mapped[str | None] = mapped_column(String(100), nullable=True)
    moderation_state: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="active",
        server_default="active",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class DiscussionComment(Base):
    __tablename__ = "discussion_comments"

    comment_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    post_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("discussion_posts.post_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_comment_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("discussion_comments.comment_id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    author_handle: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    moderation_state: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="active",
        server_default="active",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ProjectCourseAssociation(Base):
    __tablename__ = "project_course_associations"

    project_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    course_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)


class ProjectLabAssociation(Base):
    __tablename__ = "project_lab_associations"

    project_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    lab_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)
