# Agent tool log

Every tool call Claude Code or OpenCode makes in this repository is written to a local log: which command ran, which file was read or edited, which page was fetched, and when. It answers "what did the agent actually do during this task?" when you review its work ([threat model](../security/threat-model.md), ASI02 and ASI10).

## What is logged

One JSON line per event:

```json
{"time": "2026-11-11T00:08:05+00:00", "agent": "claude-code", "session": "16a04172-…", "event": "failed", "tool": "Bash", "call": "toolu_01KN…", "command": "cat missing-file.txt"}
```

| Field | Meaning |
|---|---|
| `time` | When the event happened, in UTC |
| `agent` | `claude-code` or `opencode` |
| `session` | The agent's session ID, to tell tasks apart |
| `subagent` | Which subagent made the call (`reviewer`, `security-reviewer`), when one did. Claude Code only |
| `event` | `requested`: the agent asked to run it. `ran`: it ran. `failed`: it ran and failed (Claude Code only) |
| `tool` | The tool's name (`Bash`, `Read`, `Edit`, `bash`, `write`, `mcp__server__tool`) |
| `call` | The call's ID: a `requested` line and its `ran` or `failed` line share it |
| `command`, `file_path`, `filePath`, `pattern`, `path`, `url`, `query`, … | What the tool was pointed at |

A `requested` line with no `ran` or `failed` line after it means the call never ran: a permission rule denied it, you declined it, or the session stopped.

**Never logged:** tool output, what the Write and Edit tools write, the prompt, error messages and the environment. MCP tools are logged by name only, because their arguments can carry any data.

**Logged as written, after redaction:** shell commands, up to 1,000 characters. A command can contain text it writes (`echo … > file`); the body of a heredoc (`cat > file <<EOF`) is left out. Values that look like secrets are replaced with `[REDACTED]`: `API_KEY=…`, `--password …`, `--token=…`, `--body …`, `mysql -p…`, `docker login -p …`, `curl -u user:…`, `Authorization: Bearer …`, `user:password@` in URLs, GitHub, GitLab, Slack, OpenAI, Stripe, npm, AWS and Google keys, JWTs, Slack webhook URLs and private key blocks.

## Where it lives

`~/.local/state/agent-logs/<project>/<YYYY-MM-DD>.jsonl` (or under `$XDG_STATE_HOME` when that is set), one file per day. The folder is readable only by you (`0700`, files `0600`; a folder you set with `AGENT_LOG_DIR` keeps its own permissions).

The log is outside the repository on purpose: it can never be committed, and in WSL2 the agent's sandboxed commands can't write outside the project, so they can't change or delete it. The logger runs as a hook, outside the sandbox, so its own files are protected too: the sandbox denies writes to `.claude/hooks/` and, through `denyWrite` in `.claude/settings.json`, to `.opencode/` and `opencode.json`. Hooks run `python3 -I`, so nothing planted next to the script or in `PYTHONPATH` is imported.

Log files (named `YYYY-MM-DD.jsonl`) older than 30 days are deleted when a new day's file starts; nothing else in the folder is touched. Set these environment variables before starting the agent to change it:

| Variable | Default | Effect |
|---|---|---|
| `AGENT_LOG_DIR` | `~/.local/state/agent-logs/<project>` | Where the files go. Use a folder of its own; inside the project, use `.agent-logs/`, which Git ignores, and note that the agent can then change it |
| `AGENT_LOG_DAYS` | `30` | How many days to keep (at least 1) |

## Reading it

```bash
cd ~/.local/state/agent-logs/ai-foundation
jq -r 'select(.event=="ran" and .tool=="Bash") | "\(.time) \(.command)"' 2026-11-11.jsonl  # commands that ran
jq -c 'select(.event=="failed")' *.jsonl                                                      # failed calls
jq -r 'select(.tool|test("^(Edit|MultiEdit|Write|NotebookEdit|edit|write|patch)$")) | .file_path // .filePath // .notebook_path // .tool' *.jsonl | sort -u  # files changed by the file tools
```

Commands that change files (`sed -i`, `mv`, `>`) show up only as commands. The log is untrusted content, like anything an agent wrote: a command can contain text meant for whoever reads it, or terminal control characters, which `jq -r` prints raw. Use `jq -c` to see them escaped.

