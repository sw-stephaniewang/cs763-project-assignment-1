# Research Blog & Project Discussion Board

## CS763 — Assignment 1 Service Specification

## AI Usage Summary

- **AI tool:** ChatGPT
- **Estimated AI contribution:** 50%
- **AI assistance:** ChatGPT helped explain the assignment, organize this document, suggest database fields, and draft and revise the wording.
- **My contribution and review:** I chose the features and permission rules, including group-only access, progress posts for both roles, instructor announcements, and moderation. I reviewed the suggestions and clarified that instructors cannot edit another member's writing.
- **Detailed interaction history:** See `Prompt_test_log.md` for prompts, output summaries, and my revisions.

## 1. Service Purpose

This backend service lets students and instructors share academic project progress within their group. Members can leave comments to offer support, give feedback, or discuss the work. Instructors can also publish group announcements.

Each group has a private feed. People outside the group cannot access its posts, announcements, or comments.

## 2. Technology Stack

- **Language:** Python
- **Backend framework:** FastAPI
- **Database:** PostgreSQL
- **Container environment:** Docker and Docker Compose
- **Automated pipeline:** GitHub Actions

## 3. Service Scope

The service includes progress posts, announcements, comments, and the permission rules described below.

It runs independently of other students' services. Information about users and groups comes from local mock data.

## 4. Users and Permissions

These permissions apply only within a group where the user is a member.

| Action                                                         | Student | Instructor |
| -------------------------------------------------------------- | ------- | ---------- |
| View posts, announcements, and comments                        | Yes     | Yes        |
| Create progress posts                                          | Yes     | Yes        |
| Edit or delete their own progress posts                        | Yes     | Yes        |
| Add comments                                                   | Yes     | Yes        |
| Edit or delete their own comments                              | Yes     | Yes        |
| Create announcements                                           | No      | Yes        |
| Edit or delete their own announcements                         | No      | Yes        |
| Delete another member's inappropriate progress post or comment | No      | Yes        |
| Edit another member's content                                  | No      | No         |
| Access a group without membership                              | No      | No         |

Announcements can only be edited or deleted by their author, including when a group has more than one instructor.

Instructors decide whether a progress post or comment is inappropriate. The service does not automatically judge the content.

## 5. Database Model

Posts and comments are saved in PostgreSQL. All columns below are required and cannot be null.

### 5.1 Posts Table

The `posts` table stores both progress posts and announcements.

| Column       | PostgreSQL Type | Purpose                              |
| ------------ | --------------- | ------------------------------------ |
| `post_id`    | INTEGER         | Automatically generated primary key. |
| `group_id`   | INTEGER         | Group the post belongs to.           |
| `author_id`  | INTEGER         | User who wrote the post.             |
| `post_type`  | VARCHAR(20)     | Either `progress` or `announcement`. |
| `title`      | VARCHAR(200)    | Post title.                          |
| `content`    | TEXT            | Main text of the post.               |
| `created_at` | TIMESTAMPTZ     | Time the post was created.           |
| `updated_at` | TIMESTAMPTZ     | Time the post was last edited.       |

### 5.2 Comments Table

The `comments` table stores comments on either type of post.

| Column       | PostgreSQL Type | Purpose                                                           |
| ------------ | --------------- | ----------------------------------------------------------------- |
| `comment_id` | INTEGER         | Automatically generated primary key.                              |
| `post_id`    | INTEGER         | Foreign key referencing `posts.post_id` with `ON DELETE CASCADE`. |
| `author_id`  | INTEGER         | User who wrote the comment.                                       |
| `content`    | TEXT            | Comment text.                                                     |
| `created_at` | TIMESTAMPTZ     | Time the comment was created.                                     |
| `updated_at` | TIMESTAMPTZ     | Time the comment was last edited.                                 |

### 5.3 Entity Relationships

- A user can belong to multiple groups through membership records.
- A group can have multiple users.
- Each post belongs to one group and has one author.
- A group can have many posts, and a user can write many posts.
- Each comment belongs to one post and has one author.
- A post can have many comments, and a user can write many comments.

A comment belongs to the same group as its post. Deleting a post also deletes its comments.

Users and groups are stored in the mock data file, so their IDs are checked by the backend rather than database foreign keys.

## 6. Local Static Mock Data

The following fictional records will be stored in a local static JSON file named `mock_data.json`. The service does not request this information from other services.

The file contains three arrays: `users`, `groups`, and `memberships`.

### 6.1 Mock Users

Each user has a unique integer `user_id` and a string `display_name`.

| user_id | display_name       |
| ------- | ------------------ |
| 1       | Alex Chen          |
| 2       | Bella Patel        |
| 3       | Chloe Kim          |
| 4       | Daniel Lee         |
| 5       | Emma Garcia        |
| 6       | Finn Davis         |
| 7       | Grace Wilson       |
| 8       | Dr. Xavier Morgan  |
| 9       | Dr. Yvonne Brown   |
| 10      | Dr. Zachary Taylor |

