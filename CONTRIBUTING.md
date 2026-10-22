# Contributing

Humans and AI agents follow the same flow. Agents also follow [`AGENTS.md`](AGENTS.md) and the [agent contract](docs/agents/agent-contract.md).

## The flow

```text
Issue → branch → commits → PR (Closes #N) → review → squash merge → Issue closes
```

1. **Find or open an Issue.** Use one of the forms (Feature, Bug, Task, Security hardening). It needs clear acceptance criteria before work starts. Vulnerabilities are reported privately, never in an Issue (see [`SECURITY.md`](SECURITY.md)).
2. **Create a branch** from `main`:
   `feature/<issue>-<short-name>`, `bugfix/…`, `refactor/…`, `chore/…`, `docs/…`
3. **Commit** small, focused changes. Messages start with a type: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `security:`, and mention the Issue, e.g. `docs: add MCP policy (#10)`.
4. **Open a PR** using the template. It must say `Closes #N` so the Issue closes on merge, and fill in **Validation**, **Security** and **AI assistance**.
5. **Review and merge.** The owner reviews and squash-merges. Agents never merge (see [autonomy policy](docs/agents/autonomy.md) §19).

## AI-assisted work

- Commits written with an AI agent carry a `Co-Authored-By:` trailer naming the agent, so the history shows which changes were AI-assisted.
- The PR's **AI assistance** section says which agent did what, which commands it ran and what a human verified.
- Don't put links to private agent sessions or conversations in commits or PRs; keep them in your own notes.
- An agent must never claim a check passed unless it ran it.

## Reviewing a PR

Go PR by PR, in any order unless the PR says it depends on another. For each one:

1. **Open the linked Issue** and read its acceptance criteria. That is your checklist.
2. **Open "Files changed"** and check each criterion is met. Comment on specific lines when something is unclear or wrong.
3. **Read the Validation section.** It lists what was checked and how. Ask for proof if something important isn't listed.
4. **Spot-check the two easy-to-miss items:**
   - *Docs still true:* if a changed file is mentioned elsewhere (e.g. `AGENTS.md` links), those mentions still make sense.
   - *Nothing sensitive or misleading:* search the diff (Ctrl+F) for `TODO`, `[SET]`, `password`, `token`, `secret`, real names and email addresses. Secret scanning and CI will automate most of this ([#2](https://github.com/Karsp/ai-foundation/issues/2), [#14](https://github.com/Karsp/ai-foundation/issues/14)).
5. **Rule or security changes** (labels `governance`, `security`) get a slower read: ask "what could an agent now do that it couldn't before?"
6. **Merge** with *Squash and merge*, or leave a comment and the author fixes it on the same branch.

## Board

Issues move across the project board: **Backlog → Ready → In progress → Review → Done**. An Issue is *Ready* when its acceptance criteria are clear. Keep at most two Issues *In progress*. See [labels and board](docs/development/labels.md).

## Definition of Done

A change is done when the Issue's acceptance criteria are met, the PR is merged, and the checklist under **Definition of Done** in [`AGENTS.md`](AGENTS.md) holds where it applies (tests, docs, security checks, no unrelated changes).
