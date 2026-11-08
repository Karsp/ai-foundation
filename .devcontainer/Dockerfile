# Dev container for running agents isolated from the host (ADR-0004).
# Versions are pinned (docs/security/supply-chain.md). Change them through a PR.
# Guide: docs/development/environment.md

# Ubuntu 26.04 LTS, pinned by digest
FROM ubuntu:26.04@sha256:c098726dd9b9733f3e885f8de0ef375206a311b0a317eadc40d347b1115fb944

# Agents to install, each at a version published at least 72 hours ago.
# Empty means not installed. Set them in devcontainer.json ("build.args").
ARG CLAUDE_CODE_VERSION=2.1.304
ARG OPENCODE_VERSION=
# Firewall lists to turn on besides "base" (.devcontainer/firewall/)
ARG FIREWALL_LISTS=anthropic
ARG PRE_COMMIT_VERSION=4.7.0

# Tools from the Ubuntu archive: Git, GitHub CLI, make, Node.js 22 (for npm installs),
# pipx and Go (for pre-commit and its hooks), iptables/ipset (firewall)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates curl git gh jq make nodejs npm pipx golang-go \
        iptables ipset sudo \
    && rm -rf /var/lib/apt/lists/*

# Agents, exact versions, installed globally; updates come from rebuilding
RUN if [ -n "$CLAUDE_CODE_VERSION" ]; then npm install -g "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}"; fi \
    && if [ -n "$OPENCODE_VERSION" ]; then npm install -g "opencode-ai@${OPENCODE_VERSION}"; fi
ENV OPENCODE_DISABLE_AUTOUPDATE=1

# Container-wide Claude Code settings: the container is the isolation boundary
COPY .devcontainer/managed-settings.json /etc/claude-code/managed-settings.json

# Egress firewall: only root can change it; the user may only run the script
COPY .devcontainer/init-firewall.sh /usr/local/bin/init-firewall.sh
COPY .devcontainer/firewall/ /tmp/firewall/
RUN mkdir -p /etc/devcontainer \
    && for list in base $FIREWALL_LISTS; do \
         [ -f "/tmp/firewall/$list.txt" ] || { echo "Unknown firewall list: $list" >&2; exit 1; }; \
         cat "/tmp/firewall/$list.txt"; \
       done > /etc/devcontainer/allowed-domains.txt \
    && rm -rf /tmp/firewall \
    && chmod 0755 /usr/local/bin/init-firewall.sh \
    && chmod 0644 /etc/devcontainer/allowed-domains.txt \
    && gpasswd -d ubuntu sudo \
    && echo "ubuntu ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" > /etc/sudoers.d/firewall \
    && chmod 0440 /etc/sudoers.d/firewall

# The non-root user that ships with the Ubuntu image (uid 1000, like a WSL2 user)
USER ubuntu
ENV PATH="/home/ubuntu/.local/bin:${PATH}"

# pre-commit and its hooks, built now (Go hooks with the system Go), because the
# firewall blocks the downloads a first build needs
COPY --chown=ubuntu:ubuntu .pre-commit-config.yaml /tmp/hooks/.pre-commit-config.yaml
RUN pipx install "pre-commit==${PRE_COMMIT_VERSION}" \
    && git -C /tmp/hooks init -q \
    && cd /tmp/hooks && pre-commit install-hooks \
    && rm -rf /tmp/hooks
