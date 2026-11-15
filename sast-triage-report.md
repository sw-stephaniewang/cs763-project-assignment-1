# PA2 SAST Triage Report

## AI Deliverable Metadata

- **AI tools:** ChatGPT and Claude
- **Estimated conceptual AI contribution:** 50%
- **AI assistance:** I asked ChatGPT to help interpret the scanner results, organize the report, and match the manual findings to CWE IDs. It also helps interpret the MF-1 test results and review the report against the rubric.
- **Human verification:** I downloaded the GitHub Actions artifact, checked the SonarQube Cloud Issues page for PR #1 after clearing the filters, and checked MF-1 against the running app locally.

## Scan Results

I reviewed the results for PR #1 on the `assignment-2` branch. I downloaded `cs763-pa2-devsecops-reports.zip` from the [GitHub Actions run for PA2 PR #1](https://github.com/sw-stephaniewang/cs763-project-assignment-1/actions/runs/43572189442).

| Scanner         | Evidence                                             | Result                                                                                           |
| --------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Semgrep         | `semgrep.json`                                       | Scanned five Python files under `functional-codebase/app/` and reported 0 findings and 0 errors. |
| SonarQube Cloud | PR #1 Issues page and `sonar-processing-result.json` | Analysis finished successfully and reported 0 new issues.                                        |

## Triage

Semgrep and SonarQube Cloud reported zero findings for PR #1, so there were no scanner alerts to classify as true positives or false positives. The three confirmed findings came from manual review.

### Triage Ledger

| ID              | Source            | Classification                                      | Validation                                     |
| --------------- | ----------------- | --------------------------------------------------- | ---------------------------------------------- |
| Semgrep         | `semgrep.json`    | 0 findings                                          | Scan completed with 0 errors                   |
| SonarQube Cloud | PR #1 Issues page | 0 new issues                                        | Checked after clearing the filters             |
| MF-1            | Manual review     | Confirmed finding — missing authorization           | Source review and local runtime checks         |
| MF-2            | Manual review     | Confirmed finding — missing comment export limits   | Source review                                  |
| MF-3            | Manual review     | Confirmed finding — hard-coded fallback credentials | Source review of the development configuration |

## Tests and Quality Gate

All seven PA2 integration tests passed in GitHub Actions with one deprecation warning. The SonarQube Quality Gate failed because it showed 0.0% new-code coverage against an 80% threshold. The workflow ran pytest without generating a coverage report.

## Manual Findings

### MF-1 — Post updates and deletions lack authorization

- **Layer:** API authorization
- **CWE:** CWE-862 — Missing Authorization
- **Evidence:** `functional-codebase/app/main.py`, `update_discussion_post` and `delete_discussion_post`.
- **Root cause:** Both handlers look up the post by ID and then save the requested update or delete the record. Neither handler checks the caller's identity, ownership of the post, or permission to change it.
- **Impact:** A caller without permission to manage a post could change or delete it.
- **Validation:** I reviewed the source and checked the running app locally without credentials. The update returned `200 OK`, and the response showed that both the title and author handle had changed. In a separate check on a different post, the deletion returned `204 No Content`. The app accepted both operations without verifying the caller.
- **Proposed fix:** Require an authenticated caller and check permission for the specific post before saving an update or deletion.

### MF-2 — Comment export has no size limit

- **Layer:** API response processing
- **CWE:** CWE-770 — Allocation of Resources Without Limits or Throttling
- **Evidence:** `functional-codebase/app/main.py`, `list_discussion_comments`.
- **Root cause:** The handler loads all matching comments into a list. For text export, it then builds the full visible thread in memory and joins it into one response. The query and export have no application-level row or output-size cap.
- **Impact:** Large threads can require substantial memory and processing time, reducing capacity for other requests.
- **Validation:** Source review confirmed the lack of a query limit and an export-size check. The runtime impact was not measured.
- **Proposed fix:** Paginate JSON results and enforce a maximum export size. Use bounded batches if full-thread export is needed.

### MF-3 — The database connection has hard-coded fallback credentials

- **Layer:** Database configuration
- **CWE:** CWE-798 — Use of Hard-coded Credentials
- **Evidence:** `functional-codebase/app/database.py`, `DEFAULT_DATABASE_URL` and the `create_engine` call.
- **Root cause:** When `DATABASE_URL` is unset, the application uses a connection string with a fixed PostgreSQL username and password stored in source.
- **Impact:** The fallback is intended for a loopback-only development setup. If the same credentials are reused where PostgreSQL is reachable by other clients, those clients could gain the database role's permissions.
- **Validation:** Source review confirmed that the credentials are embedded in the fallback URL and that the application selects that URL when `DATABASE_URL` is unset.
- **Proposed fix:** Require explicit database configuration outside local development and use a dedicated, least-privilege application account.
