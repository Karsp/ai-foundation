# CI and standard commands

Every repository built from this template runs the same checks in three places: on each commit (pre-commit hooks), on demand (`make`), and on each pull request (GitHub Actions). One tool, [pre-commit](https://pre-commit.com), runs them all, so a check that passes on your machine passes in CI.

## Commands

Run `make help` for the list. Agents use these commands and don't invent others ([`AGENTS.md`](../../AGENTS.md) §4).

| Command | What it does |
|---|---|
| `make setup` | Installs the Git hooks and builds them. Once per clone |
| `make lint` | Every check on every file (below) |
| `make format` | Fixes what can be fixed automatically: final newlines, trailing spaces |
| `make links` | Relative links and headings in Markdown |
| `make security` | Scans every commit in the Git history for secrets |
| `make test` | The tests. This template has none; projects put their test command here |
| `make ci` | `lint`, `security` and `test`: exactly what CI runs |

## What this repository checks

All in [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml), each tool pinned to a commit SHA.

| Check | Tool | Catches |
|---|---|---|
| Secrets in the commit | gitleaks | Keys and tokens before they are committed |
| Secrets in the history | gitleaks (`make security`, CI only) | A secret committed with the hook skipped, even if a later commit removed it |
| YAML and JSON | pre-commit-hooks | Syntax errors in config files |
| File hygiene | pre-commit-hooks | Merge conflict markers, files over 500 KB, missing final newlines, trailing spaces |
| Workflows and Dependabot | check-jsonschema, actionlint | Invalid workflow or Dependabot config; script injection from untrusted input such as a PR title |
| Shell scripts | shellcheck | Quoting bugs and unsafe patterns |
| Markdown style | markdownlint-cli2 ([rules](../../.markdownlint-cli2.yaml)) | Inconsistent headings, lists and code blocks |
| Markdown links | [`scripts/check_links.py`](../../scripts/check_links.py) | Links to files or headings that don't exist. Web links aren't checked: they need the network and change outside the repository |

CI is [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml): one job, **Checks**, that runs `make ci` on every pull request and every push to `main`. Mark it as a required check ([GitHub setup](github-setup.md)).

A second workflow, [`.github/workflows/devcontainer.yml`](../../.github/workflows/devcontainer.yml), runs only when a pull request changes `.devcontainer/` or the check tools (Dependabot's base image updates included). It builds the [dev container](environment.md#option-b-dev-container), starts its firewall, checks that an unlisted host is blocked and that the container user can't change the firewall, and runs `make ci` inside. Don't mark it as required: a required check that doesn't run on a pull request blocks it.

## Rules for every workflow

These keep a pull request, or a compromised Action, from reaching your secrets or changing the repository (OWASP ASI04, ASI05).

- **Pin every Action to a full commit SHA**, with the version in a comment, from a release at least 72 hours old ([supply-chain policy](../security/supply-chain.md)). Dependabot proposes updates weekly.
- **Read-only token:** `permissions: contents: read` at the top. A job that needs more (CodeQL uploads results) asks for it in that job only.
- **`persist-credentials: false`** on `actions/checkout`, so later steps can't reuse the token.
- **Trigger on `pull_request`, never `pull_request_target` or `workflow_run`** for code from a pull request. With `pull_request`, a pull request from a fork gets no secrets and a read-only token.
- **No `${{ github.event... }}` inside `run:`**: pass untrusted text through `env:` instead. actionlint fails the check if you forget.
- **A `timeout-minutes` on every job**, so a stuck job doesn't run for six hours.

## Adapting CI for a project

[`ci/app-ci.yml`](ci/app-ci.yml) is an example workflow for an application. Copy it over `.github/workflows/ci.yml` and change the lines marked `CHANGE`. It has three jobs:

| Job | What it does | Needs |
|---|---|---|
| **Checks** | `make ci` after setting up your language and installing dependencies from the lockfile | Your test and audit commands in the `Makefile` |
| **Dependency review** | Fails a pull request that adds a dependency with a known vulnerability (moderate or worse) | Dependency graph on. Free on public repositories; private ones need GitHub Advanced Security |
| **CodeQL** | Static analysis for security bugs, results in the Security tab. Also runs weekly | Free on public repositories; private ones need GitHub Advanced Security |

Then fill in the `Makefile`:

1. **`setup`:** add the dependency install from the lockfile (`npm ci`, `uv sync --locked`).
2. **`test`:** replace the stub with your test command. Never make it pass by skipping tests.
3. **`security`:** add your dependency audit after the secret scan, for example `npm audit --audit-level=moderate` or `uv run pip-audit` (a new tool needs the supply-chain checks first).
4. **`lint`, `typecheck`, `build`:** add your linter, formatter and type checker as pre-commit hooks so they run on commit too, or as `make` targets that `ci` depends on.
5. Keep the target names: agents and CI rely on them.

Add any new check as a required status check once it has run once on a pull request.

## Adding a check

Add it to `.pre-commit-config.yaml`, not to the workflow, so it runs everywhere. Pin it like the others: a release at least 72 hours old, its commit SHA as `rev`, and `# frozen: vX.Y.Z` after it. Check it on every file with `make lint`, and list it in the pull request with its version and release date. Changing CI or the checks needs the owner's approval ([autonomy policy](../agents/autonomy.md)).

## Known limits

- **pre-commit itself** is pinned (`4.7.0`), but the Python packages it depends on are not hash-pinned.
- **Hook environments** are downloaded the first time a hook runs, then cached. In Claude Code's sandbox that download is blocked, which is why `make setup` builds them in advance.
- **The history scan never forgets.** Once a secret is in the history, `make security` fails until you rotate the secret and record it as handled ([secrets](../security/secrets.md#a-secret-in-the-history)).
- **Web links aren't checked.**
