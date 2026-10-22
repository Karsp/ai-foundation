# Dev container for running agents isolated from the host (ADR-0004).
# Versions are pinned (docs/security/supply-chain.md). Change them through a PR.
# Guide: docs/development/environment.md

# Ubuntu 26.04 LTS, pinned by digest
FROM ubuntu:26.04@sha256:c098726dd9b9733f3e885f8de0ef375206a311b0a317eadc40d347b1115fb944

# Claude Code: a version published at least 72 hours ago
ARG CLAUDE_CODE_VERSION=2.1.304
ARG PRE_COMMIT_VERSION=4.7.0

# Tools from the Ubuntu archive: Git, GitHub CLI, Node.js 22 (for npm installs),
# pipx and Go (for pre-commit and the gitleaks hook), iptables/ipset (firewall)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates curl git gh jq nodejs npm pipx golang-go \
        iptables ipset sudo \
    && rm -rf /var/lib/apt/lists/*

# Claude Code, exact version, installed globally; updates come from rebuilding
RUN npm install -g "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}"

# Container-wide Claude Code settings: the container is the isolation boundary
COPY .devcontainer/managed-settings.json /etc/claude-code/managed-settings.json

# Egress firewall: only root can change it; the user may only run the script
COPY .devcontainer/init-firewall.sh /usr/local/bin/init-firewall.sh
COPY .devcontainer/allowed-domains.txt /etc/devcontainer/allowed-domains.txt
RUN chmod 0755 /usr/local/bin/init-firewall.sh \
    && chmod 0644 /etc/devcontainer/allowed-domains.txt \
    && gpasswd -d ubuntu sudo \
    && echo "ubuntu ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" > /etc/sudoers.d/firewall \
    && chmod 0440 /etc/sudoers.d/firewall

# The non-root user that ships with the Ubuntu image (uid 1000, like a WSL2 user)
USER ubuntu
ENV PATH="/home/ubuntu/.local/bin:${PATH}"

# pre-commit and the gitleaks hook, built now with the system Go, because the
# firewall blocks the downloads a first build needs
COPY --chown=ubuntu:ubuntu .pre-commit-config.yaml /tmp/hooks/.pre-commit-config.yaml
RUN pipx install "pre-commit==${PRE_COMMIT_VERSION}" \
    && git -C /tmp/hooks init -q \
    && cd /tmp/hooks && pre-commit install-hooks \
    && rm -rf /tmp/hooks
