# Stack: Python, FastAPI, SQLAlchemy, PostgreSQL
# Tool: GitHub Copilot Agent mode
# Prompt summary: Build the API for posts, nested comments, search,
# text export, moderation, and course and lab timelines.
# Estimated AI contribution: 80%
# Human verification: I ran the PostgreSQL integration suite locally.
# All 7 tests passed, including moderation and multi-project timelines.

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Response, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db, initialize_database
from app.models import (
    DiscussionComment,
    DiscussionPost,
    ProjectCourseAssociation,
    ProjectLabAssociation,
)
from app.schemas import (
    DiscussionCommentCreate,
    DiscussionCommentResponse,
    DiscussionCommentUpdate,
    DiscussionPostCreate,
    DiscussionPostResponse,
    DiscussionPostUpdate,
    ModerationStatusResponse,
    ModerationUpdate,
    PostCategory,
)

SCOPE_TYPE_BY_URL = {
    "projects": "project",
    "courses": "course",
    "labs": "research_lab",
}


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="Research Blog & Project Discussion Board", lifespan=lifespan)
DatabaseSession = Annotated[Session, Depends(get_db)]


@app.post(
    "/api/v1/discussions/posts",
    response_model=DiscussionPostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_discussion_post(
    post: DiscussionPostCreate,
    db: DatabaseSession,
) -> DiscussionPost:
    saved_post = DiscussionPost(
        category=post.category,
        scope_type=post.scope_type,
        scope_id=post.scope_id,
        project_id=post.project_id,
        author_handle=post.author_handle,
        title=post.title,
        body=post.body,
        tags=post.tags,
    )
    db.add(saved_post)
    db.commit()
    db.refresh(saved_post)
    return saved_post


@app.get(
    "/api/v1/discussions/posts/{post_id}",
    response_model=DiscussionPostResponse,
)
def get_discussion_post(
    post_id: UUID,
    db: DatabaseSession,
) -> DiscussionPost:
    return get_visible_post(post_id, db)


def get_post_or_404(post_id: UUID, db: Session) -> DiscussionPost:
    post = db.get(DiscussionPost, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion post not found",
        )
    return post


def get_visible_post(post_id: UUID, db: Session) -> DiscussionPost:
    post = get_post_or_404(post_id, db)
    if post.moderation_state == "hidden_by_moderator":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion post not found",
        )
    return post


def require_faculty_moderator(moderator_role: str | None) -> None:
    if moderator_role != "faculty":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Faculty moderation privileges are required",
        )


@app.get(
    "/api/v1/discussions/posts",
    response_model=list[DiscussionPostResponse],
)
def list_discussion_posts(
    db: DatabaseSession,
    keyword: str | None = Query(default=None, min_length=1),
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    author_handle: str | None = Query(default=None, min_length=1, max_length=100),
    project_id: UUID | None = None,
    course_id: UUID | None = None,
    lab_id: UUID | None = None,
    category: PostCategory | None = None,
) -> list[DiscussionPost]:
    if created_after is not None and created_after.utcoffset() is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="created_after must include a timezone",
        )
    if created_before is not None and created_before.utcoffset() is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="created_before must include a timezone",
        )
    if (
        created_after is not None
        and created_before is not None
        and created_after > created_before
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="created_after must not be later than created_before",
        )

    statement = select(DiscussionPost).where(
        DiscussionPost.moderation_state != "hidden_by_moderator"
    )
    if keyword is not None:
        statement = statement.where(
            func.lower(DiscussionPost.body).contains(keyword.lower(), autoescape=True)
        )
    if created_after is not None:
        statement = statement.where(DiscussionPost.created_at >= created_after)
    if created_before is not None:
        statement = statement.where(DiscussionPost.created_at <= created_before)
    if author_handle is not None:
        statement = statement.where(DiscussionPost.author_handle == author_handle)
    if project_id is not None:
        statement = statement.where(
            DiscussionPost.scope_type == "project",
            DiscussionPost.scope_id == project_id,
        )
    if course_id is not None:
        statement = statement.where(
            DiscussionPost.scope_type == "course",
            DiscussionPost.scope_id == course_id,
        )
    if lab_id is not None:
        statement = statement.where(
            DiscussionPost.scope_type == "research_lab",
            DiscussionPost.scope_id == lab_id,
        )
    if category is not None:
        statement = statement.where(DiscussionPost.category == category)

    statement = statement.order_by(
        DiscussionPost.created_at.desc(),
        DiscussionPost.post_id,
    )
    return list(db.scalars(statement))


@app.put(
        "/api/v1/discussions/posts/{post_id}",
        response_model=DiscussionPostResponse,
)
def update_discussion_post(
    post_id: UUID,
    post_update: DiscussionPostUpdate,
    db: DatabaseSession,
) -> DiscussionPost:
    post = get_post_or_404(post_id, db)

    post.category = post_update.category
    post.scope_type = post_update.scope_type
    post.scope_id = post_update.scope_id
    post.project_id = post_update.project_id
    post.author_handle = post_update.author_handle
    post.title = post_update.title
    post.body = post_update.body
    post.tags = post_update.tags
    db.commit()
    db.refresh(post)
    return post


