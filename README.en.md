# ▓ Paranoid Agent

[Português](README.md) | **English**

> Simulated attack to assess and measure this project's security. No real data is touched or exfiltrated. Every flaw found becomes a fix in the kill-list.

![logo](assets/readme/paranoid-agent-logo.svg)

Standalone paranoid-sweep skill. It trusts nothing and hunts open ports, leaked secrets, dead code, and exploitable holes. It ranks findings from most to least severe, asks which environment it runs in (`local/dev` or `prod/server`), audits the last 10 commits, runs contained attacks against the app itself to kill each hole, scores security before and after, and renders a hacker-terminal style 3D HTML report with animated charts.

- **Triggers** (PT phrases): `desconfie de tudo`, `sweep paranoico`, `caça brecha`, `simule ataque`, `mata porta aberta`, `audit paranoid`, `check 10 commits security`, `gitleaks sweep`, `nota de segurança antes e depois`
- **External dependencies**: none. Everything lives inside `paranoid-agent/`.
- **Safety**: secrets always redacted, `prod` = read-only, probes only on loopback with dummy data.

## Contents

1. [What it does](#what-it-does)
2. [How to trigger](#how-to-trigger)
3. [The 8 sweep phases](#the-8-sweep-phases)
4. [Before/after scorecard](#beforeafter-scorecard)
5. [3D HTML report](#3d-html-report)
6. [Install](#install)
7. [Step-by-step use](#step-by-step-use)
8. [Real output sample](#real-output-sample)
9. [Skill layout](#skill-layout)
10. [Scripts](#scripts)
11. [Internal references](#internal-references)
12. [Safety rules](#safety-rules)
13. [Known limits](#known-limits)

## What it does

| Capability | Detail |
|---|---|
| Asks the environment | Blocking `local/dev` or `prod/server` question before any scan; unclear answer defaults to `prod` (read-only) |
| 10-commit forensics | `git log -n 10 --patch`: introduced secret, removed auth, CORS `*`, dangerous sink, new dependency |
| Exposed surface | Listeners (`ss`/`netstat`), `Dockerfile EXPOSE`, compose ports, `/debug` `/admin` `/metrics` routes, CORS, cookies, HSTS |
| Secret hunting | 25+ patterns (AWS, GitHub, Slack, Stripe, OpenAI, JWT, private keys, credentialed URIs) + risky filenames (`*.bak`, `*.sql`, `.env`, `*.pem`, CI) |
| Sessions and tokens | Cookie flags, JWT `alg:none`/expiry, OAuth state+PKCE, anti-enumeration |
| Destructive paths | Resolves symlinks, requires allowlisted root + depth + ownership before delete/move |
| Data privacy | Classifies PII, requires purpose, TTL and delete path (backups, caches, indexes), no PII in logs |
| Dead code | Orphan routes, diverging duplicated auth, reachable dead flags |
| Contained self-attack | Header spoof, IDOR/BOLA, traversal, SSRF, rate-limit, body abuse, auth-oracle, business logic, race — loopback only, dummy only |
| Before/after score | 0 to 100 across 6 dimensions, with deduction math and an ordered kill-list |
| 3D report | Single-file `breach-report.html`: typing timeline, attack table, animated chart, ports, redacted secrets, kill-list, Three.js background |

## How to trigger

Tell the agent in chat, for example:

```text
desconfie de tudo neste projeto
rode um sweep paranoico aqui
simule um ataque contra minha app e mate as brechas
check 10 commits security + gitleaks sweep
me dá a nota de segurança antes e depois
```

The agent shows the simulated-attack notice and the environment question before any probe.

## The 8 sweep phases

1. **Phase 0 (environment).** Blocking question + simulation notice. `prod` = read-only, no exceptions.
2. **Phase 1 (forensics).** Diff of the 10 commits against a signal matrix (secret, auth, exposure, sink, weak crypto, dependency). A secret that reached remote = `COMPROMISED`, rotate first.
3. **Phase 2 (exposure).** `scripts/port-exposure.py` + config, route, and transport review. `0.0.0.0` without auth in prod = CRITICAL.
4. **Phase 3 (secrets).** `python3 scripts/secret-sweep.py --path . --history` (redacted JSON output). Covers CI/logs/backups.
5. **Phase 3B/3C/3D (session, destructive paths, privacy).** Cookie/JWT/OAuth review, delete/move guard, PII inventory + TTL.
6. **Phase 4 (dead code).** Reachability from entry points to sinks; proposes a deletion patch per cluster.
7. **Phase 5 (self-attack).** A1 through A8 matrix in `local/dev` (see `references/adversary-tactics.md` and `advanced-ethical-hacker.md`). Each OPEN becomes 1 kill-list item.
8. **Phases 6 and 7 (score + HTML).** Scorecard + `findings.json` → `python3 scripts/generate-breach-report.py --findings findings.json --before 42 --after 78 --out breach-report.html`.

## Before/after scorecard

6 dimensions, 100 points. Starts full, subtracts per confirmed finding. A scanner candidate without proof scores nothing:

| Dimension | Weight | Deduction samples |
|---|---|---|
| Secrets | 20 | remote-reached secret −20; tracked `.env` −10; secret in CI/log −10 |
| Exposure | 20 | `0.0.0.0` without auth in prod −10; CORS `*` with credentials −8; exposed backup −8 |
| Auth/AuthZ | 20 | `alg:none` accepted −10; missing ownership check −10; cookie without flags −5 |
| Input/injection | 15 | attacker-input sink −10; path without guard −8 |
| Supply-chain | 10 | reachable critical CVE −7; unreviewed `postinstall` −5 |
| Hygiene/privacy | 15 | dead route with sink −8; PII without TTL −5 |

Required output:

```markdown
## Security Score: 42/100 -> 78/100 (+36)
| Dimension | Weight | Before | After | Key deduction |
...
### Pontos a sanar (grave -> leve)
1. [CRITICAL] api/key.ts:12 — token com alcance remoto — mover p/ env + rotate + filter-repo
```

An `After` score with an open CRITICAL in prod caps at 60.

## 3D HTML report

Single file, opens via `file://`, no build. One external dependency: Three.js via CDN (with 2D fallback and `prefers-reduced-motion` support).

It ships an asymmetric hero with an animated score duel, OPEN/BLOCKED/PORTS status, a severity-based 3D node radar (parallax + drift, capped pixel ratio, pauses off-tab), a typing timeline, an expected-vs-observed attack table, an animated before/after chart, ports, commits with redacted secrets, and a numbered kill-list. The schema lives in `examples/findings.example.json`; a finished sample is in `examples/kill-list.md`.

## Install

Three paths: skill only (`INSTALL_SKILL.md`), MCP only (`INSTALL_MCP.md`), or both. Each file holds a ready-to-paste agent prompt.

Via npx (full skill):

```bash
npx paranoid-agent-skill
```

Installs into every standard skills dir that already exists (`~/.agents/skills`, `~/.claude/skills`, `~/.codex/skills`); creates `~/.agents/skills` when none exists. For a specific target:

```bash
npx paranoid-agent-skill --dir ~/.agents/skills
npx paranoid-agent-skill --dir /your/project/.agents/skills --force
```

Manual: copy the folder into the agent skills directory:

```bash
cp -r paranoid-agent ~/.agents/skills/
# or, in plugin layout: <plugin>/skills/paranoid-agent/
```

No build step, stdlib-only Python, no network access.

## Step-by-step use

Via MCP (preferred when the client supports it): register `paranoid-agent-mcp` as a server (see `references/mcp.md`) and call `secret_sweep`, `port_inventory`, and `render_breach_report` straight from the agent, with no scan output pasted into chat.

Via terminal:

```bash
# 1. forensics + secrets + ports
git log -n 10 --patch --no-merges -U3 -- . ':(exclude)package-lock.json'
python3 scripts/secret-sweep.py --path /your/project --history
python3 scripts/port-exposure.py --path /your/project

# 2. build findings.json (see examples/findings.example.json)

# 3. render the report
python3 scripts/generate-breach-report.py \
  --findings findings.json --before 42 --after 78 \
  --out breach-report.html
```

## Real output sample

From `examples/kill-list.md`:

```markdown
1. [CRITICAL] api/key.ts:12 (commit a1b2c3d) — token vazado com alcance remoto
2. [CRITICAL] 0.0.0.0:3000 sem auth em prod — remover /debug
3. [HIGH] GET /api/users/:id retorna vizinho (A2 OPEN) — checar owner_id
```

## Skill layout

```text
paranoid-agent/
├── SKILL.md
├── README.md
├── README.en.md
├── INSTALL_SKILL.md
├── INSTALL_MCP.md
├── LICENSE
├── package.json
├── bin/
│   ├── cli.mjs
│   ├── install.mjs
│   └── mcp.mjs
├── assets/
│   ├── breach-report-template.html
│   └── readme/
│       ├── paranoid-agent-logo.svg
│       └── paranoid-agent-logo-motion.md
├── examples/
│   ├── findings.example.json
│   └── kill-list.md
├── references/
│   ├── advanced-ethical-hacker.md
│   ├── adversary-tactics.md
│   ├── env-playbooks.md
│   ├── git-forensics.md
│   ├── privacy-data.md
│   ├── mcp.md
│   ├── report-spec.md
│   └── scorecard.md
└── scripts/
    ├── generate-breach-report.py
    ├── port-exposure.py
    └── secret-sweep.py
```

## Scripts

| Script | Role | Flags |
|---|---|---|
| `secret-sweep.py` | 25+ secret regexes over the worktree + 10 commits + risky filenames; redacted JSON output | `--path`, `--history/--no-history`, `--out` |
| `port-exposure.py` | Listeners via `ss`/`netstat` + `EXPOSE`/compose; no external scan | `--path`, `--out` |
| `generate-breach-report.py` | Injects `findings.json` into the template; refuses raw secrets | `--findings`, `--before`, `--after`, `--out` |

## Internal references

- `env-playbooks.md` — local vs prod rules
- `git-forensics.md` — 10-commit signal matrix
- `adversary-tactics.md` — contained self-attack A1–A8 matrix
- `advanced-ethical-hacker.md` — recon, mapping, analysis, proof, and fix
- `privacy-data.md` — PII, purpose, TTL, rights, sharing
- `mcp.md` — MCP server 3-tool contract
- `scorecard.md` — 0–100 rubric
- `report-spec.md` — HTML spec (design system, schema, redaction)

## Safety rules

- Every secret ships redacted in chat, scorecard, and HTML. The generator aborts on a private-key body or raw secret.
- `prod/server` = declared read-only; active probes refused with a kill plan.
- Dummies and fixtures only; stop at the first proof byte; no exfiltration, persistence, or real brute force.
- Score only after triage: confirmed data→sink flow, respected framework mitigation, discarded regex self-match.

## Known limits

- The scanner false-positives on its own pattern files; the skill requires context confirmation before scoring.
- `port-exposure.py` inventories local listeners, never scans the network.
- The animated logo GIF needs approval + exporter tooling (`animated-readme-logo`); SVG + motion spec already ship.
