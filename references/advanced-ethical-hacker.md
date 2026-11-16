# Advanced Ethical-Hacker Methodology (Contained)

Follow recon → mapping → vulnerability analysis → contained proof → fix. Never pivot beyond loopback. Dummy data only.

## 1. Recon (read-only, any env)

Map trust boundaries: external entities, processes, data stores, data flows. List assets (credentials, PII, money movement, admin actions). Record entry points and sinks before any probe.

## 2. Mapping (read-only, any env)

- Routes: pages, API, webhooks, WebSocket handlers, GraphQL operations, file upload/download, import-from-URL, admin/debug.
- State: session creation, refresh, revocation, OAuth callbacks, API keys.
- Storage: database, object store, cache, search index, backups, logs.

## 3. Vulnerability Analysis (read-only + local fixture)

Prioritize by reachability: unauthenticated + network-reachable first. Apply per-element checks (spoofing identity, tampering integrity, repudiation gaps, info disclosure, DoS amplification, elevation):

- AuthN: missing guard, `alg:none`, no expiry, weak reset token, user-oracle.
- AuthZ: IDOR/BOLA, path traversal, mass-assignment, method override, WebSocket without handshake check.
- Injection: SQL/NoSQL/shell/template/LDAP, XSS stored/reflected/DOM, SSTI, XXE, deserialization.
- SSRF: scheme/host allowlist, all-DNS-records resolution check, private-range block, redirect-follow block. Residual DNS-rebinding risk when validator checks string only.
- Logic: price/quantity tamper, coupon reuse, race double-submit, workflow skip.
- Transport/session: cookie flags, HSTS, credentialed CORS wildcard, session fixation.

## 4. Contained Proof (local/dev loopback only)

One vector at a time, `curl --max-time 5`, one retry. Stop at first boundary byte. Log command, status, redacted head (300 chars). Verdict `BLOCKED` or `OPEN`. Skipped-in-prod rows marked with code reason.

## 5. Fix Closure

Each OPEN maps 1:1 to smallest guard patch at last trusted decision point plus regression test. Re-run probe after patch; the re-run pass is the done signal. Report states measurement first, solution second.
