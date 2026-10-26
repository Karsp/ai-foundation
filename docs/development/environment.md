# Development Environment

Agents run shell commands with your permissions. A prompt injection or a malicious package can turn that into code running on your machine (OWASP ASI05). So agents never run directly on Windows: they run in **WSL2** or in the **dev container** ([ADR-0004](../decisions/ADR-0004-agents-run-in-isolated-environment.md)).

| | WSL2 | Dev container |
|---|---|---|
| Use it for | Daily work on a Windows machine | A throwaway, identical environment; agents other than Claude Code |
| What isolates the agent | Claude Code's sandbox: commands can write only in the project and reach only GitHub, npm and PyPI | The container: it sees only the project folder, and a firewall lets out only GitHub, npm, PyPI and the model providers you turn on |
| Covers OpenCode | No (OpenCode has no sandbox) | Yes: set its version in `devcontainer.json` |
| Setup | Once per machine | Docker Desktop and VS Code, then one click per project |

Both use the settings in [`.claude/settings.json`](../../.claude/settings.json) and the secret scan in [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml).

## Option A: WSL2

### 1. Install Ubuntu 26.04

In PowerShell:

```powershell
wsl --install -d Ubuntu-26.04
wsl -l -v    # the VERSION column must say 2
```

Open the new Ubuntu terminal and create your Linux user when asked.

### 2. Keep Windows out of the agent's reach

WSL2 can read your whole C: drive (`/mnt/c`) and start Windows programs, and a Windows program started from WSL runs outside Claude Code's sandbox. Turn off starting Windows programs for this distribution by adding an `[interop]` section to `/etc/wsl.conf`:

```bash
cat /etc/wsl.conf    # if it already has an [interop] section, edit that one instead
sudo tee -a /etc/wsl.conf > /dev/null <<'EOF'

[interop]
enabled=false
appendWindowsPath=false
EOF
```

Then run `wsl --shutdown` in **PowerShell** (restarting from inside Linux is not enough), wait about 10 seconds, and open Ubuntu again. Check it worked:

```bash
cmd.exe /c ver                # fails: Windows programs can't start
echo $PATH | grep -c /mnt/c   # prints 0
```

Your Windows drives are still visible under `/mnt/c`: this step doesn't hide them. Step 5 stops the agent from reading them.

The trade-off: `code .` and `explorer.exe .` no longer work from the Ubuntu terminal. Open VS Code on Windows and use **WSL: Connect to WSL** instead, and reach your Linux files from Windows Explorer at `\\wsl.localhost\Ubuntu-26.04`.

### 3. Install the tools

All from the Ubuntu archive, which is signed and versioned:

```bash
sudo apt update
sudo apt install -y git gh nodejs npm pipx bubblewrap socat ripgrep
```

`bubblewrap`, `socat` and `ripgrep` are what Claude Code's sandbox runs on (`/sandbox` lists any that are missing). Check whether Ubuntu's AppArmor blocks bubblewrap:

```bash
sysctl kernel.apparmor_restrict_unprivileged_userns
```

If it prints `0` or "No such file or directory", go on. If it prints `1`, follow the AppArmor step in Claude Code's [Linux and WSL2 setup](https://code.claude.com/docs/en/sandboxing#set-up-linux-and-wsl2).

### 4. Install Claude Code and pre-commit at fixed versions

```bash
npm config set prefix ~/.local                       # per-user installs, no sudo
npm install -g @anthropic-ai/claude-code@2.1.304     # or a newer version at least 72 hours old
pipx install pre-commit==4.7.0
pipx ensurepath                                      # adds ~/.local/bin to PATH
source ~/.bashrc                                     # or open a new terminal
claude --version                                     # prints 2.1.304 (Claude Code)
```

To pick a newer Claude Code version, list release dates with `npm view @anthropic-ai/claude-code time --json` and choose one published at least 72 hours ago ([supply-chain policy](../security/supply-chain.md)).

