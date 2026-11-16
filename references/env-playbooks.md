# Env Playbooks — Local vs Prod

## Gate

Ask environment before any scan. Default to prod restrictions on ambiguity. Record answer in output header: `ENV: local/dev` or `ENV: prod/server`.

## Local/Dev — Contained Active Allowed

Allowed:

- Read worktree, git history, configs, Docker files.
- Run `scripts/secret-sweep.py` and `scripts/port-exposure.py` locally.
- Loopback probes only (`127.0.0.1`, `localhost`): header spoof, IDOR with test accounts, traversal against fixture, SSRF validator check with `127.0.0.1:9` and `169.254.169.254` as input value (expect block), 6-request rate-limit check, 1 MB body check.
- Start/stop app locally for verification.

Requirements: dummy principals and fixtures only. Stop at first boundary byte. No external egress. No credential reuse. Low CPU/time bounds.

## Prod/Server — Read-Only

Prohibited:

- Port scan, service banner grab, or connection attempts beyond reading committed config.
- Payload execution, login attempts, enumeration, load generation.
- Secret validation by use (never test a key by calling provider).
- File writes to server, rotation, purge, firewall change.

Allowed:

- Read source, git log, lockfiles, Docker/CORS/header config.
- Infer exposure from code: `0.0.0.0`, `EXPOSE`, CORS `*`, debug routes.
- Produce kill plan ordered CRITICAL first with owner commands.

State explicitly when refusing: `Prod mode: read-only — active probe skipped, kill plan provided`.

## Evidence Rules

Cite `file:line` or commit hash. Quote config values. Never quote full secret. Mark remote-reached secret as COMPROMISED.
