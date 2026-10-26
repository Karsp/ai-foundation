#!/usr/bin/env bash
# Egress firewall for the dev container: deny all outbound traffic except DNS,
# GitHub's address ranges and the hosts in /etc/devcontainer/allowed-domains.txt,
# which the image builds from the lists in .devcontainer/firewall/.
# Runs as root at every container start (postStartCommand). Adapted from
# Anthropic's reference dev container (github.com/anthropics/claude-code).
set -euo pipefail
IFS=$'\n\t'

DOMAINS_FILE=/etc/devcontainer/allowed-domains.txt
SET=allowed-hosts

# Fail closed: if anything below fails, block all traffic instead of leaving
# the container open
lock_down() {
    status=$?
    if [ "$status" -ne 0 ]; then
        iptables -P INPUT DROP; iptables -P OUTPUT DROP; iptables -P FORWARD DROP
        iptables -A INPUT -i lo -j ACCEPT; iptables -A OUTPUT -o lo -j ACCEPT
        echo "Firewall setup failed: all outbound traffic is blocked. Fix the error above and restart the container." >&2
    fi
}
trap lock_down EXIT

# Keep Docker's internal DNS rules, then start from empty tables
DOCKER_DNS_RULES=$(iptables-save -t nat | grep "127\.0\.0\.11" || true)
iptables -F; iptables -X
iptables -t nat -F; iptables -t nat -X
iptables -t mangle -F; iptables -t mangle -X
ipset destroy "$SET" 2>/dev/null || true
if [ -n "$DOCKER_DNS_RULES" ]; then
    iptables -t nat -N DOCKER_OUTPUT 2>/dev/null || true
    iptables -t nat -N DOCKER_POSTROUTING 2>/dev/null || true
    echo "$DOCKER_DNS_RULES" | xargs -L 1 iptables -t nat
fi

# DNS and loopback
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A INPUT -p udp --sport 53 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT
iptables -A INPUT -p tcp --sport 53 -m state --state ESTABLISHED -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

ipset create "$SET" hash:net

# GitHub publishes its address ranges. If that fails (for example a rate
# limit), the GitHub hosts in the domains file still cover the basics.
if meta=$(curl -fsS --connect-timeout 10 https://api.github.com/meta) \
    && echo "$meta" | jq -e '.web and .api and .git' > /dev/null; then
    while read -r cidr; do
        [[ "$cidr" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}/[0-9]{1,2}$ ]] || continue  # IPv4 only
        ipset add -exist "$SET" "$cidr"
    done < <(echo "$meta" | jq -r '(.web + .api + .git)[]')
else
    echo "WARNING: could not read GitHub's ranges; using the domains file only" >&2
fi

# Other hosts: resolved now, so a host that changes address needs a restart
while read -r domain; do
    domain="${domain%%#*}"; domain="${domain//[[:space:]]/}"
    [ -z "$domain" ] && continue
    [[ "$domain" == *"*"* ]] && { echo "ERROR: wildcards are not allowed: $domain" >&2; exit 1; }
    ips=$(getent ahostsv4 "$domain" | awk '{print $1}' | sort -u || true)
    [ -n "$ips" ] || { echo "ERROR: cannot resolve $domain" >&2; exit 1; }
    while read -r ip; do
        [[ "$ip" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]] \
            || { echo "ERROR: bad address for $domain: $ip" >&2; exit 1; }
        ipset add -exist "$SET" "$ip"
    done <<< "$ips"
done < "$DOMAINS_FILE"

# Default deny, then allow replies and the allowed hosts
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m set --match-set "$SET" dst -j ACCEPT
iptables -A OUTPUT -j REJECT --reject-with icmp-admin-prohibited

# No IPv6 at all (the allowlist is IPv4)
if command -v ip6tables > /dev/null && ip6tables -L > /dev/null 2>&1; then
    ip6tables -F
    ip6tables -P INPUT DROP
    ip6tables -P FORWARD DROP
    ip6tables -P OUTPUT DROP
    ip6tables -A INPUT -i lo -j ACCEPT
    ip6tables -A OUTPUT -o lo -j ACCEPT
fi

# Check: a host outside the list is blocked, GitHub is reachable
# (any HTTP answer counts as reachable)
if curl -sS -o /dev/null --connect-timeout 5 https://example.com 2>/dev/null; then
    echo "ERROR: firewall check failed, example.com is reachable" >&2; exit 1
fi
if ! curl -sS -o /dev/null --connect-timeout 5 https://api.github.com/zen 2>/dev/null; then
    echo "ERROR: firewall check failed, api.github.com is not reachable" >&2; exit 1
fi
echo "Firewall ready: outbound traffic limited to GitHub and the hosts in $DOMAINS_FILE"