Each line is written by a separate process, so calls that run at the same time can appear out of order: sort by `time` and match lines by `call` when the order matters.

## How it works

| | Claude Code | OpenCode |
|---|---|---|
| Hook | `PreToolUse`, `PostToolUse` and `PostToolUseFailure` hooks for every tool in [`.claude/settings.json`](../../.claude/settings.json) | The plugin [`.opencode/plugins/log-tool-use.js`](../../.opencode/plugins/log-tool-use.js), loaded automatically, on `tool.execute.before` and `tool.execute.after` |
| Logger | [`.claude/hooks/log_tool_use.py`](../../.claude/hooks/log_tool_use.py) | The same script: the plugin passes each call to it, without the output |

There is one logger, so the redaction rules exist once. It needs `python3` (WSL2's Ubuntu and the dev container have it), always exits 0 and prints nothing, so a logging problem never blocks or changes what the agent does. In WSL2 a sandboxed command can't replace it, which is what keeps that true. Its tests are in [`tests/test_log_tool_use.py`](../../tests/test_log_tool_use.py) and run with `make test`.

## Limits

- **It is a record, not a control.** It shows what happened afterwards; the [permission rules and sandbox](adapters/README.md) are what stop things.
- **It is local.** Nothing is sent anywhere, and there is no alerting (non-goals of [#29](https://github.com/Karsp/ai-foundation/issues/29)).
- **It can be turned off.** Anyone can disable hooks in their own settings (`disableAllHooks`) or remove the plugin. Agents are asked before editing `.claude/` and `.opencode/` with their file tools, and in WSL2 the sandbox stops shell commands from writing `.claude/hooks/`, `.claude/settings.json`, `.opencode/` and `opencode.json`.
- **OpenCode has no sandbox.** Run in WSL2, an OpenCode agent's shell commands (which ask first) could change the logger; run OpenCode in the dev container.
- **In the dev container** the log is inside the container: it is lost when the container is rebuilt, and an agent there can change it, because the container is the boundary and Claude Code's sandbox is off ([ADR-0005](../decisions/ADR-0005-dev-container-is-the-boundary.md)). Copy it out with `docker cp` if you need to keep it.
- **Redaction works by pattern.** A secret in an unusual form (a bare value with no name next to it, or one in a variable with an ordinary name) can still be logged. Agents never read secrets in the first place ([secrets](../security/secrets.md)), and the log stays on your machine.
- **OpenCode has no failure event.** A failed OpenCode call can show as `ran`, or as `requested` only.
- **What OpenCode runs is checked by calling the plugin directly**, not by a live session with a model (see below).

## How it was tested

Tested on 11 November 2026 with Claude Code 2.1.322 and OpenCode 1.19.4:

| Check | Result |
|---|---|
| `make test` | 16 tests: lines and times, events, no output, contents or environment, redaction of 14 secret forms, ordinary words kept, heredoc bodies left out, MCP name only, OpenCode names, long values cut, bad input and an unwritable folder never fail, only old log files deleted, `AGENT_LOG_DAYS=0` keeps today, modes `0600`/`0700`, default location outside the project, a `..` project name |
| Claude Code runs `ls scripts`, `sudo ls` (denied), `cat missing-file.txt` (fails) and reads `README.md` | `requested` + `ran`; `requested` only; `requested` + `failed`; `requested` + `ran` with `file_path`. No output in the log |
| In the WSL2-style sandbox (bubblewrap), Claude Code runs `touch .claude/hooks/probe.py`, `echo x >> .claude/hooks/log_tool_use.py`, `touch .opencode/plugins/probe.js`, `touch opencode.json`, `touch probe-ok.txt` | `Read-only file system` for the first four; the last works |
| `opencode debug config` | `plugin` lists `.opencode/plugins/log-tool-use.js` |
| The plugin's hooks called with a `bash` call (`TOKEN=… ls`, output marker) and a `write` call (content marker) | Lines with `agent: opencode`, the command redacted, `filePath`; no output or content |

Re-run them after upgrading Claude Code or OpenCode, or after changing the logger.
