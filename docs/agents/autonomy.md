# Agent Autonomy Policy

## Purpose

This document defines what AI agents are permitted to do automatically in this repository.

It is a governance document.

The purpose is to make the boundary between:

* autonomous agent work;
* human approval;
* prohibited actions;

explicit and auditable.

This policy should be reviewed by the project owner before granting agents access to higher-risk operations.

---

# 1. Fundamental Principle

Agent capability does not imply agent permission.

An agent may technically be capable of performing an operation while still being prohibited from performing it.

When an action is not explicitly permitted, the agent must assume that approval is required.

---

# 2. Autonomy Levels

The project uses the following model.

## Level 0: Read-Only

The agent may:

* inspect repository files;
* inspect documentation;
* inspect Git history;
* inspect Issues and PRs;
* analyze code;
* propose changes;
* produce plans.

The agent may not modify project state.

---

## Level 1: Local Development

The agent may:

* modify local files;
* create local commits if permitted;
* run development commands;
* run tests;
* run linters;
* build the project;
* perform local analysis.

The agent may not:

* modify shared repository state;
* merge PRs;
* deploy;
* access production;
* perform destructive external operations.

---

## Level 2: Repository Contribution

The agent may, subject to repository permissions:

* create Issues;
* create branches;
* commit changes;
* push branches;
* open Pull Requests;
* update Issues;
* update PRs;
* respond to review feedback;
* modify project documentation;
* modify project configuration.

The agent may not automatically:

* merge protected PRs;
* deploy to production;
* access production systems;
* perform destructive infrastructure operations;
* handle secrets outside explicitly approved mechanisms.

---

## Level 3: Controlled Integration

Level 3 may allow additional automation such as:

* merging approved PRs;
* triggering controlled releases;
* modifying approved CI configuration;
* publishing non-production artifacts;
* promoting changes between controlled environments.

Level 3 should only be enabled when the project has appropriate automated safeguards.

---

## Level 4: Operational Automation

Level 4 permits controlled interaction with operational systems.

Potential capabilities include:

* deployment;
* infrastructure changes;
* production diagnostics;
* production configuration changes;
* operational remediation.

Level 4 should be considered high risk.

Production actions should require explicit safeguards, auditability, least-privilege credentials, and human approval where appropriate.

---

# 3. Default Repository Policy

Unless explicitly changed by the project owner:

| Action                                        | Default                                         |
| --------------------------------------------- | ----------------------------------------------- |
| Read repository                               | Allowed                                         |
| Read documentation                            | Allowed                                         |
| Read Issues/PRs                               | Allowed                                         |
| Create Issue                                  | Allowed                                         |
| Create branch                                 | Allowed                                         |
| Modify local files                            | Allowed                                         |
| Run tests                                     | Allowed                                         |
| Run build                                     | Allowed                                         |
| Run lint/typecheck                            | Allowed                                         |
| Commit                                        | Allowed                                         |
| Push feature branch                           | Allowed                                         |
| Open PR                                       | Allowed                                         |
| Update PR                                     | Allowed                                         |
| Update Issue                                  | Allowed                                         |
| Modify documentation                          | Allowed                                         |
| Modify application code                       | Allowed within Issue scope                      |
| Add or upgrade a dependency                   | Requires approval                               |
| Modify CI                                     | Requires review                                 |
| Modify security controls                      | Requires approval                               |
| Modify production configuration               | Requires approval                               |
| Merge protected PR                            | Requires human approval                         |
| Deploy production                             | Requires human approval                         |
| Delete production data                        | Prohibited without explicit human authorization |
| Expose secrets                                | Prohibited                                      |
| Disable security controls to bypass a problem | Prohibited                                      |

This table is the project's baseline. Project-specific rules may be stricter.

---

# 4. Issue Creation

Agents may create Issues when:

* work is discovered during implementation;
* follow-up work is required;
* technical debt needs tracking;
* a blocker requires separate work;
* the harness itself needs improvement.

Issues must be sufficiently detailed to be actionable.

Agents must not create large numbers of meaningless Issues merely to satisfy process requirements.

---

# 5. Branches

Agents may create branches for their assigned work.

Branches must follow repository conventions.

Agents should not rewrite shared branch history.

Force-push operations on shared branches are prohibited unless explicitly authorized.

---

# 6. Commits

Agents may create commits when operating at a level that permits repository contribution.

Commits should:

* represent coherent changes;
* avoid unrelated modifications;
* follow project conventions;
* reference Issues where appropriate.

Do not create meaningless commit noise solely to demonstrate activity.

---

# 7. Pull Requests

Agents may create PRs when permitted by their autonomy level.

A PR must accurately represent:

* what was changed;
* why it was changed;
* what was tested;
* what remains incomplete.

Agents must not mark incomplete work as complete merely to satisfy PR workflow.

---

# 8. Merging

Merging is a governance decision.

By default:

