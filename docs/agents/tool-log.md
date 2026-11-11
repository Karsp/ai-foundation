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
| `subagent` | Which subagent made the call (`reviewer`, `security-reviewer`), when one did |
| `event` | `requested`: the agent asked to run it. `ran`: it ran. `failed`: it ran and failed (Claude Code only) |
| `tool` | The tool's name (`Bash`, `Read`, `Edit`, `bash`, `write`, `mcp__server__tool`) |
| `call` | The call's ID: a `requested` line and its `ran` or `failed` line share it |
| `command`, `file_path`, `filePath`, `pattern`, `path`, `url`, `query`, … | What the tool was pointed at |

A `requested` line with no `ran` or `failed` line after it means the call never ran: a permission rule denied it, you declined it, or the session stopped.

**Never logged:** tool output, file contents, the text written to a file, the prompt, error messages and environment variables. MCP tools are logged by name only, because their arguments can carry any data. Values that look like secrets (`API_KEY=…`, `--password …`, `Authorization: Bearer …`, `user:password@` in URLs, GitHub, GitLab, Slack, OpenAI, AWS and Google keys, private key blocks) are replaced with `[REDACTED]`, and any value longer than 1,000 characters is cut.

## Where it lives

`~/.local/state/agent-logs/<project>/<YYYY-MM-DD>.jsonl` (or under `$XDG_STATE_HOME` when that is set), one file per day. The folder is readable only by you (`0700`, files `0600`).

The log is outside the repository on purpose: it can never be committed, and in WSL2 the agent's sandboxed commands can't write outside the project, so they can't change or delete it. The logger itself runs as a hook, outside the sandbox.

Files older than 30 days are deleted when a new day's file starts. Set these environment variables before starting the agent to change it:

| Variable | Default | Effect |
|---|---|---|
| `AGENT_LOG_DIR` | `~/.local/state/agent-logs/<project>` | Where the files go |
| `AGENT_LOG_DAYS` | `30` | How many days to keep |

## Reading it

```bash
cd ~/.local/state/agent-logs/ai-foundation
jq -r 'select(.event=="ran" and .tool=="Bash") | "\(.time) \(.command)"' 2026-11-11.jsonl  # commands that ran
jq -c 'select(.event=="failed")' *.jsonl                                                      # failed calls
jq -r 'select(.tool|test("^(Edit|Write|edit|write)$")) | .file_path // .filePath' *.jsonl | sort -u  # files changed
```

Each line is written by a separate process, so calls that run at the same time can appear out of order: sort by `time` and match lines by `call` when the order matters.

## How it works

| | Claude Code | OpenCode |
|---|---|---|
| Hook | `PreToolUse`, `PostToolUse` and `PostToolUseFailure` hooks for every tool in [`.claude/settings.json`](../../.claude/settings.json) | The plugin [`.opencode/plugins/log-tool-use.js`](../../.opencode/plugins/log-tool-use.js), loaded automatically, on `tool.execute.before` and `tool.execute.after` |
| Logger | [`.claude/hooks/log_tool_use.py`](../../.claude/hooks/log_tool_use.py) | The same script: the plugin passes each call to it, without the output |

There is one logger, so the redaction rules exist once. It needs `python3` (WSL2's Ubuntu and the dev container have it), always exits 0 and prints nothing, so a logging problem never blocks or changes what the agent does. Its tests are in [`tests/test_log_tool_use.py`](../../tests/test_log_tool_use.py) and run with `make test`.

## Limits

- **It is a record, not a control.** It shows what happened afterwards; the [permission rules and sandbox](adapters/README.md) are what stop things.
- **It is local.** Nothing is sent anywhere, and there is no alerting (non-goals of [#29](https://github.com/Karsp/ai-foundation/issues/29)).
- **It can be turned off.** Anyone can disable hooks in their own settings (`disableAllHooks`) or remove the plugin. Agents are asked before editing `.claude/` and `.opencode/`, and Claude Code's sandbox stops commands from writing `.claude/`.
- **In the dev container** the log is inside the container: it is lost when the container is rebuilt, and an agent there can change it, because the container is the boundary and Claude Code's sandbox is off ([ADR-0005](../decisions/ADR-0005-dev-container-is-the-boundary.md)). Copy it out with `docker cp` if you need to keep it.
- **Redaction works by pattern.** A secret in an unusual form (a bare value with no name next to it) can still be logged. Agents never read secrets in the first place ([secrets](../security/secrets.md)), and the log stays on your machine.
- **OpenCode has no failure event.** A failed OpenCode call can show as `ran`, or as `requested` only.
- **What OpenCode runs is checked by calling the plugin directly**, not by a live session with a model (see below).

## How it was tested

Tested on 11 November 2026 with Claude Code 2.1.322 and OpenCode 1.19.4:

| Check | Result |
|---|---|
| `make test` | 12 tests: lines and times, events, no output, contents or environment, redaction of 7 secret forms, MCP name only, OpenCode names, long values cut, bad input and an unwritable folder never fail, old files deleted, file mode `0600`, default location outside the project |
| Claude Code runs `ls scripts`, `sudo ls` (denied), `cat missing-file.txt` (fails) and reads `README.md` | `requested` + `ran`; `requested` only; `requested` + `failed`; `requested` + `ran` with `file_path`. No output in the log |
| `opencode debug config` | `plugin` lists `.opencode/plugins/log-tool-use.js` |
| The plugin's hooks called with a `bash` call (`TOKEN=… ls`, output marker) and a `write` call (content marker) | Lines with `agent: opencode`, the command redacted, `filePath`; no output or content |

Re-run them after upgrading Claude Code or OpenCode, or after changing the logger.
