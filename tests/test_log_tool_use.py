"""Tests for the agent tool log (.claude/hooks/log_tool_use.py).

Run with `make test`.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / ".claude" / "hooks" / "log_tool_use.py"


class ToolLogTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.logs = Path(self.dir.name)

    def tearDown(self):
        self.dir.cleanup()

    def run_hook(self, event, extra_env=None):
        env = {**os.environ, "AGENT_LOG_DIR": str(self.logs), **(extra_env or {})}
        stdin = event if isinstance(event, str) else json.dumps(event)
        return subprocess.run([sys.executable, str(SCRIPT)], input=stdin, env=env,
                              capture_output=True, text=True, timeout=10)

    def lines(self):
        files = list(self.logs.glob("*.jsonl"))
        return [json.loads(line) for f in files for line in f.read_text().splitlines()]

    def bash(self, command, event="PostToolUse", **extra):
        return {"hook_event_name": event, "session_id": "s1", "tool_use_id": "t1",
                "tool_name": "Bash", "tool_input": {"command": command}, **extra}

    def test_logs_a_shell_command_with_its_time(self):
        result = self.run_hook(self.bash("git status"))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        [line] = self.lines()
        self.assertEqual(line["tool"], "Bash")
        self.assertEqual(line["command"], "git status")
        self.assertEqual(line["event"], "ran")
        self.assertEqual(line["agent"], "claude-code")
        self.assertRegex(line["time"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+00:00$")

    def test_records_requested_and_failed_events(self):
        self.run_hook(self.bash("rm -rf build", event="PreToolUse"))
        self.run_hook(self.bash("ls /missing", event="PostToolUseFailure", error="No such file"))
        events = [line["event"] for line in self.lines()]
        self.assertEqual(events, ["requested", "failed"])
        self.assertNotIn("No such file", json.dumps(self.lines()))

    def test_never_logs_output_contents_or_environment(self):
        event = {"hook_event_name": "PostToolUse", "tool_name": "Write",
                 "tool_input": {"file_path": "notes.md", "content": "FILE-CONTENT-MARKER"},
                 "tool_response": {"stdout": "OUTPUT-MARKER"}}
        self.run_hook(event, {"API_TOKEN_FOR_TEST": "ENV-MARKER"})
        text = json.dumps(self.lines())
        self.assertIn("notes.md", text)
        for marker in ("FILE-CONTENT-MARKER", "OUTPUT-MARKER", "ENV-MARKER"):
            self.assertNotIn(marker, text)

    def test_redacts_values_that_look_like_secrets(self):
        commands = [
            "API_KEY=abc123secret npm start",
            "export GITHUB_TOKEN='abc def'",
            "curl -H 'Authorization: Bearer " + "abcdefghijklmnop' https://x",  # split so the secret scan skips it
            "mysql --password=hunter2 db",
            "git clone https://user:hunter2@example.com/repo.git",
            "echo ghp_" + "A" * 36,
            "aws s3 ls # AKIA" + "ABCDEFGHIJKLMNOP",
        ]
        for command in commands:
            self.run_hook(self.bash(command))
        text = json.dumps(self.lines())
        for secret in ("abc123secret", "abc def", "abcdefghijklmnop", "hunter2", "A" * 36, "ABCDEFGHIJKLMNOP"):
            self.assertNotIn(secret, text)
        self.assertEqual(text.count("[REDACTED]"), len(commands))

    def test_mcp_tools_log_the_name_only(self):
        self.run_hook({"hook_event_name": "PostToolUse", "tool_name": "mcp__db__query",
                       "tool_input": {"sql": "SELECT secret FROM users"}})
        [line] = self.lines()
        self.assertEqual(line["tool"], "mcp__db__query")
        self.assertNotIn("SELECT", json.dumps(line))

    def test_opencode_names_and_subagents(self):
        self.run_hook({"hook_event_name": "PostToolUse", "agent": "opencode", "tool_name": "read",
                       "tool_input": {"filePath": "src/app.py"}})
        self.run_hook({"hook_event_name": "PreToolUse", "tool_name": "Read", "agent_type": "reviewer",
                       "tool_input": {"file_path": "README.md"}})
        first, second = self.lines()
        self.assertEqual((first["agent"], first["filePath"]), ("opencode", "src/app.py"))
        self.assertEqual(second["subagent"], "reviewer")

    def test_long_commands_are_cut(self):
        self.run_hook(self.bash("echo " + "x" * 5000))
        [line] = self.lines()
        self.assertLess(len(line["command"]), 1100)

    def test_bad_input_never_fails(self):
        for stdin in ("not json", "", json.dumps({"hook_event_name": "Stop"})):
            result = self.run_hook(stdin)
            self.assertEqual((result.returncode, result.stdout), (0, ""))
        self.assertEqual(self.lines(), [])

    def test_unwritable_log_never_fails(self):
        result = self.run_hook(self.bash("ls"), {"AGENT_LOG_DIR": "/proc/forbidden/logs"})
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_old_logs_are_deleted(self):
        old = self.logs / "2000-01-01.jsonl"
        old.write_text("{}\n")
        stamp = time.time() - 40 * 86400
        os.utime(old, (stamp, stamp))
        self.run_hook(self.bash("ls"))
        self.assertFalse(old.exists())

    def test_log_is_private(self):
        self.run_hook(self.bash("ls"))
        [path] = self.logs.glob("*.jsonl")
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_default_location_is_outside_the_project(self):
        env = {k: v for k, v in os.environ.items() if k != "AGENT_LOG_DIR"}
        env.update({"XDG_STATE_HOME": str(self.logs), "CLAUDE_PROJECT_DIR": "/work/my-app"})
        subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(self.bash("ls")), env=env,
                       capture_output=True, text=True, timeout=10)
        self.assertEqual(len(list((self.logs / "agent-logs" / "my-app").glob("*.jsonl"))), 1)


if __name__ == "__main__":
    unittest.main()
