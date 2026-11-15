# Code AI History

## AI Usage Log

- **Estimated conceptual AI contribution to this document:** 85%
- **GitHub Copilot Agent mode in VS Code:** I used Copilot to build the PA2 discussion board, add integration tests, update course and lab timelines, and configure GitHub Actions.
- **ChatGPT:** I used ChatGPT to understand the PA2 requirements, draft prompts, interpret scan results, and organize the SAST report, security analysis, and AI logs. I also asked it to check the feedback on my SAST report against the assignment rubric.
- **Claude:** I used Claude to interpret my local MF-1 results and review the SAST report.
- **My work:** I set up the branch, reviewed the generated changes, reran integration tests, checked the hosted scan results, and tested MF-1 locally.

## GitHub Copilot

The dates in this section come from the Copilot session history in Pacific Time. The prompts and responses are summarized.

### 1. Save and retrieve a project update

- **Date:** November 12, 2026
- **Prompt summary:** I asked Copilot to build FastAPI endpoints that save a project update in PostgreSQL and retrieve the same update by UUID. I also asked for an integration test that checks both operations.
- **Response summary:** Copilot added the endpoints and test. The root pytest command picked up the PA2 test in the A1 environment, which lacked the PA2 dependencies. Copilot renamed the test file and documented how to run it directly.
- **What I checked:** I ran the integration test twice with PostgreSQL running. Both runs passed.

### 2. Complete the post lifecycle

- **Date:** November 12, 2026
- **Prompt summary:** I asked Copilot to support both post categories, add project, course, and lab scopes, and implement post updates and deletions.
- **Response summary:** Copilot added the remaining operations and preserved compatibility with requests that use `project_id`. It reported checking whether a post saved before the schema upgrade could still be read afterward.
- **What I checked:** I reran the expanded integration test and got `1 passed`.

### 3. Add post filters and timelines

- **Date:** November 12, 2026
- **Prompt summary:** I asked Copilot to let users filter posts by keyword, date, author, scope, and category and to return a chronological timeline for the requested scope.
- **Response summary:** Copilot combined the filters and built timelines from posts attached directly to each scope.
- **What I checked:** The local run returned `2 passed`. Those tests covered directly scoped posts. The requirement to include posts from associated projects still needed a test.

### 4. Build comment threads, search, and export

- **Date:** November 12, 2026
- **Prompt summary 1:** I asked Copilot to support replies at multiple levels and test how comment deletion affects the thread.
- **Response summary 1:** Copilot used parent comment IDs to connect replies and blocked deletion of a comment that still had replies. It reported `3 passed` for PA2.
- **Prompt summary 2:** I asked Copilot to add keyword and author filters and a plain-text export of the full comment thread.
- **Response summary 2:** Copilot added case-insensitive keyword matching, exact author matching, and a text export that indents replies. It reported `4 passed` for PA2 and `1 passed` for A1.

### 5. Add moderation

- **Date:** November 12, 2026
- **Prompt summary:** I asked Copilot to implement reporting, hiding, and restoring for posts and comments and check how those actions affect content visibility.
- **Response summary:** Copilot added moderation states and tested visibility in feeds, timelines, comment lists, and exports. I chose a mock faculty header for the PA2 workflow.
- **Verification:** Copilot reported `6 passed` for PA2 and `1 passed` for A1. I later documented the risk of trusting the role supplied by the client.

### 6. Fix course and lab timelines

- **Date:** November 12, 2026
- **Prompt summary:** I asked Copilot to include posts from associated projects alongside directly scoped posts, keep them in chronological order, and exclude unrelated or hidden content.
- **Response summary:** Copilot added PostgreSQL tables to associate projects with courses and labs. Its first query failed because `DISTINCT` tried to compare the JSON tags column. Copilot removed `DISTINCT` and reran the tests.
- **What I checked:** My later local run passed all seven PA2 tests, including the test for course and lab timelines with associated projects.

### 7. Update GitHub Actions

- **Date:** November 13, 2026
- **Prompt summary:** I asked Copilot to keep the A1 health test, run the PA2 integration suite against PostgreSQL, scan the PA2 app with Semgrep and SonarQube, save the results as artifacts, and pin the actions to full commit SHAs.
- **Response summary:** Copilot updated the workflow and kept the SonarQube processing wait and scanner error reporting. Trivy continued to scan the A1 Docker image.
- **What I checked:** The hosted run passed all seven PA2 tests. I checked the Semgrep results and the SonarQube Cloud Issues page for PR #1.

## ChatGPT and Claude

### 1. Plan PA2 and set up the branch

- **Documented on:** November 13, 2026
- **Tool:** ChatGPT
- **Prompt summary:** I asked which parts of A1 I could reuse and how the Domain 4 master specification would affect the PA2 implementation.
- **Response summary:** ChatGPT helped me identify which parts of the FastAPI setup and GitHub Actions workflow could carry forward.
- **What I checked:** I created `assignment-2` and confirmed it started from commit `11ef840`, tagged `Assignment-1-1`.

### 2. Interpret the hosted scan results

- **Date:** November 13, 2026
- **Tool:** ChatGPT
- **Prompt summary:** I uploaded the GitHub Actions artifact and asked whether it contained the evidence I needed for the PA2 SAST report.
- **Response summary:** ChatGPT identified the pytest log, the Semgrep report, and the SonarQube processing result. It explained why I also needed to check the SonarQube Cloud PR page.
- **What I checked:** All seven PA2 tests passed. Semgrep reported zero findings and zero errors. After clearing the Issues filters, I confirmed that SonarQube showed zero new issues. The Quality Gate failed on new-code coverage. The workflow ran pytest without generating a coverage report.

### 3. Draft and revise the SAST triage report

- **Date:** November 14, 2026
- **Tool:** ChatGPT
- **Prompt summary:** I asked how to report zero scanner alerts while addressing the rubric’s requirement for three validated vulnerabilities across different software layers.
- **Response summary:** ChatGPT helped me organize the manual findings by API authorization, response processing, and database configuration and explain each finding’s CWE mapping, root cause, and proposed fix.
- **What I changed:** I gave each manual finding its own ledger row and identified the evidence supporting it.

### 4. Review the MF-1 evidence and SAST report

- **Transcript reviewed on:** November 14, 2026
- **Tools:** Claude and ChatGPT
- **Prompt summary:** I asked Claude to review my SAST report and check whether the MF-1 wording matched my local results. I then shared Claude’s feedback with ChatGPT and asked it to reread the rubric.
- **Response summary:** Claude recommended keeping the local MF-1 evidence and distinguishing the manual findings from the scanner results. ChatGPT checked that advice against the rubric and helped me describe what the local checks established.
- **What I checked:** My local update returned `200 OK` and showed changes to the title and author handle. A separate deletion returned `204 No Content`. I recorded both outcomes under MF-1 and documented MF-2 and MF-3 as source-review findings.

### 5. Analyze the PA2 architecture and propose controls

- **Date:** November 14, 2026
- **Tool:** ChatGPT
- **Prompt summary:** I asked for help analyzing how data moves between the client, FastAPI, and PostgreSQL and how to connect those trust boundaries to STRIDE, abuse cases, attack trees, and proposed controls.
- **Response summary:** ChatGPT helped me draft the security requirements, attack surface map, data flow diagram, STRIDE matrix, and three attack trees.
- **What I learned:** A client-supplied role does not establish faculty permission. The server needs a verified identity and a permission check for the target scope. Course and lab timelines also include posts from associated projects, so authorization needs to account for those posts.
- **What I changed:** I linked the mitigation table to MF-1 through MF-3 and added recommendations for audit records and HTTPS.
