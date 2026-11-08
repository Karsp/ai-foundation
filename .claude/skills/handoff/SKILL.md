---
name: handoff
description: Writes and posts the handoff note for unfinished work, so another agent or a human can continue from the repository alone. Use when stopping before an Issue is done, when blocked, when the session or context is about to end, or when asked for a handoff.
---

# Handoff

Leave the work so the next agent can continue without this conversation. The template and rules are in [`docs/agents/handoff.md`](../../../docs/agents/handoff.md); this skill fills them in from facts, not memory.

## Input

The Issue being worked on. Everything else comes from the repository.

## Steps

1. **Save the work.** Commit what works to the Issue's branch (never to the default branch) and push the branch. Don't commit broken code silently: if something is half done, commit it only if the note says so, or leave it out and describe it.
2. **Collect the facts:**
   - `git status` and `git log --oneline <default-branch>..HEAD` for what is committed;
   - `gh pr list --head <branch>` for the PR, if any;
   - the Issue's acceptance criteria, ticked against what is done.
3. **Check validation now** rather than from memory: run `make ci` if it is quick, otherwise report the last real result. Use only `PASS`, `FAIL`, `NOT RUN`, `NOT APPLICABLE` or `BLOCKED`, with the command next to each.
4. **Fill the template** from `docs/agents/handoff.md`. *Remaining* is an ordered checklist. *Tried and ruled out* names the symptom and the likely cause, so nobody repeats it. *Next recommended action* is one concrete step.
5. **Split off out-of-scope work:** anything found that the Issue doesn't cover becomes a new Issue (use the `new-issue` skill), linked from the note.
6. **Check the note:** no secrets, tokens, personal data or private session links; nothing claimed as done or passing without evidence.
7. **Post it** on the PR if there is one, otherwise on the Issue:

   ```bash
   gh pr comment <number> --body-file - <<'EOF'
   <note>
   EOF
   ```

   Use `gh issue comment` when there is no PR.

## Output

The link to the posted comment, and the note itself in the reply.

## Fails safely

If pushing or posting fails, give the user the note and say which step failed. Work that isn't pushed is named as such in the note.
