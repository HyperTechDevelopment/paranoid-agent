# Report Spec — Hacker-Terminal HTML 3D

## Artifact

Single file `breach-report.html`. Open via `file://`, no build. Inline CSS/JS. Only external dependency: Three.js CDN with graceful fallback when offline or under `prefers-reduced-motion`.

## Design System (awwwards + ui-taste + 3d-web-experience)

Concept: incident-response radar room. Asymmetric hero (readout left, radar status right) — never centered hero over blob. One signature moment: the score duel `antes → depois` with animated duel bars. Palette hacker-terminal, type mono fluid scale, one radius (14px), one easing family, motion on transform/opacity only, single rAF clock. Loader with real progress fades to hero intro; sections reveal via IntersectionObserver; tables become labeled cards under 760px. Empty states explicit. Skip link, landmarks, focus-visible, AA contrast, canvas with role/aria-label.

## Sections (in order)

1. Header: `PARANOID AGENT`, mandatory attack notice, ENV badge, date, target, score duel count-up `before -> after` with duel bars.
2. Timeline `O que foi feito`: env gate, 10 commits scanned, files scanned, ports inventoried, attacks run.
3. `Ataques simulados`: table Technique / Target / Dummy payload / Expected / Observed / Verdict pill `BLOCKED` green / `OPEN` red. Skipped-in-prod rows marked `SKIPPED (prod read-only)`.
4. `Antes vs Depois`: animated grouped bars (6 dimensions) + delta line, canvas 2D, animated draw on scroll into view, responsive resize, `prefers-reduced-motion` disables animation.
5. `Portas identificadas`: cards `host:port -> service`, transport, auth status, severity color. Mirror list for mobile when WebGL unavailable.
6. `Commits com segredos (gitleaks-style)`: commit short hash, date, file:line, rule id (e.g. `github-pat`, `aws-key`, `private-key`), redacted match `ghp_***9f2c`. Never full value. Banner `COMPROMISED — rotate first` when remote exists.
7. `Kill-list + Pontos a sanar`: ordered CRITICAL first, each with evidence pointer and patch/command block.
8. Footer: scope limits, prod disclaimer when applicable, generator version.

## findings.json Schema (minimal)

```json
{
  "env": "local/dev",
  "target": "my-app",
  "before": 42, "after": 78,
  "attacks": [{"id":"A2","target":"/api/users/:id","payload":"GET neighbor id","expected":"403","observed":"200 (dummy PII)","verdict":"OPEN"}],
  "ports": [{"host":"127.0.0.1","port":3000,"service":"nextjs","auth":"none","severity":"HIGH"}],
  "leaks": [{"commit":"a1b2c3d","date":"2026-11-10","file":"api/key.ts:12","rule":"github-pat","redacted":"ghp_***9f2c","remote_reached":true}],
  "kills": [{"sev":"CRITICAL","where":"api/key.ts:12","impact":"hardcoded token","fix":"move to env + rotate"}],
  "scores": {"secrets":[5,18],"exposure":[8,16],"auth":[10,15],"input":[12,12],"supply":[5,7],"hygiene":[2,10]}
}
```

## Palette and Motion

- Bg `#070b11`, panels `#0e141d`, text `#d3deeb`, neon `#00ff41`, amber `#ffb454`, red `#ff4d5e`, cyan `#41e6ff`.
- Scanlines overlay, glow on CRITICAL, severity rails (not equal cards), grid backdrop.
- Animations: loader 450ms, count-up 900ms, duel bars 1s ease, chart draw 850ms with value labels, typing 10ms/char timeline, reveal on scroll. Three.js node network (ports=red/cyan nodes, links, fog) with pointer parallax + scroll drift, pixel-ratio capped, fewer particles on mobile, paused off-tab. Honor `prefers-reduced-motion` everywhere.
- Responsive: hero stacks <900px, tables to cards <760px, canvas 320px/280px.

## Redaction Rule

Generator rejects findings containing `-----BEGIN .*PRIVATE KEY-----` with key body or `sk-live-[A-Za-z0-9]{10,}` full value. Only redacted forms pass.
