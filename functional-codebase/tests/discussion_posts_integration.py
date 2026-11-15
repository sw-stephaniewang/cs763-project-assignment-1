# Stack: Python, pytest, FastAPI TestClient, SQLAlchemy, PostgreSQL
# Tool: GitHub Copilot Agent mode
# Prompt summary: Add PostgreSQL integration tests for posts, nested
# comments, search, text export, moderation, and course and lab timelines.
# Estimated AI contribution: 80%
# Human verification: I ran this test file locally against PostgreSQL.
# The result was 7 passed with 1 deprecation warning.


from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete, update

from app.database import SessionLocal
from app.main import app
from app.models import (
    DiscussionComment,
    DiscussionPost,
    ProjectCourseAssociation,
    ProjectLabAssociation,
)


def test_post_lifecycle_across_categories_and_scopes() -> None:
    created_post_ids: list[UUID] = []
    categories = ["Academic Announcements", "Project Update Blogs"]
    scopes = ["project", "course", "research_lab"]

    try:
        with TestClient(app) as client:
            for category in categories:
                for scope_type in scopes:
                    scope_id = uuid4()
                    payload = {
                        "category": category,
                        "scope_type": scope_type,
                        "scope_id": str(scope_id),
                        "title": f"{category} for {scope_type}",
                        "body": "<p>Saved <strong>rich text</strong>.</p>",
                        "tags": ["research", scope_type],
                    }
                    create_response = client.post(
                        "/api/v1/discussions/posts",
                        json=payload,
                    )

                    assert create_response.status_code == 201
                    created_post = create_response.json()
                    post_id = UUID(created_post["post_id"])
                    created_post_ids.append(post_id)
                    assert created_post["category"] == category
                    assert created_post["scope_type"] == scope_type
                    assert created_post["scope_id"] == str(scope_id)
                    assert created_post["project_id"] == (
                        str(scope_id) if scope_type == "project" else None
                    )
                    assert created_post["title"] == payload["title"]
                    assert created_post["body"] == payload["body"]
                    assert created_post["tags"] == payload["tags"]
                    assert created_post["moderation_state"] == "active"
                    assert datetime.fromisoformat(
                        created_post["created_at"]
                    ).tzinfo is not None

                    retrieve_response = client.get(
                        f"/api/v1/discussions/posts/{post_id}"
                    )
                    assert retrieve_response.status_code == 200
                    assert retrieve_response.json() == created_post

            legacy_project_id = uuid4()
            legacy_response = client.post(
                "/api/v1/discussions/posts",
                json={
                    "project_id": str(legacy_project_id),
                    "title": "Legacy-compatible update",
                    "body": "<p>Created with the original project_id field.</p>",
                    "tags": ["legacy"],
                },
            )
            assert legacy_response.status_code == 201
            legacy_post = legacy_response.json()
            legacy_post_id = UUID(legacy_post["post_id"])
            created_post_ids.append(legacy_post_id)
            assert legacy_post["scope_type"] == "project"
            assert legacy_post["scope_id"] == str(legacy_project_id)
            assert legacy_post["project_id"] == str(legacy_project_id)

            update_post_id = created_post_ids[0]
            updated_payload = {
                "category": "Academic Announcements",
                "scope_type": "research_lab",
                "scope_id": str(uuid4()),
                "title": "Updated announcement",
                "body": "<p>The saved <em>updated</em> content.</p>",
                "tags": ["announcement", "updated"],
            }
            update_response = client.put(
                f"/api/v1/discussions/posts/{update_post_id}",
                json=updated_payload,
            )
            assert update_response.status_code == 200
            updated_post = update_response.json()
            assert updated_post["post_id"] == str(update_post_id)
            assert updated_post["category"] == updated_payload["category"]
            assert updated_post["scope_type"] == updated_payload["scope_type"]
            assert updated_post["scope_id"] == updated_payload["scope_id"]
            assert updated_post["project_id"] is None
            assert updated_post["title"] == updated_payload["title"]
            assert updated_post["body"] == updated_payload["body"]
            assert updated_post["tags"] == updated_payload["tags"]
            assert updated_post["created_at"] == client.get(
                f"/api/v1/discussions/posts/{update_post_id}"
            ).json()["created_at"]

            retrieve_updated_response = client.get(
                f"/api/v1/discussions/posts/{update_post_id}"
            )
            assert retrieve_updated_response.status_code == 200
            assert retrieve_updated_response.json() == updated_post

            delete_post_id = created_post_ids[1]
            delete_response = client.delete(
                f"/api/v1/discussions/posts/{delete_post_id}"
            )
            assert delete_response.status_code == 204
            missing_response = client.get(
                f"/api/v1/discussions/posts/{delete_post_id}"
            )
            assert missing_response.status_code == 404
            created_post_ids.remove(delete_post_id)
    finally:
        if created_post_ids:
            with SessionLocal.begin() as db:
                db.execute(
                    delete(DiscussionPost).where(
                        DiscussionPost.post_id.in_(created_post_ids)
                    )
                )


