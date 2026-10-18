# Agent Contract

## Purpose

This document defines the mandatory engineering lifecycle for AI agents working in this repository.

It is intentionally independent of any specific model, vendor, CLI, or agent runtime.

The objective is to ensure that different agents behave consistently and that work remains reproducible when responsibility moves between humans and agents.

---

# 1. Contract

Every meaningful engineering task follows this lifecycle:

```text
Repository Instructions
        ↓
Understand Context
        ↓
Inspect GitHub
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

Not every task requires the same depth at every stage.

The lifecycle is mandatory; the amount of work performed at each stage should be proportional to the task.

---

# 2. Stage 1: Repository Instructions

Before meaningful work:

* read `AGENTS.md`;
* read the autonomy policy;
* identify relevant project documentation;
* identify relevant architecture documentation;
* identify available development commands.

Do not begin implementation before understanding the repository's operating rules.

---

# 3. Stage 2: Understand Context

Inspect the existing implementation.

Determine:

* what already exists;
* how the relevant component works;
* what depends on it;
* what it depends on;
* what tests exist;
* what constraints apply;
* whether similar work has already been implemented.

Avoid rewriting existing functionality simply because a different implementation would be preferable.

---

# 4. Stage 3: Inspect GitHub

Identify the relevant Issue.

Determine:

* objective;
* scope;
* non-goals;
* acceptance criteria;
* dependencies;
* related Issues;
* related PRs;
* relevant decisions.

If no suitable Issue exists, create one when permitted.

If the task does not have a suitable Issue and the agent cannot create one, stop and request one.

---

# 5. Stage 4: Issue

The Issue is the implementation contract.

Before coding, ensure that the Issue answers:

```text
What problem are we solving?
Why are we solving it?
What is in scope?
What is out of scope?
What does success look like?
How will it be tested?
What dependencies exist?
What risks exist?
```

If the Issue is insufficiently defined, improve it when permitted or request clarification.

---

# 6. Stage 5: Branch

Create a branch associated with the Issue.

Example:

```text
feature/123-add-user-search
```

Keep work isolated to the Issue.

---

# 7. Stage 6: Plan

Determine the implementation approach.

For simple tasks, the plan may be short.

For complex tasks, identify:

* affected components;
* implementation sequence;
* interfaces;
* migrations;
* tests;
* documentation;
* risks;
* rollback strategy.

If the implementation reveals that the Issue is incorrectly scoped, stop and restructure the work rather than silently expanding scope.

---

# 8. Stage 7: Implement

Implement only the required change.

Follow existing project conventions unless there is a documented reason to change them.

Prefer:

* small changes;
* clear interfaces;
* explicit behavior;
* testable code;
* reversible decisions.

Avoid unrelated cleanup.

---

# 9. Stage 8: Test

Test the behavior introduced or modified by the Issue.

Use the project's testing strategy.

Consider:

* happy paths;
* failure paths;
* edge cases;
* regressions;
* security implications;
* concurrency;
* compatibility.

Do not equate test quantity with quality.

---

# 10. Stage 9: Validate

Run the authoritative project validation commands.

Depending on the project:

```text
lint
format
typecheck
unit tests
integration tests
e2e tests
build
security checks
```

Record relevant results.

Distinguish between:

```text
PASS
FAIL
NOT RUN
NOT APPLICABLE
BLOCKED
```

Never convert `NOT RUN` into `PASS`.

---

# 11. Stage 10: Document

Update documentation when required.

Create or update an ADR when the implementation introduces a significant architectural decision.

Document:

* important assumptions;
* operational changes;
* migration requirements;
* limitations;
* follow-up work.

The implementation should leave the repository more understandable, not less.

---

# 12. Stage 11: Pull Request

Create a PR using the repository's PR template.

The PR must:

* reference the Issue;
* explain the implementation;
* summarize validation;
* identify architectural changes;
* identify limitations;
* identify follow-up work.

The PR should allow a reviewer to understand the change without relying on private agent context.

---

# 13. Stage 12: Review

Review the implementation before considering it complete.

Check:

* correctness;
* tests;
* security;
* maintainability;
* scope;
* documentation;
* compatibility;
* accidental changes.

If automated or human review identifies issues, address them through the same PR.

---

# 14. Stage 13: Merge

Merge only when the repository's required conditions are satisfied.

Those conditions may include:

* required CI checks;
* human approval;
* security approval;
* deployment approval;
* other project-specific gates.

The exact authority is defined in `docs/agents/autonomy.md`.

---

# 15. Stage 14: Close

After successful merge:

* ensure the Issue is correctly linked;
* verify that the Issue can be closed;
* document any remaining work;
* create follow-up Issues where necessary.

Do not close an Issue merely because a PR was created.

---

# 16. Scope Control

An agent must not silently expand an Issue.

If implementation reveals additional work:

```text
Current Issue
      ↓
Complete original scope
      +
Create follow-up Issue
```

Unless the additional work is necessary to safely complete the original objective.

---

# 17. Discovery of New Problems

If unrelated problems are discovered:

* do not automatically fix them;
* assess whether they block the current Issue;
* create a follow-up Issue if appropriate.

Exception: security vulnerabilities or severe correctness problems may require immediate escalation.

---

# 18. Failed Implementation

If an implementation attempt fails:

Document:

* what was attempted;
* what failed;
* error symptoms;
* likely cause;
* what was ruled out;
* current repository state;
* recommended next step.

If necessary, create a follow-up Issue.

Failed attempts are useful engineering information when recorded correctly.

---

# 19. Interrupted Work

If work is interrupted:

Leave enough information for another agent to continue.

At minimum:

```text
Current state
Completed work
Remaining work
Known failures
Relevant files
Relevant Issues
Relevant decisions
Next recommended action
```

The handoff must not depend on remembering the previous conversation.

---

# 20. Architecture Escalation

If implementation requires a decision that changes:

* system boundaries;
* public interfaces;
* data architecture;
* deployment architecture;
* security model;
* agent permissions;
* major dependencies;

the agent must treat it as an architectural decision.

Consult relevant ADRs and create a new ADR when appropriate.

---

# 21. Autonomy Boundary

This contract defines **how** agents work.

It does not independently grant permission to perform every action.

Whether an agent may:

* create Issues;
* create branches;
* commit;
* push;
* open PRs;
* merge;
* modify CI;
* modify infrastructure;
* deploy;
* access production;

is defined by:

`docs/agents/autonomy.md`

When permission is unclear, assume the more restrictive interpretation and request approval.

---

# 22. Completion Contract

An agent may declare an Issue complete only when:

1. the intended behavior is implemented;
2. acceptance criteria are satisfied;
3. appropriate tests exist;
4. relevant validation has been executed;
5. failures are understood;
6. documentation is updated;
7. architectural decisions are recorded;
8. remaining work is tracked;
9. the PR accurately describes the resulting state.

**Completion is a verified state, not a feeling.**
