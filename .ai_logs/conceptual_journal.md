# Master Conceptual Journal & AI Telemetry Log

- **Student:** Stephanie Wang
- **Assignment:** Project Assignment 2 — The Naive Baseline
- **Assigned domain:** Domain 4 — Research Blog & Project Discussion Board
- **Core stack:** Python, FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Docker Compose, and GitHub Actions

## AI Usage Log

- **Estimated conceptual AI contribution to this journal:** 70%
- **AI assistance:** I used GitHub Copilot to generate and revise the application, integration tests, and CI workflow. I used ChatGPT to interpret the rubric, draft the security reports, and revise this journal. I used Claude to review my SAST report and interpret the local MF-1 results, then asked ChatGPT to check that feedback against the rubric.
- **My contribution:** I compared the implementation and tests with the Domain 4 requirements, ran integration tests, checked the hosted scanner results, and tested MF-1 locally.

## 1. System Environment & Tool Specification

### 1.1 AI Tool & Engine Deployments

| Tool context                                 | Platform                  | Model or setting I could verify                                                                                              | Access mode                              |
| -------------------------------------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| Application code, integration tests, and CI  | GitHub Copilot in VS Code | Auto mode. Some session entries show `agent-host-copilotcli:auto`. The underlying model was not identified in those entries. | Agent mode in my local VS Code workspace |
| Planning, documentation, and threat modeling | ChatGPT                   | Exact model identifier unverified                                                                                            | Web chat                                 |
| SAST report and MF-1 evidence review         | Claude                    | Exact model identifier unverified                                                                                            | Web chat                                 |

### 1.2 Verification Telemetry Access Checklist

- **AI usage summary:** `code_AI_history.md` records the dates and summaries of my PA2 prompts and responses.
- **Copilot session export:** I used the export to verify the dates of my Copilot interactions. I retained the export privately.
- **Repository records:** The `.ai_logs/` folder contains my conceptual journal and dated AI usage summaries.

## 2. Cognitive Reflection — Code Generation & Comprehension

### 2.1 The Architectural Flow

I followed the post-creation route because it was the first feature I tested. FastAPI takes the JSON request body and parses it using the `DiscussionPostCreate` schema. Pydantic checks the structure and types before the handler processes the request. FastAPI also provides a SQLAlchemy session through the `get_db` dependency.

The handler uses the parsed fields to create a `DiscussionPost` object. It adds the object to the session, commits the transaction, and refreshes the object with the stored values. FastAPI uses the response schema to return the saved post, including the UUID used by the retrieval route. The `get_db` dependency opens the session in a context manager, which closes it when the dependency exits. I verified that the service could save and retrieve a post. I did not test a forced database failure or observe rollback behavior.

The code uses dependency injection to provide the database session and SQLAlchemy’s ORM to map Python objects to PostgreSQL tables. The route handler performs the database operations directly. The request and response schemas are defined separately from the database models.

### 2.2 Defensive Edge-Case Evaluation

| Area                       | Code or test reviewed                                                                                         | What I found and checked                                                                                                                                                                                                      |
| -------------------------- | ------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Directly scoped timelines  | `test_post_listing_filters_and_scope_timeline` in `functional-codebase/tests/discussion_posts_integration.py` | The original test covered a post attached directly to the course. It left the master specification’s associated-project behavior untested.                                                                                    |
| Course and lab timelines   | `test_course_and_lab_timelines_include_associated_projects` in the same test file                             | The revised test covers posts from associated projects and checks ordering and visibility. I reran the full PA2 suite locally and all seven tests passed.                                                                     |
| PostgreSQL JSON comparison | Timeline query in `functional-codebase/app/main.py`                                                           | Copilot’s first revision used `DISTINCT`. PostgreSQL could not compare the JSON tags column for equality, so that test run failed. Copilot removed `DISTINCT` and reported a passing rerun. My later local suite also passed. |
| Nested comment visibility  | `test_hidden_comment_suppresses_nested_replies_only` in the integration test file                             | A reply can keep its `active` state while its parent is hidden. The test covers how hiding a parent affects nested replies. That visibility rule matters for the comment list and the text export.                            |

The lecture discussion about AI-generated tests helped me understand the timeline gap. The original test passed because its expected result matched the initial implementation. Comparing that result with the Domain 4 specification showed me that I needed a test with posts from multiple associated projects.