def test_post_listing_filters_and_scope_timeline() -> None:
    created_post_ids: list[UUID] = []
    test_token = uuid4().hex
    author_handle = f"author-{test_token}"
    project_id = uuid4()
    unrelated_project_id = uuid4()
    course_id = uuid4()
    lab_id = uuid4()
    post_definitions = {
        "announcement": {
            "category": "Academic Announcements",
            "scope_type": "project",
            "scope_id": project_id,
            "author_handle": author_handle,
            "title": "Project announcement",
            "body": f"{test_token} research starts here",
            "tags": ["test"],
            "created_at": datetime.fromisoformat("2026-01-10T09:00:00+00:00"),
        },
        "project_update": {
            "category": "Project Update Blogs",
            "scope_type": "project",
            "scope_id": project_id,
            "author_handle": author_handle,
            "title": "Project update",
            "body": f"{test_token} research continues",
            "tags": ["test"],
            "created_at": datetime.fromisoformat("2026-01-11T09:00:00+00:00"),
        },
        "unrelated_project": {
            "category": "Project Update Blogs",
            "scope_type": "project",
            "scope_id": unrelated_project_id,
            "author_handle": f"other-{test_token}",
            "title": "Unrelated project update",
            "body": f"{test_token} research elsewhere",
            "tags": ["test"],
            "created_at": datetime.fromisoformat("2026-01-12T09:00:00+00:00"),
        },
        "course": {
            "category": "Academic Announcements",
            "scope_type": "course",
            "scope_id": course_id,
            "author_handle": author_handle,
            "title": "Course announcement",
            "body": f"{test_token} research for class",
            "tags": ["test"],
            "created_at": datetime.fromisoformat("2026-01-13T09:00:00+00:00"),
        },
        "lab": {
            "category": "Project Update Blogs",
            "scope_type": "research_lab",
            "scope_id": lab_id,
            "author_handle": author_handle,
            "title": "Lab update",
            "body": f"{test_token} research in lab",
            "tags": ["test"],
            "created_at": datetime.fromisoformat("2026-01-14T09:00:00+00:00"),
        },
    }

    try:
        with TestClient(app) as client:
            post_ids: dict[str, UUID] = {}
            for name, definition in post_definitions.items():
                payload = {
                    key: str(value) if key == "scope_id" else value
                    for key, value in definition.items()
                    if key != "created_at"
                }
                response = client.post("/api/v1/discussions/posts", json=payload)
                assert response.status_code == 201, response.text
                post_id = UUID(response.json()["post_id"])
                post_ids[name] = post_id
                created_post_ids.append(post_id)

            with SessionLocal.begin() as db:
                for name, definition in post_definitions.items():
                    db.execute(
                        update(DiscussionPost)
                        .where(DiscussionPost.post_id == post_ids[name])
                        .values(created_at=definition["created_at"])
                    )

            def listed_ids(**filters: str) -> set[UUID]:
                response = client.get(
                    "/api/v1/discussions/posts",
                    params=filters,
                )
                assert response.status_code == 200, response.text
                return {UUID(post["post_id"]) for post in response.json()}

            expected_all = set(post_ids.values())
            assert listed_ids(keyword=test_token.upper()) == expected_all
            assert listed_ids(
                created_after="2026-01-11T00:00:00Z",
                created_before="2026-01-13T23:59:59Z",
            ) == {post_ids["project_update"], post_ids["unrelated_project"], post_ids["course"]}
            assert listed_ids(author_handle=author_handle) == {
                post_ids["announcement"],
                post_ids["project_update"],
                post_ids["course"],
                post_ids["lab"],
            }
            assert listed_ids(project_id=str(project_id)) == {
                post_ids["announcement"],
                post_ids["project_update"],
            }
            assert listed_ids(course_id=str(course_id)) == {post_ids["course"]}
            assert listed_ids(lab_id=str(lab_id)) == {post_ids["lab"]}
            assert listed_ids(category="Academic Announcements") == {
                post_ids["announcement"],
                post_ids["course"],
            }
            assert listed_ids(
                keyword="research",
                created_after="2026-01-11T00:00:00Z",
                created_before="2026-01-11T23:59:59Z",
                author_handle=author_handle,
                project_id=str(project_id),
                category="Project Update Blogs",
            ) == {post_ids["project_update"]}

            for url_scope, scope_id, expected_names in (
                ("projects", project_id, ["announcement", "project_update"]),
                ("courses", course_id, ["course"]),
                ("labs", lab_id, ["lab"]),
            ):
                timeline_response = client.get(
                    f"/api/v1/discussions/scopes/{url_scope}/{scope_id}/timeline"
                )
                assert timeline_response.status_code == 200, timeline_response.text
                timeline = timeline_response.json()
                assert [UUID(post["post_id"]) for post in timeline] == [
                    post_ids[name] for name in expected_names
                ]
                timestamps = [
                    datetime.fromisoformat(post["created_at"]) for post in timeline
                ]
                assert timestamps == sorted(timestamps)
            project_timeline = client.get(
                f"/api/v1/discussions/scopes/projects/{project_id}/timeline"
            ).json()
            assert [post["category"] for post in project_timeline] == [
                "Academic Announcements",
                "Project Update Blogs",
            ]
    finally:
        if created_post_ids:
            with SessionLocal.begin() as db:
                db.execute(
                    delete(DiscussionPost).where(
                        DiscussionPost.post_id.in_(created_post_ids)
                    )
                )


