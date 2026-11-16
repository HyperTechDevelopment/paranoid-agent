# Scorecard — 0-100 Before/After Rubric

## Dimensions and Weights

Total 100. Start each dimension at full marks, subtract per finding. Floor at 0 per dimension.

- Secrets (20): CRITICAL secret with remote reach -20; local-only tracked `.env` -10; secret in CI definition/log/artifact/backup -10; historical-only (rotated, purged) -5; MEDIUM pattern (weak entropy, example key in test) -2.
- Exposure (20): `0.0.0.0` unauth prod listener -10; CORS `*` with credentials -8; debug/admin route in prod -8; backup/dump/log exposed -8; missing HSTS/redirect -3; verbose error -2.
- Auth/AuthZ (20): missing ownership check on resource -10; auth bypass -10; JWT `alg:none`/no-expiry accepted -10; weak session (no HttpOnly/Secure in prod) -5; no rate limit on login -5; account-oracle messages -3.
- Input/injection (15): unsanitized sink with attacker input -10; destructive path without root+depth+ownership check -8; sink with unclear input -5 (cap); framework-escaped only -0.
- Supply-chain (10): critical reachable CVE -7; install scripts unreviewed -5; lockfile missing/drift -3.
- Hygiene/privacy (15): reachable dead route with sink -8; duplicated auth logic diverging -5; unmapped PII or missing TTL/delete path -5; orphan code unreachable -2 each (cap -10).

## Before/After Semantics

- Before: measured state from sweep. Show math: list deductions per dimension.
- After: projected state if all proposed kills applied. Never credit unapplied work. If owner defers a kill, keep deduction and list under `Pontos a sanar`.
- Prod cap: if any CRITICAL OPEN remains, cap total After at 60 with note `capped: critical open`.

## Output Contract

Emit exactly:

```markdown
## Security Score: <before>/100 -> <after>/100 (+<delta>)
| Dimension | Weight | Before | After | Key deduction |
|---|---|---|---|---|
...
### Pontos a sanar (grave -> leve)
1. [SEV] file:line ou commit — one-sentence impact — kill command/patch
```

Order kills CRITICAL > HIGH > MEDIUM > LOW. Every kill carries evidence pointer. No score without kill-list.
