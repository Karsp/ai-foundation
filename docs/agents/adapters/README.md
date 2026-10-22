# Agent Adapters

The rules live in [`AGENTS.md`](../../../AGENTS.md) and the documents it links. An adapter is the small set of files that makes one agent read those rules and **enforces** part of them in that agent's own settings. Markdown rules are advice an agent can ignore or be talked out of; settings are checked by the tool before anything runs.

Adapters never repeat rule text. If a rule is missing, add it to `AGENTS.md` or the right document, not to an adapter.

## Which files each agent reads

| Agent | Instructions | Enforcement | MCP servers |
|---|---|---|---|
| Claude Code | [`CLAUDE.md`](../../../CLAUDE.md), which imports `AGENTS.md` | [`.claude/settings.json`](../../../.claude/settings.json): permissions and sandbox | [`.mcp.json`](../../../.mcp.json) |
| OpenCode | `AGENTS.md` (read natively) | [`opencode.json`](../../../opencode.json): `permission` | `opencode.json` → `mcp` |
| GGA (pre-commit reviewer) | `AGENTS.md` (`RULES_FILE` in `.gga`) | none: it reviews, it doesn't act | none |
| Any other agent | `AGENTS.md` | Add an adapter here before using it | Follow the [MCP policy](../../security/mcp-policy.md) |

Personal overrides go in files that are not committed (`.claude/settings.local.json`, user-level settings). They may tighten the project settings but should not loosen them.

## What the settings enforce

| Rule in `AGENTS.md` / policy | Claude Code (`.claude/settings.json`) | OpenCode (`opencode.json`) |
|---|---|---|
| Never read secrets (§5) | `deny` Read and Edit of `.env`, `.env.local`, `.env.*.local`, `.env.development`, `.env.production`, `.env.staging`, `.env.test`, `*.pem`, `*.key`, `~/.ssh`, `~/.aws`, `~/.config/gh`, `~/.gnupg`; the sandbox also hides these from shell commands | `read`/`edit` deny `*.env`, `*.env.*` (except `*.env.example`), `*.pem`, `*.key`; `external_directory` deny the same home folders; `shell` deny commands mentioning `.env` |
| No destructive actions without approval (§5) | `deny` `git push --force`/`-f`, `rm -rf`, `sudo`, and bare `sh`/`bash`/`zsh` (blocks `curl … \| sh`) | `shell` deny the same patterns, including `* \| sh` and `* \| bash` |
| Dependencies need approval ([supply chain](../../security/supply-chain.md)) | `ask` for `npm install/i/add/update`, `npx`, `pnpm add/install/update`, `yarn add`, `pip install`, `uv add`, `uv pip install`, `uvx`, `curl`, `wget` | `shell` ask by default; installs explicitly `ask` |
| Agent rules and CI change only with approval (§5, §6) | `ask` before editing `AGENTS.md`, `CLAUDE.md`, `.claude/**`, `opencode.json`, `.mcp.json`, `.github/workflows/**` | `edit` ask for the same files |
| Never skip the secret scan ([secrets](../../security/secrets.md)) | `deny` `git commit --no-verify`/`-n` and `git push --no-verify` | `shell` deny the same patterns |
| Run isolated ([ADR-0004](../../decisions/ADR-0004-agents-run-in-isolated-environment.md)) | `sandbox.enabled` with `failIfUnavailable`: Claude Code refuses to start without a working sandbox; `allowUnsandboxedCommands: false`; network limited to GitHub, npm and PyPI | No built-in sandbox: run OpenCode inside WSL2 or the dev container ([#13](https://github.com/Karsp/ai-foundation/issues/13)) |
| MCP servers only from the approved list ([MCP policy](../../security/mcp-policy.md)) | `enableAllProjectMcpServers: false`: each server in `.mcp.json` needs approval | Servers only in `opencode.json` → `mcp`, through a PR |
| No bypass | `disableBypassPermissionsMode: "disable"` | n/a |

## Known limits

- **The sandbox needs Linux, WSL2 or macOS.** It does not run on native Windows, and on Linux/WSL2 it needs `bubblewrap` and `socat` installed. With `failIfUnavailable`, Claude Code stops with an error instead of running unprotected. Install them (`sudo apt install bubblewrap socat`) or use the dev container (#13).
- **`git` and `gh` run outside the sandbox** (`excludedCommands`), because they need your GitHub credentials. Permission rules still apply to them (for example, force pushes are denied), and the ruleset on `main` blocks the rest ([GitHub setup](../../development/github-setup.md)).
- **The sandbox does not cover MCP servers or hooks.** They run with your user's rights, which is why the [MCP policy](../../security/mcp-policy.md) exists.
- **Pattern rules can be worked around** by a determined or injected agent (for example a script that reads a secret). They catch mistakes and obvious attacks; isolation and least privilege do the rest.
- **The example env file must be named `.env.example`.** Other names like `.env.sample` are not on the deny lists but are also not meant to hold secrets.

## Checking the adapters

Run these in a throwaway folder with a fake `.env` (for example `API_KEY=fake`), after copying the settings:

| Check | Expected |
|---|---|
| Ask Claude Code to read `.env` with the Read tool | "File is in a directory that is denied by your permission settings" |
| Ask it to run `cat .env` | "Permission to use Bash with command cat .env has been denied" |
| Ask it to read `.env.example` | It shows the file |
| Ask it to run `git push --force origin main` | Denied |
| Ask it to run `git commit --no-verify -m test` | Denied |
| Start Claude Code where `bubblewrap` is missing | "sandbox required but unavailable … refusing to start" |
| Run `opencode debug config` | The `permission` block appears as written |

Re-run them after upgrading Claude Code or OpenCode, and validate `.claude/settings.json` against the [Claude Code settings schema](https://json.schemastore.org/claude-code-settings.json).