> **Agents may prepare a PR for merge, but protected branches require human approval.**

Automated merging may be enabled only when:

* the project explicitly permits it;
* required CI gates pass;
* branch protection is correctly configured;
* the risk level is appropriate.

---

# 9. CI/CD

Agents may modify CI configuration only when:

* the modification is within Issue scope;
* the change is reviewable;
* the consequences are understood.

Agents must not disable or weaken CI checks merely to make a PR pass.

Temporary exceptions require explicit authorization and must be documented.

---

# 10. Database Changes

Database migrations require additional caution.

Agents may implement migrations when the Issue explicitly requires them.

Before applying migrations to shared or production environments, verify the project's deployment and approval policy.

Agents must not:

* silently drop production data;
* perform destructive schema changes without authorization;
* bypass migration tooling;
* delete historical data without explicit approval.

For potentially destructive migrations, document:

* impact;
* migration strategy;
* rollback strategy;
* compatibility considerations.

---

# 11. Infrastructure

Infrastructure changes must follow the project's Infrastructure-as-Code and review policies where applicable.

Agents should prefer:

```text
Code
→ Review
→ CI
→ Controlled Deployment
```

over ad-hoc manual changes.

Agents must not make irreversible infrastructure changes without appropriate authorization.

---

# 12. Production

Production is a separate trust boundary.

By default, agents may not independently:

* deploy;
* modify production configuration;
* alter production infrastructure;
* delete production data;
* rotate production credentials;
* disable production security controls.

Production actions require explicit project-specific authorization.

---

# 13. Secrets and Credentials

Agents must never:

* commit secrets;
* intentionally expose secrets;
* place credentials in logs;
* copy secrets into Issues or PRs;
* bypass secret-management systems.

If a secret is accidentally exposed:

1. stop;
2. avoid further propagation;
3. report the exposure;
4. follow the project's credential-rotation procedure.

---

# 14. Destructive Commands

Examples include:

```text
rm -rf
git reset --hard
git push --force
database deletion
infrastructure destruction
data deletion
credential revocation
```

The existence of a command in an agent's toolset does not authorize its use.

When an operation is irreversible or potentially destructive, require the appropriate approval.

---

# 15. External Services

Agents may interact with external services only when:

* the service is within the Issue scope;
* credentials are available through an approved mechanism;
* the action is permitted by this policy.

Agents should prefer dry runs, sandbox environments, and read-only operations where available.

---

# 16. Human Approval

Agents must request human approval when an operation:

* is irreversible;
* affects production;
* changes security boundaries;
* changes critical infrastructure;
* exposes sensitive data;
* requires elevated privileges;
* merges protected changes;
* introduces substantial architectural risk;
* has consequences that cannot be safely validated automatically.

When requesting approval, explain:

```text
Action:
Reason:
Expected impact:
Risks:
Rollback:
What has already been verified:
```

---

# 17. Safety Over Completion

If completing an Issue requires violating this policy:

**do not complete the operation.**

Instead:

1. stop at the permission boundary;
2. document the blocker;
3. update the Issue/PR;
4. request approval or create follow-up work.

A blocked implementation is preferable to an unauthorized operation.

---

# 18. Policy Changes

This document itself is governance.

Agents must not silently weaken their own autonomy policy.

Changes to this file should normally:

* have an explicit Issue;
* be reviewed;
* explain the reason for the change;
* document new risks;
* receive the appropriate human approval.

---

# 19. Current Project Configuration

Set by the project owner on 2026-10-18 (see [ADR-0002](../decisions/ADR-0002-default-autonomy-level-2.md)). Projects created from this template inherit these values and record any change in their own ADR.

```text
Default agent autonomy level: 2 (Repository Contribution)
Issue creation: ALLOW
Branch creation: ALLOW
Commit creation: ALLOW
Push feature branches: ALLOW
PR creation: ALLOW (draft or ready for review)
Add or upgrade dependencies: REQUIRE APPROVAL
Handle secrets or credentials: REQUIRE APPROVAL
CI modification: REQUIRE APPROVAL
Agent rules, autonomy or security controls: REQUIRE APPROVAL
PR merge: REQUIRE APPROVAL
Release creation: REQUIRE APPROVAL
Deployment: REQUIRE APPROVAL
Production access: DENY
Infrastructure changes: DENY
Database migrations: APPROVAL
External service actions: DENY (read-only lookups needed for the Issue are allowed)
```

"REQUIRE APPROVAL" means the owner says yes for that specific action, in the Issue, the PR or the conversation. Approval for one action does not carry over to the next.

Agents always run in an isolated environment (WSL2 or a dev container), never directly on a native Windows host. See [ADR-0004](../decisions/ADR-0004-agents-run-in-isolated-environment.md).

---

# 20. Governance Rule

When there is uncertainty about whether an action is permitted:

> **Stop at the boundary and ask.**

Do not interpret ambiguity as permission.
