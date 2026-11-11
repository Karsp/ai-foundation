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
LOG_NAME = re.compile(r"^\d{4}-\d\d-\d\d\.jsonl$")
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
    # --password value, --token=value, --body value (gh secret set; also hides PR and Issue bodies)
    (re.compile(r"(--?(?:password|passwd|pass|token|secret|api-?key|auth|body)[= ]\s*)(\"[^\"]*\"|'[^']*'|\S+)", re.I),
     r"\1[REDACTED]"),
    # mysql -pX, docker login -p X, sshpass -p X
    (re.compile(r"(\b(?:mysql\w*|mariadb)\b[^\n|;&]*?\s-p)(?=\S)(\S+)"), r"\1[REDACTED]"),
    (re.compile(r"(\b(?:docker login|podman login|sshpass)\b[^\n|;&]*?\s-p\s+)(\S+)"), r"\1[REDACTED]"),
    # curl -u user:password
    (re.compile(r"(\s(?:-u|--user)[= ]\s*[^\s:]+:)(\S+)"), r"\1[REDACTED]"),
    # Authorization headers: a value with a digit, or a long one, so "Basic structure" stays
    (re.compile(r"\b(Bearer|Basic|token)\s+(?:(?=[A-Za-z._~+/=-]*\d)[A-Za-z0-9._~+/=-]{8,}|[A-Za-z0-9._~+/=-]{20,})", re.I),
     r"\1 [REDACTED]"),
    # user:password@ in URLs
    (re.compile(r"(://[^/\s:@]+:)[^@\s]+@"), r"\1[REDACTED]@"),
    # Well-known token formats
    (re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|glpat-[A-Za-z0-9_-]{20,}"
                r"|xox[abprs]-[A-Za-z0-9-]{10,}|sk-[A-Za-z0-9_-]{20,}|[sr]k_(?:live|test)_[A-Za-z0-9]{16,}|npm_[A-Za-z0-9]{36}"
                r"|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]+)\b"),
     "[REDACTED]"),
    # Webhook URLs that are themselves the secret
    (re.compile(r"https://hooks\.slack\.com/services/\S+"), "[REDACTED]"),
    # Private key blocks
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?(-----END [A-Z ]*PRIVATE KEY-----|$)", re.S), "[REDACTED]"),
]


HEREDOC = re.compile(r"<<-?\s*['\"]?\w+")


def redact(text: str) -> str:
    # A heredoc carries file contents: keep the command up to the line that starts it
    heredoc = HEREDOC.search(text)
    end = text.find("\n", heredoc.end()) if heredoc else -1
    if end != -1:
        text = f"{text[:end]}\n... [heredoc, {len(text) - end - 1} characters not logged]"
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
        directory = Path(configured).expanduser()
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        return directory
    state = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    name = re.sub(r"[^A-Za-z0-9._-]", "_", Path(project).name)
    if name.strip(".") == "":
        name = "project"
    directory = Path(state) / "agent-logs" / name
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    directory.chmod(0o700)  # our own folder: keep it private even if it existed
    return directory


def prune(directory: Path) -> None:
    try:
        days = max(1, int(os.environ.get("AGENT_LOG_DAYS", "30")))
    except ValueError:
        days = 30
    cutoff = time.time() - days * 86400
    for old in directory.glob("*.jsonl"):  # only the logger's own files
        if LOG_NAME.match(old.name) and old.is_file() and not old.is_symlink() and old.stat().st_mtime < cutoff:
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
    path = directory / f"{now:%Y-%m-%d}.jsonl"
    new = not path.exists()
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as log:
        log.write(json.dumps({k: v for k, v in line.items() if v != ""}) + "\n")
    if new:
        prune(directory)


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - logging must never break the agent
        pass
    sys.exit(0)
