# Secrets Hygiene

A secret is anything that grants access: API keys, tokens, passwords, private keys, connection strings. The goal is that a secret never reaches the repository, an Issue, a PR, a log or an agent's context, and that a mistake is caught before it leaves your machine.

If a secret has already leaked, follow [`SECURITY.md`](../../SECURITY.md#if-a-secret-is-exposed).

## Where secrets live

| Place | Use it for |
|---|---|
| A password manager | The source of truth for every secret you own |
| The OS keychain or a CLI's own login (`gh auth login`, cloud CLIs) | Credentials your tools need on your machine; they keep tokens out of files |
| GitHub Actions secrets / the hosting platform's secret store | Secrets CI or a deployed app needs |
| A local `.env` file | Development values a project reads at runtime. Ignored by Git, denied to agents, filled from the password manager |

Never put a secret in: committed files, `.env.example`, Issues, PRs, commit messages, notes, agent memory or instruction files, prompts, or logs.

## The `.env` pattern

- `.env.example` is committed. It lists the variable **names** the project needs, with empty or obviously fake values.
- `.env` (and `.env.local`, `.env.production` and so on) holds real values, stays on your machine and is ignored by Git (`.gitignore` blocks `.env` and `.env.*`, except `.env.example`).
- Agents cannot read `.env` files: Claude Code and OpenCode deny it in their settings ([adapters](../agents/adapters/README.md)). If an agent needs to know which variables exist, it reads `.env.example`.
- Name the example file exactly `.env.example`; other names are not covered by these rules.

## Agents and credentials

- **No long-lived credentials for agents.** Never paste an API key or token into a chat or a prompt, and never give an agent a token "to make it work".
- **Short-lived and narrow when a token is unavoidable.** Use a GitHub fine-grained token limited to one repository, the minimum permissions and an expiry of days, not months. Revoke it when the task ends.
- **Prefer the tool's own login.** `gh auth login` stores the token in the OS keychain; the agent uses `gh` without seeing the token. Agent settings deny reads of `~/.config/gh`, `~/.ssh` and `~/.aws`.
- **Apps that call a model** read their key from the environment at runtime, never from code. Keep keys out of prompts and model output.

## Pre-commit secret scan

[`.pre-commit-config.yaml`](../../.pre-commit-config.yaml) runs [gitleaks](https://github.com/gitleaks/gitleaks) (v8.30.1, pinned to its commit) on every commit. If it finds something that looks like a secret, the commit is blocked and gitleaks shows the file, line and rule (the value itself is redacted).

### Install the hook in WSL2 (once per clone)

```bash
# 1. pre-commit itself, pinned (pipx keeps it out of system Python)
sudo apt install pipx
pipx install pre-commit==4.7.0

# 2. in the repository folder (--install-hooks builds gitleaks now, so the
#    hook also works inside Claude Code's sandbox, which blocks the download)
pre-commit install --install-hooks

# 3. optional: scan every file once
pre-commit run gitleaks --all-files
```

Installing the hooks takes a few minutes the first time: pre-commit builds gitleaks (it installs Go by itself if you don't have it). The same steps work on Linux and macOS. The full WSL2 setup is in the [environment guide](../development/environment.md); the dev container has the hook built in.

### When the hook blocks a commit

1. **A real secret:** remove it from the file, move the value to `.env` or the password manager, and commit again. If the secret was ever pushed or shared, treat it as exposed ([`SECURITY.md`](../../SECURITY.md#if-a-secret-is-exposed)).
2. **A fake value in a test or doc:** change it so it does not look like a real key (`AKIA` followed by 16 characters matches the AWS rule), or add an inline `gitleaks:allow` comment on that line and say why in the PR.
3. **Never** skip the hook with `git commit --no-verify`. Agents are denied that command in their settings.

## Layers

| Layer | Catches | Where |
|---|---|---|
| `.gitignore` | `.env` files, `*.pem`, `*.key` | Local |
| Agent settings | Agents reading `.env` and credential folders, skipping hooks | [Adapters](../agents/adapters/README.md) |
| gitleaks pre-commit | Secrets in any committed file | Local, every commit |
| GitHub push protection | Known token formats on push | GitHub ([setup](../development/github-setup.md)) |
| gitleaks in CI | Anything that skipped the hook | CI ([#14](https://github.com/Karsp/ai-foundation/issues/14)) |
