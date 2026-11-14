# Code AI History

## AI Usage Log

- I used ChatGPT to understand the PA2 instructions, draft prompts for Copilot, and organize this history.
- I used GitHub Copilot Agent mode in VS Code to build the app, add tests, and update GitHub Actions.
- I reviewed the results and reran several tests myself.
- Estimated conceptual AI contribution to this document — 50%

## Project Assignment 2

### 1. Set up my PA2 branch

- I asked ChatGPT how to start PA2 using my A1 work and Steve’s feedback.
- I created the `assignment-2` branch and verified that it started from my submitted A1 commit, `11ef840`.

### 2. Create and retrieve a project update

- I asked Copilot to save a project update in PostgreSQL and retrieve it by UUID.
- The A1 pytest run picked up the PA2 test and failed because the A1 environment lacked the PA2 dependencies. Copilot renamed the test and documented how to run it by its file path.
- I ran the PostgreSQL integration test twice. Both runs passed.

### 3. Finish the post lifecycle

- I asked Copilot to support both post categories, add course and lab scopes, and add update and delete endpoints.
- Copilot kept the original `project_id` request working and reported checking the database upgrade with an existing post.
- I reran the expanded integration test and got `1 passed`.

### 4. Add post search and timelines

- I asked Copilot to add post filters and chronological timelines.
- The first version only included posts attached directly to the requested scope.
- I ran the PostgreSQL integration tests and got `2 passed`.

### 5. Add nested comments

- I asked Copilot to add comment endpoints and test replies at multiple levels.
- Copilot used parent comment IDs to connect replies and blocked deletion of comments that still had replies.
- Copilot reported `3 passed` for PA2.

### 6. Add comment search and text export

- I asked Copilot to add keyword and author filters and a plain-text download of the full comment thread.
- Copilot kept JSON as the default and added `?format=text` for the download. The text file uses indentation to show nested replies.
- Copilot reported `4 passed` for PA2 and `1 passed` for A1.

### 7. Add moderation

- I asked Copilot to add reporting, hiding, and restoring for posts and comments. I chose a mock faculty header to test the moderation workflow.
- Copilot added tests for how hiding and restoring content affects feeds, timelines, comments, and text downloads.
- Copilot reported `6 passed` for PA2. I got `8 passed` in a separate local run before the timeline fix.

### 8. Review timelines against the master spec

- I asked Copilot to compare the course and lab timelines with the Domain 4 master spec.
- The review found that the tests only checked directly scoped posts. They never linked two projects to the same course and checked that posts from both projects appeared.
- I used that gap to write the next prompt.

### 9. Fix course and lab timelines

- I asked Copilot to include posts from associated projects alongside posts attached directly to the course or lab. I also asked it to test that unrelated and hidden posts stayed out.
- Copilot added PostgreSQL association tables. The first test run failed because `DISTINCT` tried to compare the JSON tags column. Copilot removed `DISTINCT` and reran the tests.
- Copilot reported `7 passed` for PA2 and `1 passed` for A1.

### 10. Update GitHub Actions for PA2

- I asked Copilot to keep the A1 test, run the PA2 tests against PostgreSQL, scan the PA2 app with Semgrep and SonarQube, and save the results as workflow artifacts.
- Copilot pinned the actions to full commit SHAs and kept the SonarQube processing wait and scanner error reporting. Trivy still scans the A1 image.
- Copilot reported that the workflow YAML parsed and that the local checks passed with `1 passed` for A1 and `7 passed` for PA2. I still need to verify the hosted GitHub Actions run.