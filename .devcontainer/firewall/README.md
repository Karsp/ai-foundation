# Firewall lists

The dev container's firewall lets traffic out only to the hosts in these files (plus DNS and GitHub's published address ranges). `base` is always on; choose the others with `FIREWALL_LISTS` in [`devcontainer.json`](../devcontainer.json), then rebuild.

| List | Hosts for | Turn on when |
|---|---|---|
| `base` | GitHub, npm, PyPI | Always |
| `anthropic` | Claude Code (API and sign-in) or any agent using Anthropic models | Claude Code is installed, or a model provider is Anthropic |
| `openai` | OpenAI models | An agent uses OpenAI |
| `openrouter` | OpenRouter models | An agent uses OpenRouter |
| `opencode` | OpenCode's model catalog | OpenCode is installed (add the list for its model provider too) |

Rules:

- One host per line, `#` for comments. No wildcards: the firewall refuses them.
- Only specific API hosts. Never a whole cloud provider, CDN or storage service: anyone can host a server there, so it would let data out to anyone.
- Every host is a way out for code and credentials (Rule of Two). Add or turn on a list only through a PR that says why.
