# Labels and board

## Labels

| Label | Meaning |
|---|---|
| `phase-0` … `phase-5` | Roadmap phase (decide/setup, enforceable rules, security layer, CI, skills/subagents, pilot) |
| `security` | Changes a security control or boundary |
| `governance` | Changes agent rules or autonomy; needs owner approval |
| `needs-owner` | Only the repository owner can do it (settings, approvals) |
| `chore` | Repository maintenance |
| `enhancement`, `bug`, `documentation` | GitHub defaults, used by the Issue forms |

## Board

One GitHub Project board with the columns **Backlog → Ready → In progress → Review → Done**.

- An Issue moves to **Ready** only when its acceptance criteria are clear.
- Keep **In progress** small (WIP limit 2) so work finishes before new work starts.
- A PR in review keeps its Issue in **Review** until it is merged.