def test_nested_comment_lifecycle() -> None:
    post_id: UUID | None = None

    try:
        with TestClient(app) as client:
            post_response = client.post(
                "/api/v1/discussions/posts",
                json={
                    "project_id": str(uuid4()),
                    "title": "Comment thread test",
                    "body": "<p>Post for nested comments.</p>",
                    "tags": ["comments"],
                },
            )
            assert post_response.status_code == 201, post_response.text
            post_id = UUID(post_response.json()["post_id"])
            comments_url = f"/api/v1/discussions/posts/{post_id}/comments"

            direct_response = client.post(
                comments_url,
                json={
                    "message": "Top-level comment",
                    "author_handle": "alice",
                },
            )
            assert direct_response.status_code == 201, direct_response.text
            direct_comment = direct_response.json()
            direct_id = UUID(direct_comment["comment_id"])
            assert direct_comment["post_id"] == str(post_id)
            assert direct_comment["parent_comment_id"] is None
            assert direct_comment["message"] == "Top-level comment"
            assert direct_comment["author_handle"] == "alice"
            assert direct_comment["moderation_state"] == "active"
            assert direct_comment["created_at"] == direct_comment["updated_at"]

            reply_response = client.post(
                comments_url,
                json={
                    "message": "Reply to the post comment",
                    "author_handle": "bob",
                    "parent_comment_id": str(direct_id),
                },
            )
            assert reply_response.status_code == 201, reply_response.text
            reply_comment = reply_response.json()
            reply_id = UUID(reply_comment["comment_id"])
            assert reply_comment["parent_comment_id"] == str(direct_id)

            deeper_reply_response = client.post(
                comments_url,
                json={
                    "message": "Reply one level deeper",
                    "author_handle": "carol",
                    "parent_comment_id": str(reply_id),
                },
            )
            assert deeper_reply_response.status_code == 201, deeper_reply_response.text
            deeper_reply = deeper_reply_response.json()
            deeper_reply_id = UUID(deeper_reply["comment_id"])
            assert deeper_reply["parent_comment_id"] == str(reply_id)

            ordered_times = [
                datetime.now(timezone.utc) - timedelta(minutes=3),
                datetime.now(timezone.utc) - timedelta(minutes=2),
                datetime.now(timezone.utc) - timedelta(minutes=1),
            ]
            comment_ids = [direct_id, reply_id, deeper_reply_id]
            with SessionLocal.begin() as db:
                for comment_id, created_at in zip(comment_ids, ordered_times):
                    db.execute(
                        update(DiscussionComment)
                        .where(DiscussionComment.comment_id == comment_id)
                        .values(created_at=created_at, updated_at=created_at)
                    )

            list_response = client.get(comments_url)
            assert list_response.status_code == 200
            thread = list_response.json()
            assert [UUID(comment["comment_id"]) for comment in thread] == comment_ids
            assert [comment["parent_comment_id"] for comment in thread] == [
                None,
                str(direct_id),
                str(reply_id),
            ]
            timestamps = [
                datetime.fromisoformat(comment["created_at"]) for comment in thread
            ]
            assert timestamps == sorted(timestamps)

            get_response = client.get(f"{comments_url}/{reply_id}")
            assert get_response.status_code == 200
            assert get_response.json() == thread[1]

            previous_created_at = client.get(f"{comments_url}/{reply_id}").json()[
                "created_at"
            ]
            old_updated_at = datetime.now(timezone.utc) - timedelta(days=1)
            with SessionLocal.begin() as db:
                db.execute(
                    update(DiscussionComment)
                    .where(DiscussionComment.comment_id == reply_id)
                    .values(updated_at=old_updated_at)
                )
            update_response = client.put(
                f"{comments_url}/{reply_id}",
                json={"message": "Edited reply text"},
            )
            assert update_response.status_code == 200
            updated_reply = update_response.json()
            assert updated_reply["message"] == "Edited reply text"
            assert updated_reply["author_handle"] == "bob"
            assert updated_reply["created_at"] == previous_created_at
            assert datetime.fromisoformat(updated_reply["updated_at"]) > old_updated_at
            assert client.get(f"{comments_url}/{reply_id}").json() == updated_reply

            parent_delete_response = client.delete(f"{comments_url}/{reply_id}")
            assert parent_delete_response.status_code == 409

            delete_response = client.delete(f"{comments_url}/{deeper_reply_id}")
            assert delete_response.status_code == 204
            missing_response = client.get(f"{comments_url}/{deeper_reply_id}")
            assert missing_response.status_code == 404
            remaining_response = client.get(comments_url)
            assert [
                UUID(comment["comment_id"]) for comment in remaining_response.json()
            ] == [direct_id, reply_id]
    finally:
        if post_id is not None:
            with SessionLocal.begin() as db:
                db.execute(delete(DiscussionPost).where(DiscussionPost.post_id == post_id))


