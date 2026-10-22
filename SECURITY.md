# Security Policy

## Reporting a vulnerability

**Do not open a public Issue, PR or discussion for a vulnerability.**

Report it privately through GitHub: go to the repository's **Security** tab and click **Report a vulnerability** ([direct link](https://github.com/Karsp/ai-foundation/security/advisories/new)). Only the maintainer can see the report.

Please include:

- what is affected (file, rule, template or setting);
- how it can be exploited, with steps or a proof of concept;
- what an attacker gains (for example: an agent skips an approval, a secret leaks, untrusted content gets executed);
- a suggested fix, if you have one.

This project is maintained by one person. What to expect:

- **Within 7 days:** an acknowledgement that the report was received.
- **Within 30 days:** a fix, or a plan with a date if the fix takes longer.

Please do not disclose the issue publicly until a fix is published or we agree on a date.

## What is in scope

This repository is a template of rules, documents and settings for AI-assisted development. In scope:

- rules or templates that would let an agent bypass the [autonomy policy](docs/agents/autonomy.md), the Rule of Two or human approval;
- instructions that could make an agent leak secrets or personal data;
- unsafe defaults in agent adapters, CI workflows, dev container or scripts shipped here;
- anything that weakens the controls listed in the [threat model](docs/security/threat-model.md).

Out of scope: vulnerabilities in projects created from this template (report them to that project), and in third-party tools such as agent CLIs, models or GitHub itself (report them to their vendors).

## Supported versions

| Version | Supported |
|---|---|
| Latest commit on `main` | Yes |
| Latest `v1.x` release (once tagged) | Yes |
| Anything older | No: update to the latest template |

Projects created from the template do not receive fixes automatically. Each release note says which files changed so projects can copy the fix.

## If a secret is exposed

A secret (API key, token, password, private key, connection string) counts as exposed as soon as it reaches a commit, an Issue, a PR, a log, a chat with an agent or any shared place, even if it is deleted a minute later.

1. **Stop.** Do not push more commits, re-run the job or paste the value anywhere else to "check" it. An agent stops and reports to the owner; it never revokes or rotates credentials itself ([autonomy policy](docs/agents/autonomy.md)).
2. **Revoke.** The owner revokes the secret at the provider that issued it. This is the step that removes the risk.
3. **Rotate.** Create a new secret, store it in the password manager or secret store, and update whatever uses it. Never put the new value in the repository.
4. **Clean up.** Remove the value from the code. Rewriting Git history is optional and does not make a leaked secret safe again: forks, clones, caches and PR refs keep it.
5. **Record.** Write a short private note or a draft security advisory: what leaked, when, where, how long it was exposed and what was done. Never include the secret itself.

Push protection is on for this repository. If a push is blocked because it contains a secret, remove the secret from the commit. Only use GitHub's "allow secret" link for a value you know is fake (for example in a test), and say so in the PR.
