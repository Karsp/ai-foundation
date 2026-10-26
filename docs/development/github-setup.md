# GitHub setup

One-time settings for every repository created from this template. Only the owner can change them; agents may not (see the [autonomy policy](../agents/autonomy.md)). Open an Issue labelled `needs-owner` with this checklist and tick it as you go.

Most of these protections are free only on **public** repositories. On a free private repository, rulesets, secret scanning and push protection are refused (GitHub Pro or a public repo is needed). Decide visibility first, and scan the history for secrets and personal data before making a repository public.

## Checklist

### General

- [ ] Visibility decided (public, or private with what that loses written down in the Issue)
- [ ] **Template repository** ticked (only for template repos like this one)
- [ ] Pull Requests: allow **squash merging** only; default commit message = **Pull request title** (keeps commit trailers and PR text out of `main`)
- [ ] Pull Requests: **Automatically delete head branches**

### Advanced Security

- [ ] **Private vulnerability reporting** on (the Issue forms link to it)
- [ ] **Dependabot alerts** on
- [ ] **Secret scanning** on, then **Push protection** on

### Rules > Rulesets

One branch ruleset on the default branch, enforcement **Active**, no bypass actors.

- [ ] Require a pull request before merging; required approvals **0** while there is a single maintainer (GitHub does not let you approve your own PR); raise it when a second reviewer joins
- [ ] Require status checks to pass: add **Checks** (the [CI workflow](ci-template.md)) after it has run once on a pull request; tick **Require branches to be up to date** only if you don't mind updating each branch before merging
- [ ] Block force pushes
- [ ] Restrict deletions

### Actions > General

- [ ] Workflow permissions: **Read repository contents**; do not allow Actions to create or approve pull requests
- [ ] Actions permissions: tick **Require actions to be pinned to a full-length commit SHA**
- [ ] Fork pull request workflows: **require approval for all outside collaborators** (public repos)

### Projects

- [ ] Board with Backlog / Ready / In progress / Review / Done ([labels and board](labels.md)), linked to the repo
- [ ] Built-in workflows on: *Item added → Backlog*, *Item closed → Done*, *Pull request merged → Done*

## Verify

Run both checks from a clone. Neither leaves anything behind when the settings are right, because GitHub rejects the push.

1. **Push protection.** Commit a file containing a fake but well-formed token (for example a GitHub personal access token with a valid checksum) and push it to a new branch. Expected: `push declined due to repository rule violations` naming the secret type. Do **not** use the unblock URL GitHub offers.
2. **Protected default branch.** Commit any change on top of the current `main` and run `git push origin HEAD:main`. Expected: `GH013: Repository rule violations found` with `Changes must be made through a pull request`. Make sure your local `main` is up to date first, or you get a plain non-fast-forward error that proves nothing.

Then delete the local test commits (`git reset --hard origin/main`).

For this repository both checks passed on 2026-10-19 (#2).
