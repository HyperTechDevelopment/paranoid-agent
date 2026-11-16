---
name: paranoid-agent
description: This skill should be used when the user asks to "desconfie de tudo", "sweep paranoico", "caça brecha", "simule ataque contra minha app", "mata porta aberta", "audit paranoid", "check 10 commits security", "gitleaks sweep", "nota de segurança antes e depois", or mentions paranoia mode with self-attack and HTML 3D breach report.
---

# Paranoid Breach Sweep

Assume breach. Distrust code, history, runtime, and defaults. Find exploitable exposure, rank by kill priority, simulate contained attacks locally, score before/after, generate hacker-terminal 3D report.

## Standalone Scope

Cover the full sweep inside this skill with original procedures: environment-aware triage, last-10-commits forensics, open-port and secret-exposure hunt, session and token review, destructive-path review, CI/log/backup secret hunt, data-privacy minimization check, dead-code attack surface, contained self-attack, before/after score, animated HTML 3D report. Depend on nothing outside this skill directory.

Out of scope by safety limit: probes against prod/shared/staging hosts, external network egress, brute force with real accounts, exfiltration, persistence, real secret validation by use. Produce a kill plan instead.

## Mandatory Attack Notice

Display this warning before any active probe, every run, without exception:

> "Ataque simulado apenas para avaliar e medir a segurança deste projeto. Nenhum dado real será tocado, exfiltrado ou persistido. Cada falha encontrada vira solução: a kill-list mata a brecha com patch mínimo."

Proceed with active probes only after environment gate passes and this notice is shown.

Activate this skill only for paranoid sweep as defined above.

## Phase 0 — Interrogate Environment

Ask exactly one blocking question before any scan:

> " sweeping onde agora: `local/dev` ou `prod/server`?"

Apply environment playbook from `references/env-playbooks.md`:

- `local/dev`: allow read + contained active probes with dummy data against loopback only.
- `prod/server`: enforce read-only mode. Prohibit port scans beyond config review, prohibit payload execution, prohibit load. Produce kill plan without touching runtime.
- On ambiguous answer, default to `prod` restrictions.

Record answer at top of output. Never skip this gate.

## Phase 1 — Forense dos Últimos 10 Commits

Run git forensics before reading current code:

```bash
git log -n 10 --pretty=format:'%H %ad %an %s' --date=short
git log -n 10 --patch --no-merges -U3 -- . ':(exclude)package-lock.json' ':(exclude)pnpm-lock.yaml' ':(exclude)*.min.js'
git show --stat HEAD~10..HEAD
```

Hunt for patterns defined in `references/git-forensics.md`:

- Secret introduced: AWS key, GitHub token, private key, connection string, `sk-`, `xoxb-`, `.pem`.
- Auth weakened: middleware removed, `skipAuth`, `allowUnauthorized`, guard commented.
- Exposure widened: CORS `*`, new `EXPOSE`, `0.0.0.0`, debug route, `NODE_ENV=development` in prod.
- Dangerous sink added: `eval`, `exec`, `innerHTML`, `dangerouslySetInnerHTML`, `shell: true`, raw SQL.
- Dependency risk: new package without lockfile update, install script change.

Map each hit to commit hash, file, line, author date. Treat secrets in history as compromised even if later removed. Recommend rotation first, purge second.

## Phase 2 — Mapear Superfície Exposta

Inspect runtime exposure without external probing:

- List listeners: run `scripts/port-exposure.py` or manually check `ss -tlnp`, `netstat -ano`, `Dockerfile EXPOSE`, `docker-compose ports`, `fly.toml`, `Procfile`.
- Inspect config: `.env*` tracked by git, `config/*.ts` with hardcoded host, `next.config.js` headers, CORS origin list, proxy rewrites.
- Enumerate routes: `/debug`, `/admin`, `/metrics`, `/actuator`, `/_next`, GraphQL playground, Swagger UI enabled in prod.
- Check transport: HTTP listener without redirect, `secure: false` cookie in prod, missing HSTS, wildcard subdomain cookie.

Flag `0.0.0.0` + unauthenticated + prod as CRITICAL. Flag debug route in prod as HIGH.

## Phase 3 — Caçar Segredos Vazados

Run deterministic sweep:

```bash
python3 scripts/secret-sweep.py --path . --history --redact --format json
```

Cover 25+ patterns: AWS, GCP, Azure, GitHub, GitLab, Slack, Stripe, OpenAI, Anthropic, JWT, RSA/EC private keys, `mongodb://`, `postgres://`, `redis://` with credentials.

Rules:

