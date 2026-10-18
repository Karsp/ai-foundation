# ADR-0002: Default agent autonomy is Level 2

- **Status:** Accepted
- **Date:** 2026-10-18
- **Deciders:** Karsp
- **Issue:** #4

## Context

`docs/agents/autonomy.md` defines Levels 0 to 4 but left the project's configuration unset. The earlier OpenCode setup guide forbade agents from committing or pushing at all (closer to Level 1), which makes the human a bottleneck for every change. On the other side, 2025-2026 incidents (prompt injection, compromised packages, MCP tool poisoning) show that agents with broad autonomy plus access to secrets and the outside world are a real attack path (OWASP Top 10 for Agentic Applications, Meta's "Agents Rule of Two").

## Decision

The default is **Level 2 (Repository Contribution)**. Agents may create Issues, branches, commits, pushes to feature branches and PRs. These need the owner's explicit approval: merging, changing CI, changing agent rules or security controls, adding or upgrading dependencies, handling secrets, releases and deployments. Production access, infrastructure changes and writes to external services are denied by default. The exact values are in `docs/agents/autonomy.md` §19.

## Alternatives considered

- **Level 1 (agents edit, human commits):** safest, but slow, and it loses the agent's own traceability (branch, PR description).
- **Level 3 (agents merge approved PRs):** not before CI, branch protection and security scanning exist (#2, #14).

## Consequences

- Branch protection on `main` (#2) is what technically enforces "merge needs approval"; until then it is a documented rule.
- Dependency additions become an approval step, which slows agents down where it matters most (supply chain, #9).
- Revisit when CI and scanning are in place; raising the level needs a new ADR.
