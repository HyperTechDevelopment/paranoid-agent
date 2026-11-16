#!/usr/bin/env python3
"""Paranoid secret sweep: worktree + last-10-commits, redacted JSON output."""
import argparse, json, os, re, subprocess, sys

RULES = [
    ("aws-key", r"AKIA[0-9A-Z]{16}"),
    ("aws-secret", r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{30,}"),
    ("github-pat", r"ghp_[A-Za-z0-9]{20,}"),
    ("github-oauth", r"gho_[A-Za-z0-9]{20,}"),
    ("github-token-generic", r"github_pat_[A-Za-z0-9_]{10,}"),
    ("gitlab-token", r"glpat-[A-Za-z0-9_\-]{12,}"),
    ("slack-token", r"xox[baprs]-[A-Za-z0-9\-]{8,}"),
    ("stripe-live", r"sk-live-[A-Za-z0-9]{10,}"),
    ("stripe-test", r"sk-test-[A-Za-z0-9]{10,}"),
    ("openai-key", r"sk-[A-Za-z0-9]{20,}"),
    ("anthropic-key", r"sk-ant-[A-Za-z0-9\-_]{10,}"),
    ("google-api", r"AIza[0-9A-Za-z\-_]{20,}"),
    ("jwt", r"eyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}"),
    ("private-key", r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ("azure-key", r"(?i)AccountKey\s*=\s*[A-Za-z0-9+/=]{40,}"),
    ("heroku-key", r"(?i)heroku.*[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}"),
    ("twilio-sid", r"AC[a-f0-9]{32}"),
    ("sendgrid-key", r"SG\.[A-Za-z0-9_\-]{16,}"),
    ("discord-token", r"[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}"),
    ("npm-token", r"npm_[A-Za-z0-9]{20,}"),
    ("generic-password", r"(?i)(?:password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{6,}['\"]"),
    ("mongo-uri", r"mongodb(?:\+srv)?://[^\s'\"]+:[^\s'\"]+@[^\s'\"]+"),
    ("postgres-uri", r"postgres(?:ql)?://[^\s'\"]+:[^\s'\"]+@[^\s'\"]+"),
    ("redis-uri", r"redis://(?::[^\s@'\"]+@)?[^\s'\"]+"),
    ("connection-string-pass", r"(?i)(?:connectionstring|connstr)[^=]*=\s*['\"][^'\"]*(?:password|pwd)=[^'\";]+"),
    ("bearer-hardcoded", r"(?i)bearer\s+[A-Za-z0-9_\-\.=~+/]{20,}"),
]

SKIP_DIRS = {".git", "node_modules", "dist", "build", ".next", "coverage", "__pycache__", "vendor"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".ttf", ".eot", ".map", ".lock"}
MAX_BYTES = 512_000

def redact(rule, match):
    s = match.strip().strip("'\"")
    if rule == "private-key":
        return "-----BEGIN PRIVATE KEY-----***REDACTED***"
    if len(s) <= 10:
        return s[:2] + "***" + s[-2:]
    return s[:6] + "***" + s[-4:]

def scan_text(text, source, out):
    for rule, pat in RULES:
        for m in re.finditer(pat, text):
            raw = m.group(0)
            # never emit full secret for high-risk rules
            out.append({"rule": rule, "source": source,
                        "redacted": redact(rule, raw), "length": len(raw)})

RISKY_FILES = [
    ("backup-dump", r".*\.(bak|backup|dump|sql|sqlite|db)$"),
    ("env-tracked", r"(^|/)\.env(\..+)?$"),
    ("private-key-file", r"(^|/)(id_rsa|id_ed25519|.*\.pem|.*\.key)$"),
    ("ci-definition", r"(^|/)\.(github/workflows|gitlab-ci\.yml|jenkinsfile)$"),
]

def scan_filenames(root, out):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, root).replace(os.sep, "/")
            for rule, pat in RISKY_FILES:
                if re.match(pat, rel.lower()) or re.match(pat, fn.lower()):
                    out.append({"rule": rule, "source": rel,
                                "redacted": fn[:4] + "***", "length": 0})

def scan_worktree(root, out):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, root)
            if any(rel.endswith(e) for e in SKIP_EXT):
                continue
            try:
                if os.path.getsize(p) > MAX_BYTES:
                    continue
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    scan_text(f.read(), rel, out)
            except OSError:
                continue

def scan_history(root, out):
    try:
        r = subprocess.run(["git", "-C", root, "log", "-n", "10", "--patch", "--no-merges",
                            "-U0", "--", ".", ":(exclude)package-lock.json"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=30)
    except Exception:
        return
    if r.returncode != 0:
        return
    cur = ""
    for line in r.stdout.splitlines():
        if line.startswith("commit "):
            cur = line.split()[1][:7]
        for rule, pat in RULES:
            for m in re.finditer(pat, line):
                if line.startswith("+") and not line.startswith("+++"):
                    out.append({"rule": rule, "source": f"commit:{cur}",
                                "redacted": redact(rule, m.group(0)), "length": len(m.group(0))})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=".")
    ap.add_argument("--history", action="store_true", default=True)
    ap.add_argument("--no-history", dest="history", action="store_false")
    ap.add_argument("--redact", action="store_true", default=True)
    ap.add_argument("--format", default="json", choices=["json"])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    root = os.path.abspath(a.path)
    hits = []
    scan_worktree(root, hits)
    scan_filenames(root, hits)
    if a.history:
        scan_history(root, hits)
    # de-dupe
    seen, uniq = set(), []
    for h in hits:
        k = (h["rule"], h["source"], h["redacted"])
        if k not in seen:
            seen.add(k)
            uniq.append(h)
    payload = {"target": root, "hits": uniq, "count": len(uniq),
               "note": "values redacted; any hit with remote reach = COMPROMISED, rotate first"}
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)

if __name__ == "__main__":
    sys.exit(main())