### 5. Your personal Claude Code settings

Create `~/.claude/settings.json` in Ubuntu. It applies to every project on this machine and adds to the project settings. The `~/.claude` folder appears only after Claude Code's first start, so create it first:

```bash
mkdir -p ~/.claude
cat > ~/.claude/settings.json <<'EOF'
{
  "autoUpdatesChannel": "stable",
  "permissions": {
    "deny": ["Read(//mnt/**)", "Edit(//mnt/**)"]
  },
  "sandbox": {
    "filesystem": { "denyRead": ["/mnt"] }
  }
}
EOF
```

- `autoUpdatesChannel: stable`: automatic updates install a version about a week old instead of the newest one.
- The `/mnt` rules stop Claude Code from reading your Windows drives, even if you leave them mounted. A side effect: a repository stored under `/mnt/c` won't work, which is intended (step 7).

### 6. Sign in to GitHub

```bash
gh auth login        # GitHub.com, HTTPS, log in with a web browser
gh auth setup-git    # Git uses gh for its credentials
git config --global user.name "<your GitHub username>"
git config --global user.email "<your GitHub noreply address>"
```

Without interop, `gh` can't open the browser: open the address it prints in your Windows browser and type the code.

The token stays in `gh`'s own storage. Agents are denied reading it, and the sandbox hides it from the commands they run. Only `git push`, `git fetch`, `git pull`, `git clone`, `git ls-remote` and `gh` run outside the sandbox, because they need the token ([adapters](../agents/adapters/README.md)). Never put a GitHub token in `.env` or give it to an agent ([secrets](../security/secrets.md)).

### 7. Clone into the Linux filesystem

```bash
mkdir -p ~/code && cd ~/code
git clone https://github.com/<owner>/<repo>.git
cd <repo>
pre-commit install --install-hooks
```

Keep repositories under `~/code`, never under `/mnt/c`: it is faster, and the Windows drive is outside the agent's reach (step 5). `--install-hooks` builds the gitleaks hook now; inside the sandbox it couldn't download what it needs.

### 8. Check it works

Run `claude` in the repository. It must start without "sandbox required but unavailable". The first time, sign in: the browser doesn't open by itself (step 2), so copy the address it shows into your Windows browser and paste the code back. When it asks whether you trust the folder, answer yes for your own repository. Then:

| Check | Expected |
|---|---|
| `/sandbox` | Sandbox enabled; no Dependencies tab |
| Ask Claude to run `touch ~/sandbox-probe` | `Read-only file system` |
| Ask Claude to run `curl --noproxy '*' https://example.com` | `Could not resolve host` |
| Ask Claude to read a file under `/mnt/c` | Denied by your permission settings |
| Ask Claude to run `git fetch` | Works (it runs outside the sandbox with your credentials) |
| Ask Claude to commit a file containing `AKIA` followed by 16 capital letters or digits | The gitleaks hook blocks the commit |

