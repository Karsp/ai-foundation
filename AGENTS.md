# AGENTS.md

## Purpose

This repository is developed by humans and AI agents.

This document is the primary entry point for any AI agent working in this repository. It defines the minimum rules every agent must follow.

The repository is governed by three complementary documents:

* [`AGENTS.md`](AGENTS.md): operational rules and repository entry point.
* [`docs/agents/agent-contract.md`](docs/agents/agent-contract.md): mandatory engineering lifecycle.
* [`docs/agents/autonomy.md`](docs/agents/autonomy.md): agent permissions, approval boundaries, and prohibited actions.

These documents are part of the project's engineering system and must be treated as authoritative.

If instructions conflict, stop and resolve the conflict rather than guessing.

---

# 1. Core Principles

Every agent working in this repository must follow these principles:

### Issue First

Meaningful work starts with a GitHub Issue.

Do not begin implementation of a feature, bug fix, refactor, architectural change, infrastructure change, or other significant work without an Issue unless the change is explicitly classified as trivial repository maintenance.

### One Issue, One Change

An Issue should represent a coherent, independently understandable unit of work.

If a task is too large, ambiguous, or contains multiple independent objectives, split it into multiple Issues.

### One Issue, One Branch

Each Issue should normally be implemented in its own branch.

### One Issue, One PR

Each completed Issue should normally result in its own Pull Request.

### Repository as Source of Truth

Important project knowledge must not exist only in an agent conversation.

Persist important information in the appropriate repository or GitHub artifact:

* code;
* tests;
* Issues;
* Pull Requests;
* ADRs;
* documentation;
* configuration;
* workflows;
* runbooks.

### Verify Before Claiming Completion

Never claim that something is implemented, tested, passing, reviewed, merged, or deployed unless that state has actually been verified.

---

# 2. Required Reading

Before making meaningful changes, inspect the relevant project documentation.

At minimum, read:

1. `AGENTS.md`
2. `docs/agents/agent-contract.md`
3. `docs/agents/autonomy.md`
4. `README.md`
5. relevant architecture documentation under `docs/architecture/`
6. relevant ADRs under `docs/decisions/`
7. relevant development documentation under `docs/development/`

Do not read every document indiscriminately.

Read the documentation relevant to the task.

Before making architectural changes, **architecture documentation and relevant ADRs are mandatory reading**.

---

# 3. Source of Truth Hierarchy

When determining project state, use the following hierarchy:

1. Current repository state
2. GitHub Issues and Pull Requests
3. Architecture documentation and ADRs
4. CI/test results
5. Project configuration
6. Agent conversation context

Conversation context is the least durable source of truth.

If the conversation contradicts the repository, investigate before proceeding.

---

# 4. Standard Engineering Lifecycle

All meaningful work follows:

```text
Understand
    ↓
Issue
    ↓
Branch
    ↓
Plan
    ↓
Implement
    ↓
Test
    ↓
Validate
    ↓
Document
    ↓
Pull Request
    ↓
Review
    ↓
Merge
    ↓
Close Issue
```

The complete lifecycle and responsibilities are defined in:

`docs/agents/agent-contract.md`

Do not bypass lifecycle stages without an explicit reason.

---

# 5. GitHub Issue Policy

Before implementation:

* identify the relevant Issue;
* confirm its scope;
* understand acceptance criteria;
* identify dependencies;
* identify relevant architectural constraints;
* identify testing requirements.

If no suitable Issue exists, create one if your autonomy level permits it.

If you cannot create one, stop and request the required action.

Do not create vague placeholder Issues such as:

```text
"Implement authentication"
"Fix API"
"Improve architecture"
```

Issues must contain enough information for another engineer or agent to understand the intended work.

---

# 6. Branch Policy

Create a branch associated with the Issue.

Preferred naming:

```text
feature/<issue-number>-<short-description>
bugfix/<issue-number>-<short-description>
refactor/<issue-number>-<short-description>
chore/<issue-number>-<short-description>
docs/<issue-number>-<short-description>
```

Do not commit implementation work directly to the default branch.

---

# 7. Planning Before Implementation

Before writing substantial code:

1. understand the existing implementation;
2. identify affected components;
3. identify tests;
4. identify documentation;
5. identify architectural implications;
6. identify risks;
7. determine the smallest reasonable implementation.

For complex work, record the plan in the Issue or another appropriate project artifact.

Do not produce elaborate plans for trivial changes.

---

# 8. Architecture Changes

Do not make significant architectural decisions silently.

Before changing architecture:

1. read relevant architecture documentation;
2. inspect existing ADRs;
3. determine whether an existing decision applies;
4. evaluate alternatives;
5. document the decision in an ADR when appropriate;
6. create or update the relevant Issue;
7. implement through the normal branch/PR workflow.