- Redact values on display: show `sk-live-***a3f9` (first 3 + last 4 only).
- Check tracked files, staged diff, last 10 commits, CI definitions (`.github/workflows`, `.gitlab-ci.yml`, `Jenkinsfile`), log samples, backup and dump files (`*.sql`, `*.bak`, `*.dump`, `seed/*`).
- Hunt secrets in CI logs output, artifact uploads, cache restores, and example files copied to prod.
- Never print full secret to chat or HTML report.
- Mark any secret that reached remote as `COMPROMISED — rotate now`, not merely `remove`.

## Phase 3B — Revisar Sessão e Tokens

Inspect session and token handling without validating secrets by use:

- Cookie flags: `HttpOnly`, `Secure` (prod HTTPS only), `SameSite=lax|strict`, bounded `Max-Age`, `__Host-`/`__Secure-` prefix where applicable.
- Token rules: JWT rejects `alg:none`, enforces `exp`/`aud`/`iss`, short lifetime, rotation on privilege change, server-side revocation list.
- OAuth: state random per request, PKCE enforced, exact redirect allowlist, encrypted tokens at rest.
- Enumeration: identical generic messages for bad user vs bad password, dummy work on invalid account, no user-oracle timing.

Flag `alg:none` accepted, missing expiry, or credentialed CORS wildcard as CRITICAL/HIGH.

## Phase 3C — Revisar Paths Destrutivos

Treat every delete/move/overwrite target as untrusted, including values from another process command line, job payload, or shared volume:

- Resolve symlinks, require resolved target under allowlisted root, minimum one level below root, plus ownership evidence read before the operation.
- Reject on traversal (`..`, encoded `%2e`, backslash, null byte). Log rejected target, stop, never fall back to broader default.
- Check time-of-check/time-of-use gap: re-verify after open, use exclusive create, never follow symlink on write.

## Phase 3D — Cobrir Privacidade de Dados

Classify fields (non-personal, PII, sensitive). Collect only against stated purpose. Set retention TTL plus working deletion path covering backups, caches, search indexes, analytics copies. Support export/correct/delete flows. Gate third-party sharing on consent. Keep PII out of logs, telemetry, and model context. Detail lives in `references/privacy-data.md`.

## Phase 4 — Eliminar Código Morto e Redundante

Treat dead code as attack surface:

- Find unused exports, orphan routes, duplicated auth checks, commented crypto, disabled-but-reachable handlers, stale feature flags (`if (false)` with network call inside).
- Trace reachability: entry points (`app/`, `pages/`, `src/routes/`, `server.ts`) to sinks. Flag reachable-but-unmaintained code HIGHER than unreachable code.
- Propose deletion patch per cluster, not generic cleanup advice.

## Phase 5 — Auto-Ataque Ético Contido

Apply tactics from `references/adversary-tactics.md` only after Phase 0 gate passes.

Allowed in `local/dev` only, loopback only, dummy data only:

- Header spoof: `X-Forwarded-For: 127.0.0.1`, `Host` override, missing-auth replay.
- IDOR/BOLA probe: request own resource `id` then `id+1` with test account. Stop at 403 vs 200 difference. Do not enumerate.
- Traversal probe: `GET /static/..%2f..%2fetc/passwd` plus encoded variants (`%252e`, backslash, null byte) against local fixture. Stop at normalized-path check result.
- SSRF probe: webhook URL `http://127.0.0.1:9/` and `http://169.254.169.254/` against local validator. Expect block, no fetch, no redirect follow to private range. Never probe external URL. Note DNS-rebinding TOCTOU as residual risk when only string allowlist exists.
- Rate-limit probe: 6 rapid logins with dummy credentials. Record 429 vs 200.
- Body abuse: oversized JSON (1 MB), type confusion (`{"isAdmin":"true"}`), mass-assignment (`role`, `owner_id`), method override header.
- Session/token abuse: replay without cookie flags, `alg:none` JWT, expired token, cross-subdomain cookie replay — expect reject.
- Auth-oracle probe: identical dummy user vs dummy password responses compared for message and timing sameness.

Advanced vectors from `references/advanced-ethical-hacker.md` (ethical-hacker methodology: recon, mapping, vulnerability analysis, contained exploitation, post-proof fix): business-logic bypass (price/quantity tamper with dummy cart), race-condition double-submit with two loopback requests, WebSocket handshake without auth, GraphQL introspection in prod, JWT key-confusion only against local fixture key.

Convert every OPEN into a kill: each attack maps 1:1 to a patch in the kill-list. Attacks exist only to measure, then they become solutions when the flaw dies. State this closure per finding.

Prohibited everywhere: DoS, brute force with real accounts, exfiltration, persistence, privesc beyond proof, any probe against prod/shared/staging host, any external network egress.

Record per attack: target, dummy payload, expected block, observed result, verdict `BLOCKED` or `OPEN`. Stop at first byte proving boundary crossing. Never continue to exploit.

## Phase 6 — Scorecard Antes/Depois + Kill-List

