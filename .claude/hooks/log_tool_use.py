#!/usr/bin/env python3
"""Append one line per agent tool call to a local log (docs/agents/tool-log.md).

Claude Code runs this as a hook (.claude/settings.json) with the event as JSON
on stdin. OpenCode's plugin (.opencode/plugins/log-tool-use.js) sends the same
shape. Logged: time, agent, session, subagent, event, tool, and what the tool
was pointed at (a command, a path, a URL). Never logged: tool output, file
contents, the prompt or the environment. Values that look like secrets are
replaced with [REDACTED].

The log lives outside the repository, where sandboxed commands can't change
it: $AGENT_LOG_DIR, or ~/.local/state/agent-logs/<project>/<date>.jsonl.
Files older than $AGENT_LOG_DAYS days (default 30) are deleted.

This script must never block or break the agent: it always exits 0 and
prints nothing.
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

MAX_TEXT = 1000
EVENTS = {"PreToolUse": "requested", "PostToolUse": "ran", "PostToolUseFailure": "failed"}

# What each tool was pointed at. Claude Code and OpenCode names.
TARGET_FIELDS = {
    "bash": ["command"],
    "read": ["file_path", "filePath"],
    "write": ["file_path", "filePath"],
    "edit": ["file_path", "filePath"],
    "multiedit": ["file_path", "filePath"],
    "notebookedit": ["notebook_path"],
    "glob": ["pattern", "path"],
    "grep": ["pattern", "path"],
    "list": ["path"],
    "webfetch": ["url"],
    "websearch": ["query"],
    "agent": ["subagent_type", "description"],
    "task": ["subagent_type", "description"],
    "skill": ["skill", "name"],
}

SENSITIVE_NAME = r"[A-Za-z_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|PASS|AUTH|CREDENTIALS?|COOKIE|SESSION)[A-Za-z0-9_]*"
REDACTIONS = [
    # NAME=value and NAME: value where the name looks sensitive ("Authorization: Bearer x" keeps "Bearer")
    (re.compile(rf"\b({SENSITIVE_NAME})(\s*[=:]\s*)((?:Bearer|Basic|Token)\s+)?(\"[^\"]*\"|'[^']*'|[^\s'\"]+)", re.I),
     r"\1\2\3[REDACTED]"),
    # --password value, --token=value
    (re.compile(r"(--?(?:password|passwd|pass|token|secret|api-?key|auth)[= ])(\S+)", re.I), r"\1[REDACTED]"),
    # Authorization headers
    (re.compile(r"\b(Bearer|Basic|token)\s+[A-Za-z0-9._~+/=-]{8,}", re.I), r"\1 [REDACTED]"),
    # user:password@ in URLs
    (re.compile(r"(://[^/\s:@]+:)[^@\s]+@"), r"\1[REDACTED]@"),
    # Well-known token formats
    (re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|glpat-[A-Za-z0-9_-]{20,}"
                r"|xox[abprs]-[A-Za-z0-9-]{10,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35})\b"),
     "[REDACTED]"),
    # Private key blocks
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?(-----END [A-Z ]*PRIVATE KEY-----|$)", re.S), "[REDACTED]"),
]


def redact(text: str) -> str:
    for pattern, replacement in REDACTIONS:
        text = pattern.sub(replacement, text)
    if len(text) > MAX_TEXT:
        text = text[:MAX_TEXT] + f"... [{len(text) - MAX_TEXT} more characters]"
    return text


def target(tool: str, tool_input: dict) -> dict:
    """The fields that say what the tool was pointed at, redacted."""
    if not isinstance(tool_input, dict):
        return {}
    name = tool.lower()
    if name.startswith("mcp__"):
        return {}  # MCP arguments can carry any data: log the tool name only
    result = {}
    for field in TARGET_FIELDS.get(name, []):
        value = tool_input.get(field)
        if isinstance(value, (str, int, float)) and str(value):
            result[field] = redact(str(value))
    return result


def log_dir(project: str) -> Path:
    configured = os.environ.get("AGENT_LOG_DIR")
    if configured:
        return Path(configured).expanduser()
    state = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    name = re.sub(r"[^A-Za-z0-9._-]", "_", Path(project).name or "project")
    return Path(state) / "agent-logs" / name


def prune(directory: Path) -> None:
    try:
        days = int(os.environ.get("AGENT_LOG_DAYS", "30"))
    except ValueError:
        days = 30
    cutoff = time.time() - days * 86400
    for old in directory.glob("*.jsonl"):
        if old.stat().st_mtime < cutoff:
            old.unlink()


def main() -> None:
    event = json.load(sys.stdin)
    kind = EVENTS.get(event.get("hook_event_name", ""))
    tool = str(event.get("tool_name", ""))
    if not kind or not tool:
        return
    project = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
    now = datetime.now(timezone.utc)
    line = {
        "time": now.isoformat(timespec="seconds"),
        "agent": event.get("agent", "claude-code"),
        "session": event.get("session_id", ""),
        "subagent": event.get("agent_type", ""),
        "event": kind,
        "tool": tool,
        "call": event.get("tool_use_id", ""),
        **target(tool, event.get("tool_input") or {}),
    }
    directory = log_dir(project)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = directory / f"{now:%Y-%m-%d}.jsonl"
    new = not path.exists()
    with open(path, "a", encoding="utf-8") as log:
        log.write(json.dumps({k: v for k, v in line.items() if v != ""}) + "\n")
    if new:
        path.chmod(0o600)
        prune(directory)


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - logging must never break the agent
        pass
    sys.exit(0)
