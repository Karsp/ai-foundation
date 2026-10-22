# ADR-0005: In the dev container, the container is the boundary

- **Status:** Proposed
- **Date:** 2026-10-22
- **Deciders:** Karsp
- **Issue:** #13

## Context

[ADR-0004](ADR-0004-agents-run-in-isolated-environment.md) says agents run in WSL2 or a dev container, with Claude Code's sandbox enabled and set to fail if it is unavailable. The sandbox uses bubblewrap, which needs to create Linux user namespaces. Inside a Docker container with Docker's default seccomp profile, it can't: tested on 22 October 2026 with Ubuntu 26.04, bubblewrap fails with "No permissions to create a new namespace". With seccomp turned off it works only in the weaker nested mode (`enableWeakerNestedSandbox`), which shares the container's `/proc`.

So in the dev container, Claude Code with the project settings refuses to start.

## Decision

In the dev container, the container itself is the isolation boundary, and Claude Code's sandbox is turned off there through `/etc/claude-code/managed-settings.json` in the image. The container:

- mounts only the project folder (no home folder, credentials or Docker socket);
- runs as a non-root user whose only `sudo` right is starting the firewall;
- blocks all outbound traffic except DNS, GitHub and the hosts in `.devcontainer/allowed-domains.txt`, and all IPv6, with an iptables firewall at every start;
- keeps Docker's default seccomp profile.

In WSL2, nothing changes: Claude Code's sandbox stays enabled with `failIfUnavailable`.

## Alternatives considered

- **Loosen Docker** (`seccomp=unconfined` plus `enableWeakerNestedSandbox`): Claude Code's sandbox would run, but removing Docker's system-call filter makes escaping the container easier, and it protects Claude Code only, not OpenCode.
- **Privileged container:** gives the container almost full access to the host. Rejected.
- **No firewall, sandbox off:** the agent could send data anywhere. Rejected.

This follows the design of Anthropic's [reference dev container](https://code.claude.com/docs/en/devcontainer).

## Consequences

- The same boundary covers every agent in the container, including OpenCode, which has no sandbox of its own.
- Inside the container, an agent can write anywhere in the container and read any file in it; only the project folder reaches the host. Nothing outside the project survives a rebuild, including Claude Code's sign-in.
- The firewall needs the `NET_ADMIN` and `NET_RAW` capabilities, resolves host addresses at start (restart when a CDN changes address), and leaves DNS open.
- Changes to `.devcontainer/` widen or narrow the boundary, so agents must ask before editing it and changes go through a PR.