### 6.2 Mock Groups

Each group has a unique integer `group_id` and a string `group_name`.

| group_id | group_name      |
| -------- | --------------- |
| 1        | Project Group A |
| 2        | Project Group B |

### 6.3 Mock Memberships

A membership connects a user to a group. Both IDs are integers. The `role` is a string containing either `student` or `instructor`.

The same user cannot be listed twice in the same group. Every membership must refer to an existing user and group.

| user_id | group_id | role       |
| ------- | -------- | ---------- |
| 1       | 1        | student    |
| 2       | 1        | student    |
| 3       | 1        | student    |
| 4       | 1        | student    |
| 5       | 2        | student    |
| 6       | 2        | student    |
| 7       | 2        | student    |
| 8       | 1        | instructor |
| 9       | 2        | instructor |
| 10      | 2        | instructor |

Group A has four students and one instructor. Group B has three students and two instructors.

The backend checks these memberships to decide which group a user can access and which actions they can take.

### 6.4 Planned JSON File Structure

The complete contents of `mock_data.json` will follow this structure:

```json
{
  "users": [
    { "user_id": 1, "display_name": "Alex Chen" },
    { "user_id": 2, "display_name": "Bella Patel" },
    { "user_id": 3, "display_name": "Chloe Kim" },
    { "user_id": 4, "display_name": "Daniel Lee" },
    { "user_id": 5, "display_name": "Emma Garcia" },
    { "user_id": 6, "display_name": "Finn Davis" },
    { "user_id": 7, "display_name": "Grace Wilson" },
    { "user_id": 8, "display_name": "Dr. Xavier Morgan" },
    { "user_id": 9, "display_name": "Dr. Yvonne Brown" },
    { "user_id": 10, "display_name": "Dr. Zachary Taylor" }
  ],
  "groups": [
    { "group_id": 1, "group_name": "Project Group A" },
    { "group_id": 2, "group_name": "Project Group B" }
  ],
  "memberships": [
    { "user_id": 1, "group_id": 1, "role": "student" },
    { "user_id": 2, "group_id": 1, "role": "student" },
    { "user_id": 3, "group_id": 1, "role": "student" },
    { "user_id": 4, "group_id": 1, "role": "student" },
    { "user_id": 5, "group_id": 2, "role": "student" },
    { "user_id": 6, "group_id": 2, "role": "student" },
    { "user_id": 7, "group_id": 2, "role": "student" },
    { "user_id": 8, "group_id": 1, "role": "instructor" },
    { "user_id": 9, "group_id": 2, "role": "instructor" },
    { "user_id": 10, "group_id": 2, "role": "instructor" }
  ]
}
```

This structure describes the proposed service. Loading and using the mock data will be implemented with the discussion-board features, subject to the professor's standardized specification for the later assignments.

## 7. REST API Endpoints

All endpoints require membership in the group shown in the URL. The ownership and instructor permissions in Section 4 also apply.

### 7.1 Posts and Announcements

Both types of posts use the same endpoints.

| Method | Endpoint                             | Purpose                                   |
| ------ | ------------------------------------ | ----------------------------------------- |
| GET    | `/groups/{group_id}/posts`           | List the group's posts and announcements. |
| POST   | `/groups/{group_id}/posts`           | Create a progress post or announcement.   |
| GET    | `/groups/{group_id}/posts/{post_id}` | View one post or announcement.            |
| PATCH  | `/groups/{group_id}/posts/{post_id}` | Edit the title or content.                |
| DELETE | `/groups/{group_id}/posts/{post_id}` | Delete a post and its comments.           |

Posts appear newest first. If two posts have the same creation time, the higher `post_id` comes first.

### 7.2 Comments

| Method | Endpoint                                                   | Purpose                  |
| ------ | ---------------------------------------------------------- | ------------------------ |
| GET    | `/groups/{group_id}/posts/{post_id}/comments`              | List comments on a post. |
| POST   | `/groups/{group_id}/posts/{post_id}/comments`              | Add a comment.           |
| PATCH  | `/groups/{group_id}/posts/{post_id}/comments/{comment_id}` | Edit a comment.          |
| DELETE | `/groups/{group_id}/posts/{post_id}/comments/{comment_id}` | Delete a comment.        |

Comments appear oldest first. If two comments have the same creation time, the lower `comment_id` comes first.

### 7.3 Checking the URL

The backend checks that the post belongs to the group shown in the URL. For comment requests, it also checks that the comment belongs to the specified post.

Changing an ID in the URL must not give someone access to another group's content.

## 8. Requests and Responses

Requests and responses with a body use JSON.

All IDs are whole numbers greater than zero. Every field shown in a post or comment response is returned with a value rather than null.

