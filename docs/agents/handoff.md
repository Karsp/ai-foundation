# Handoff

Use this when you stop before an Issue is done: the session ends, you hit a blocker, or another agent or human takes over. Post it as a comment on the Issue (or the PR if one exists). The next agent must be able to continue from the repository and this note alone, without your conversation.

## Template

```markdown
## Handoff: <Issue title> (#N)

**State:** in progress | blocked | ready for review
**Branch / PR:** `<branch>` · #<PR or "none yet">

### Done
- What is finished and committed (link commits if useful)

### Remaining
- [ ] Next steps, in order

### Blockers
- What stops progress, and who or what can unblock it

### Decisions and assumptions
- Choices made and why; link ADRs if any

### Tried and ruled out
- Approaches that failed, the symptom, the likely cause

### Validation
- Commands run and result: PASS / FAIL / NOT RUN / NOT APPLICABLE / BLOCKED

### Next recommended action
- One concrete first step for whoever picks this up
```

## Rules

- Commit working changes to the branch before writing the handoff; never leave important work only on a local machine.
- Report validation honestly. `NOT RUN` is never `PASS`.
- No secrets, tokens or personal data in the note.
- Remaining work that is outside the Issue's scope becomes a new Issue, linked from the note.