def test_comment_filters_and_plain_text_thread_download() -> None:
    post_id: UUID | None = None

    try:
        with TestClient(app) as client:
            post_response = client.post(
                "/api/v1/discussions/posts",
                json={
                    "project_id": str(uuid4()),
                    "title": "Comment filter test",
                    "body": "<p>Post for comment search.</p>",
                    "tags": ["comments"],
                },
            )
            assert post_response.status_code == 201, post_response.text
            post_id = UUID(post_response.json()["post_id"])
            comments_url = f"/api/v1/discussions/posts/{post_id}/comments"

            direct_response = client.post(
                comments_url,
                json={
                    "message": "Needle appears in the direct comment",
                    "author_handle": "alice",
                },
            )
            assert direct_response.status_code == 201, direct_response.text
            direct_comment = direct_response.json()
            direct_id = UUID(direct_comment["comment_id"])

            reply_response = client.post(
                comments_url,
                json={
                    "message": "Needle appears in this reply",
                    "author_handle": "bob",
                    "parent_comment_id": str(direct_id),
                },
            )
            assert reply_response.status_code == 201, reply_response.text
            reply_comment = reply_response.json()
            reply_id = UUID(reply_comment["comment_id"])

            unrelated_response = client.post(
                comments_url,
                json={
                    "message": "A separate note without the search word",
                    "author_handle": "alice",
                },
            )
            assert unrelated_response.status_code == 201, unrelated_response.text
            unrelated_comment = unrelated_response.json()
            unrelated_id = UUID(unrelated_comment["comment_id"])

            timestamps = [
                datetime.now(timezone.utc) - timedelta(minutes=3),
                datetime.now(timezone.utc) - timedelta(minutes=2),
                datetime.now(timezone.utc) - timedelta(minutes=1),
            ]
            for comment_id, created_at in zip(
                (direct_id, reply_id, unrelated_id),
                timestamps,
            ):
                with SessionLocal.begin() as db:
                    db.execute(
                        update(DiscussionComment)
                        .where(DiscussionComment.comment_id == comment_id)
                        .values(created_at=created_at, updated_at=created_at)
                    )

            default_response = client.get(comments_url)
            assert default_response.status_code == 200
            assert default_response.headers["content-type"].startswith(
                "application/json"
            )
            assert [
                UUID(comment["comment_id"]) for comment in default_response.json()
            ] == [direct_id, reply_id, unrelated_id]

            keyword_response = client.get(comments_url, params={"keyword": "NEEDLE"})
            assert keyword_response.status_code == 200
            assert [
                UUID(comment["comment_id"]) for comment in keyword_response.json()
            ] == [direct_id, reply_id]

            author_response = client.get(
                comments_url,
                params={"author_handle": "alice"},
            )
            assert author_response.status_code == 200
            assert [
                UUID(comment["comment_id"]) for comment in author_response.json()
            ] == [direct_id, unrelated_id]

            combined_response = client.get(
                comments_url,
                params={"keyword": "needle", "author_handle": "alice"},
            )
            assert combined_response.status_code == 200
            assert [
                UUID(comment["comment_id"]) for comment in combined_response.json()
            ] == [direct_id]

            download_response = client.get(comments_url, params={"format": "text"})
            assert download_response.status_code == 200
            assert download_response.headers["content-type"].startswith("text/plain")
            assert (
                f'filename="post-{post_id}-comments.txt"'
                in download_response.headers["content-disposition"]
            )
            thread_text = download_response.text
            assert "alice (" in thread_text
            assert "Needle appears in the direct comment" in thread_text
            assert "bob (" in thread_text
            assert "Needle appears in this reply" in thread_text
            assert "A separate note without the search word" in thread_text
            assert thread_text.index("Needle appears in the direct comment") < (
                thread_text.index("Needle appears in this reply")
            )
            assert "  bob (" in thread_text
    finally:
        if post_id is not None:
            with SessionLocal.begin() as db:
                db.execute(
                    delete(DiscussionPost).where(DiscussionPost.post_id == post_id)
                )


