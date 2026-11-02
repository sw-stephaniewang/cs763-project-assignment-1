# AI Agent Environment

## CS763 — Assignment 1

## AI Usage Summary

- **AI tool:** ChatGPT
- **Estimated AI contribution:** 40%
- **AI assistance:** Helped organize the information from my chat history, reform my question promt and write this document.
- **My contribution:** I set up Copilot, checked my computer information, and tested whether Copilot could respond, and drafted the question I would like to ask.
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

| Setting                                                           | Recorded Value                                  |
| ----------------------------------------------------------------- | ----------------------------------------------- |
| Model selection                                                   | Auto                                            |
| Model self-reported during the initial model-identification check | MAI-Code-1.1-Flash                              |
| Model displayed for a later workflow-review response              | GPT-5-Luna                                      |
| Temperature                                                       | Not accessible to the agent; no value confirmed |
| Top-p                                                             | Not accessible to the agent; no value confirmed |
| Maximum output tokens                                             | Not accessible to the agent; no value confirmed |

I used Auto model selection and did not manually change
temperature, top-p, or maximum output tokens. Their actual
values were not available to me.

## 4. Tools and Permissions

I used GitHub Copilot in VS Code Agent mode, running locally
with Default permissions.

When asked about its available tools, Copilot reported tools
for reading, searching, creating, and editing files, checking
code errors, running terminal commands, and accessing webpages.

The full response is retained in the exported Copilot chat
history. Prompt_test_log.md summarizes the interaction and
records observed tool IDs.

### 4.1 Tools Observed in the Chat Export

The following serialized tool IDs appear in the exported
execution history.

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

The original prompts and recorded outcomes are included in
Prompt_test_log.md.

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
GitHub Actions and the security scans have not yet been run.

Detailed prompts, commands, results, and corrections are
recorded in `Prompt_test_log.md`.
