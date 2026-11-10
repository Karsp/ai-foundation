#!/usr/bin/env python3
"""Check the skills and subagents in this repository (docs/agents/skills.md):

- every skill in .claude/skills/<name>/SKILL.md has a matching name and a
  description, and doesn't pre-approve tools (`allowed-tools`);
- every subagent exists for Claude Code (.claude/agents/) and OpenCode
  (.opencode/agents/), with the same instructions;
- every subagent whose name ends in "reviewer" is read-only: Claude Code
  `tools` limited to Read, Grep, Glob; OpenCode denies edits, commands, web,
  other agents, skills and folders outside the project.

Usage: python3 scripts/check_agents.py   (exit code 1 if a check fails)
"""

import re
import sys
from pathlib import Path

SKILLS = Path(".claude/skills")
CLAUDE_AGENTS = Path(".claude/agents")
OPENCODE_AGENTS = Path(".opencode/agents")

NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
READ_ONLY_TOOLS = {"Read", "Grep", "Glob"}
READ_ONLY_DENY = ["edit", "bash", "webfetch", "websearch", "task", "skill", "external_directory"]
OPENCODE_FORBIDDEN = ["tools"]  # legacy switches that could turn tools back on
CLAUDE_FORBIDDEN = ["permissionMode", "mcpServers", "hooks"]


def split(path: Path) -> tuple[dict, str]:
    """Frontmatter (top-level keys, one level of nesting) and body.
    A key written twice raises ValueError, so a later line can't override."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not match:
        return {}, text
    meta: dict = {}
    parent = None
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, _, value = line.strip().partition(":")
        value = value.strip()
        target = meta[parent] if line.startswith((" ", "\t")) and parent else meta
        if key in target:
            raise ValueError(f"{path}: '{key}' is written twice")
        if target is meta:
            parent = key if not value else None
        target[key] = {} if (target is meta and not value) else value
    return meta, match.group(2).strip()


def check_skills() -> list[str]:
    errors = []
    for skill in sorted(SKILLS.glob("*/SKILL.md")):
        meta, _ = split(skill)
        folder = skill.parent.name
        if meta.get("name") != folder:
            errors.append(f"{skill}: name must be '{folder}', the folder name")
        if not NAME.match(folder) or len(folder) > 64:
            errors.append(f"{skill}: use lowercase words and hyphens, up to 64 characters")
        if not meta.get("description"):
            errors.append(f"{skill}: missing description")
        if "allowed-tools" in meta:
            errors.append(f"{skill}: allowed-tools skips permission prompts; remove it")
    return errors


def check_agents() -> list[str]:
    errors = []
    claude = {p.stem: p for p in CLAUDE_AGENTS.glob("*.md")}
    opencode = {p.stem: p for p in OPENCODE_AGENTS.glob("*.md")}
    for name in sorted(claude.keys() ^ opencode.keys()):
        have = claude.get(name) or opencode.get(name)
        errors.append(f"{have}: add the same agent for the other tool ({CLAUDE_AGENTS}/ and {OPENCODE_AGENTS}/)")
    for name in sorted(claude.keys() & opencode.keys()):
        c_meta, c_body = split(claude[name])
        o_meta, o_body = split(opencode[name])
        if c_body != o_body:
            errors.append(f"{claude[name]}: instructions differ from {opencode[name]}")
        if c_meta.get("name") != name:
            errors.append(f"{claude[name]}: name must be '{name}', the file name")
        for path, meta in ((claude[name], c_meta), (opencode[name], o_meta)):
            if not meta.get("description"):
                errors.append(f"{path}: missing description")
        if o_meta.get("mode") != "subagent":
            errors.append(f"{opencode[name]}: mode must be subagent")
        if not name.endswith("reviewer"):
            continue
        tools = {t.strip() for t in str(c_meta.get("tools", "")).split(",") if t.strip()}
        if not tools or not tools <= READ_ONLY_TOOLS:
            errors.append(f"{claude[name]}: a reviewer's tools must be a subset of {', '.join(sorted(READ_ONLY_TOOLS))}")
        for key in CLAUDE_FORBIDDEN:
            if key in c_meta:
                errors.append(f"{claude[name]}: a reviewer must not set {key}")
        permission = o_meta.get("permission")
        permission = permission if isinstance(permission, dict) else {}
        for key in READ_ONLY_DENY:
            if permission.get(key) != "deny":
                errors.append(f"{opencode[name]}: a reviewer needs permission {key}: deny")
        for key in OPENCODE_FORBIDDEN:
            if key in o_meta:
                errors.append(f"{opencode[name]}: a reviewer must not set {key}")
    return errors


def main() -> int:
    try:
        errors = check_skills() + check_agents()
    except ValueError as error:
        errors = [str(error)]
    for error in errors:
        print(error)
    skills = len(list(SKILLS.glob("*/SKILL.md")))
    agents = len(list(CLAUDE_AGENTS.glob("*.md")))
    print(f"Checked {skills} skills and {agents} subagents: {len(errors)} problems.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
