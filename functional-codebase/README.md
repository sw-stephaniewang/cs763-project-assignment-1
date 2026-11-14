# Research Blog & Project Discussion Board API

This service stores Academic Announcements and Project Update Blogs in
PostgreSQL. Posts can be scoped to a project, course, or research lab. The
`body` field accepts rich-text content (for example, an HTML fragment) and is
stored as submitted.

## Run locally

From `functional-codebase/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
docker compose up -d --wait db
uvicorn app.main:app --reload
```

The database URL defaults to the PostgreSQL instance in `docker-compose.yml`.
Set `DATABASE_URL` to override it. The API is available at
`http://127.0.0.1:8000`; interactive API documentation is at `/docs`.

## Run the integration test

Start PostgreSQL if it is not already running, then run from
`functional-codebase/` with the virtual environment activated:

```bash
docker compose up -d --wait db
python -m pytest -q tests/discussion_posts_integration.py
```

The test uses the real PostgreSQL database to create and retrieve both post
categories across all three scope types, update and verify a saved post,
delete a post and verify it is no longer retrievable, and remove test rows.

To stop PostgreSQL:

```bash
docker compose down
```

## Endpoints

- `POST /api/v1/discussions/posts` — create a post with `category`,
  `scope_type`, `scope_id`, `title`, `body`, and `tags`; returns the saved post
  with its generated `post_id` and `created_at`. The original `project_id`
  field remains supported for project-scoped posts.
- `GET /api/v1/discussions/posts/{post_id}` — retrieve a saved post by UUID;
  returns `404` if no post exists.
- `GET /api/v1/discussions/posts` — list posts, optionally filtered by
  case-insensitive body `keyword`, inclusive `created_after` and
  `created_before` timestamps (timezone required), exact `author_handle`,
  `project_id`, `course_id`, `lab_id`, and `category`. Multiple filters are
  combined with AND; results are newest first.
- `PUT /api/v1/discussions/posts/{post_id}` — replace a saved post's category,
  scope, title, body, and tags; returns `404` if no post exists.
- `DELETE /api/v1/discussions/posts/{post_id}` — delete a saved post; returns
  `204`, or `404` if no post exists.
- `GET /api/v1/discussions/scopes/{scope_type}/{scope_id}/timeline` — list
  posts for a scope in oldest-first chronological order. URL scope types are
  `projects`, `courses`, and `labs`; the timeline includes both categories.
- `POST /api/v1/discussions/posts/{post_id}/comments` — create a comment with
  `message` and `author_handle`, optionally with a `parent_comment_id` to reply
  to another comment on the same post.
- `GET /api/v1/discussions/posts/{post_id}/comments` — list the post's comments
  oldest first, including parent IDs to represent nested replies. Optional
  `keyword` searches comment messages case-insensitively and
  `author_handle` filters by an exact handle. Both filters can be combined;
  results remain oldest first.
- The same comments URL returns JSON by default. Add `?format=text` to download
  the complete thread as an attached plain-text file, with replies indented
  under their parent comments. Thread downloads cannot be combined with list
  filters.
- `GET /api/v1/discussions/posts/{post_id}/comments/{comment_id}` — retrieve a
  comment belonging to the specified post.
- `PUT /api/v1/discussions/posts/{post_id}/comments/{comment_id}` — update a
  comment's message without changing its author or thread position.
- `DELETE /api/v1/discussions/posts/{post_id}/comments/{comment_id}` — delete
  a comment with no replies (`204`); returns `409` if it has replies.
- `POST /api/v1/discussions/posts/{post_id}/report` — report a post; moves it
  from `active` to `reported`.
- `POST /api/v1/discussions/posts/{post_id}/comments/{comment_id}/report` —
  report a comment; moves it from `active` to `reported`.
- `PUT /api/v1/discussions/moderation/posts/{post_id}` and
  `PUT /api/v1/discussions/moderation/posts/{post_id}/comments/{comment_id}` —
  faculty moderation actions. Require `X-Moderator-Role: faculty` and a JSON
  body containing `{"moderation_state":"active"}` or
  `{"moderation_state":"hidden_by_moderator"}`.

Posts and comments begin in the `active` state. A report changes active content
to `reported`; repeated reports leave it reported. Faculty can resolve reported
content to active or hide active/reported content. Faculty can restore hidden
content to active. Reports do not hide content by themselves.

The faculty header is a development-only trust assumption for this service's
local prototype, not authentication: clients can spoof it. Replace it with
verified identity and role authorization before deployment.

Hidden posts are omitted from post feeds and scope timelines, and direct post
retrieval and all comment-thread reads return `404`. Hiding a comment also
hides its entire descendant reply tree from direct retrieval, comment lists,
and text downloads; unrelated comments and their branches remain visible.
Replies cannot be created under a hidden post or a hidden comment. Hidden
content can be restored by faculty moderation, which makes the still-active
descendants visible again.

Posts are associated with exactly one direct scope. Course and lab timelines
also include project-scoped posts whose project IDs are explicitly associated
with that course or lab. These relationships are stored in the
`project_course_associations` and `project_lab_associations` PostgreSQL tables,
respectively, with each `(project_id, course_id)` and `(project_id, lab_id)`
pair unique. The many-to-many model allows a course or lab to have multiple
projects and a project to be associated with multiple courses and labs.
Association IDs are UUIDs; this service does not maintain separate course,
lab, or project entity tables to validate their existence.

Comments are stored in their own table and are deleted when their root post is
deleted. A comment that has replies cannot be deleted; delete its leaf replies
first to preserve the rest of the thread.