@app.delete(
    "/api/v1/discussions/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_discussion_post(post_id: UUID, db: DatabaseSession) -> None:
    post = get_post_or_404(post_id, db)
    db.delete(post)
    db.commit()


def get_comment_for_post(
    post_id: UUID,
    comment_id: UUID,
    db: Session,
) -> DiscussionComment:
    get_visible_post(post_id, db)
    comment = db.get(DiscussionComment, comment_id)
    if comment is None or comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion comment not found",
        )
    if not is_comment_visible(comment, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion comment not found",
        )
    return comment


def get_comment_for_moderation(
    post_id: UUID,
    comment_id: UUID,
    db: Session,
) -> DiscussionComment:
    get_post_or_404(post_id, db)
    comment = db.get(DiscussionComment, comment_id)
    if comment is None or comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion comment not found",
        )
    return comment


def is_comment_visible(comment: DiscussionComment, db: Session) -> bool:
    current: DiscussionComment | None = comment
    while current is not None:
        if current.moderation_state == "hidden_by_moderator":
            return False
        if current.parent_comment_id is None:
            break
        current = db.get(DiscussionComment, current.parent_comment_id)
        if current is None or current.post_id != comment.post_id:
            return False
    return True


@app.post(
    "/api/v1/discussions/posts/{post_id}/comments",
    response_model=DiscussionCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_discussion_comment(
    post_id: UUID,
    comment: DiscussionCommentCreate,
    db: DatabaseSession,
) -> DiscussionComment:
    get_visible_post(post_id, db)
    if comment.parent_comment_id is not None:
        parent = db.get(DiscussionComment, comment.parent_comment_id)
        if parent is None or parent.post_id != post_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found for this post",
            )
        if not is_comment_visible(parent, db):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found for this post",
            )

    saved_comment = DiscussionComment(
        post_id=post_id,
        parent_comment_id=comment.parent_comment_id,
        author_handle=comment.author_handle,
        message=comment.message,
    )
    db.add(saved_comment)
    db.commit()
    db.refresh(saved_comment)
    return saved_comment


@app.get(
    "/api/v1/discussions/posts/{post_id}/comments",
    response_model=list[DiscussionCommentResponse],
)
def list_discussion_comments(
    post_id: UUID,
    db: DatabaseSession,
    keyword: str | None = Query(default=None, min_length=1),
    author_handle: str | None = Query(default=None, min_length=1, max_length=100),
    format: str = Query(default="json", pattern="^(json|text)$"),
) -> list[DiscussionComment] | Response:
    get_visible_post(post_id, db)
    if format == "text" and (keyword is not None or author_handle is not None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Text download includes the full thread and cannot be filtered",
        )

    statement = select(DiscussionComment).where(DiscussionComment.post_id == post_id)
    if format == "json" and keyword is not None:
        statement = statement.where(
            func.lower(DiscussionComment.message).contains(
                keyword.lower(),
                autoescape=True,
            )
        )
    if format == "json" and author_handle is not None:
        statement = statement.where(DiscussionComment.author_handle == author_handle)
    comments = list(
        db.scalars(
            statement.order_by(
                DiscussionComment.created_at.asc(),
                DiscussionComment.comment_id.asc(),
            )
        )
    )
    visible_comments = [
        comment for comment in comments if is_comment_visible(comment, db)
    ]
    if format == "json":
        return visible_comments

    children: dict[UUID | None, list[DiscussionComment]] = {}
    for comment in visible_comments:
        children.setdefault(comment.parent_comment_id, []).append(comment)

    lines = [f"Comment thread for post {post_id}"]
    stack = [
        (comment, 0)
        for comment in reversed(children.get(None, []))
    ]
    while stack:
        comment, depth = stack.pop()
        indent = "  " * depth
        timestamp = comment.created_at.isoformat()
        lines.append(f"{indent}{comment.author_handle} ({timestamp}):")
        lines.extend(f"{indent}  {line}" for line in comment.message.splitlines())
        stack.extend(
            (child, depth + 1)
            for child in reversed(children.get(comment.comment_id, []))
        )
    return Response(
        content="\n\n".join(lines) + "\n",
        media_type="text/plain",
        headers={
            "Content-Disposition": (
                f'attachment; filename="post-{post_id}-comments.txt"'
            )
        },
    )


@app.get(
    "/api/v1/discussions/posts/{post_id}/comments/{comment_id}",
    response_model=DiscussionCommentResponse,
)
def get_discussion_comment(
    post_id: UUID,
    comment_id: UUID,
    db: DatabaseSession,
) -> DiscussionComment:
    return get_comment_for_post(post_id, comment_id, db)


