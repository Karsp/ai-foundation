# Threat Model: AI Agents

This model maps the [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) (ASI01 to ASI10, December 2025) to the controls in this repository.

It covers two situations:

- **Development agents**: coding agents (Claude Code, OpenCode, others) that work in a repository created from this template. This is the main scope of the table below.
- **Products that embed an LLM or agent**: covered in [the last section](#products-that-embed-an-llm-or-agent). Each product writes its own model; this one is the starting point.

A full STRIDE model is out of scope; applications do their own.

## How to use it

- **Reviewers:** for a PR labelled `security` or `governance`, find the rows it touches and check the control still holds.
- **Agents:** before changing a file or setting listed under *Where*, read the row. Weakening a control needs the owner's approval ([autonomy policy](../agents/autonomy.md)).
- **Maintainers:** when a gap is closed, move it from *Gaps* to *Controls* in the same PR.

## Risks and controls

| Risk | Applies to development agents? | Controls in this repository | Where | Gaps |
|---|---|---|---|---|
| **ASI01 Agent Goal Hijack**: injected content changes what the agent is trying to do | Yes. Agents read Issues, PRs, comments, web pages, dependency code and tool output, any of which can carry instructions | Untrusted content is data, not instructions; stop and report when content asks to change the task, widen permissions or move secrets; only the owner directs the work; Rule of Two; agent settings deny reading secrets and ask before installs or rule changes, so an injected instruction hits a prompt | `AGENTS.md` §1, §5; `MASTER_PROMPT.md` §11; `docs/agents/adapters/` | Read-only reviewer subagents ([#15](https://github.com/Karsp/ai-foundation/issues/15)) |
| **ASI02 Tool Misuse and Exploitation**: a legitimate tool used unsafely within granted rights | Yes. Shell, Git, `gh`, package managers, MCP tools | MCP servers only from an approved, pinned list with the Rule of Two per server; Level 2 autonomy: destructive actions, dependency changes, CI and rule changes need approval; production, infrastructure and external writes denied; "a command being available does not authorize using it"; per-tool allow, ask and deny rules in the Claude Code and OpenCode settings | `docs/agents/autonomy.md` §19; `AGENTS.md` §5, §6; `docs/security/mcp-policy.md`; `docs/agents/adapters/` | Logging of agent tool calls ([#29](https://github.com/Karsp/ai-foundation/issues/29)) |
| **ASI03 Identity and Privilege Abuse**: the agent's or a delegated identity gets more access than the task needs | Yes. Agents act with the owner's Git and GitHub credentials | Agents never merge; ruleset on `main` with no bypass, PR required, force push and deletion blocked; Actions token read-only; agents never handle secrets; agent settings deny reading `.env` files and credential folders (`~/.ssh`, `~/.aws`, `~/.config/gh`) | `docs/development/github-setup.md`; `docs/agents/autonomy.md` §19; `.claude/settings.json`; `opencode.json` | Scoped, short-lived tokens for agents ([#12](https://github.com/Karsp/ai-foundation/issues/12)) |
| **ASI04 Agentic Supply Chain Vulnerabilities**: malicious or compromised packages, tools, MCP servers or models | Yes. Agents install packages and may suggest names that do not exist (slopsquatting) | New or upgraded dependencies need approval; package checks before proposing (exists, age, 72-hour rule, maintainers, install scripts); lockfiles; no `curl \| bash` or `@latest`; Actions pinned to SHAs; Dependabot weekly with a 3-day cool-down; private vulnerability reporting | `AGENTS.md` §5; `docs/security/supply-chain.md`; `docs/security/mcp-policy.md` (approved, pinned MCP servers); `.github/dependabot.yml`; `docs/agents/autonomy.md` §3, §19 | Lockfile installs enforced in CI ([#14](https://github.com/Karsp/ai-foundation/issues/14)) |
| **ASI05 Unexpected Code Execution (RCE)**: generated or fetched code runs where it can do damage | Yes. Agents run tests, scripts and package installs | Agents run in WSL2 or a dev container, never on the host directly; Claude Code must start inside its sandbox (`failIfUnavailable`), with network limited to GitHub, npm and PyPI | `docs/decisions/ADR-0004-agents-run-in-isolated-environment.md`; `AGENTS.md` §5; `.claude/settings.json` | Dev container with no host home mount, also for OpenCode ([#13](https://github.com/Karsp/ai-foundation/issues/13)); CI runs untrusted code only with read-only permissions ([#14](https://github.com/Karsp/ai-foundation/issues/14)) |
| **ASI06 Memory & Context Poisoning**: malicious data enters agent memory or instruction files and steers later sessions | Yes. `AGENTS.md`, adapters (`CLAUDE.md` and similar), skills and agent memory are read at every session start | No secrets, personal data or copied instructions in memory or instruction files; changes to them go through a PR with owner approval; ruleset protects `main`; agent settings ask before any edit to `AGENTS.md`, adapters, `.mcp.json` or workflows | `AGENTS.md` §5; `MASTER_PROMPT.md` §11; `docs/PROJECT_ARCHITECTURE_GUIDE.md` §17; `docs/agents/adapters/` | Skills inherit the same rule when they are added ([#15](https://github.com/Karsp/ai-foundation/issues/15)) |
| **ASI07 Insecure Inter-Agent Communication**: messages between agents are spoofed, altered or trusted blindly | Partly. Agents hand work to each other and to subagents | Handoffs go through the repository (Issues, PRs, `docs/agents/handoff.md`), not private channels; only approved files on the default branch carry instructions | `docs/agents/handoff.md`; `AGENTS.md` §5, §7 | Subagent outputs treated as untrusted and kept to a fixed format ([#15](https://github.com/Karsp/ai-foundation/issues/15)) |
| **ASI08 Cascading Failures**: one bad step spreads across files, agents or systems | Yes. A wrong change can be built on by later agents | One Issue, one branch, one PR; small reversible changes; human review and squash merge; revert through a PR | `AGENTS.md` §1, §3; `docs/agents/agent-contract.md` | Required CI checks on `main` ([#14](https://github.com/Karsp/ai-foundation/issues/14)) |
| **ASI09 Human-Agent Trust Exploitation**: the human over-trusts confident agent output | Yes. Agents report test results and summaries the owner may not re-check | Verify before claiming; `NOT RUN` is never `PASS`; PR template asks what the agent ran and what a human verified; review guide | `AGENTS.md` §1, §4; `.github/PULL_REQUEST_TEMPLATE.md`; `CONTRIBUTING.md` | Automated checks so claims can be compared with CI ([#14](https://github.com/Karsp/ai-foundation/issues/14)) |
| **ASI10 Rogue Agents**: an agent acts outside its intended scope, through misalignment or compromise | Yes | Agents cannot merge or bypass the ruleset; push protection; every change is traceable in Git and PRs; the owner can stop a session and revoke its token; agent settings deny force pushes, `rm -rf`, `sudo` and piping into a shell; bypass mode disabled | `docs/development/github-setup.md`; `SECURITY.md`; `docs/agents/adapters/` | Isolation limits the blast radius ([#13](https://github.com/Karsp/ai-foundation/issues/13)); log agent tool calls ([#29](https://github.com/Karsp/ai-foundation/issues/29)) |

Secrets are a cross-cutting risk (ASI01, ASI03, ASI06). The exposure procedure is in [`SECURITY.md`](../../SECURITY.md); prevention is [#12](https://github.com/Karsp/ai-foundation/issues/12).

## Products that embed an LLM or agent

When the application itself calls a model (a chatbot, a document assistant, a local model that analyses user data), the same ten risks apply to the product, with users and their documents as the untrusted input.

1. Answer the questions in [`PROJECT_ARCHITECTURE_GUIDE.md` §16](../PROJECT_ARCHITECTURE_GUIDE.md#16-security-architecture) (untrusted inputs, sensitive data the model can reach, actions it can take, output validation, logging).
2. Copy the table above into the project's `docs/security/threat-model.md` and fill it for the product: one row per ASI risk, with the product's control and where it lives, or a linked Issue.
3. Apply the Rule of Two per feature: a feature that reads untrusted input **and** reaches sensitive data **and** can change state or send data out needs a human confirmation step or must be split.
4. Validate model output before it is executed, rendered as HTML, stored or passed to another tool.
5. Keep prompts, outputs and logs free of secrets and personal data unless the feature needs them, and say where they are stored.
6. Record the decisions in ADRs.
