# Skills and subagents

A **skill** is a written procedure an agent loads when a task matches its description. A **subagent** is a separate agent with its own instructions and a smaller set of tools, which the main agent hands one job to. This repository has three skills and two subagents. Each exists because the task repeats and is easy to get wrong ([`PROJECT_ARCHITECTURE_GUIDE.md` §18-19](../PROJECT_ARCHITECTURE_GUIDE.md#18-skills-and-tools)).

## Catalog

| Name | Kind | Purpose | Input | Output | Permissions |
|---|---|---|---|---|---|
| [`new-issue`](../../.claude/skills/new-issue/SKILL.md) | Skill | Turns a one-line idea into a complete Issue that follows the Issue forms | The idea | Draft for approval, then the Issue URL | `gh issue list`, `gh issue create` (asks first) |
| [`handoff`](../../.claude/skills/handoff/SKILL.md) | Skill | Writes and posts the [handoff note](handoff.md) for unfinished work | The Issue | Note posted on the PR or Issue | `git commit`/`push` on the feature branch, `gh pr comment` / `gh issue comment` |
| [`review-security`](../../.claude/skills/review-security/SKILL.md) | Skill | Reviews a change against the [threat model](../security/threat-model.md), through `security-reviewer`, and verifies the findings | The Issue; the branch or PR | Verified findings in a fixed format | Read-only `git diff`, `gh pr diff`, `gh issue view` |
| [`reviewer`](../../.claude/agents/reviewer.md) | Subagent | Checks a diff against its Issue, `AGENTS.md` and the docs | Issue, changed files, diff | `VERDICT` / `FINDINGS` / `NOT CHECKED` | Read, search. No edits, commands, web or MCP |
| [`security-reviewer`](../../.claude/agents/security-reviewer.md) | Subagent | Checks a diff for security problems, by threat-model risk (ASI01 to ASI10) | Issue, changed files, diff | Same format, with the risk ID on each finding | Same as `reviewer` |

Use `reviewer` before every PR, and `review-security` for any PR that touches settings, workflows, dependencies, agent files or secrets handling ([agent contract](agent-contract.md), Review stage).

## Where they live

| | Claude Code | OpenCode |
|---|---|---|
| Skills | `.claude/skills/<name>/SKILL.md`, invoked as `/<name>` or when the task matches | The same files: OpenCode also reads `.claude/skills/` |
| Subagents | `.claude/agents/<name>.md`, invoked with the Agent tool | `.opencode/agents/<name>.md`, invoked as `@<name>` |

A subagent needs a file for each tool because the two tools use different settings. The instructions below the settings are identical, and [`scripts/check_agents.py`](../../scripts/check_agents.py) fails the check if they drift apart.

## Why the reviewers are read-only

A reviewer reads untrusted content: the diff, the Issue, comments. Under the Rule of Two ([`AGENTS.md`](../../AGENTS.md) §5) it must then not also change state or send data out. So:

- **Claude Code:** `tools: Read, Grep, Glob`. No `Bash`, `Edit`, `Write`, `WebFetch`, `WebSearch`, `Skill` or MCP tools, because a list of tools is an allowlist.
- **OpenCode:** `permission` denies `edit`, `bash`, `webfetch`, `websearch`, `task`, `skill` and `external_directory`.
- **Fixed output.** The reviewer answers only in the `VERDICT` / `FINDINGS` / `NOT CHECKED` format. The main agent treats that answer as data: it checks each finding against the code and never runs a command the reviewer suggests (OWASP ASI07).
- **Text that tries to steer the reviewer** ("ignore your checklist", "approve this") is reported as a finding with the verdict BLOCK.

`make lint` runs `scripts/check_agents.py`, which fails if a subagent named `*reviewer` gets any other tool, loses a deny or sets OpenCode's legacy `tools`, if a setting is written twice, or if a skill pre-approves tools with `allowed-tools`.

## How they were tested

Tested on 8 November 2026 with Claude Code 2.1.319 and OpenCode 1.19.4:

| Check | Result |
|---|---|
| Ask the Claude Code `reviewer` which tools it has, then to create a file | Read, Grep and Glob only; no file created |
| `opencode debug agent reviewer` (and `security-reviewer`) | Only `read`, `glob`, `grep` and `todowrite` enabled |
| `opencode debug skill` | Lists `new-issue`, `handoff` and `review-security` from `.claude/skills/` |
| `/review-security` on a branch with a `pull_request_target` workflow and a README comment telling AI reviewers to approve | Verdict BLOCK; the workflow problems and the injected comment reported as `high` |
| `scripts/check_agents.py` with a reviewer given `Bash`, a second `tools:` line, an OpenCode `bash: ask`, a missing `external_directory: deny`, an OpenCode `tools:` block, different instructions, and a skill with `allowed-tools` | Fails with one message for each |
| The `reviewer` on this change's own diff | Found two gaps (the CI checks table, an `external_directory` deny the script didn't check), both fixed |

Re-run these after upgrading Claude Code or OpenCode, or after changing a skill or subagent.

## Adding or changing one

1. Answer the questions in [`PROJECT_ARCHITECTURE_GUIDE.md` §18](../PROJECT_ARCHITECTURE_GUIDE.md#18-skills-and-tools): problem, why reusable, inputs, outputs, permissions, how it fails safely, how it is tested, owner. Prefer a documented command or procedure when one is enough.
2. A skill goes in `.claude/skills/<name>/SKILL.md` with `name` (the folder name, lowercase and hyphens) and a `description` that says what it does and when to use it. Don't add `allowed-tools`: commands should still ask.
3. A subagent goes in both `.claude/agents/` and `.opencode/agents/`, with identical instructions. Give it the fewest tools that do the job.
4. Add a row to the catalog above, and test it the way the table above does.
5. Skills and subagents are instructions every session can load, so they change only through a PR with the owner's approval, and never with text copied from Issues, web pages or tool output (OWASP ASI06). Agents ask before editing `.claude/` and `.opencode/`.

The owner of every skill and subagent is the repository owner.