@app.put(
    "/api/v1/discussions/posts/{post_id}/comments/{comment_id}",
    response_model=DiscussionCommentResponse,
)
def update_discussion_comment(
    post_id: UUID,
    comment_id: UUID,
    comment_update: DiscussionCommentUpdate,
    db: DatabaseSession,
) -> DiscussionComment:
    comment = get_comment_for_post(post_id, comment_id, db)
    comment.message = comment_update.message
    db.commit()
    db.refresh(comment)
    return comment


@app.delete(
    "/api/v1/discussions/posts/{post_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_discussion_comment(
    post_id: UUID,
    comment_id: UUID,
    db: DatabaseSession,
) -> None:
    comment = get_comment_for_post(post_id, comment_id, db)
    has_replies = db.scalar(
        select(DiscussionComment.comment_id)
        .where(DiscussionComment.parent_comment_id == comment_id)
        .limit(1)
    )
    if has_replies is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Discussion comment has replies and cannot be deleted",
        )
    db.delete(comment)
    db.commit()


@app.post(
    "/api/v1/discussions/posts/{post_id}/report",
    response_model=ModerationStatusResponse,
)
def report_discussion_post(
    post_id: UUID,
    db: DatabaseSession,
) -> ModerationStatusResponse:
    post = get_visible_post(post_id, db)
    if post.moderation_state == "active":
        post.moderation_state = "reported"
        db.commit()
        db.refresh(post)
    return ModerationStatusResponse(moderation_state=post.moderation_state)


@app.post(
    "/api/v1/discussions/posts/{post_id}/comments/{comment_id}/report",
    response_model=ModerationStatusResponse,
)
def report_discussion_comment(
    post_id: UUID,
    comment_id: UUID,
    db: DatabaseSession,
) -> ModerationStatusResponse:
    comment = get_comment_for_post(post_id, comment_id, db)
    if comment.moderation_state == "active":
        comment.moderation_state = "reported"
        db.commit()
        db.refresh(comment)
    return ModerationStatusResponse(moderation_state=comment.moderation_state)


@app.put(
    "/api/v1/discussions/moderation/posts/{post_id}",
    response_model=ModerationStatusResponse,
)
def moderate_discussion_post(
    post_id: UUID,
    moderation_update: ModerationUpdate,
    db: DatabaseSession,
    moderator_role: Annotated[str | None, Header(alias="X-Moderator-Role")] = None,
) -> ModerationStatusResponse:
    require_faculty_moderator(moderator_role)
    post = get_post_or_404(post_id, db)
    post.moderation_state = moderation_update.moderation_state
    db.commit()
    db.refresh(post)
    return ModerationStatusResponse(moderation_state=post.moderation_state)


@app.put(
    "/api/v1/discussions/moderation/posts/{post_id}/comments/{comment_id}",
    response_model=ModerationStatusResponse,
)
def moderate_discussion_comment(
    post_id: UUID,
    comment_id: UUID,
    moderation_update: ModerationUpdate,
    db: DatabaseSession,
    moderator_role: Annotated[str | None, Header(alias="X-Moderator-Role")] = None,
) -> ModerationStatusResponse:
    require_faculty_moderator(moderator_role)
    comment = get_comment_for_moderation(post_id, comment_id, db)
    comment.moderation_state = moderation_update.moderation_state
    db.commit()
    db.refresh(comment)
    return ModerationStatusResponse(moderation_state=comment.moderation_state)


@app.get(
    "/api/v1/discussions/scopes/{scope_type}/{scope_id}/timeline",
    response_model=list[DiscussionPostResponse],
)
def get_scope_timeline(
    scope_type: str,
    scope_id: UUID,
    db: DatabaseSession,
) -> list[DiscussionPost]:
    normalized_scope_type = SCOPE_TYPE_BY_URL.get(scope_type)
    if normalized_scope_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion scope not found",
        )
    matching_scopes = [
        and_(
            DiscussionPost.scope_type == normalized_scope_type,
            DiscussionPost.scope_id == scope_id,
        )
    ]
    if normalized_scope_type == "course":
        project_ids = select(ProjectCourseAssociation.project_id).where(
            ProjectCourseAssociation.course_id == scope_id
        )
        matching_scopes.append(
            and_(
                DiscussionPost.scope_type == "project",
                DiscussionPost.scope_id.in_(project_ids),
            )
        )
    elif normalized_scope_type == "research_lab":
        project_ids = select(ProjectLabAssociation.project_id).where(
            ProjectLabAssociation.lab_id == scope_id
        )
        matching_scopes.append(
            and_(
                DiscussionPost.scope_type == "project",
                DiscussionPost.scope_id.in_(project_ids),
            )
        )

    statement = (
        select(DiscussionPost)
        .where(
            or_(*matching_scopes),
            DiscussionPost.moderation_state != "hidden_by_moderator",
        )
        .order_by(
            DiscussionPost.created_at.asc(),
            DiscussionPost.post_id.asc(),
        )
    )
    return list(db.scalars(statement))
