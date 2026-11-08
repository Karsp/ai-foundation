#!/usr/bin/env python3
"""Check relative links in Markdown files: the target file exists and, for
`file.md#heading` links, the heading exists. External links are not checked
(they need the network and change outside this repository).

Usage: python3 scripts/check_links.py [FILE.md ...]   (default: every tracked .md)
Exit code 1 if any link is broken.
"""

import re
import subprocess
import sys
from pathlib import Path

LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")


def slug(heading: str) -> str:
    """GitHub's anchor for a heading: lowercase, drop punctuation, spaces to '-'."""
    text = re.sub(r"`|\*\*|__", "", heading).strip().lower()
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def strip_code(text: str) -> list[str]:
    """Lines outside fenced code blocks, with inline code removed."""
    lines, in_fence = [], False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(re.sub(r"`[^`]*`", "", line))
    return lines


def anchors(path: Path) -> set[str]:
    seen: dict[str, int] = {}
    result = set()
    for line in strip_code(path.read_text(encoding="utf-8")):
        match = HEADING.match(line)
        if not match:
            continue
        base = slug(match.group(2))
        count = seen.get(base, 0)
        seen[base] = count + 1
        result.add(base if count == 0 else f"{base}-{count}")
    return result


def tracked_markdown() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "*.md"], capture_output=True, text=True, check=True
    ).stdout
    return [Path(p) for p in out.splitlines()]


def check(path: Path) -> list[str]:
    errors = []
    for number, line in enumerate(strip_code(path.read_text(encoding="utf-8")), 1):
        for target in LINK.findall(line):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):  # http:, mailto:, ...
                continue
            file_part, _, anchor = target.partition("#")
            dest = (path.parent / file_part).resolve() if file_part else path.resolve()
            if not dest.exists():
                errors.append(f"{path}: link to missing file: {target}")
            elif anchor and dest.suffix == ".md" and anchor not in anchors(dest):
                errors.append(f"{path}: link to missing heading: {target}")
    return errors


def main(argv: list[str]) -> int:
    files = [Path(a) for a in argv] or tracked_markdown()
    errors = [e for f in files if f.suffix == ".md" for e in check(f)]
    for error in errors:
        print(error)
    print(f"Checked {len(files)} Markdown files: {len(errors)} broken links.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
