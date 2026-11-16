# Git Forensics — Last 10 Commits

## Commands

```bash
git log -n 10 --pretty=format:'%H %ad %an %s' --date=short --no-merges
git log -n 10 --patch --no-merges -U3 -- . ':(exclude)package-lock.json' ':(exclude)pnpm-lock.yaml' ':(exclude)*.min.js' ':(exclude)*.map'
git log -n 10 --diff-filter=A --name-only --pretty=format:'--- %H %s'
```

## Hunt Matrix

| Signal | Patch pattern | Severity hint |
|---|---|---|
| Secret added | `AKIA[0-9A-Z]{16}`, `ghp_`, `gho_`, `xox[bap]-`, `sk-live-`, `-----BEGIN (RSA )?PRIVATE KEY`, `mongodb://.*:.*@`, `postgres://.*:.*@` | CRITICAL |
| Auth removed | `-.*requireAuth`, `-.*isAuthenticated`, `+.*skipAuth`, `+.*allowUnauthorized`, `-.*middleware.*auth` | CRITICAL/HIGH |
| Exposure widened | `+.*Access-Control-Allow-Origin.*\*`, `+.*CORS.*origin.*\*`, `+.*0\.0\.0\.0`, `+.*EXPOSE`, `+.*/debug`, `+.*/metrics.*auth.*false` | HIGH |
| Sink added | `+.*eval\(`, `+.*exec\(`, `+.*shell:\s*true`, `+.*innerHTML`, `+.*dangerouslySetInnerHTML`, `+.*query.*\+.*req\.` | HIGH |
| Crypto weakened | `-.*bcrypt`, `-.*argon2`, `+.*md5.*password`, `+.*sha1.*password`, `+.*verify.*false` | HIGH |
| Dep risk | `+.*dependencies`, lockfile unchanged, `postinstall` script added | MEDIUM |

## Rules

- Inspect full diff, not commit message. A message saying `fix` can hide `CORS *`.
- Track renames: secret moved file-to-file is still exposure.
- If secret appears in any of 10 commits and remote exists (`git remote -v` non-empty), mark COMPROMISED. Recommend rotation before purge.
- Purge requires history rewrite (`git filter-repo`, BFG) plus rotation plus invalidating caches. Never present purge alone as fix.
- Output per hit: short hash, date, file, line context, redacted snippet, kill action.