Architecture decisions should remain understandable after the original agent is gone.

---

# 9. Code and Repository Changes

Agents may modify files required to implement the active Issue, subject to the permissions defined in:

`docs/agents/autonomy.md`

Avoid unrelated changes.

Do not perform opportunistic refactors merely because you noticed something that could be improved.

If unrelated work is important, create or propose a separate Issue.

---

# 10. Tests

Every implementation must include appropriate tests unless there is a documented reason why testing is not applicable.

Use the project's established testing strategy.

Do not:

* remove tests merely to make CI pass;
* weaken assertions without justification;
* disable quality gates;
* hide failures;
* claim tests passed without running them.

If a test cannot be executed, state that explicitly.

---

# 11. Authoritative Commands

The repository's documented development commands are authoritative.

Use the commands documented by the project rather than inventing alternative workflows.

At minimum, the repository should expose appropriate commands for:

```text
setup
build
test
lint
format
typecheck
validate
```

Additional commands may exist depending on the project.

Before declaring completion, run the relevant validation commands.

If commands fail:

1. determine whether the failure is caused by your change;
2. fix it when within scope;
3. document unrelated failures;
4. never conceal the failure.

---

# 12. Pull Requests

Every substantial implementation should be delivered through a Pull Request.

The PR must:

* reference the Issue;
* explain the change;
* describe validation;
* document important technical decisions;
* identify limitations;
* identify follow-up work;
* pass required quality gates.

Do not create a PR merely to make the workflow appear complete.

The PR should represent the actual state of the implementation.

---

# 13. Incomplete Work

If work cannot be completed:

Do not pretend it is complete.

Instead:

1. preserve the working changes;
2. document the current state;
3. identify blockers;
4. update the Issue/PR;
5. create follow-up Issues where necessary;
6. define those Issues sufficiently for another agent to continue;
7. document relevant decisions and failed approaches.

The next agent should be able to continue without reconstructing the previous agent's entire context.

---

# 14. Security

Never expose, commit, or intentionally print secrets.

Do not bypass security controls merely to complete an Issue.

Treat the following as potentially sensitive:

* API keys;
* credentials;
* tokens;
* private keys;
* production configuration;
* personal data;
* customer data;
* internal infrastructure details.

Agent permissions are governed by `docs/agents/autonomy.md`.

When uncertain whether an action has security implications, stop and ask.

---

# 15. Destructive Operations

Never perform destructive or irreversible operations without the required authorization.

Examples include:

* deleting production data;
* dropping databases;
* rewriting shared Git history;
* force-pushing protected branches;
* deleting infrastructure;
* rotating credentials;
* modifying production systems;
* disabling security controls.

Consult `docs/agents/autonomy.md`.

---

# 16. External Systems

Treat external systems as separate trust boundaries.

Before interacting with:

* production;
* cloud infrastructure;
* third-party services;
* customer systems;
* deployment environments;

verify that the action is permitted by the project's autonomy policy.

---

# 17. Documentation

Update documentation when behavior, architecture, operations, or developer workflow changes.

Do not create documentation that merely repeats the implementation.

Documentation should answer questions future developers or agents are likely to have.

---

# 18. Skills, Tools, and Subagents

If the repository provides skills, tools, or subagents:

* use them when appropriate;
* follow their documented interfaces;
* respect their permissions;
* do not assume capabilities they do not explicitly provide.

Do not create a new skill, tool, or subagent when a simpler existing mechanism is sufficient.

---

# 19. Agent Independence

The project's engineering process must not depend on a specific AI model or vendor.

Agent-specific instructions should adapt to the common project contract rather than replace it.

The same Issue, branch, testing strategy, quality gates, and documentation standards should apply regardless of which supported agent performs the work.

---

# 20. Definition of Done

Before declaring an Issue complete, verify:

* [ ] Scope is satisfied
* [ ] Acceptance criteria are satisfied
* [ ] Appropriate tests exist
* [ ] Tests pass
* [ ] Lint passes
* [ ] Formatting is correct
* [ ] Type checks pass where applicable
* [ ] Build passes where applicable
* [ ] Security checks pass where applicable
* [ ] Documentation is updated
* [ ] Architecture decisions are documented
* [ ] Known limitations are documented
* [ ] Follow-up Issues exist for remaining work
* [ ] PR is linked to the Issue
* [ ] Required CI checks pass
* [ ] No unrelated changes were introduced

Only after verification should work be described as complete.

---

# 21. When in Doubt

When uncertain:

1. inspect the repository;
2. inspect GitHub;
3. read the relevant documentation;
4. check the autonomy policy;
5. prefer the smallest reversible action;
6. document the uncertainty;
7. ask for human approval when required.

**Never guess when guessing could change project architecture, security, data, infrastructure, or production state.**