def test_post_reporting_and_hidden_root_visibility() -> None:
    post_id: UUID | None = None
    project_id = uuid4()

    try:
        with TestClient(app) as client:
            create_post_response = client.post(
                "/api/v1/discussions/posts",
                json={
                    "scope_type": "project",
                    "scope_id": str(project_id),
                    "title": "Post to moderate",
                    "body": "Root post visibility test",
                    "tags": ["moderation"],
                },
            )
            assert create_post_response.status_code == 201
            created_post = create_post_response.json()
            post_id = UUID(created_post["post_id"])
            assert created_post["moderation_state"] == "active"

            comments_url = f"/api/v1/discussions/posts/{post_id}/comments"
            comment_response = client.post(
                comments_url,
                json={
                    "message": "Comment under moderated post",
                    "author_handle": "commenter",
                },
            )
            assert comment_response.status_code == 201
            comment = comment_response.json()
            comment_id = UUID(comment["comment_id"])
            assert comment["moderation_state"] == "active"

            report_response = client.post(
                f"/api/v1/discussions/posts/{post_id}/report"
            )
            assert report_response.status_code == 200
            assert report_response.json() == {"moderation_state": "reported"}
            assert client.get(f"/api/v1/discussions/posts/{post_id}").json()[
                "moderation_state"
            ] == "reported"
            reported_feed = client.get(
                "/api/v1/discussions/posts",
                params={"project_id": str(project_id)},
            ).json()
            assert [post["post_id"] for post in reported_feed] == [str(post_id)]

            unauthorized_moderation = client.put(
                f"/api/v1/discussions/moderation/posts/{post_id}",
                json={"moderation_state": "hidden_by_moderator"},
            )
            assert unauthorized_moderation.status_code == 403

            moderation_response = client.put(
                f"/api/v1/discussions/moderation/posts/{post_id}",
                headers={"X-Moderator-Role": "faculty"},
                json={"moderation_state": "hidden_by_moderator"},
            )
            assert moderation_response.status_code == 200
            assert moderation_response.json() == {
                "moderation_state": "hidden_by_moderator"
            }

            assert client.get(f"/api/v1/discussions/posts/{post_id}").status_code == 404
            feed_response = client.get(
                "/api/v1/discussions/posts",
                params={"project_id": str(project_id)},
            )
            assert feed_response.status_code == 200
            assert all(
                post["post_id"] != str(post_id) for post in feed_response.json()
            )
            timeline_response = client.get(
                f"/api/v1/discussions/scopes/projects/{project_id}/timeline"
            )
            assert timeline_response.status_code == 200
            assert all(
                post["post_id"] != str(post_id) for post in timeline_response.json()
            )
            assert client.get(comments_url).status_code == 404
            assert client.get(comments_url, params={"format": "text"}).status_code == 404
            assert client.get(f"{comments_url}/{comment_id}").status_code == 404

            restore_response = client.put(
                f"/api/v1/discussions/moderation/posts/{post_id}",
                headers={"X-Moderator-Role": "faculty"},
                json={"moderation_state": "active"},
            )
            assert restore_response.status_code == 200
            assert client.get(f"/api/v1/discussions/posts/{post_id}").status_code == 200
            assert [
                comment["comment_id"] for comment in client.get(comments_url).json()
            ] == [str(comment_id)]
    finally:
        if post_id is not None:
            with SessionLocal.begin() as db:
                db.execute(
                    delete(DiscussionPost).where(DiscussionPost.post_id == post_id)
                )