Close every run with scorecard defined in `references/scorecard.md`. Compute deterministically:

| Dimension | Weight |
|---|---|
| Secrets | 20 |
| Exposure (ports/routes/debug/CORS) | 20 |
| Auth/AuthZ | 20 |
| Input/injection | 15 |
| Supply-chain | 10 |
| Hygiene (dead code) | 15 |
| Total | 100 |

Emit markdown:

```markdown
## Security Score: 42/100 -> 78/100 (+36)
| Dimension | Before | After |
...
### Pontos a sanar
1. [CRITICAL] file:line — fix — patch/command
```

Order kill-list CRITICAL > HIGH > MEDIUM > LOW. Each entry carries file:line or commit hash, evidence snippet (redacted), impact in one sentence, smallest kill patch. Cap prod score at 60 until CRITICAL kills land.

## Phase 7 — Gerar Relatório HTML 3D Hacker-Terminal

Generate single-file `breach-report.html` after scorecard. Follow `references/report-spec.md`. Use template in `assets/breach-report-template.html` via:

```bash
python3 scripts/generate-breach-report.py --findings findings.json --before 42 --after 78 --out breach-report.html
```

Report contains: timeline do sweep, ataques simulados vs esperado, gráfico animado antes/depois, portas identificadas, commits com segredos redatados, kill-list. Style: hacker-terminal dark, animated canvas charts, CSS 3D tilt, Three.js node-network background with 2D fallback. Responsive. Never embed full secrets.

Verify output opens via `file://` with no build step. Keep full secrets out of HTML source.

## Triage and False-Positive Control

Treat scanner output as candidates, not findings. Confirm each candidate before scoring and before rendering HTML:

- Trace data flow from source to sink. Flag only attacker-reachable paths with concrete evidence.
- Distinguish server-controlled config (`settings.X`, env-provided URL) from attacker-controlled input (`req.query`, `req.body`, headers, upload names, neighbor IDs).
- Respect framework mitigations: parameterized ORM, auto-escaped templates, signed cookies. Flag only bypasses (`raw()`, `|safe`, `dangerouslySetInnerHTML` with user data).
- Discard self-matches: regex literals inside `scripts/secret-sweep.py` and pattern docs in `references/` are not leaks. Verify file context before reporting.
- Downgrade theoretical issues to `Needs verification`. Score only confirmed exposure.
- Redact before display. Never paste full token, key body, or connection string into chat, scorecard, or HTML.

## Execution Order Example

Execute phases in order without skipping:

1. Ask environment, record `ENV:` header.
2. Run `git log` forensics, collect commit hashes.
3. Run `scripts/port-exposure.py` and `scripts/secret-sweep.py`, save JSON.
4. Map dead code from entry points to sinks.
5. Run contained self-attack matrix in local only (skip with prod note otherwise).
6. Compute before/after scorecard, order kill-list grave to leve.
7. Build `findings.json`, run generator, verify HTML renders and contains no raw secret.

Failure in any phase blocks scoring. Report blocker explicitly instead of guessing.

## Safety Rails

- Redact secrets everywhere: chat, scorecard, HTML.
- Prod means read-only. State restriction explicitly when refusing active probe.
- Prefer smallest deletion or guard patch over generic advice.
- Cite `file:line` or commit hash for every finding. No finding without evidence.
- Delete nothing and rotate nothing automatically. Propose commands for owner approval.

## Additional Resources

### Reference Files

- **`references/env-playbooks.md`** — local vs prod rules, allowed commands per env.
- **`references/git-forensics.md`** — 10-commit patterns, gitleaks-equivalent regex set.
- **`references/adversary-tactics.md`** — contained self-attack matrix, expected blocks.
- **`references/advanced-ethical-hacker.md`** — recon-to-fix methodology, advanced vectors (BOLA, SSRF rebinding, logic, race).
- **`references/privacy-data.md`** — PII classification, TTL, delete/export, sharing gates.
- **`references/mcp.md`** — MCP server 3-tool contract (sweep, inventory, render).
- **`references/scorecard.md`** — 0-100 rubric, weighting, capping rules.
- **`references/report-spec.md`** — HTML 3D spec, palette, animations, findings.json schema.

### Scripts

- **`scripts/secret-sweep.py`** — 25+ secret patterns over worktree + last 10 commits, redacted JSON.
- **`scripts/port-exposure.py`** — listener inventory from OS + Dockerfile/compose, no external scan.
- **`scripts/generate-breach-report.py`** — findings.json to hacker-terminal HTML.

### Examples and Assets

- **`examples/kill-list.md`** — worked kill-list + scorecard example.
- **`examples/findings.example.json`** — minimal findings.json accepted by generator.
- **`assets/breach-report-template.html`** — animated hacker-terminal template with 3D background.
