# Stack: Python, FastAPI, Pydantic
# Tool: GitHub Copilot Agent mode
# Prompt summary: Define the request and response models for posts,
# comments, and moderation, including the supported categories and scopes.
# Estimated AI contribution: 80%
# Human verification: I ran the API integration tests covering post
# categories and scopes, comment requests, and moderation.


from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


PostCategory = Literal["Academic Announcements", "Project Update Blogs"]
ScopeType = Literal["project", "course", "research_lab"]
ModerationState = Literal["active", "reported", "hidden_by_moderator"]
FacultyModerationState = Literal["active", "hidden_by_moderator"]


class DiscussionPostInput(BaseModel):
    category: PostCategory = "Project Update Blogs"
    scope_type: ScopeType = "project"
    scope_id: UUID | None = None
    project_id: UUID | None = None
    author_handle: str | None = Field(default=None, min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)
    tags: list[str]

    @model_validator(mode="after")
    def validate_scope(self) -> "DiscussionPostInput":
        if self.scope_type == "project":
            if self.scope_id is None:
                self.scope_id = self.project_id
            if self.scope_id is None:
                raise ValueError("scope_id is required for project-scoped posts")
            if self.project_id is None:
                self.project_id = self.scope_id
            elif self.project_id != self.scope_id:
                raise ValueError("project_id must match scope_id for project posts")
        else:
            if self.scope_id is None:
                raise ValueError("scope_id is required")
            if self.project_id is not None:
                raise ValueError("project_id is only valid for project-scoped posts")
        return self


class DiscussionPostCreate(DiscussionPostInput):
    pass


class DiscussionPostUpdate(DiscussionPostInput):
    pass


class DiscussionPostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    post_id: UUID
    category: PostCategory
    scope_type: ScopeType
    scope_id: UUID
    project_id: UUID | None
    author_handle: str | None
    moderation_state: ModerationState
    title: str
    body: str
    tags: list[str]
    created_at: datetime


class DiscussionCommentCreate(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    author_handle: str = Field(min_length=1, max_length=100)
    parent_comment_id: UUID | None = None

    @model_validator(mode="after")
    def normalize_text(self) -> "DiscussionCommentCreate":
        self.message = self.message.strip()
        self.author_handle = self.author_handle.strip()
        if not self.message:
            raise ValueError("message must not be blank")
        if not self.author_handle:
            raise ValueError("author_handle must not be blank")
        return self


class DiscussionCommentUpdate(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

    @model_validator(mode="after")
    def normalize_message(self) -> "DiscussionCommentUpdate":
        self.message = self.message.strip()
        if not self.message:
            raise ValueError("message must not be blank")
        return self


class DiscussionCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    comment_id: UUID
    post_id: UUID
    parent_comment_id: UUID | None
    author_handle: str
    message: str
    moderation_state: ModerationState
    created_at: datetime
    updated_at: datetime


class ModerationUpdate(BaseModel):
    moderation_state: FacultyModerationState


class ModerationStatusResponse(BaseModel):
    moderation_state: ModerationState
