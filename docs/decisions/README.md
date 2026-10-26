# Architecture Decision Records

Decisions that would be expensive or confusing to rediscover later (see `docs/PROJECT_ARCHITECTURE_GUIDE.md` §24). Trivial implementation details don't get an ADR.

- Copy `ADR-0000-template.md`, take the next number, and open it in the same PR as the change it explains.
- ADRs are never edited after acceptance except for status. A new decision supersedes an old one with a new ADR.

| ADR | Decision | Status |
|---|---|---|
| [0001](ADR-0001-agent-first-issue-first-engineering.md) | Agent-first, Issue-first engineering | Accepted |
| [0002](ADR-0002-default-autonomy-level-2.md) | Default agent autonomy is Level 2 | Accepted |
| [0003](ADR-0003-template-in-its-own-repository.md) | The foundation lives in its own template repository | Accepted |
| [0004](ADR-0004-agents-run-in-isolated-environment.md) | Agents run in WSL2 or a dev container | Accepted |
| [0005](ADR-0005-dev-container-is-the-boundary.md) | In the dev container, the container is the boundary | Accepted |