The backend creates post and comment IDs automatically. It gets the author ID from the requesting user and the group or post ID from the URL.

Times use ISO 8601 format in UTC, such as `2026-11-01T15:00:00Z`. When a record is created, `created_at` and `updated_at` are equal. An edit changes `updated_at` but keeps `created_at` the same.

### 8.1 Identifying the User

For local testing, requests include a mock user header:

```http
X-Mock-User-ID: 1
```

The value `1` means the request is being made as Alex Chen. The backend looks up the user and their memberships.

This is only for testing. Anyone can change the number, so it does not work as a real login. The later secure version will use JWT authentication.

### 8.2 Creating a Post

`POST /groups/{group_id}/posts`

| Field       | Type   | Required | Rule                                 |
| ----------- | ------ | -------- | ------------------------------------ |
| `post_type` | string | Yes      | Either `progress` or `announcement`. |
| `title`     | string | Yes      | 1–200 characters.                    |
| `content`   | string | Yes      | 1–10,000 characters.                 |

Example request:

```json
{
  "post_type": "progress",
  "title": "Database design completed",
  "content": "I finished the first draft of our tables."
}
```

A successful request returns `201 Created` with the saved post:

```json
{
  "post_id": 1,
  "group_id": 1,
  "author_id": 1,
  "post_type": "progress",
  "title": "Database design completed",
  "content": "I finished the first draft of our tables.",
  "created_at": "2026-11-01T15:00:00Z",
  "updated_at": "2026-11-01T15:00:00Z"
}
```

The IDs are integers. The other response fields are strings.

Announcements use the same fields with `post_type` set to `announcement`. Only a group instructor can create one.

### 8.3 Viewing and Editing Posts

Viewing one post returns `200 OK` with the same response fields shown above.

Viewing the group's feed returns `200 OK` with a JSON array of posts, ordered as described in Section 7. An empty feed returns `[]`.

To edit a post, its author sends:

`PATCH /groups/{group_id}/posts/{post_id}`

The request can contain `title`, `content`, or both, using the same types and length limits as creating a post. Fields left out stay the same.

Example:

```json
{
  "content": "I updated the tables after reviewing feedback."
}
```

The response is `200 OK` with the updated post.

Editing cannot change the post ID, group, author, or post type.

### 8.4 Creating and Editing Comments

`POST /groups/{group_id}/posts/{post_id}/comments`

| Field     | Type   | Required | Rule                |
| --------- | ------ | -------- | ------------------- |
| `content` | string | Yes      | 1–2,000 characters. |

Example request:

```json
{
  "content": "Thanks for the update. The table design looks clear."
}
```

A successful request returns `201 Created` with the saved comment:

```json
{
  "comment_id": 1,
  "post_id": 1,
  "author_id": 2,
  "content": "Thanks for the update. The table design looks clear.",
  "created_at": "2026-11-01T15:10:00Z",
  "updated_at": "2026-11-01T15:10:00Z"
}
```

The IDs are integers. The content and timestamps are strings.

To edit a comment, its author sends:

`PATCH /groups/{group_id}/posts/{post_id}/comments/{comment_id}`

The request must contain `content`, using the same rules as creating a comment.

Example:

```json
{
  "content": "Thanks for the update. Could you also explain the comments table?"
}
```

The response is `200 OK` with the updated comment.

Editing cannot change the comment ID, post ID, or author.

### 8.5 Viewing Comments

`GET /groups/{group_id}/posts/{post_id}/comments`

The response is `200 OK` with a JSON array of comment objects using the fields shown above. Comments follow the order described in Section 7.

A post without comments returns `[]`.

### 8.6 Deleting Content

DELETE requests do not need a JSON body.

A successful deletion returns `204 No Content` with no response body.

Deleting a post removes its comments through the database relationship described in Section 5. Deleting a comment leaves the post in place.

### 8.7 Invalid Requests and Errors

Extra spaces at the start or end of a title, post content, or comment are removed before checking its length.

Text cannot be empty, contain only whitespace, or be null. An edit request must include at least one field to update.

Users should send only the fields listed for that request. Extra fields are rejected. IDs, authors, groups, and timestamps cannot be set through the JSON body.

| Status                     | When it is returned                                                                                           |
| -------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `401 Unauthorized`         | The mock user header is missing or contains an unknown positive user ID.                                      |
| `403 Forbidden`            | The user is outside the group or does not have permission for the action.                                     |
| `404 Not Found`            | A group, post, or comment does not exist, or the post/comment does not belong to the parent shown in the URL. |
| `422 Unprocessable Entity` | A field, path ID, or mock user header has an invalid format or value.                                         |

Application errors explain the problem in a field called `detail`.

Example:

```json
{
  "detail": "You do not have permission to edit this post."
}
```

Input validation errors return a list of input problems under `detail`. A missing mock user header is handled separately with `401 Unauthorized`.



