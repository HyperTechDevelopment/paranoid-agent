## Security Score: 42/100 -> 78/100 (+36)

| Dimension | Weight | Before | After | Key deduction |
|---|---|---|---|---|
| Secrets | 20 | 5 | 18 | `api/key.ts:12` hardcoded `ghp_***9f2c` (-15) |
| Exposure | 20 | 8 | 16 | `0.0.0.0:3000` + `/debug` in prod (-12) |
| Auth/AuthZ | 20 | 10 | 15 | `/api/users/:id` sem ownership check (-10) |
| Input | 15 | 12 | 12 | sink com input incerto (-3, verificado framework escapa) |
| Supply-chain | 10 | 5 | 7 | `postinstall` não revisado (-5) |
| Hygiene | 15 | 2 | 10 | rota morta `/v1/legacy` alcançável (-8) |

### Pontos a sanar (grave -> leve)

1. [CRITICAL] `api/key.ts:12` (commit `a1b2c3d`) — token vazado com alcance a remote — kill: mover para env + `rotate token` + `git filter-repo` + invalidar cache.
   ```bash
   # 1. rotate no provedor PRIMEIRO
   # 2. remover do código
   sed -i 's/ghp_.*/process.env.GITHUB_TOKEN/' api/key.ts
   ```
2. [CRITICAL] `0.0.0.0:3000` sem auth em prod — kill: bind `127.0.0.1` ou exigir auth + remover `/debug`.
3. [HIGH] `GET /api/users/:id` retorna vizinho (A2 OPEN) — kill: checar `owner_id === session.user_id` antes de ler.
   ```ts
   if (row.owner_id !== session.user_id) return res.status(403).end();
   ```
4. [HIGH] CORS `*` com credentials — kill: allowlist explícita de origens.
5. [MEDIUM] `postinstall` não revisado — kill: auditar script + fixar versão + `npm audit signatures`.
6. [LOW] `/v1/legacy` morta mas roteada — kill: deletar handler + teste de regressão.
