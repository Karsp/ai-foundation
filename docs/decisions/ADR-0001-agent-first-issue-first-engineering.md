# ADR-0001: Agent-first, Issue-first engineering

- **Status:** Accepted
- **Date:** 2026-10-18
- **Deciders:** Karsp
- **Issue:** #4

## Context

Projects built from this foundation are developed by one human and several AI agents (Claude Code, OpenCode, Codex and others), often in short sessions. Agent conversations are lost when a session ends, and different agents read different instruction files. Without a shared, durable process, work becomes untraceable and each agent re-derives decisions.

## Decision

All meaningful work starts as a GitHub Issue with acceptance criteria, is done on its own branch, and lands through a PR that closes the Issue. The rules are model-agnostic: `AGENTS.md` is the entry point, `docs/agents/agent-contract.md` defines the lifecycle, and agent-specific files are thin adapters that point back to them. Anything that matters beyond a session is persisted in the repository (code, docs, ADRs, Issues, PRs), never only in a conversation.

## Alternatives considered

- **Agent-specific instruction files only (e.g. only CLAUDE.md):** duplicates rules per tool and drifts.
- **Lightweight process (commit to main, notes in chat):** fast at first, but loses traceability and makes handoff between agents unreliable.

## Consequences

- Every change is reviewable and can be continued by another agent from the Issue alone.
- Small changes carry some overhead (Issue + branch + PR); trivial maintenance is exempt, as `AGENTS.md` §1 says.
- Templates (#3), the handoff guide (#5) and CI (#14) are needed to keep the overhead low.
