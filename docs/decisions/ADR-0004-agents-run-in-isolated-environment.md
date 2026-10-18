# ADR-0004: Agents run in WSL2 or a dev container

- **Status:** Accepted
- **Date:** 2026-10-18
- **Deciders:** Karsp
- **Issue:** #4

## Context

The owner develops on Windows. Coding agents run shell commands with the user's permissions; a prompt injection or a malicious dependency can turn that into code execution on the host (OWASP ASI05). Claude Code's sandbox (filesystem and network isolation for shell commands) is available on Linux, WSL2 and macOS, but not on native Windows, where commands run unsandboxed.

## Decision

Agents run inside WSL2 or a dev container, with repositories stored inside that environment. They are never run directly on the native Windows host. Agent sandboxing is enabled and set to fail if it is unavailable (#11). The setup is documented in #13.

## Alternatives considered

- **Native Windows with permission prompts only:** prompts are easy to approve by habit and don't stop network exfiltration.
- **Cloud environments only:** good isolation, but less convenient for local tools and a local AI model (FinTrack).

## Consequences

- One-time setup on the owner's machine (WSL2, bubblewrap, socat) or a dev container.
- Host secrets (`~/.ssh`, cloud credentials) must not be mounted or must be denied to agents (#11, #12).