def test_hidden_comment_suppresses_nested_replies_only() -> None:
    post_id: UUID | None = None

    try:
        with TestClient(app) as client:
            post_response = client.post(
                "/api/v1/discussions/posts",
                json={
                    "project_id": str(uuid4()),
                    "title": "Comment moderation",
                    "body": "Nested visibility test",
                    "tags": ["moderation"],
                },
            )
            assert post_response.status_code == 201
            post_id = UUID(post_response.json()["post_id"])
            comments_url = f"/api/v1/discussions/posts/{post_id}/comments"

            root_response = client.post(
                comments_url,
                json={"message": "Hidden parent", "author_handle": "root-author"},
            )
            assert root_response.status_code == 201
            root_comment = root_response.json()
            root_id = UUID(root_comment["comment_id"])

            reply_response = client.post(
                comments_url,
                json={
                    "message": "Reply hidden by its parent",
                    "author_handle": "reply-author",
                    "parent_comment_id": str(root_id),
                },
            )
            assert reply_response.status_code == 201
            reply_comment = reply_response.json()
            reply_id = UUID(reply_comment["comment_id"])

            deep_reply_response = client.post(
                comments_url,
                json={
                    "message": "Nested reply also hidden",
                    "author_handle": "deep-author",
                    "parent_comment_id": str(reply_id),
                },
            )
            assert deep_reply_response.status_code == 201
            deep_reply_id = UUID(deep_reply_response.json()["comment_id"])

            unrelated_response = client.post(
                comments_url,
                json={
                    "message": "Unrelated visible comment",
                    "author_handle": "unrelated-author",
                },
            )
            assert unrelated_response.status_code == 201
            unrelated_id = UUID(unrelated_response.json()["comment_id"])

            report_response = client.post(
                f"{comments_url}/{root_id}/report"
            )
            assert report_response.status_code == 200
            assert report_response.json() == {"moderation_state": "reported"}
            reported_thread = client.get(comments_url).json()
            assert reported_thread[0]["moderation_state"] == "reported"
            assert UUID(reported_thread[0]["comment_id"]) == root_id

            moderation_response = client.put(
                f"/api/v1/discussions/moderation/posts/{post_id}/comments/{root_id}",
                headers={"X-Moderator-Role": "faculty"},
                json={"moderation_state": "hidden_by_moderator"},
            )
            assert moderation_response.status_code == 200
            assert moderation_response.json() == {
                "moderation_state": "hidden_by_moderator"
            }

            list_response = client.get(comments_url)
            assert list_response.status_code == 200
            assert [UUID(comment["comment_id"]) for comment in list_response.json()] == [
                unrelated_id
            ]
            for hidden_id in (root_id, reply_id, deep_reply_id):
                assert client.get(f"{comments_url}/{hidden_id}").status_code == 404

            text_response = client.get(comments_url, params={"format": "text"})
            assert text_response.status_code == 200
            assert "Unrelated visible comment" in text_response.text
            assert "Hidden parent" not in text_response.text
            assert "Reply hidden by its parent" not in text_response.text
            assert "Nested reply also hidden" not in text_response.text

            blocked_reply_response = client.post(
                comments_url,
                json={
                    "message": "Cannot reply under hidden content",
                    "author_handle": "new-author",
                    "parent_comment_id": str(root_id),
                },
            )
            assert blocked_reply_response.status_code == 404

            restore_response = client.put(
                f"/api/v1/discussions/moderation/posts/{post_id}/comments/{root_id}",
                headers={"X-Moderator-Role": "faculty"},
                json={"moderation_state": "active"},
            )
            assert restore_response.status_code == 200
            restored_comments = client.get(comments_url).json()
            assert [UUID(comment["comment_id"]) for comment in restored_comments] == [
                root_id,
                reply_id,
                deep_reply_id,
                unrelated_id,
            ]
    finally:
        if post_id is not None:
            with SessionLocal.begin() as db:
                db.execute(
                    delete(DiscussionPost).where(DiscussionPost.post_id == post_id)
                )