If Claude asks to retry a failed command outside the sandbox, decline. More checks are in the [adapters guide](../agents/adapters/README.md#checking-the-adapters).

## Option B: Dev container

[`.devcontainer/`](../../.devcontainer/) defines a container where agents run with no access to the rest of your machine.

### What it contains

| Part | File | What it does |
|---|---|---|
| Base image | [`Dockerfile`](../../.devcontainer/Dockerfile) | Ubuntu 26.04, pinned by digest. Dependabot proposes digest updates weekly |
| Tools | `Dockerfile` | Git, `gh`, Node.js 22, Go and pipx from the Ubuntu archive; the agents you choose (Claude Code, OpenCode) and pre-commit at exact versions; the gitleaks hook built in advance |
| Mounts | [`devcontainer.json`](../../.devcontainer/devcontainer.json) | Only the project folder, at `/workspace`. No home folder, `~/.ssh`, cloud credentials or Docker socket |
| User | `Dockerfile` | `ubuntu` (uid 1000), not root. Its only `sudo` right is starting the firewall |
| Firewall | [`init-firewall.sh`](../../.devcontainer/init-firewall.sh), [`firewall/`](../../.devcontainer/firewall/README.md) | Runs at every start. Blocks all outbound traffic except DNS, GitHub and the hosts in the lists you turn on (`base` plus, by default, `anthropic`); refuses wildcards; blocks IPv6. Needs the `NET_ADMIN` and `NET_RAW` capabilities |
| Claude Code policy | [`managed-settings.json`](../../.devcontainer/managed-settings.json) | Turns Claude Code's own sandbox off inside the container, where it cannot run, because the container and its firewall are the boundary ([ADR-0005](../decisions/ADR-0005-dev-container-is-the-boundary.md)). Also turns off auto-updates and non-essential traffic |

Claude Code's sign-in is not kept in a volume: after a rebuild you sign in again. This is deliberate, so nothing an agent writes to `~/.claude` (settings, hooks) survives a rebuild.

### Use it

1. Install [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) with the WSL2 backend, VS Code, and the **Dev Containers** extension.
2. Clone the repository inside WSL2 (Option A, steps 1 and 7) or let VS Code clone it into a container volume.
3. In VS Code: **Dev Containers: Reopen in Container**. The first build takes several minutes. The terminal shows `Firewall ready` when the container is up.
4. In the container terminal: `claude` and sign in (open the printed address in your browser). If the clone is new, also run `pre-commit install`. For `gh`, run `gh auth login` with a [fine-grained token](https://github.com/settings/personal-access-tokens/new) limited to this repository, with the permissions the task needs and an expiry of a few days.

VS Code shares your Git credentials with the container by default, so `git push` works there. Agents in the container can use them too, as in WSL2.

### Check it works

| Check (in the container terminal) | Expected |
|---|---|
| `curl -sS https://example.com` | Fails: the host is not on the list |
| `curl -sS -o /dev/null -w "%{http_code}\n" https://registry.npmjs.org/` | `200` |
| `sudo iptables -F` | Asks for a password, which the user doesn't have |
| `claude` | Starts and asks you to sign in (no sandbox error) |
| Commit a file containing a fake AWS key | The gitleaks hook blocks it |

### Change it

All changes go through a PR, and agents must ask before editing `.devcontainer/` ([adapters](../agents/adapters/README.md)).

Agents and firewall lists are set in `build.args` in [`devcontainer.json`](../../.devcontainer/devcontainer.json). After any change, run **Dev Containers: Rebuild Container**.

- **Agent versions:** `CLAUDE_CODE_VERSION` and `OPENCODE_VERSION`, each at least 72 hours old. Leave one empty to not install it.
- **OpenCode:** set `OPENCODE_VERSION` (for example `1.19.4`) and add `opencode` plus your model provider's list to `FIREWALL_LISTS`, for example `"anthropic opencode openai"`. Its own settings are in [`opencode.json`](../../opencode.json).
- **Model providers:** turn on a list from [`.devcontainer/firewall/`](../../.devcontainer/firewall/README.md) (`anthropic`, `openai`, `openrouter`, `opencode`). For another provider, add a short list file with its API host only. Every host is a new way out for data (Rule of Two), so say why in the PR.
- **Project tools** (Python, a database client): add them to the `Dockerfile` from the Ubuntu archive, or at exact versions.

### Known limits

- **DNS is open.** The firewall allows DNS to any server, which a determined attacker could use to leak small amounts of data.
- **Addresses are resolved at start.** If a host on the list changes address (CDNs do), restart the container.
- **The project folder is shared.** An agent can change any file in it, including Git hooks. Review diffs before you commit from the host.
- **Docker Desktop runs with your Windows rights.** Keep it updated, and never mount the Docker socket into the container.

## Which one to use

Use WSL2 every day. Use the dev container when you want a clean environment, when you run an agent that has no sandbox of its own, or before letting an agent work with fewer permission prompts.