### 2.3 Security Shortcuts in the Baseline

I chose a mock faculty header so I could test hiding and restoring content. The baseline used that value to decide whether to allow moderation. For a deployed service, I proposed verifying the caller’s identity and checking whether that person has permission to moderate the specific scope.

The post routes also helped me see the difference between request validation and authorization. The schema checks the request fields. The handler still needs to check whether the caller has permission to change that specific post. My local MF-1 checks showed that the baseline accepted an update and a separate deletion without credentials.

The text export returns the visible thread, but the source builds the entire response in memory without an application-level size limit. I documented the missing limit from the source. I did not measure memory use or response time for large exports.

## 3. Cognitive Reflection — Document Authoring & Threat Design

### 3.1 AI Collaboration for Security Analysis

I first asked ChatGPT to break down the PA2 rubric. I then used my route list and database structure to describe what moves between the client, FastAPI, and PostgreSQL. That data flow gave me a basis for the security requirements, abuse cases, attack trees, and STRIDE matrix. After documenting the SAST findings, I revised the mitigation table so it addressed the same weaknesses.

For the SAST report, I used ChatGPT to interpret the GitHub Actions artifact and organize the findings. Claude helped me review the local MF-1 evidence and the report draft. I then asked ChatGPT to compare that feedback with the assignment rubric and refine the validation wording.

### 3.2 Evaluation of AI Blind Spots

My first triage draft stopped after recording zero findings from both scanners. The rubric also required three validated vulnerabilities across different layers. I kept the scanner results in the ledger and added the manual findings with a CWE ID, root cause, and evidence for each.

I distinguished the evidence for each finding. MF-1 had local runtime evidence. MF-2 came from source review of the comment query and export. MF-3 came from source review of the database connection fallback. I kept the deployment impact conditional because the configuration I reviewed was for local development.

The hosted run also showed why passing tests and reported coverage are different. The test log showed that all seven tests passed. SonarQube showed 0.0% new-code coverage, and the workflow did not generate a coverage report for it to import. I recorded both results in the SAST report.

When I compared the STRIDE matrix with the first mitigation table, I saw that the matrix discussed risks on the client-to-API connection, while the mitigation table only addressed protecting database connections. I added HTTPS for client-to-API traffic outside local development. This gave me a specific example of checking whether each risk in the matrix had a corresponding control.

## 4. Human Verification & Audit Trail

Dates indicate when I reviewed, shared, or documented the evidence. They identify the record when the original execution timestamp is unavailable.

| Date and record                             | Component                                      | Method                                                                                           | Verified outcome                                                                                                                                                  |
| ------------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| November 13, 2026 (terminal log shared)     | Post creation and retrieval                    | Ran the PostgreSQL integration test locally.                                                     | Both runs passed. The test checked that a saved post could be retrieved by UUID.                                                                                  |
| November 13, 2026 (terminal log shared)     | Post lifecycle, filters, and initial timelines | Reran the PostgreSQL integration tests after the changes.                                        | The lifecycle run reported `1 passed`. The filters and direct-scope timeline run reported `2 passed`.                                                             |
| November 13, 2026 (terminal log shared)     | Revised course and lab timelines               | Ran the full PA2 PostgreSQL integration suite locally.                                           | All seven tests passed, including the test for timelines with associated projects.                                                                                |
| November 13, 2026 (hosted results reviewed) | GitHub Actions and SAST scans                  | Reviewed the PR artifact and checked the SonarQube Cloud Issues page after clearing the filters. | All seven PA2 tests passed. Semgrep reported zero findings and zero errors. SonarQube showed zero new issues, and its Quality Gate failed on new-code coverage.   |
| November 14, 2026 (result documented)       | MF-1 — Post authorization                      | Reviewed the handlers and checked the running application locally.                               | The update returned `200 OK` and showed a changed title and author handle. A separate deletion returned `204 No Content`. Both were accepted without credentials. |
| November 14, 2026 (finding documented)      | MF-2 — Comment export                          | Reviewed the comment query and text response assembly.                                           | The query has no row limit, and the export has no output-size cap. Runtime resource usage was not measured.                                                       |
| November 14, 2026 (finding documented)      | MF-3 — Database configuration                  | Reviewed `DEFAULT_DATABASE_URL` and how the database engine selects it.                          | The engine uses fixed development credentials when `DATABASE_URL` is unset. Exposure outside local development was not established.                               |
