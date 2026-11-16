# Adversary Tactics — Contained Self-Attack

Local/dev loopback only. Dummy data only. Stop at first boundary byte.

## Matrix

| # | Attack | Dummy payload | Expected block | OPEN signal |
|---|---|---|---|---|
| A1 | Host/auth bypass | `curl -H "X-Forwarded-For: 127.0.0.1" -H "Host: localhost" http://127.0.0.1:PORT/admin` | 401/403 | 200 with admin body |
| A2 | IDOR | Login as test user A, `GET /api/users/<own-id>` then `/api/users/<own-id+1>` | 403 on neighbor | 200 with neighbor PII |
| A3 | Traversal | `GET /static/..%2f..%2f..%2fetc/hostname` against local fixture | Normalized under root, 400/404 | File content outside root |
| A4 | SSRF validator | `POST /webhook {"url":"http://169.254.169.254/latest/meta-data/"}` and `http://127.0.0.1:9/` | 422 block, no fetch | Outbound connection or fetched body |
| A5 | Rate limit | 6x `POST /login` dummy creds in 10s | 429 by attempt 5-6 | All 200/401 without 429 |
| A6 | Body abuse | 1 MB JSON, `{"role":"admin"}`, `{"isAdmin":"true"}`, method `X-HTTP-Method-Override: DELETE` | 413/422, role ignored | Privilege flip or crash |
| A7 | CORS/cookie | `Origin: https://evil.test` preflight + check `Secure; HttpOnly; SameSite` | No `Access-Control-Allow-Origin: https://evil.test`, flags present | Wildcard echo with credentials |

## Execution Bounds

- Single target port from `scripts/port-exposure.py`. No subnet sweep.
- `curl --max-time 5`, one retry max. No parallel flood.
- Log exact command, wall time, status code, redacted body head (first 300 chars, no secrets).
- On OPEN, halt that vector. Record evidence. Propose smallest guard patch. Do not escalate to exfiltration or persistence.

## Prod Refusal Template

`Prod mode: vector A2 skipped (active probe). Code shows /api/users/:id without ownership check at file:line — treat as HIGH, kill plan provided.`
