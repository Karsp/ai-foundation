// Logs every OpenCode tool call to the same local log as Claude Code
// (docs/agents/tool-log.md). The logging and redaction live in one place,
// .claude/hooks/log_tool_use.py; this plugin only passes each call to it.
// No tool output is passed on.
import { spawn } from "node:child_process"
import path from "node:path"

export const LogToolUse = async ({ directory, worktree }) => {
  const root = worktree || directory
  const script = path.join(root, ".claude", "hooks", "log_tool_use.py")

  const log = (event, input, args) => {
    try {
      const child = spawn("python3", ["-I", script], {
        env: { ...process.env, CLAUDE_PROJECT_DIR: root },
        stdio: ["pipe", "ignore", "ignore"],
      })
      child.on("error", () => {})
      child.stdin.on("error", () => {})
      child.stdin.end(
        JSON.stringify({
          hook_event_name: event,
          agent: "opencode",
          session_id: input.sessionID,
          tool_use_id: input.callID,
          tool_name: input.tool,
          tool_input: args ?? {},
        }),
      )
    } catch {
      // Logging must never break the agent.
    }
  }

  return {
    "tool.execute.before": async (input, output) => log("PreToolUse", input, output?.args),
    "tool.execute.after": async (input) => log("PostToolUse", input, input.args),
  }
}
