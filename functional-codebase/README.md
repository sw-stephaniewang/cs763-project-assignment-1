# Research Blog & Project Discussion Board API

## AI Usage Summary

- **AI tools:** GitHub Copilot and ChatGPT
- **Estimated AI contribution to this README:** 75%
- **Prompt summary:** Copilot created the README and updated it as it added each endpoint. I then asked ChatGPT to polish the wording and add detail about running the app and the tests.
- **My review:** I checked the setup and test commands against the project files and compared the endpoint descriptions with the FastAPI code.

## Overview

I built this API to store Academic Announcements and Project Update Blogs in PostgreSQL. Each post belongs directly to one project, course, or research lab. The `body` field accepts rich text, such as an HTML fragment, and the API stores it as submitted.

## Run locally

From `functional-codebase/`, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
docker compose up -d --wait db
uvicorn app.main:app --reload
```

The app uses the PostgreSQL database defined in `docker-compose.yml` by default. Set `DATABASE_URL` to use a different database. Once the app starts, you can try the endpoints in the [interactive API docs](http://127.0.0.1:8000/docs).

## Run the integration tests

From `functional-codebase/`, activate the virtual environment and run:

```bash
docker compose up -d --wait db
python -m pytest -q tests/discussion_posts_integration.py
```

The tests use a running PostgreSQL database. They cover both post categories, all three scope types, post updates and deletions, nested comments, filtering, text downloads, moderation, and timelines. The tests clean up the rows they create.

When you’re done, stop PostgreSQL:

```bash
docker compose down
```

## API endpoints

All paths below start with `/api/v1/discussions`.

### Posts and timelines

| Method and path                                | What it does                                                                                                                                                                                                                 |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST /posts`                                  | Creates a post with a `category`, `scope_type`, `scope_id`, `title`, `body`, and `tags`. The response includes the generated `post_id` and `created_at`. Project-scoped posts can still use the original `project_id` field. |
| `GET /posts`                                   | Lists posts newest first. You can combine filters for body keyword, date range, author, category, and scope.                                                                                                                 |
| `GET /posts/{post_id}`                         | Looks up a post by UUID. Returns `404` if the post is missing or hidden.                                                                                                                                                     |
| `PUT /posts/{post_id}`                         | Replaces a saved post’s category, scope, title, body, and tags. Returns `404` if the post does not exist.                                                                                                                    |
| `DELETE /posts/{post_id}`                      | Deletes a post and its comments. Returns `204` on success or `404` if the post does not exist.                                                                                                                               |
| `GET /scopes/{scope_type}/{scope_id}/timeline` | Shows announcements and project updates oldest first. The URL accepts `projects`, `courses`, and `labs` as scope types.                                                                                                      |

For `GET /posts`, `keyword` searches the post body without regard to case, and `author_handle` matches an exact handle. The `created_after` and `created_before` filters include their boundary timestamps and require a timezone. Use `project_id`, `course_id`, or `lab_id` to filter by scope. A post must match every filter you supply.

Course and lab timelines include posts assigned directly to that scope and posts from associated projects. PostgreSQL stores these links in `project_course_associations` and `project_lab_associations`. Each project-to-course or project-to-lab pair is unique. A course or lab can include multiple projects, and a project can belong to multiple courses and labs. The IDs are UUIDs, and the app does not keep separate project, course, or lab tables to check whether those IDs exist.

### Comments

| Method and path                                 | What it does                                                                                                                                                                                |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST /posts/{post_id}/comments`                | Adds a comment with a `message` and `author_handle`. To reply to another comment on the same post, include its `parent_comment_id`.                                                         |
| `GET /posts/{post_id}/comments`                 | Lists visible comments oldest first. The parent IDs show which comments are replies.                                                                                                        |
| `GET /posts/{post_id}/comments/{comment_id}`    | Retrieves a comment from the specified post.                                                                                                                                                |
| `PUT /posts/{post_id}/comments/{comment_id}`    | Updates a comment’s message while keeping its author and position in the thread.                                                                                                            |
| `DELETE /posts/{post_id}/comments/{comment_id}` | Returns `204` after deleting a comment with no replies. If the comment has replies, the API returns `409`. To remove that branch, start with the replies that have no replies of their own. |

You can filter the JSON comment list by a case-insensitive `keyword`, an exact `author_handle`, or both. Comments get their project, course, or lab scope from the parent post. Date-range filtering is available on the post list.

Add `?format=text` to the comment-list URL to download the full visible thread as a plain-text file. The file indents replies under their parent comments. Request the download without the comment-list filters.

### Reporting and moderation

| Method and path                                         | What it does                                          |
| ------------------------------------------------------- | ----------------------------------------------------- |
| `POST /posts/{post_id}/report`                          | Reports a post.                                       |
| `POST /posts/{post_id}/comments/{comment_id}/report`    | Reports a comment.                                    |
| `PUT /moderation/posts/{post_id}`                       | Lets faculty hide a post or set it back to active.    |
| `PUT /moderation/posts/{post_id}/comments/{comment_id}` | Lets faculty hide a comment or set it back to active. |

Posts and comments start as `active`. Reporting changes active content to `reported`, and repeat reports leave it in that state. Reported content stays visible until a faculty moderation action hides it.

The moderation endpoints use `X-Moderator-Role: faculty` and accept either `{"moderation_state":"active"}` or `{"moderation_state":"hidden_by_moderator"}`. The app relies on a client-supplied role for local development. A deployed version would need to verify the caller’s identity and check their permission to moderate the content.

A hidden post disappears from feeds and timelines. Direct requests for the post or its comments return `404`. Hiding a comment also hides all its replies from individual comment reads, lists, and text downloads. Other branches stay visible. The app blocks new replies under hidden content. Restoring a hidden post or comment makes its still-active descendants visible again.
