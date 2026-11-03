# AI Agent Environment

## CS763 — Assignment 1

## AI Usage Summary

- **AI tool:** ChatGPT
- **Estimated AI contribution:** 40%
- **AI assistance:** Helped organize information from my chat history, refine my prompts, and write this document.
- **My contribution:** I set up Copilot, checked my computer information, tested whether Copilot could respond, and drafted the questions I wanted to ask.
- **Detailed log:** See `Prompt_test_log.md`.

## 1. My Computer and Software

| Item             | Version or Details                     |
| ---------------- | -------------------------------------- |
| Computer         | MacBook Air, 2020                      |
| Chip             | Apple M1                               |
| Memory           | 8 GB                                   |
| Operating system | macOS Tahoe 26.5.1                     |
| Editor           | Visual Studio Code 1.144.0 (Universal) |
| Python           | 3.13.5                                 |
| Docker           | 29.4.3, build 055a478                  |
| Docker Compose   | v5.1.3                                 |

## 2. Coding Agent Setup

| Setting                   | What I Am Using                    |
| ------------------------- | ---------------------------------- |
| Agent                     | GitHub Copilot Chat                |
| Publisher                 | GitHub                             |
| Installation              | Built into my VS Code installation |
| Extension ID              | github.copilot-chat                |
| Copilot component version | 1.0.103.r40031404408.gba6c003      |
| Mode                      | Agent                              |
| Location                  | Local                              |
| Permissions               | Default permissions                |

## 3. Model Settings

| Setting                                                           | Recorded Value                          |
| ----------------------------------------------------------------- | --------------------------------------- |
| Model selection                                                   | Auto (Balance)                          |
| Model self-reported during the initial model-identification check | MAI-Code-1.1-Flash                      |
| Model displayed for a later workflow-review response              | GPT-6-Luna                              |
| Temperature                                                       | Not shown in VS Code; no value recorded |
| Top-p                                                             | Not shown in VS Code; no value recorded |
| Maximum output tokens                                             | Not shown in VS Code; no value recorded |

I used Auto model selection (Balance). The other models in the
picker needed a plan upgrade, so Auto was the only choice I could use. I searched VS Code Settings for temperature, top-p, and max tokens and only found unrelated settings, so I did not change or record any values.

## 4. Tools and Permissions

I used GitHub Copilot in VS Code Agent mode, running locally
with Default permissions.

When asked about its available tools, Copilot reported tools
for reading, searching, creating, and editing files, checking
code errors, running terminal commands, and accessing webpages.

The prompts, response summaries, and verification results
are recorded in Prompt_test_log.md.

### 4.1 Tools Observed

The following tool IDs were recorded during my Copilot
sessions.

| Tool ID                      | Observed purpose                                                 |
| ---------------------------- | ---------------------------------------------------------------- |
| copilot_listDirectory        | List project files and folders.                                  |
| copilot_findFiles            | Find files in the workspace.                                     |
| copilot_readFile             | Read project files.                                              |
| copilot_createFile           | Create application, test, dependency, and configuration files.   |
| copilot_multiReplaceString   | Update existing file contents.                                   |
| copilot_applyPatch           | Create and revise the GitHub Actions workflow.                   |
| copilot_getErrors            | Check editor diagnostics for the workflow.                       |
| run_in_terminal              | Run local validation, tests, Docker commands, and health checks. |
| tool_search                  | Discover additional tools during workflow preparation.           |
| copilot_fetchWebPage         | Retrieve documentation during workflow preparation.              |
| vscode_fetchWebPage_internal | Retrieve webpage content during documentation checks.            |
| copilot_memory               | Access agent memory during workspace inspection.                 |

### 4.2 Permissions and Approval Behavior

| Item                  | Recorded behavior                                                                                                            |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Operational mode      | Agent                                                                                                                        |
| Execution location    | Local                                                                                                                        |
| Permission setting    | Default permissions                                                                                                          |
| File changes          | Copilot created and edited files in the project workspace.                                                                   |
| Terminal approvals    | VS Code displayed approval prompts for Docker build/run and container status/log commands. I clicked Allow.                  |
| Container replacement | I explicitly authorized replacing only the assignment container, cs763-a1-check.                                             |
| Initial setup command | The agent's environment setup/test command was skipped. I completed the initial environment setup and pytest check manually. |

Copilot initially reported that no approval prompts appeared
during the Docker checks. I corrected that statement because
VS Code had displayed prompts that I approved.

### 4.3 Task Instructions

I supplied task-specific instructions in my prompts, including:

- Leave spec.md and Agent_environment.md unchanged during
  application and pipeline generation.
- Use the project-local .venv rather than installing packages
  into my global/base Python environment.
- Leave unrelated containers unchanged.
- Report actual commands, results, and approval prompts.
- Do not claim that a check passed unless it was executed.
- Do not commit, push, upload, publish, or create a release
  during local workflow preparation.

Selected original prompts, summaries of other requests,
and their results are included in Prompt_test_log.md.

## 5. Setup and Verification Results

I tested the agent with this prompt:

> Reply with “Agent test successful.” Do not edit files or run commands.

Copilot replied:

> Agent test successful.

Copilot generated the basic FastAPI app, automated test,
dependency files, and Docker configuration.

I manually set up the project-local .venv, installed the
dependencies, and ran `python -m pytest -q`. The result was:

```text
1 passed, 1 warning in 0.73s
```

I also confirmed that `/health` returned `{"status":"ok"}`
in the browser.

Copilot later validated the Compose configuration, built the
multi-stage image, and verified that the Compose-managed app
returned HTTP 200 with `{"status":"ok"}`.

The GitHub Actions workflow was created and locally checked.
After uploading the project, I checked the GitHub Actions
run. The tests and Docker build succeeded. Trivy, Semgrep,
and SonarQube Cloud also ran successfully, and the reports
were saved. Security findings did not block the pipeline.

The prompts, commands, results, corrections, and GitHub
Actions run link are recorded in Prompt_test_log.md.
