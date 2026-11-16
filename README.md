# ▓ Paranoid Agent

[English](README.en.md) | **Português**

> Ataque simulado para avaliar e medir a segurança deste projeto. Nenhum dado real é tocado ou exfiltrado. Cada falha encontrada vira solução na kill-list.

![logo](assets/readme/paranoid-agent-logo.svg)

Skill standalone de sweep paranóico. Ela desconfia de tudo e caça portas abertas, segredos vazados, código morto e brechas exploráveis. Ordena da mais grave à mais leve, pergunta o ambiente (`local/dev` ou `prod/server`), audita os últimos 10 commits, simula ataques contidos contra a própria aplicação para matar cada brecha, dá nota de segurança antes e depois e gera um relatório HTML 3D estilo hacker-terminal com gráficos animados.

- **Trigger**: `desconfie de tudo`, `sweep paranoico`, `caça brecha`, `simule ataque`, `mata porta aberta`, `audit paranoid`, `check 10 commits security`, `gitleaks sweep`, `nota de segurança antes e depois`
- **Dependências externas**: nenhuma. Tudo vive dentro de `paranoid-agent/`.
- **Segurança**: segredos sempre redatados, `prod` = read-only, probes só em loopback com dados dummy.

## Índice

1. [O que ela faz](#o-que-ela-faz)
2. [Como acionar](#como-acionar)
3. [As 8 fases do sweep](#as-8-fases-do-sweep)
4. [Scorecard antes/depois](#scorecard-antesdepois)
5. [Relatório HTML 3D](#relatório-html-3d)
6. [Instalação](#instalação)
7. [Uso passo a passo](#uso-passo-a-passo)
8. [Exemplo real de saída](#exemplo-real-de-saída)
9. [Estrutura da skill](#estrutura-da-skill)
10. [Scripts](#scripts)
11. [Referências internas](#referências-internas)
12. [Regras de segurança](#regras-de-segurança)
13. [Limites conhecidos](#limites-conhecidos)

## O que ela faz

| Capacidade | Detalhe |
|---|---|
| Interroga o ambiente | Pergunta bloqueante `local/dev` ou `prod/server` antes de qualquer scan; sem resposta clara, assume `prod` (read-only) |
| Forense de 10 commits | `git log -n 10 --patch`: segredo introduzido, auth removida, CORS `*`, sink perigoso, dependência nova |
| Superfície exposta | Listeners (`ss`/`netstat`), `Dockerfile EXPOSE`, portas do compose, rotas `/debug` `/admin` `/metrics`, CORS, cookies, HSTS |
| Caça segredos | 25+ padrões (AWS, GitHub, Slack, Stripe, OpenAI, JWT, private keys, URIs com credencial) + nomes de arquivo (`*.bak`, `*.sql`, `.env`, `*.pem`, CI) |
| Sessão e tokens | Flags de cookie, JWT `alg:none`/expiry, OAuth state+PKCE, anti-enumeração |
| Paths destrutivos | Resolve symlink, exige raiz allowlisted + profundidade + ownership antes de delete/move |
| Privacidade de dados | Classifica PII, exige propósito, TTL e delete path (backups, caches, índices), sem PII em logs |
| Código morto | Rotas órfãs, auth duplicada divergente, flags mortas alcançáveis |
| Auto-ataque contido | Header spoof, IDOR/BOLA, traversal, SSRF, rate-limit, body abuse, auth-oracle, lógica de negócio, race — só loopback, só dummy |
| Score antes/depois | 0 a 100 em 6 dimensões, com matemática das deduções e kill-list ordenada |
| Relatório 3D | Single-file `breach-report.html`: timeline com typing, tabela de ataques, gráfico animado, portas, segredos redatados, kill-list, fundo Three.js |

## Como acionar

No chat com o agente, diga por exemplo:

```text
desconfie de tudo neste projeto
rode um sweep paranoico aqui
simule um ataque contra minha app e mate as brechas
check 10 commits security + gitleaks sweep
me dá a nota de segurança antes e depois
```

O agente exibe o aviso de ataque simulado e a pergunta de ambiente antes de qualquer probe.

## As 8 fases do sweep

1. **Fase 0 (ambiente).** Pergunta bloqueante + aviso de simulação. `prod` = read-only, sem exceção.
2. **Fase 1 (forense).** Diff dos 10 commits com matriz de sinais (segredo, auth, exposição, sink, cripto fraca, dependência). Segredo que chegou ao remoto = `COMPROMISED`, rotacione primeiro.
3. **Fase 2 (exposição).** `scripts/port-exposure.py` + revisão de config, rotas, transporte. `0.0.0.0` sem auth em prod = CRITICAL.
4. **Fase 3 (segredos).** `python3 scripts/secret-sweep.py --path . --history` (saída JSON redatada). Inclui CI/logs/backups.
5. **Fase 3B/3C/3D (sessão, paths destrutivos, privacidade).** Revisão de cookies/JWT/OAuth, guard de delete/move, inventário PII + TTL.
6. **Fase 4 (código morto).** Alcançabilidade de entry points até sinks; propõe patch de deleção por cluster.
7. **Fase 5 (auto-ataque).** Matriz A1 a A8+ em `local/dev` (ver `references/adversary-tactics.md` e `advanced-ethical-hacker.md`). Cada OPEN vira 1 item da kill-list.
8. **Fases 6 e 7 (score + HTML).** Scorecard + `findings.json` → `python3 scripts/generate-breach-report.py --findings findings.json --before 42 --after 78 --out breach-report.html`.

## Scorecard antes/depois

6 dimensões, 100 pontos. Começa cheio, subtrai por achado confirmado. Candidato de scanner sem prova não pontua:

| Dimensão | Peso | Exemplos de dedução |
|---|---|---|
| Secrets | 20 | segredo com alcance remoto −20; `.env` trackeado −10; segredo em CI/log −10 |
| Exposure | 20 | `0.0.0.0` sem auth em prod −10; CORS `*` com credential −8; backup exposto −8 |
| Auth/AuthZ | 20 | `alg:none` aceito −10; sem ownership check −10; cookie sem flags −5 |
| Input/injection | 15 | sink com input de atacante −10; path sem guard −8 |
| Supply-chain | 10 | CVE crítico alcançável −7; `postinstall` não revisado −5 |
| Hygiene/privacidade | 15 | rota morta com sink −8; PII sem TTL −5 |

Saída obrigatória:

```markdown
## Security Score: 42/100 -> 78/100 (+36)
| Dimension | Weight | Before | After | Key deduction |
...
### Pontos a sanar (grave -> leve)
1. [CRITICAL] api/key.ts:12 — token com alcance remoto — mover p/ env + rotate + filter-repo
```

Nota `After` com CRITICAL aberto em prod é capada em 60.

## Relatório HTML 3D

Single-file, abre via `file://`, sem build. Dependência externa única: Three.js via CDN (com fallback 2D e respeito a `prefers-reduced-motion`).

Traz hero assimétrico com duelo de score animado, status OPEN/BLOCKED/PORTAS, radar 3D de nós por severidade (parallax + drift, pixel-ratio limitado, pausa fora da aba), timeline com typing, tabela de ataques × esperado, gráfico antes/depois animado, portas, commits com segredos redatados e kill-list numerada. O schema está em `examples/findings.example.json`; há um exemplo pronto em `examples/kill-list.md`.

## Instalação

Três caminhos: só a skill (`INSTALL_SKILL.md`), só o MCP (`INSTALL_MCP.md`), ou os dois. Cada arquivo tem um prompt pronto para colar no agente.

Via npx (skill completa):

```bash
npx paranoid-agent-skill
```

Instala em cada diretório padrão de skills que já existe (`~/.agents/skills`, `~/.claude/skills`, `~/.codex/skills`); se nenhum existir, cria `~/.agents/skills`. Para um destino específico:

```bash
npx paranoid-agent-skill --dir ~/.agents/skills
npx paranoid-agent-skill --dir /seu/projeto/.agents/skills --force
```

Manual: copie a pasta para o diretório de skills do agente:

```bash
cp -r paranoid-agent ~/.agents/skills/
# ou, no layout de plugin: <plugin>/skills/paranoid-agent/
```

Não precisa de build, usa só a stdlib do Python e não acessa a rede.

## Uso passo a passo

Via MCP (recomendado quando o cliente suporta): configure `paranoid-agent-mcp` como servidor (ver `references/mcp.md`) e chame `secret_sweep`, `port_inventory` e `render_breach_report` direto do agente, sem colar output de scan no chat.

Via terminal:

```bash
# 1. forense + segredos + portas
git log -n 10 --patch --no-merges -U3 -- . ':(exclude)package-lock.json'
python3 scripts/secret-sweep.py --path /seu/projeto --history
python3 scripts/port-exposure.py --path /seu/projeto

# 2. monte findings.json (veja examples/findings.example.json)

# 3. gere o relatório
python3 scripts/generate-breach-report.py \
  --findings findings.json --before 42 --after 78 \
  --out breach-report.html
```

## Exemplo real de saída

Trecho de `examples/kill-list.md`:

```markdown
1. [CRITICAL] api/key.ts:12 (commit a1b2c3d) — token vazado com alcance remoto
2. [CRITICAL] 0.0.0.0:3000 sem auth em prod — remover /debug
3. [HIGH] GET /api/users/:id retorna vizinho (A2 OPEN) — checar owner_id
```

## Estrutura da skill

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

| Script | Função | Flags |
|---|---|---|
| `secret-sweep.py` | 25+ regex de segredo na worktree + 10 commits + nomes de arquivo arriscados; saída JSON redatada | `--path`, `--history/--no-history`, `--out` |
| `port-exposure.py` | Listeners via `ss`/`netstat` + `EXPOSE`/compose; sem scan externo | `--path`, `--out` |
| `generate-breach-report.py` | Injeta `findings.json` no template; recusa segredo cru | `--findings`, `--before`, `--after`, `--out` |

## Referências internas

- `env-playbooks.md` — regras local vs prod
- `git-forensics.md` — matriz de sinais nos 10 commits
- `adversary-tactics.md` — matriz A1–A8 de auto-ataque contido
- `advanced-ethical-hacker.md` — recon, mapping, análise, prova e fix
- `privacy-data.md` — PII, propósito, TTL, direitos, sharing
- `mcp.md` — contrato das 3 tools do servidor MCP
- `scorecard.md` — rubrica 0–100
- `report-spec.md` — spec do HTML (design system, schema, redação)

## Regras de segurança

- Todo segredo sai redatado no chat, no scorecard e no HTML. O gerador aborta se achar corpo de private key ou segredo cru.
- `prod/server` = read-only declarado; probe ativo recusado com plano de kill.
- Dummies e fixtures apenas; parar no primeiro byte de prova; sem exfiltração, persistência ou força bruta real.
- Só pontua após triagem: fluxo dado→sink confirmado, mitigação de framework respeitada e self-match de regex descartado.

## Limites conhecidos

- Scanner gera falsos positivos nos próprios arquivos de padrão; a skill manda confirmar contexto antes de pontuar.
- `port-exposure.py` inventaria listeners locais, não faz scan de rede.
- GIF animado do logo requer aprovação + tooling do exporter (`animated-readme-logo`); SVG + motion spec já entregues.