def test_course_and_lab_timelines_include_associated_projects() -> None:
    created_post_ids: list[UUID] = []
    course_id = uuid4()
    lab_id = uuid4()
    course_project_ids = [uuid4(), uuid4()]
    lab_project_ids = [uuid4(), uuid4()]
    unrelated_project_id = uuid4()
    base_time = datetime(2026, 2, 1, tzinfo=timezone.utc)

    try:
        with TestClient(app) as client:
            with SessionLocal.begin() as db:
                db.add_all(
                    [
                        *(ProjectCourseAssociation(
                            project_id=project_id,
                            course_id=course_id,
                        ) for project_id in course_project_ids),
                        *(ProjectLabAssociation(
                            project_id=project_id,
                            lab_id=lab_id,
                        ) for project_id in lab_project_ids),
                    ]
                )

            def create_timed_post(
                title: str,
                scope_type: str,
                scope_id: UUID,
                created_at: datetime,
            ) -> UUID:
                response = client.post(
                    "/api/v1/discussions/posts",
                    json={
                        "category": "Project Update Blogs",
                        "scope_type": scope_type,
                        "scope_id": str(scope_id),
                        "title": title,
                        "body": f"Timeline fixture: {title}",
                        "tags": ["timeline"],
                    },
                )
                assert response.status_code == 201, response.text
                post_id = UUID(response.json()["post_id"])
                created_post_ids.append(post_id)
                with SessionLocal.begin() as db:
                    db.execute(
                        update(DiscussionPost)
                        .where(DiscussionPost.post_id == post_id)
                        .values(created_at=created_at)
                    )
                return post_id

            course_direct = create_timed_post(
                "Course direct",
                "course",
                course_id,
                base_time,
            )
            course_project_one = create_timed_post(
                "Course project one",
                "project",
                course_project_ids[0],
                base_time + timedelta(minutes=1),
            )
            course_project_two = create_timed_post(
                "Course project two",
                "project",
                course_project_ids[1],
                base_time + timedelta(minutes=2),
            )
            course_unrelated = create_timed_post(
                "Course unrelated project",
                "project",
                unrelated_project_id,
                base_time + timedelta(minutes=3),
            )
            course_hidden = create_timed_post(
                "Course hidden associated project post",
                "project",
                course_project_ids[0],
                base_time + timedelta(minutes=4),
            )

            lab_direct = create_timed_post(
                "Lab direct",
                "research_lab",
                lab_id,
                base_time,
            )
            lab_project_one = create_timed_post(
                "Lab project one",
                "project",
                lab_project_ids[0],
                base_time + timedelta(minutes=1),
            )
            lab_project_two = create_timed_post(
                "Lab project two",
                "project",
                lab_project_ids[1],
                base_time + timedelta(minutes=2),
            )
            lab_unrelated = create_timed_post(
                "Lab unrelated project",
                "project",
                unrelated_project_id,
                base_time + timedelta(minutes=3),
            )
            lab_hidden = create_timed_post(
                "Lab hidden associated project post",
                "project",
                lab_project_ids[1],
                base_time + timedelta(minutes=4),
            )

            for post_id in (course_hidden, lab_hidden):
                response = client.put(
                    f"/api/v1/discussions/moderation/posts/{post_id}",
                    headers={"X-Moderator-Role": "faculty"},
                    json={"moderation_state": "hidden_by_moderator"},
                )
                assert response.status_code == 200

            for scope_url, scope_id, expected_ids, excluded_ids in (
                (
                    "courses",
                    course_id,
                    [course_direct, course_project_one, course_project_two],
                    [course_unrelated, course_hidden],
                ),
                (
                    "labs",
                    lab_id,
                    [lab_direct, lab_project_one, lab_project_two],
                    [lab_unrelated, lab_hidden],
                ),
            ):
                response = client.get(
                    f"/api/v1/discussions/scopes/{scope_url}/{scope_id}/timeline"
                )
                assert response.status_code == 200, response.text
                timeline = response.json()
                timeline_ids = [UUID(post["post_id"]) for post in timeline]
                assert timeline_ids == expected_ids
                assert len(timeline_ids) == len(set(timeline_ids))
                assert not set(excluded_ids).intersection(timeline_ids)
                timeline_times = [
                    datetime.fromisoformat(post["created_at"]) for post in timeline
                ]
                assert timeline_times == sorted(timeline_times)
    finally:
        with SessionLocal.begin() as db:
            db.execute(
                delete(ProjectCourseAssociation).where(
                    ProjectCourseAssociation.course_id == course_id
                )
            )
            db.execute(
                delete(ProjectLabAssociation).where(
                    ProjectLabAssociation.lab_id == lab_id
                )
            )
            if created_post_ids:
                db.execute(
                    delete(DiscussionPost).where(
                        DiscussionPost.post_id.in_(created_post_ids)
                    )
                )
